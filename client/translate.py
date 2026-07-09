#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cc-lingua — MessageDisplay hook for Claude Code (open-source; you supply your own
DeepSeek API key, bought from DeepSeek — none is bundled with this project).

Claude Code reasons and replies in ENGLISH (best reasoning, no CJK "token tax");
this hook translates only the ON-SCREEN narration into your language by calling the
DeepSeek API directly with your own key. Code, inline code, file paths, shell
commands, URLs, numbers and markdown structure are preserved verbatim.

Display-only: the saved transcript and the model's context stay English; only the
rendered text is swapped. It FAILS OPEN on anything unexpected (toggle off /
non-final / empty / already in the target language / missing key / network error)
-> prints nothing -> the original English is shown. It never blanks or blocks a
message.

Files (all under ~/.claude/cc-lingua/):
    enabled       on/off switch — this file must exist for the hook to act
    config.json   { "api_key", "base_url", "model", "target" }
    cache/        identical strings are translated once, then reused (saves money)
    hook.log      one line per event, for debugging

Env override: DEEPSEEK_API_KEY (takes precedence over config.json).

Privacy: no telemetry. The only network call is to your configured `base_url`
(DeepSeek by default), sending only the text Claude Code was about to display.
stdlib only — no pip install required.
"""
import sys, os, re, json, time, hashlib, urllib.request

HOME    = os.path.expanduser("~")
BASE    = os.path.join(HOME, ".claude", "cc-lingua")
TOGGLE  = os.path.join(BASE, "enabled")
CONF    = os.path.join(BASE, "config.json")
CACHE   = os.path.join(BASE, "cache")
HOOKLOG = os.path.join(BASE, "hook.log")

SYS_PROMPT = (
    "You are a translation engine. Translate the user's text into {target}. "
    "Output ONLY the translation: no preamble, no notes, no explanation, no quoting. "
    "Do NOT translate or alter -- reproduce verbatim -- code blocks, inline code, "
    "file paths, shell commands, URLs, numbers, and identifiers. "
    "Preserve all markdown structure and formatting exactly."
)

# Targets whose script we can cheaply detect, to skip text that is already translated.
CJK_TARGETS = ("chinese", "japanese", "korean", "中文", "日", "韓", "한")


def logline(sid, final, action, ms="-", note=""):
    try:
        with open(HOOKLOG, "a", encoding="utf-8") as f:
            f.write("%s sid=%s final=%s %s ms=%s %s\n"
                    % (time.strftime("%H:%M:%S"), sid, final, action, ms, note))
    except Exception:
        pass


def stop():
    sys.exit(0)


def load_conf():
    try:
        with open(CONF, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def cache_path(key):
    return os.path.join(CACHE, hashlib.sha256(key.encode("utf-8")).hexdigest() + ".txt")


def cache_get(key):
    try:
        with open(cache_path(key), encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def cache_put(key, value):
    try:
        os.makedirs(CACHE, exist_ok=True)
        with open(cache_path(key), "w", encoding="utf-8") as f:
            f.write(value)
    except Exception:
        pass


def emit(text):
    sys.stdout.write(json.dumps({"hookSpecificOutput": {
        "hookEventName": "MessageDisplay", "displayContent": text}}))


def deepseek(base_url, api_key, model, target, text, timeout=9.5):
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYS_PROMPT.format(target=target)},
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read().decode("utf-8"))
    return ((d.get("choices") or [{}])[0].get("message", {}) or {}).get("content", "") or ""


def main():
    if not os.path.exists(TOGGLE):
        stop()
    raw = sys.stdin.read()
    if not raw.strip():
        stop()
    try:
        data = json.loads(raw)
    except Exception:
        logline("?", "?", "skip:badjson"); stop()

    sid = (data.get("session_id") or "?")[:8]
    final = data.get("final")
    if final is False:
        logline(sid, final, "skip:nonfinal"); stop()
    text = data.get("delta") or ""
    if not text.strip():
        logline(sid, final, "skip:empty"); stop()

    cfg = load_conf()
    api_key  = os.environ.get("DEEPSEEK_API_KEY") or cfg.get("api_key") or ""
    base_url = cfg.get("base_url") or "https://api.deepseek.com"
    model    = cfg.get("model") or "deepseek-v4-flash"
    target   = cfg.get("target") or "Simplified Chinese"
    if not api_key:
        logline(sid, final, "skip:nokey"); stop()

    # Already in the target language? (only decidable for CJK targets — skip re-translation.)
    if any(t in target.lower() for t in CJK_TARGETS):
        cjk = sum(1 for ch in text if "一" <= ch <= "鿿"      # CJK Han
                  or "぀" <= ch <= "ヿ"                        # Hiragana + Katakana
                  or "가" <= ch <= "힣")                       # Hangul syllables
        letters = sum(1 for ch in text if ("a" <= ch <= "z") or ("A" <= ch <= "Z"))
        if cjk > letters:
            logline(sid, final, "skip:alreadytarget", note="len=%d" % len(text)); stop()

    ckey = model + "|" + target + "|" + text
    hit = cache_get(ckey)
    if hit is not None:
        logline(sid, final, "ok:cache", note="len=%d" % len(text))
        emit(hit); stop()

    t0 = time.time()
    try:
        out = deepseek(base_url, api_key, model, target, text)
    except Exception as e:
        logline(sid, final, "FAIL:api", ms=int((time.time() - t0) * 1000),
                note="%r len=%d" % (e, len(text))); stop()

    out = re.sub(r"<think>.*?</think>", "", out, flags=re.DOTALL).strip()
    if not out:
        logline(sid, final, "FAIL:empty", ms=int((time.time() - t0) * 1000)); stop()

    cache_put(ckey, out)
    logline(sid, final, "ok", ms=int((time.time() - t0) * 1000), note="len=%d" % len(text))
    emit(out)
    sys.exit(0)


try:
    main()
except SystemExit:
    raise
except Exception:
    # Absolute last-resort fail-open: show the original English rather than break the UI.
    sys.exit(0)

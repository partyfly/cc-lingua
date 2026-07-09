# cc-lingua · Install (Claude Code: read this file and execute the steps)

> **Instruction to Claude Code:** install cc-lingua for the current user, so that
> your English narration is translated to the user's language on the **display
> layer** while you keep reasoning and replying in English. Write ONLY under
> `~/.claude/cc-lingua/`, `~/.claude/settings.json`, and `~/.claude/CLAUDE.md`.
> Briefly tell the user what each step did. Everything fails open — if the user
> declines a step, skip it and continue.
>
> `REPO_DIR` below is the directory of this repository (where this INSTALL.md
> lives); `client/translate.py` sits next to it.

## Step 1 · Create the config directory
```bash
mkdir -p ~/.claude/cc-lingua
```

## Step 2 · Install the hook script
Copy the client into place (single source of truth — do not retype it):
```bash
cp "REPO_DIR/client/translate.py" ~/.claude/cc-lingua/translate.py
```

## Step 3 · Choose the display language, get a key, write the config

**First decide `target` — the language Claude Code's narration is translated into:**
- **Default to the language the user has been writing to you in THIS
  conversation.** If they've been talking to you in Chinese → `"Simplified
  Chinese"`; in Japanese → `"Japanese"`; in Korean → `"Korean"`; in Spanish →
  `"Spanish"`, and so on.
- **If that is unclear** — e.g. they've been writing to you in English, or mixing
  languages — **ask them explicitly** which language they want the on-screen text
  translated into. Do not silently pick a default.

Then ask for their DeepSeek API key. If they don't have one, tell them to create
one at **https://platform.deepseek.com/api_keys** (top up a few dollars;
translation is cheap). Now write `~/.claude/cc-lingua/config.json`, substituting
the key and the `target` language you settled on above:
```json
{
  "api_key": "PASTE_THE_USER_DEEPSEEK_KEY",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-v4-flash",
  "target": "<the language you determined, e.g. Simplified Chinese>"
}
```
Notes:
- Keep `config.json` local; it holds a secret and must never be committed.
- `deepseek-v4-flash` is DeepSeek's cheapest tier and the right default. (Do NOT use
  `deepseek-chat` — it is deprecated on 2026-07-24.) For higher quality at ~3x the
  price, set `deepseek-v4-pro`.
- `target` is free text — any language name works.

## Step 4 · Register the MessageDisplay hook
Resolve the absolute python3 path first:
```bash
command -v python3      # use this absolute path as <PY> below
```
Merge this object into the `hooks.MessageDisplay` array in
`~/.claude/settings.json` (create the file if missing; **append — do not
overwrite** existing hooks; replace `<PY>` and `<USER_HOME>` with real absolute
values):
```json
{ "matcher": "", "hooks": [ { "type": "command", "command": "<PY> <USER_HOME>/.claude/cc-lingua/translate.py", "timeout": 12 } ] }
```

## Step 5 · Keep the model thinking in English (this is the whole point)
Append one line to `~/.claude/CLAUDE.md` (create it if missing; skip if a similar
line already exists):
```
Always reason and respond in English. (cc-lingua translates the display to the user's language.)
```

## Step 6 · Turn it on and self-check
```bash
touch ~/.claude/cc-lingua/enabled
```
`settings.json` hooks hot-reload, so **your very next reply should render in the
user's target language on their screen** while the transcript stays English.

Tell the user:
- Installed. Pause anytime: `rm ~/.claude/cc-lingua/enabled` (re-enable with `touch`).
- Debug log: `~/.claude/cc-lingua/hook.log`. `FAIL:api` there usually means a bad
  key, no balance, or a wrong `model`/`base_url`.
- Uninstall: read and run `UNINSTALL.md`.

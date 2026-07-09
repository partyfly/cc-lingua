# cc-lingua

**A native multi-language display layer for [Claude Code](https://claude.com/claude-code).**
The model keeps reasoning and replying in **English** (best reasoning, no CJK
"token tax"); cc-lingua translates only the **on-screen** narration into your
language. Code, file paths, shell commands, URLs and markdown are preserved
verbatim. It runs as a `MessageDisplay` hook that **fails open** — if anything
goes wrong, you just see the original English.

This is the **open-source, bring-your-own-key** edition: no server, no account,
no subscription. **No API key is bundled** — you buy your own from
[DeepSeek](https://platform.deepseek.com) (a paid third-party service, cents per
day) and the hook calls DeepSeek directly with it, stored locally. ~120 lines of
stdlib Python, nothing to run in the background.

> 中文用户：纯开源版，无服务器 / 账号 / 订阅。**本项目不含 key** —— 你需要自己到
> [DeepSeek 官网](https://platform.deepseek.com)购买一个 API key（第三方付费服务，
> 每天通常只花几分钱），翻译直接用你自己的 key。安装见下方「快速安装」。

---

## Install

You need [Claude Code](https://claude.com/claude-code) and a **DeepSeek API key**
(get one at <https://platform.deepseek.com/api_keys> and top up a few dollars —
translation is very cheap).

Then just paste this to Claude Code and let it install itself:

```
Clone https://github.com/partyfly/cc-lingua and follow its INSTALL.md to install cc-lingua for me.
```

Claude Code will clone the repo, read [`INSTALL.md`](INSTALL.md), write the hook,
pick your display language (the one you're chatting in — or it asks), take your
DeepSeek key, register the hook, and turn it on. Because `settings.json` hooks
hot-reload, **its very next reply appears in your language.**

> 把上面这句（替换成你的仓库地址）贴给 Claude Code 即可；它会读 `INSTALL.md` 自动装好，
> 中途会向你要 DeepSeek key。装完当前这条回复就变中文。

## How it works

```
Claude Code ──(English narration)──► MessageDisplay hook ──► DeepSeek ──► your language
   │                                        translate.py           on screen only
   └── transcript & model context stay English (full reasoning, no token tax)
```

- **Display-only.** The saved transcript and everything the model sees stay
  English. Only the rendered text on your screen is swapped.
- **Fail-open.** Toggle off, non-final chunk, empty text, already-in-your-language,
  missing key, network error → the hook prints nothing and you see the original
  English. It never blanks or blocks a message.
- **Code-safe.** The translation prompt reproduces code blocks, inline code, paths,
  commands, URLs, numbers and identifiers verbatim and preserves markdown.
- **Cached.** Identical strings are translated once and reused from
  `~/.claude/cc-lingua/cache/`, so repeats cost nothing.

## Configuration

`~/.claude/cc-lingua/config.json` (see [`client/config.example.json`](client/config.example.json)):

```json
{
  "api_key": "sk-your-deepseek-key",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-v4-flash",
  "target": "Simplified Chinese"
}
```

| field | meaning |
|-------|---------|
| `api_key` | Your DeepSeek key. Or set env `DEEPSEEK_API_KEY` (takes precedence). |
| `base_url` | OpenAI-compatible endpoint. DeepSeek by default; any compatible provider works. |
| `model` | `deepseek-v4-flash` — cheapest tier, the right default. `deepseek-v4-pro` for higher quality (~3x price). **Don't use `deepseek-chat`; it's deprecated 2026-07-24.** |
| `target` | Any language as free text: `"Simplified Chinese"`, `"Japanese"`, `"Korean"`, `"Spanish"`, `"French"`, … |

## Turn off / on / uninstall

```bash
rm    ~/.claude/cc-lingua/enabled   # pause (display back to English)
touch ~/.claude/cc-lingua/enabled   # resume
```

To uninstall, paste to Claude Code: *"follow UNINSTALL.md"* — or manually
`rm -rf ~/.claude/cc-lingua` and remove the hook from `~/.claude/settings.json`.
See [`UNINSTALL.md`](UNINSTALL.md).

## Cost & privacy

- **Cost.** `deepseek-v4-flash` is ~$0.14 / 1M input tokens, ~$0.28 / 1M output.
  Typical Claude Code sessions translate to cents per day; the local cache cuts
  repeats to zero. You pay DeepSeek directly.
- **Privacy.** No telemetry, no middleman. The only network call is from your
  machine to your configured `base_url`, sending only the narration text Claude
  Code was about to show you. Your `config.json` (with the key) is git-ignored and
  never leaves your machine.

## Debugging

`~/.claude/cc-lingua/hook.log` has one line per event. `FAIL:api` almost always
means a bad key, no account balance, or a wrong `model` / `base_url`. `skip:nokey`
means `config.json` has no `api_key`.

## License

MIT — see [LICENSE](LICENSE). Contributions welcome.

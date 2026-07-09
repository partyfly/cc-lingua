# cc-lingua · Uninstall (Claude Code: read this file and execute the steps)

> **Instruction to Claude Code:** remove cc-lingua and restore the original
> behavior. Tell the user what you did.

1. Delete the switch and all local files (config, cache, logs, hook script):
   ```bash
   rm -rf ~/.claude/cc-lingua
   ```
2. In `~/.claude/settings.json`, remove the entry from the `hooks.MessageDisplay`
   array whose `command` contains `cc-lingua/translate.py`. Keep any other hooks;
   an empty array is fine.
3. (Optional) Remove the line
   `Always reason and respond in English. (cc-lingua translates the display to the user's language.)`
   from `~/.claude/CLAUDE.md`.
4. Tell the user: uninstalled — the display is back to the original English.

> To pause without uninstalling, just `rm ~/.claude/cc-lingua/enabled`
> (re-enable with `touch ~/.claude/cc-lingua/enabled`).

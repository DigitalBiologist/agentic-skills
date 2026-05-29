# agentic-skills

A curated, **de-identified** collection of [Claude Code](https://claude.com/claude-code) skills — battle-tested prompts and workflows for research, writing, and automation, packaged so anyone can drop them into their own setup.

> 一套经过脱敏的、成熟的 Claude Code 技能合集。每个技能都附带独立的配置指南,clone 下来填入自己的密钥/路径即可使用。

## What is a Claude Code skill?

A *skill* (a.k.a. slash command) is a Markdown file with YAML frontmatter that lives in `~/.claude/commands/`. Claude Code auto-discovers it and you invoke it by name. A skill can be a single `.md` file, or a folder containing a `SKILL.md` plus helper scripts, templates, and references.

## Repository layout

```
agentic-skills/
├── README.md            # this file — also the skills index
├── LICENSE              # MIT
├── CONTRIBUTING.md      # de-identification checklist (read before adding a skill)
└── skills/
    └── <skill-name>/
        ├── README-配置指南.md   # how to install & configure this skill
        ├── <skill-name>.md      # the skill itself (de-identified)
        └── ...                  # optional scripts / templates / references
```

Each skill is self-contained: its folder has everything you need plus a setup guide.

## Skills index

| Skill | What it does | Status |
|-------|--------------|--------|
| [快速阅读论文](skills/快速阅读论文) <br>(paper speed-reader) | Turn a paper PDF into a self-contained, offline HTML reader — PDF on the left, a concise Chinese walkthrough (term cards / per-figure notes) on the right. Free, fully local. | ✅ ready |
| [生成脑图](skills/生成脑图) <br>(mind-map generator) | Turn a long document into an interactive, self-contained markmap mind map (HTML) — toolbar for expand/collapse, show/hide detail, and L1–L5 level jumps. Free, no install. | ✅ ready |
| [技能分享](skills/技能分享) <br>(skill de-identifier) | Meta-skill: de-identify and package any Claude Code skill into a self-contained folder — scans for API keys / passwords / usernames / emails / org / internal IPs, replaces with placeholders, grep self-checks. Share or open-source any skill safely. | ✅ ready |

## How to install a skill

1. Browse `skills/` and pick one.
2. Read its `README-配置指南.md` for prerequisites (API keys, env vars, dependencies).
3. Copy the skill file/folder into your `~/.claude/commands/`:
   ```bash
   cp -r skills/<skill-name> ~/.claude/commands/
   ```
4. Fill in your own credentials/paths where the guide marks placeholders (`<YOUR_API_KEY>`, `<YOUR_PATH>`, …).
5. Restart Claude Code (or start a new session) and invoke the skill by name.

## Safety

Every skill in this repo has been run through a de-identification pass: API keys, passwords, tokens, SSH paths, personal usernames/emails, team/organization names, internal IPs, and subscription URLs are stripped or replaced with placeholders. See [CONTRIBUTING.md](CONTRIBUTING.md) for the exact checklist. **If you ever spot a leaked secret, open an issue — do not include the secret in the issue body.**

## License

[MIT](LICENSE) — use freely, attribution appreciated.

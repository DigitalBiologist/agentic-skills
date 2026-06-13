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
├── CONTRIBUTING.md      # de-identification + contrib→skills promotion rules (read first)
├── skills/              # the shared library — promoted, community-approved skills
│   └── <skill-name>/
│       ├── README-配置指南.md   # how to install & configure this skill
│       ├── <skill-name>.md      # the skill itself (de-identified)
│       └── ...                  # optional scripts / templates / references
└── contrib/             # staging area — each contributor's work-in-progress skills
    └── <your-name>/     # your own folder; try others' skills here and leave feedback
        └── <skill-name>/    # promoted into skills/ once the team finds it useful
```

Each skill is self-contained: its folder has everything you need plus a setup guide.

## Skills index

| Skill | What it does | Status |
|-------|--------------|--------|
| [快速阅读论文](skills/快速阅读论文) <br>(paper speed-reader) | Turn a paper PDF into a self-contained, offline HTML reader — PDF on the left, a concise Chinese walkthrough (term cards / per-figure notes) on the right. Free, fully local. | ✅ ready |
| [生成脑图](skills/生成脑图) <br>(mind-map generator) | Turn a long document into an interactive, self-contained markmap mind map (HTML) — toolbar for expand/collapse, show/hide detail, and L1–L5 level jumps. Free, no install. | ✅ ready |
| [技能分享](skills/技能分享) <br>(skill de-identifier) | Meta-skill: de-identify and package any Claude Code skill into a self-contained folder — scans for API keys / passwords / usernames / emails / org / internal IPs, replaces with placeholders, grep self-checks. Share or open-source any skill safely. | ✅ ready |
| [发布到技能库](skills/发布到技能库) <br>(skill publisher) | Meta-skill: de-identify a skill and publish it into this repo — place by convention, write the config guide, grep self-check, update this index, commit & push. Repo URL & commit identity resolve dynamically, so forks publish to their own repo. | ✅ ready |
| [提交技能](skills/提交技能) <br>(newbie contributor) | **Newbie-friendly:** tell your Claude *"submit my skill to agentic-skills"* and it does everything — sync the repo, place the skill, quick de-id check, branch, commit, push, open a PR. No git knowledge needed; you just wait for the maintainer to merge. Falls back to fork-based PR if you're not yet a collaborator. | ✅ ready |
| [西湖大学PPT单页-v2](skills/西湖大学PPT单页-v2) <br>(slide-page generator) | Render a content-only layout file into a 4K single-page conference slide PNG: fixed wrapper + your content → image-to-image (reference template inlined locally, no image host) → composite (signature arc / dual logo / page number). A general, project-agnostic workflow — bring your own image-gen API key, and swap in your own lab template if you like. | ✅ ready |

## Contrib — community staging area

Skills under [`contrib/<your-name>/`](contrib/) are **work-in-progress** contributions (this is where new contributors and interns share first). They live here so everyone can install them, try them out, and leave feedback *before* they join the shared library above. Once a skill proves genuinely useful to the team, a maintainer **promotes** it into `skills/` and adds it to the index. See [contrib/README.md](contrib/README.md) for what's currently in staging, and [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## How to install a skill

1. Browse `skills/` (or `contrib/<name>/` to try a staging skill) and pick one.
2. Read its `README-配置指南.md` for prerequisites (API keys, env vars, dependencies).
3. Copy the skill file/folder into your `~/.claude/commands/`:
   ```bash
   cp -r skills/<skill-name> ~/.claude/commands/
   ```
4. Fill in your own credentials/paths where the guide marks placeholders (`<YOUR_API_KEY>`, `<YOUR_PATH>`, …).
5. Restart Claude Code (or start a new session) and invoke the skill by name.

## How to contribute your own skill (newbie-friendly)

This repo is something we build **together** — adding a skill is meant to be easy, even if you've never used git.

**New here (e.g. an intern)?** Put your skill under your own folder, **`contrib/<your-name>/`**. That's a low-pressure space to share work — the rest of the team installs it, tries it, and leaves feedback. When people find it genuinely useful, a maintainer promotes it into the main `skills/` library. (More participation, more interaction — that's the point.)

**Easiest way — let your Claude do it.** Install the [`提交技能`](skills/提交技能) skill, then just say:

```
帮我把 我的新技能 提交到 agentic-skills
```

Your Claude will sync the repo, place the skill, run a quick de-identification check, create a branch, push, and open a Pull Request for you. Then a maintainer reviews and merges — you don't touch git at all.

**No command line? Pure web, 3 clicks.** Open the repo → `contrib/` → **Add file → Create new file**, name it `<your-name>/your-skill/SKILL.md`, paste your skill, then **Propose changes → Create pull request**. (Eyeball it first for any keys / real names / home paths.)

> Why a Pull Request instead of pushing directly? `main` is protected so a maintainer can glance at each change before it lands — that keeps the shared library clean while we all work on it. It's not strict; PRs usually get merged quickly.

## Safety

Every skill in this repo has been run through a de-identification pass: API keys, passwords, tokens, SSH paths, personal usernames/emails, team/organization names, internal IPs, and subscription URLs are stripped or replaced with placeholders. See [CONTRIBUTING.md](CONTRIBUTING.md) for the exact checklist. **If you ever spot a leaked secret, open an issue — do not include the secret in the issue body.**

## License

[MIT](LICENSE) — use freely, attribution appreciated.

# skills-public

Skills I use with [Claude Code](https://claude.com/claude-code) and am happy to share.

Each skill is a self-contained folder under `skills/` — a `SKILL.md` telling the agent how to use it, a `README.md` explaining it to a human, and whatever scripts it needs. No build step, no install, no dependencies beyond what each skill's README notes.

## Skills

| Skill | What it does |
| --- | --- |
| [`annotate`](skills/annotate) | Turns a self-contained HTML report into an annotatable version — select any text, leave a comment, export the notes |

## Install

Copy a skill into a project, or into `~/.claude/skills/` to have it everywhere:

```bash
git clone https://github.com/rbpp3042/skills-public.git
cp -r skills-public/skills/annotate ~/.claude/skills/
```

Or symlink it instead of copying, so a `git pull` updates the skill in place — Claude Code follows symlinked skill directories:

```bash
ln -s "$PWD/skills-public/skills/annotate" ~/.claude/skills/annotate
```

See each skill's own README for what it does and how to use it.

## License

MIT — see [LICENSE](LICENSE).

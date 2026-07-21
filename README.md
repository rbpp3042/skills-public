# skills-public

A small collection of [Claude Code](https://claude.com/claude-code) skills I use and am happy to share. Each one lives in `skills/<name>/` with a `SKILL.md` and whatever scripts it needs — no build step, no dependencies beyond what's noted.

## Skills

| Skill | What it does |
| --- | --- |
| [`annotate`](skills/annotate) | Turns a self-contained HTML report into an annotatable version — select any text, leave a comment, export the notes as Markdown/JSON/HTML |

## Install

**Copy into a project:**

```bash
git clone https://github.com/rbpp3042/skills-public.git
cp -r skills-public/skills/annotate <your-project>/.claude/skills/
```

**Or install globally for every project:**

```bash
cp -r skills-public/skills/annotate ~/.claude/skills/
```

**Or symlink it**, so a `git pull` updates the skill in place:

```bash
ln -s "$PWD/skills-public/skills/annotate" ~/.claude/skills/annotate
```

Claude Code follows symlinked skill directories, so there's only ever one copy to keep current.

## Using `annotate` without Claude Code

The builder is a plain Python 3 script with no dependencies — usable on its own:

```bash
python3 skills/annotate/build_annotated.py \
  report.html \
  report_annotated.html \
  "Report title" \
  "unique-localstorage-key"
```

Open the output in a browser, select text, hit **💬 Comment**. Comments persist in `localStorage`; the **⬇ HTML** export produces a standalone file with the comments embedded, so you can send it to someone who doesn't have the tool.

### What it expects

A single-file HTML document with an inline `<style>` and a `<body>` — the kind of report an LLM or a static generator emits. External stylesheets are not inlined and their styling will be lost. The review shell is themed via CSS custom properties and ships light/dark defaults, which a source document's own variables override.

## License

MIT — see [LICENSE](LICENSE).

# annotate

Turns a self-contained HTML report into an annotatable version: a review shell around the original document where you select any fragment, leave a comment, and export the notes.

Built for reviewing generated reports — the kind of single-file HTML an LLM or a static generator emits. The original file is never modified; the output is a new `_annotated.html` next to it.

## What you get

- **Highlight and comment** — select text, hit **💬 Comment**, write a note. The fragment gets marked in the document and the note appears in the sidebar. Clicking either one scrolls to the other.
- **Editable document** — the report body is `contenteditable`, so you can fix typos directly instead of writing a note about them.
- **Autosave** to `localStorage`, keyed per document. Close the tab, come back later, everything is still there.
- **Export**:
  - **MD** — a numbered list of notes with the quoted fragment above each one. This is the thing you hand back to whoever wrote the report.
  - **JSON** — full snapshot (document HTML + comments), for re-import.
  - **HTML** — a standalone file with the comments baked in. Send it to someone who doesn't have this tool; it opens in any browser.
- **Import** — load a `.json` or exported `.html` back in, to continue a review or merge someone else's pass.
- Resizable/collapsible sidebar, dark mode, and a print stylesheet that hides the shell so `⌘P` prints just the report.

## Usage

### As a Claude Code skill

Ask for it in plain language once the skill is installed:

> annotate the report at reports/q3.html

`SKILL.md` tells the agent how to locate the source, run the builder, and hand back a clickable `file://` link.

### As a standalone script

The builder is plain Python 3 with no dependencies:

```bash
python3 build_annotated.py <input.html> <output.html> ["<title>"] ["<localStorage-key>"]
```

```bash
python3 build_annotated.py report.html report_annotated.html "Q3 report" "q3-report-notes"
```

The last two arguments are optional and default to the input filename stem.

**The localStorage key must be unique per document.** Two reports sharing a key will overwrite each other's comments.

## What it expects of the input

A single-file HTML document with an inline `<style>` and a `<body>`. Multiple `<style>` blocks are fine, and attributes on `<body>` or `<style>` are fine.

- **External stylesheets are not inlined** — `<link rel="stylesheet">` styling will be lost in the output.
- **No `<body>` → the script exits** with an error rather than producing a broken file.
- **No `<style>` is fine** — the report just inherits the shell's defaults.

## Theming

The review shell is themed through CSS custom properties: `--ink`, `--ink-soft`, `--ink-faint`, `--ground`, `--surface`, `--surface-2`, `--rule`, `--accent`, `--accent-soft`, `--warn`, `--warn-soft`, `--bad`, `--sans`, `--serif`.

It ships light and dark defaults, so it looks reasonable on a report that defines none of them. A source document that _does_ define them wins — its stylesheet is emitted after the defaults — so the shell picks up the report's own look automatically.

## Known limitations

- HTML only, not Markdown.
- Comments are anchored by wrapping the selection in a `<mark>`. Selections that cross element boundaries (half a heading plus half a paragraph) still work, but the resulting markup can be a little untidy.
- Class-name collisions are possible: the shell uses `.toolbar`, `.sidebar`, `.popup`, `.comment-card`, `.resizer`, `.float-btn`, and `#doc`. If a report defines the same names, check the output before sending it on.

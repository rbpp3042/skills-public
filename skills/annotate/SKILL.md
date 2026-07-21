---
name: annotate
description: Turn an HTML report into an annotatable version — a review shell for highlighting text and leaving comments
---

# Annotatable HTML report

Builds an `_annotated.html` version of an HTML file: adds a toolbar, a comment sidebar, and the ability to select any fragment and attach a note to it.

## When to use

When the user wants to:

- Comment on an HTML report directly in the browser
- Collect a list of edits/review notes on a document
- Hand review notes back to whoever wrote the source

## How it works

1. **Locate the source HTML** — by path, or offer a choice of what's available
2. **Parse the structure** — extract every `<style>` block and the `<body>` content
3. **Wrap it in the shell** — add CSS/JS for commenting (toolbar, sidebar, popup, export/import)
4. **Save as `_annotated.html`** — the original is never modified

## Running the builder

The script lives next to this file:

```bash
python3 <skill-dir>/build_annotated.py <input.html> <output_annotated.html> "<title>" "<localStorage-key>"
```

Example:

```bash
python3 build_annotated.py \
  report_v3.html \
  report_v3_annotated.html \
  "Report v3" \
  "report-v3-annotations"
```

The last two arguments are optional; they default to the input filename stem. The localStorage key must be unique per document — two reports sharing a key will overwrite each other's comments.

## After the build

1. Tell the user the file is ready: `<path>_annotated.html`
2. **Always give the full `file://` link** in the reply, on its own line in a code block, so it can be clicked or pasted straight into the browser. For example: `file:///Users/name/reports/report_v3_annotated.html`. Do not settle for a relative path or a "just double-click it" instruction.
3. Briefly describe the mechanics:
   - Select a fragment → the "💬 Comment" button appears
   - Comments are saved to localStorage automatically
   - Export: MD (list of notes), JSON (full snapshot), HTML (self-contained, for sharing)

## If the page is already open in the browser

If the page is open and browser state is readable:

- Read the comments via JS: `JSON.stringify(comments, null, 1)`
- Offer the options: apply the edits right now vs. export the file

## Limitations

- HTML only (not Markdown)
- Expects a self-contained, single-file HTML document with an inline `<style>` and a `<body>`. External stylesheets are not inlined and their styling will be lost. If there's no `<body>`, the script exits with a clear error.
- CSS class collisions are unlikely but possible — the shell uses `.toolbar`, `.sidebar`, `.popup`, `.comment-card`, `#doc`. Check the source if the layout looks off.

See [README.md](README.md) for the full feature list, theming variables, and standalone usage.

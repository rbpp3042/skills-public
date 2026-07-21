#!/usr/bin/env python3
"""Wrap an HTML report in a review shell: the source CSS and body inside a
commenting UI (toolbar, sidebar, highlight-and-comment, export)."""
import re, pathlib, sys

USAGE = 'usage: build_annotated.py <input.html> <output.html> ["<title>"] ["<localStorage-key>"]'

if len(sys.argv) < 3:
    sys.exit(USAGE)

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
LABEL = sys.argv[3] if len(sys.argv) > 3 else SRC.stem
STORAGE = sys.argv[4] if len(sys.argv) > 4 else 'annotations-' + SRC.stem

if not SRC.is_file():
    sys.exit(f'error: input file not found: {SRC}')

src = SRC.read_text(encoding="utf-8")

body_match = re.search(r"<body[^>]*>(.*)</body>", src, re.S)
if not body_match:
    sys.exit(f'error: no <body> element found in {SRC}. '
             'This tool expects a self-contained HTML document.')
report_body = body_match.group(1)

# Concatenate every <style> block; a report with none still works, it just
# inherits the shell defaults below.
report_css = "\n".join(
    m.group(1) for m in re.finditer(r"<style[^>]*>(.*?)</style>", src, re.S)
)

# The shell is themed through CSS custom properties. A report that defines its
# own wins, because the report's stylesheet is emitted after this block.
FALLBACK_CSS = """
  :root {
    --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    --serif: Georgia, "Times New Roman", serif;
    --ink: #1a1a1a;
    --ink-soft: #444;
    --ink-faint: #888;
    --ground: #fff;
    --surface: #fff;
    --surface-2: #fafafa;
    --rule: #e0e0e0;
    --accent: #2563eb;
    --accent-soft: #dbeafe;
    --warn: #f59e0b;
    --warn-soft: #fef3c7;
    --bad: #dc2626;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --ink: #e8e8e8;
      --ink-soft: #b0b0b0;
      --ink-faint: #808080;
      --ground: #1a1a1a;
      --surface: #242424;
      --surface-2: #1f1f1f;
      --rule: #3a3a3a;
      --accent: #60a5fa;
      --accent-soft: #1e3a5f;
      --warn: #fbbf24;
      --warn-soft: #4a3a15;
      --bad: #f87171;
    }
  }
"""

UI_CSS = """
  /* ─── Review shell (sits on top of the report's own styles) ─── */
  body { overflow: hidden; }

  .toolbar {
    display: flex; align-items: center; gap: 12px;
    padding: 9px 20px; background: var(--surface);
    border-bottom: 1px solid var(--rule);
    font-family: var(--sans); min-height: 52px;
    flex-wrap: wrap;
  }
  .toolbar h1 { font-size: 14px; font-weight: 600; margin-right: auto; font-family: var(--sans); }
  .toolbar button {
    padding: 6px 12px; border: 1px solid var(--rule);
    border-radius: 6px; background: var(--surface); color: var(--ink);
    cursor: pointer; font-size: 12px; font-family: var(--sans);
  }
  .toolbar button:hover { border-color: var(--accent); background: var(--accent-soft); }
  .save-status { font-size: 12px; color: var(--ink-faint); }
  .author-input {
    border: none; border-bottom: 1px solid var(--rule); outline: none;
    font-size: 12px; padding: 3px 0; width: 90px; color: var(--ink-soft);
    background: transparent; font-family: var(--sans);
  }

  .main { display: flex; height: calc(100vh - 52px); }
  .editor-wrap { flex: 1; overflow-y: auto; background: var(--ground); min-width: 200px; }
  #doc { outline: none; }
  #doc:focus-visible { outline: none; }

  /* Resizer between editor and sidebar */
  .resizer {
    width: 4px; flex-shrink: 0; background: var(--rule);
    cursor: col-resize; position: relative; z-index: 10;
  }
  .resizer:hover, .resizer.dragging { background: var(--accent); }
  .resizer::after {
    content: ''; position: absolute; top: 50%; left: 50%;
    width: 2px; height: 24px; background: var(--ink-faint);
    transform: translate(-50%, -50%); border-radius: 1px;
  }

  .sidebar {
    width: var(--sidebar-width, 320px); flex-shrink: 0; background: var(--surface-2);
    border-left: 1px solid var(--rule); overflow-y: auto;
    padding: 18px; font-family: var(--sans);
    position: relative;
    transition: width 0.15s ease;
  }

  /* Collapsed state */
  .sidebar.collapsed {
    width: 44px !important; padding: 0; overflow: hidden;
  }
  .sidebar.collapsed .sidebar-inner {
    opacity: 0; pointer-events: none;
  }
  .sidebar.collapsed .collapsed-badge {
    display: flex;
  }

  /* Counter badge shown while collapsed */
  .collapsed-badge {
    display: none; position: absolute; top: 32px; left: 50%;
    transform: translate(-50%, 0);
    flex-direction: column; gap: 6px;
    font-size: 11px; color: var(--ink-soft); font-family: var(--sans);
  }
  .collapsed-badge .count {
    background: var(--accent); color: #fff;
    padding: 2px 8px; border-radius: 10px; font-weight: 600;
  }

  /* Sidebar toggle button */
  .toggle-btn {
    padding: 6px 12px; border: 1px solid var(--rule);
    border-radius: 6px; background: var(--surface); color: var(--ink);
    cursor: pointer; font-size: 12px; font-family: var(--sans);
  }
  .toggle-btn:hover { border-color: var(--accent); background: var(--accent-soft); }
  .toggle-btn .icon { margin-right: 4px; }
  .sidebar h2 {
    font-size: 12px; font-weight: 600; margin: 0 0 14px; color: var(--ink-faint);
    text-transform: uppercase; letter-spacing: .06em; font-family: var(--sans);
  }
  .comment-count {
    background: var(--accent); color: #fff; font-size: 11px;
    padding: 1px 7px; border-radius: 10px; margin-left: 6px;
  }
  .comment-card {
    background: var(--surface); border: 1px solid var(--rule); border-radius: 6px;
    padding: 12px; margin-bottom: 10px; cursor: pointer; transition: all .15s;
  }
  .comment-card:hover { border-color: var(--accent); }
  .comment-card.active { border-color: var(--warn); box-shadow: 0 0 0 2px var(--warn-soft); }
  .comment-quote {
    font-size: 12px; font-family: var(--serif); color: var(--ink-soft);
    background: var(--warn-soft); padding: 5px 9px; border-radius: 4px;
    margin-bottom: 7px; line-height: 1.4; border-left: 3px solid var(--warn);
    max-height: 76px; overflow-y: auto;
  }
  .comment-body { font-size: 13px; line-height: 1.5; color: var(--ink); white-space: pre-wrap; }
  .comment-meta {
    display: flex; justify-content: space-between; align-items: center;
    margin-top: 8px; font-size: 11px; color: var(--ink-faint);
  }
  .comment-actions button {
    border: none; background: none; cursor: pointer; font-size: 11px;
    color: var(--ink-faint); padding: 2px 3px;
  }
  .comment-actions button:hover { color: var(--bad); }
  .sidebar-empty { color: var(--ink-faint); font-size: 13px; text-align: center; padding: 36px 12px; line-height: 1.5; }

  mark.annotation {
    background: var(--warn-soft); color: inherit; padding: 1px 2px; border-radius: 2px;
    cursor: pointer; border-bottom: 2px solid var(--warn); transition: background .2s;
  }
  mark.annotation:hover { background: var(--accent-soft); }
  mark.annotation.flash { animation: flash .8s ease; }
  @keyframes flash {
    0%, 100% { background: var(--warn-soft); }
    30% { background: var(--accent-soft); }
  }

  .float-btn {
    position: fixed; display: none; z-index: 200;
    background: var(--accent); color: #fff; border: none;
    padding: 7px 15px; border-radius: 20px; font-size: 13px;
    cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,.25);
    font-family: var(--sans); white-space: nowrap;
  }

  .popup-overlay {
    position: fixed; inset: 0; background: rgba(0,0,0,.4);
    display: none; z-index: 300; justify-content: center; align-items: center;
  }
  .popup-overlay.show { display: flex; }
  .popup {
    background: var(--surface); border-radius: 10px; padding: 22px;
    width: 440px; max-width: 90vw; box-shadow: 0 8px 32px rgba(0,0,0,.3);
    font-family: var(--sans);
  }
  .popup h3 { font-size: 14px; margin: 0 0 12px; font-family: var(--sans); }
  .quote-preview {
    font-family: var(--serif); font-size: 13px; color: var(--ink-soft);
    background: var(--warn-soft); padding: 8px 11px; border-radius: 4px;
    margin-bottom: 12px; max-height: 90px; overflow-y: auto;
    border-left: 3px solid var(--warn); line-height: 1.45;
  }
  .popup textarea {
    width: 100%; border: 1px solid var(--rule); border-radius: 6px;
    padding: 9px; font-size: 14px; resize: vertical; min-height: 90px;
    font-family: var(--sans); outline: none; background: var(--surface); color: var(--ink);
  }
  .popup textarea:focus { border-color: var(--accent); }
  .popup-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 14px; }
  .popup-actions button {
    padding: 7px 16px; border-radius: 6px; cursor: pointer; font-size: 13px;
    border: 1px solid var(--rule); background: var(--surface); color: var(--ink);
    font-family: var(--sans);
  }
  .popup-actions .primary { background: var(--accent); color: #fff; border-color: var(--accent); }

  @media (max-width: 900px) {
    .toolbar h1 { font-size: 12px; }
    .toolbar button { font-size: 11px; padding: 5px 10px; }
    .toggle-btn .icon { margin-right: 2px; }
    .sidebar { width: 44px !important; padding: 0; }
    .sidebar-inner { opacity: 0; pointer-events: none; }
    .sidebar .collapsed-badge { display: flex; }
    .resizer { display: none; }
  }

  @media print {
    .toolbar, .sidebar, .float-btn, .popup-overlay { display: none !important; }
    body { overflow: visible; }
    .main { display: block; height: auto; }
    .editor-wrap { overflow: visible; }
  }
"""

JS = r"""
// ─── State ───
let comments = [];
let pendingRange = null;
const STORAGE_KEY = '__STORAGE_KEY__';

function init() {
  loadState();
  renderSidebar();
  initSidebarState();
  initResizer();
  document.getElementById('doc').addEventListener('input', debounce(autoSave, 800));
  document.addEventListener('mouseup', updateFloatButton);
  document.addEventListener('keyup', updateFloatButton);
  bindMarks();
}

// ─── Selection ───
function updateFloatButton() {
  const sel = window.getSelection();
  const text = sel.toString().trim();
  const btn = document.getElementById('floatBtn');
  if (text.length > 0 && isInEditor(sel)) {
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    btn.style.display = 'block';
    btn.style.left = Math.max(8, rect.left + rect.width / 2 - 70) + 'px';
    btn.style.top = Math.max(58, rect.top - 42) + 'px';
  } else {
    btn.style.display = 'none';
  }
}

function isInEditor(sel) {
  if (!sel.rangeCount) return false;
  const node = sel.getRangeAt(0).commonAncestorContainer;
  const editor = document.getElementById('doc');
  return editor === node || editor.contains(node);
}

// ─── Popup ───
function openCommentPopup() {
  const sel = window.getSelection();
  if (!sel.rangeCount) return;
  const text = sel.toString().trim();
  if (!text) return;
  pendingRange = sel.getRangeAt(0).cloneRange();
  document.getElementById('quotePreview').textContent = text;
  document.getElementById('commentText').value = '';
  document.getElementById('popupOverlay').classList.add('show');
  setTimeout(() => document.getElementById('commentText').focus(), 50);
}

function closeCommentPopup() {
  document.getElementById('popupOverlay').classList.remove('show');
  pendingRange = null;
  document.getElementById('floatBtn').style.display = 'none';
}

function addComment() {
  const text = document.getElementById('commentText').value.trim();
  if (!text || !pendingRange) return;
  const quote = document.getElementById('quotePreview').textContent;
  const id = 'c' + Date.now() + Math.random().toString(36).slice(2, 6);
  const author = 'Guest';

  const mark = document.createElement('mark');
  mark.className = 'annotation';
  mark.dataset.commentId = id;
  mark.id = 'mark-' + id;
  try {
    pendingRange.surroundContents(mark);
  } catch (e) {
    mark.appendChild(pendingRange.extractContents());
    pendingRange.insertNode(mark);
  }
  mark.addEventListener('click', () => highlightComment(id));

  comments.push({ id, quote, text, author, timestamp: new Date().toISOString() });
  window.getSelection().removeAllRanges();
  renderSidebar();
  autoSave();
  closeCommentPopup();
  highlightComment(id);
}

// ─── Sidebar ───
function renderSidebar() {
  const list = document.getElementById('commentList');
  document.getElementById('commentCount').textContent = comments.length;
  document.getElementById('collapsedCount').textContent = comments.length;
  if (comments.length === 0) {
    list.innerHTML = '<div class="sidebar-empty">Nothing yet.<br>Select any text in the report to get a Comment button.</div>';
    return;
  }
  list.innerHTML = comments.map(c => `
    <div class="comment-card" id="card-${c.id}" onclick="highlightComment('${c.id}')">
      <div class="comment-quote">${escapeHtml(c.quote)}</div>
      <div class="comment-body">${escapeHtml(c.text)}</div>
      <div class="comment-meta">
        <span>${escapeHtml(c.author)} · ${formatDate(c.timestamp)}</span>
        <div class="comment-actions">
          <button onclick="event.stopPropagation(); deleteComment('${c.id}')">🗑 Delete</button>
        </div>
      </div>
    </div>`).join('');
}

function highlightComment(id) {
  const mark = document.getElementById('mark-' + id);
  if (mark) {
    mark.scrollIntoView({ behavior: 'smooth', block: 'center' });
    mark.classList.add('flash');
    setTimeout(() => mark.classList.remove('flash'), 800);
  }
  document.querySelectorAll('.comment-card').forEach(c => c.classList.remove('active'));
  const card = document.getElementById('card-' + id);
  if (card) {
    card.classList.add('active');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function deleteComment(id) {
  comments = comments.filter(c => c.id !== id);
  const mark = document.getElementById('mark-' + id);
  if (mark) {
    const parent = mark.parentNode;
    while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
    parent.removeChild(mark);
    parent.normalize();
  }
  renderSidebar();
  autoSave();
}

function bindMarks() {
  document.querySelectorAll('mark.annotation').forEach(mark => {
    const id = mark.dataset.commentId;
    mark.addEventListener('click', () => highlightComment(id));
  });
}

// ─── Sidebar width resizer ───
function initResizer() {
  const resizer = document.querySelector('.resizer');
  const sidebar = document.querySelector('.sidebar');
  if (!resizer || !sidebar) return;

  let isDragging = false;

  // Restore width from localStorage
  const savedWidth = localStorage.getItem(STORAGE_KEY + '-sidebar-width');
  if (savedWidth) {
    sidebar.style.setProperty('--sidebar-width', savedWidth + 'px');
  }

  resizer.addEventListener('mousedown', (e) => {
    isDragging = true;
    resizer.classList.add('dragging');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  });

  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const newWidth = window.innerWidth - e.clientX;
    if (newWidth >= 200 && newWidth <= 600) {
      sidebar.style.setProperty('--sidebar-width', newWidth + 'px');
    }
  });

  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      resizer.classList.remove('dragging');
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      // Persist the current width
      const currentWidth = sidebar.getBoundingClientRect().width;
      localStorage.setItem(STORAGE_KEY + '-sidebar-width', currentWidth.toString());
    }
  });
}

// ─── Toggle sidebar visibility ───
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const btn = document.getElementById('toggleBtn');
  sidebar.classList.toggle('collapsed');
  const isCollapsed = sidebar.classList.contains('collapsed');
  localStorage.setItem(STORAGE_KEY + '-sidebar-collapsed', isCollapsed);
  btn.innerHTML = isCollapsed ? '<span class="icon">◫</span>Show' : '<span class="icon">◧</span>Panel';
}

function initSidebarState() {
  const sidebar = document.getElementById('sidebar');
  const btn = document.getElementById('toggleBtn');
  const saved = localStorage.getItem(STORAGE_KEY + '-sidebar-collapsed');
  if (saved === 'true') {
    sidebar.classList.add('collapsed');
    btn.innerHTML = '<span class="icon">◫</span>Show';
  }
}

// ─── Persistence ───
function autoSave() {
  const state = {
    html: document.getElementById('doc').innerHTML,
    comments
  };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    flashSave('Saved');
  } catch (e) {
    flashSave('⚠ Not saved');
  }
}

function loadState() {
  // Local edits take priority over data embedded in the file
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) {
    try {
      const state = JSON.parse(raw);
      if (state.html) document.getElementById('doc').innerHTML = state.html;
      if (state.comments) comments = state.comments;
      return;
    } catch (e) { console.error('Failed to read localStorage', e); }
  }
  const embedded = document.getElementById('embeddedComments');
  if (embedded && embedded.textContent.trim()) {
    try { comments = JSON.parse(embedded.textContent); } catch (e) { console.error('Failed to read embedded comments', e); }
  }
}

function resetDoc() {
  if (!confirm('Discard all edits and comments and restore the original report?')) return;
  localStorage.removeItem(STORAGE_KEY);
  location.reload();
}

// ─── Export ───
function exportJSON() {
  download(JSON.stringify({
    document: '__LABEL__',
    exported: new Date().toISOString(),
    html: document.getElementById('doc').innerHTML,
    comments
  }, null, 2), '__LABEL__-comments.json', 'application/json');
}

function exportMarkdown() {
  let md = `# Review notes — __LABEL__\n\n_Exported ${formatDate(new Date().toISOString())} · ${comments.length} comment(s)_\n\n`;
  md += comments.map((c, i) =>
    `## ${i + 1}. ${c.author}\n\n> ${c.quote.replace(/\n+/g, ' ')}\n\n${c.text}\n`
  ).join('\n');
  download(md, '__LABEL__-comments.md', 'text/markdown');
}

function exportHTML() {
  // Embed the comments in the file so it opens standalone for anyone
  const clone = document.documentElement.cloneNode(true);
  let slot = clone.querySelector('#embeddedComments');
  slot.textContent = JSON.stringify(comments);
  clone.querySelector('#doc').innerHTML = document.getElementById('doc').innerHTML;
  download('<!doctype html>\n' + clone.outerHTML, '__LABEL__-annotated-export.html', 'text/html');
}

// ─── Import ───
function importData(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    const content = e.target.result;
    try {
      if (file.name.endsWith('.json')) {
        const data = JSON.parse(content);
        if (data.html) document.getElementById('doc').innerHTML = data.html;
        comments = data.comments || [];
      } else if (file.name.endsWith('.html')) {
        const doc = new DOMParser().parseFromString(content, 'text/html');
        const body = doc.getElementById('doc');
        const embedded = doc.getElementById('embeddedComments');
        if (body) document.getElementById('doc').innerHTML = body.innerHTML;
        comments = embedded && embedded.textContent.trim() ? JSON.parse(embedded.textContent) : [];
      } else {
        alert('Expected a .json or .html file');
        return;
      }
      bindMarks();
      renderSidebar();
      autoSave();
    } catch (err) {
      alert('Could not read the file: ' + err.message);
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// ─── Utilities ───
function download(content, filename, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function flashSave(msg) {
  const el = document.getElementById('saveStatus');
  el.textContent = msg;
  el.style.color = 'var(--accent)';
  setTimeout(() => { el.style.color = 'var(--ink-faint)'; }, 1500);
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { day: 'numeric', month: 'short' }) + ' ' +
         d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function debounce(fn, ms) {
  let t;
  return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeCommentPopup(); });

init();
"""

out = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{LABEL} — review</title>

<style>
{FALLBACK_CSS}
</style>

<style>
{report_css}
</style>

<style>
{UI_CSS}
</style>
</head>
<body>

<div class="toolbar">
  <h1>📝 {LABEL} — review</h1>
  <span class="save-status" id="saveStatus">Ready</span>
  <button onclick="exportMarkdown()">⬇ Notes as MD</button>
  <button onclick="exportJSON()">⬇ JSON</button>
  <button onclick="exportHTML()">⬇ HTML</button>
  <button onclick="document.getElementById('importFile').click()">⬆ Import</button>
  <button onclick="resetDoc()">↺ Reset</button>
  <button class="toggle-btn" onclick="toggleSidebar()" id="toggleBtn">
    <span class="icon">◧</span>Panel
  </button>
  <input type="file" id="importFile" accept=".json,.html" style="display:none" onchange="importData(event)">
</div>

<div class="main">
  <div class="editor-wrap">
    <div id="doc" contenteditable="true" spellcheck="false">
{report_body}
    </div>
  </div>

  <div class="resizer"></div>

  <aside class="sidebar" id="sidebar">
    <div class="collapsed-badge">
      <div>💬</div>
      <span class="count" id="collapsedCount">0</span>
    </div>
    <div class="sidebar-inner">
      <h2>Comments<span class="comment-count" id="commentCount">0</span></h2>
      <div id="commentList"></div>
    </div>
  </aside>
</div>

<button class="float-btn" id="floatBtn" onclick="openCommentPopup()">💬 Comment</button>

<div class="popup-overlay" id="popupOverlay" onclick="if(event.target===this)closeCommentPopup()">
  <div class="popup">
    <h3>New comment</h3>
    <div class="quote-preview" id="quotePreview"></div>
    <textarea id="commentText" placeholder="What's wrong / what to change…" onkeydown="if(event.key==='Enter'&&(event.metaKey||event.ctrlKey))addComment()"></textarea>
    <div class="popup-actions">
      <button onclick="closeCommentPopup()">Cancel</button>
      <button class="primary" onclick="addComment()">Add (⌘↵)</button>
    </div>
  </div>
</div>

<script type="application/json" id="embeddedComments"></script>
<script>
{JS}
</script>
</body>
</html>
"""

out = out.replace('__STORAGE_KEY__', STORAGE).replace('__LABEL__', LABEL)
OUT.write_text(out, encoding="utf-8")
print(f"Done: {OUT} ({len(out)} bytes)")

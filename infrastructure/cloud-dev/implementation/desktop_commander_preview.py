#!/usr/bin/python3
"""Apply the pinned, UI-only Desktop Commander compact preview overlay."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat

VERSION = "0.3.1"
OVERLAY = "compact-file-preview-v1"
BASE_SHA256 = {
    "dist/ui/file-preview/styles.css": "5ba1f38a3966d7f4b5b3f88f1395b40025eeb4c085bd156872954e0df378a4e1",
    "dist/ui/file-preview/preview-runtime.js": "5236825837a2be4afc29c67cd5f15350d8b3ebec5a214477161c9cf410afa1f4",
    "dist/ui/file-preview/src/app.js": "b602a3c2b0dd9665e8f0a6045ad9b28b8cdf4860763ff0450bae6df237a41b5f",
    "dist/ui/file-preview/src/document-layout.js": "dcd12cc9e8b5c6a9b99325c699060cb8f3c0c074ae0025781d6532da96772d1a",
    "dist/ui/file-preview/src/file-type-handlers.js": "327a7d1adfa3eccf12d70daab593212b6d140bc847aca6e27931496e652dccc2",
    "dist/ui/shared/compact-row.js": "59e78661a42ad39d199a5a0c439cf5ae48811ab244c109e8294e66be4faa4769",
}
HELPER_PATH = "dist/ui/file-preview/src/compact-preview.js"
MARKER_PATH = "dist/ui/file-preview/.compact-preview-overlay.json"
CSS = """
/* Compact preview overlay: identity first, bounded mobile content. */
#compact-toggle { min-width: 0; line-height: 1.4; }
#compact-toggle .compact-label {
  flex: 1 1 auto; min-width: 0; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap;
  color: var(--text); font-weight: 600;
}
#compact-toggle .compact-label::after { content: none; }
#compact-toggle .compact-filename {
  flex: 0 0 auto; color: var(--text-secondary); font-weight: 400; font-size: 12px;
}
.panel-breadcrumb {
  direction: ltr; text-align: left; flex: 1 1 0; max-width: none;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  overflow-wrap: normal; line-height: 1.4; font-size: 12px;
}
.packet-preview .code-viewer,
.packet-preview .code-viewer code {
  white-space: pre-wrap; overflow-wrap: anywhere; word-break: normal;
}
.packet-preview .code-viewer { padding: 12px; font-size: 12px; }
.panel-footer { color: var(--text-secondary); }
@media (max-width: 600px) {
  .tool-shell:not(.fullscreen) .panel-content-wrapper {
    max-height: min(35vh, 140px);
    max-height: min(35svh, 140px);
    overflow: auto;
  }
  .shell { padding: 4px; }
  #compact-toggle { padding: 4px 2px; }
  .panel { margin-top: 4px; }
  .panel-topbar { gap: 6px; padding: 6px 10px; }
  .notice { padding: 6px 10px; line-height: 1.4; }
  .panel-footer { padding: 6px 10px; font-size: 11px; }
  .panel-action { padding: 6px; }
}
"""


def digest(value):
    return hashlib.sha256(value).hexdigest()


def replace_once(source, before, after):
    if source.count(before) != 1:
        raise RuntimeError("Unsupported Desktop Commander UI source boundary")
    return source.replace(before, after, 1)


def replace_span(source, start, end, replacement):
    if source.count(start) != 1:
        raise RuntimeError("Unsupported Desktop Commander UI function boundary")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


def bundled_function(source, name, aliases):
    """Reuse the readable vendor function; only bind its known bundle names."""
    function = source[source.index("export function " + name):]
    function = function.replace("export function ", "function ", 1)
    return re.sub(r"\b(" + "|".join(map(re.escape, aliases)) + r")\b",
                  lambda match: aliases[match.group()], function)


def build_overlay(originals, helper):
    source = {name: value.decode("utf8") for name, value in originals.items()}
    row_path = "dist/ui/shared/compact-row.js"
    row = source[row_path]
    row = replace_once(row, "    const chevron = options.expandable", """    const title = options.title ? ' title="' + escapeHtml(options.title) + '"' : '';
    const ariaLabel = options.ariaLabel ? ' aria-label="' + escapeHtml(options.ariaLabel) + '"' : '';
    const chevron = options.expandable""")
    row = replace_once(row, "${ariaExpanded}>", "${ariaExpanded}${title}${ariaLabel}>")
    source[row_path] = row

    layout_path = "dist/ui/file-preview/src/document-layout.js"
    layout = source[layout_path]
    layout = "import { dcParentLabel, dcPacketFooter, dcCopySourceLabel } from './compact-preview.js';\n" + layout
    layout = replace_once(layout, "buildBreadcrumb(options.payload.filePath)",
                          "buildBreadcrumb(options.currentDisplayMode === 'fullscreen' ? options.payload.fileName : dcParentLabel(options.payload.filePath))")
    layout = replace_span(layout, "    const compactLabel =", "    let footerLabel =", """    const compactLabel = options.payload.fileName || options.payload.filePath;
    const compactDetail = range?.isPartial
        ? 'Lines ' + range.fromLine + '–' + range.toLine
        : options.payload.fileType === 'directory' ? 'Directory' : '';
    """)
    layout = replace_once(layout, "label: compactLabel, filename: options.payload.fileName,",
                          "label: compactLabel, filename: compactDetail, title: options.payload.filePath, ariaLabel: options.payload.filePath + (range?.isPartial ? ', lines ' + range.fromLine + '–' + range.toLine : ''),")
    layout = replace_once(layout, "<span>${footerLabel}</span>",
                          "<span>${dcPacketFooter(options.payload, footerLabel)}</span>")
    layout = replace_once(layout, 'id="copy-source" title="Copy source" aria-label="Copy source"',
                          'id="copy-source" title="${dcCopySourceLabel(options.payload)}" aria-label="${dcCopySourceLabel(options.payload)}"')
    source[layout_path] = layout

    handlers_path = "dist/ui/file-preview/src/file-type-handlers.js"
    handlers = "import { dcPacketPreviewBody } from './compact-preview.js';\n" + source[handlers_path]
    handlers = replace_once(handlers, """        renderBody: ({ payload }) => {
            const rawContent = stripReadStatusLine(payload.content);""", """        renderBody: ({ payload }) => {
            const packet = dcPacketPreviewBody(payload, renderRawFallback);
            if (packet) return packet;
            const rawContent = stripReadStatusLine(payload.content);""")
    source[handlers_path] = handlers

    app_path = "dist/ui/file-preview/src/app.js"
    app = "import { dcPreparePacketPreview, dcIsPacket, dcDisablePacketSelection } from './compact-preview.js';\n" + source[app_path]
    app = replace_once(app, "    const body = renderPayloadBody({", """    dcPreparePacketPreview(payload, stripReadStatusLine(payload.content), range, () => {
        if (currentPayload === payload && container.isConnected) {
            renderApp(container, payload, htmlMode, isExpanded);
        }
    });
    const body = renderPayloadBody({""")
    app = replace_once(app, "selectionAbortController = attachSelectionContext({",
                      "selectionAbortController = dcIsPacket(payload) ? dcDisablePacketSelection(selectionAbortController, rpcUpdateContext) : attachSelectionContext({")
    source[app_path] = app

    runtime_path = "dist/ui/file-preview/preview-runtime.js"
    runtime = source[runtime_path]
    row_function = bundled_function(row, "renderCompactRow", {
        "renderCompactRow": "pa", "escapeHtml": "gn"})
    start = runtime.index("function pa(e)")
    end = runtime.index("function ", start + len("function pa(e)"))
    runtime = runtime[:start] + row_function + "\n" + runtime[end:]
    layout_function = bundled_function(layout, "buildDocumentLayout", {
        "buildDocumentLayout": "k3", "renderCompactRow": "pa", "escapeHtml": "gn",
        "parseReadRange": "Gt", "stripReadStatusLine": "tt",
        "renderMarkdownCopyButton": "m3", "renderMarkdownModeToggle": "g3",
        "buildBreadcrumb": "HC", "countContentLines": "o0", "renderCopyIcon": "y3",
        "renderFolderIcon": "sJ", "renderUndoIcon": "aJ", "renderExpandIcon": "lJ",
        "renderMarkdownSaveStatus": "uJ"})
    runtime = replace_span(runtime, "function k3(e)", "var cJ=", layout_function + "\n")
    runtime = replace_once(runtime,
        "renderBody:({payload:e})=>{let t=tt(e.content);return t.trim().length===0?",
        "renderBody:({payload:e})=>{let packet=dcPacketPreviewBody(e,S3);if(packet)return packet;let t=tt(e.content);return t.trim().length===0?")
    runtime = replace_once(runtime, "let o=Gt(t.content),s=$3(",
        "let o=Gt(t.content);dcPreparePacketPreview(t,tt(t.content),o,()=>{if(xt===t&&e.isConnected)wl(e,t,n,Sn)});let s=$3(")
    runtime = replace_once(runtime, "us=A3({payload:t,",
        "us=dcIsPacket(t)?dcDisablePacketSelection(us,G3):A3({payload:t,")
    runtime = replace_once(runtime, '"use strict";(()=>{',
        '"use strict";(()=>{\n' + helper.replace("export function ", "function ") + "\n")
    source[runtime_path] = runtime
    source["dist/ui/file-preview/styles.css"] += CSS
    source[HELPER_PATH] = helper
    return {name: value.encode("utf8") for name, value in source.items()}


def atomic_write(path, content, mode=0o644):
    temporary = path.with_name("." + path.name + ".preview-" + str(os.getpid()))
    try:
        temporary.write_bytes(content)
        temporary.chmod(mode)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def apply_overlay(package):
    """Validate all inputs before writing; fail closed on package drift."""
    package = Path(package)
    if json.loads((package / "package.json").read_text())["version"] != VERSION:
        raise RuntimeError("Unsupported Desktop Commander preview package version")
    helper = Path(__file__).with_name("desktop_commander_preview_ui.js").read_text()
    fingerprint = digest(Path(__file__).read_bytes() + helper.encode("utf8"))
    marker = package / MARKER_PATH
    if marker.exists():
        recorded = json.loads(marker.read_text())
        if recorded.get("overlay") != OVERLAY or recorded.get("fingerprint") != fingerprint:
            raise RuntimeError("A different Desktop Commander preview overlay is installed")
        if set(recorded.get("sha256", {})) != set(BASE_SHA256) | {HELPER_PATH}:
            raise RuntimeError("Incomplete Desktop Commander preview overlay manifest")
        for name, expected in recorded["sha256"].items():
            if digest((package / name).read_bytes()) != expected:
                raise RuntimeError("Installed Desktop Commander preview overlay has changed: " + name)
        return False
    originals = {name: (package / name).read_bytes() for name in BASE_SHA256}
    for name, expected in BASE_SHA256.items():
        if digest(originals[name]) != expected:
            raise RuntimeError("Unsupported Desktop Commander preview asset: " + name)
    if (package / HELPER_PATH).exists():
        raise RuntimeError("Untracked Desktop Commander preview helper already exists")
    outputs = build_overlay(originals, helper)
    written = []
    try:
        for name, value in outputs.items():
            path = package / name
            mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
            atomic_write(path, value, mode)
            written.append(name)
        atomic_write(marker, (json.dumps({
            "overlay": OVERLAY, "fingerprint": fingerprint,
            "sha256": {name: digest(value) for name, value in outputs.items()},
        }, indent=2) + "\n").encode("utf8"))
    except BaseException:
        for name in reversed(written):
            if name in originals:
                atomic_write(package / name, originals[name])
            else:
                (package / name).unlink(missing_ok=True)
        raise
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({"overlay": OVERLAY, "changed": apply_overlay(args.package)}))

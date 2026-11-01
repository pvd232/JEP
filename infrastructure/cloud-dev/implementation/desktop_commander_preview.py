#!/usr/bin/python3
"""Apply the pinned, Desktop Commander file and process preview overlay."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat

VERSION = "0.3.1"
OVERLAY = "compact-file-preview-v2"
BASE_SHA256 = {
    "dist/ui/file-preview/styles.css": "5ba1f38a3966d7f4b5b3f88f1395b40025eeb4c085bd156872954e0df378a4e1",
    "dist/ui/file-preview/preview-runtime.js": "5236825837a2be4afc29c67cd5f15350d8b3ebec5a214477161c9cf410afa1f4",
    "dist/ui/file-preview/src/app.js": "b602a3c2b0dd9665e8f0a6045ad9b28b8cdf4860763ff0450bae6df237a41b5f",
    "dist/ui/file-preview/src/document-layout.js": "dcd12cc9e8b5c6a9b99325c699060cb8f3c0c074ae0025781d6532da96772d1a",
    "dist/ui/file-preview/src/file-type-handlers.js": "327a7d1adfa3eccf12d70daab593212b6d140bc847aca6e27931496e652dccc2",
    "dist/ui/shared/compact-row.js": "59e78661a42ad39d199a5a0c439cf5ae48811ab244c109e8294e66be4faa4769",
}
BASE_SHA256.update({'dist/server.js': '8772e70baa8a19b6a3799b0d012392f96b4db67149971fa6eb9453d90993eced', 'dist/handlers/terminal-handlers.js': 'e0e67f4ed78e421bd42dc438fb48f5994347f14437a5c2516fb9ed197405236d', 'dist/ui/file-preview/src/panel-actions.js': 'b0aa001defdbf956090d2430a8b86c9f3aff6d3c406aa34f2bbd1cc84ff87d22'})
V1_FINGERPRINT = '5f95fcda3cd38e50dfa3464833edba3e766664c0fd37971154bc3e588f5d1286'
V1_SHA256 = {'dist/ui/file-preview/styles.css': '7d3faadf0ffb27937dcf9cea7ad0216c6ffd40ef9df775b7d0aed7a088a97423', 'dist/ui/file-preview/preview-runtime.js': '502a8ad06863ccad96160dac9c802fa947422524fa72b7a605f1f95a51dc5229', 'dist/ui/file-preview/src/app.js': 'a1606725147982b54e02336f58de64c30bff4aba92f53e2b83328f3e28c854be', 'dist/ui/file-preview/src/document-layout.js': '00f617aed493947e3d28cc9d587a2d187f7425fff43338eec439e46d11f87232', 'dist/ui/file-preview/src/file-type-handlers.js': '3c849b255026b21fbc9bebcdaa656bd968cb2635e7f6e58ae45d4fdee6f9f257', 'dist/ui/shared/compact-row.js': '622ca3fb2e88622b4cc24604fd99cad94869ba48c6094c654f7e46423c7c1949', 'dist/ui/file-preview/src/compact-preview.js': '206ded1abd6a0d65ff1f5a1f1c3b1cc0124ad4efcb1c20d892d2cad5fe80107d'}
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


def build_file_overlay(originals, helper):
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



def build_process_overlay(previous, helper):
    """Extend the same widget with original process-result snapshots."""
    source = {name: value.decode("utf8") for name, value in previous.items()}
    old_helper = source[HELPER_PATH]
    source[HELPER_PATH] = helper
    server = "dist/server.js"
    source[server] = replace_once(source[server],
        "inputSchema: zodToJsonSchema(ReadProcessOutputArgsSchema),",
        "inputSchema: zodToJsonSchema(ReadProcessOutputArgsSchema),\n                _meta: buildUiToolMeta(FILE_PREVIEW_RESOURCE_URI, false, showMcpUiPreviews),")
    handler = "dist/handlers/terminal-handlers.js"
    source[handler] = replace_once(source[handler],
        "    return readProcessOutput(parsed);",
        """    const result = await readProcessOutput(parsed);
    return {
        ...result,
        _meta: { ...result._meta, 'desktop-commander/preview': { kind: 'process_output', pid: parsed.pid } },
    };""")

    layout_path = "dist/ui/file-preview/src/document-layout.js"
    layout = "import { dcIsProcessSnapshot } from './compact-preview.js';\n" + source[layout_path]
    layout = replace_once(layout, "const range = parseReadRange(options.payload.content);",
        "const range = dcIsProcessSnapshot(options.payload) ? undefined : parseReadRange(options.payload.content);")
    layout = replace_once(layout, "const breadcrumb = buildBreadcrumb(",
        "const breadcrumb = dcIsProcessSnapshot(options.payload) ? 'Output snapshot' : buildBreadcrumb(")
    layout = replace_once(layout, "const lineCount = range ?",
        "const lineCount = dcIsProcessSnapshot(options.payload) ? 0 : range ?")
    layout = replace_once(layout, "title: options.payload.filePath, ariaLabel: options.payload.filePath +",
        "title: dcIsProcessSnapshot(options.payload) ? options.payload.fileName : options.payload.filePath, ariaLabel: (dcIsProcessSnapshot(options.payload) ? options.payload.fileName : options.payload.filePath) +")
    source[layout_path] = layout

    body_path = "dist/ui/file-preview/src/file-type-handlers.js"
    body = "import { dcIsProcessSnapshot, dcProcessSnapshotBody } from './compact-preview.js';\n" + source[body_path]
    body = replace_once(body, "export function getFileTypeCapabilities(payload) {",
        """export function getFileTypeCapabilities(payload) {
    if (dcIsProcessSnapshot(payload)) return { supportsPreview: true, canCopy: true, canOpenInFolder: false };""")
    body = replace_once(body, "export function renderPayloadBody(options) {",
        """export function renderPayloadBody(options) {
    const snapshot = dcProcessSnapshotBody(options.payload, renderRawFallback);
    if (snapshot) return snapshot;""")
    source[body_path] = body

    actions_path = "dist/ui/file-preview/src/panel-actions.js"
    actions = "import { dcIsProcessSnapshot } from './compact-preview.js';\n" + source[actions_path]
    actions = replace_once(actions, "copyTextData(stripReadStatusLine(options.payload.content))",
        "copyTextData(dcIsProcessSnapshot(options.payload) ? options.payload.content : stripReadStatusLine(options.payload.content))")
    actions = replace_once(actions, "    const activeCopyButton = queryById('copy-active-markdown');",
        "    if (dcIsProcessSnapshot(options.payload)) return;\n    const activeCopyButton = queryById('copy-active-markdown');")
    source[actions_path] = actions

    app_path = "dist/ui/file-preview/src/app.js"
    app = "import { dcIsProcessSnapshot, dcCreateProcessPreview, dcBindProcessSnapshot } from './compact-preview.js';\n" + source[app_path]
    app = replace_once(app, "dcIsPacket(payload) ? dcDisablePacketSelection",
        "(dcIsPacket(payload) || dcIsProcessSnapshot(payload)) ? dcDisablePacketSelection")
    app = replace_once(app, "    const renderAndSync = (payload) => {",
        "    const renderAndSync = (payload) => {\n        if (!processPreview.allowsFileState()) return;")
    app = replace_once(app, "    const syncFromPersistedWidgetState = () => {",
        "    const syncFromPersistedWidgetState = () => {\n        if (!processPreview.allowsFileState()) return;")
    app = replace_once(app, "        widgetState.write(payload);\n    };",
        "        if (processPreview.allowsFileState()) widgetState.write(payload);\n    };")
    app = replace_once(app, "        renderApp(container, currentPayload, currentHtmlMode, isExpanded);",
        "        if (processPreview.allowsFileState() || dcIsProcessSnapshot(currentPayload)) renderApp(container, currentPayload, currentHtmlMode, isExpanded);")
    app = replace_once(app, "    let initialStateResolved = false;",
        """    let initialStateResolved = false;
    let previewGeneration = 0;
    let handleToolResult;
    const releaseFileSource = () => {
        pendingCachedPayload = currentPayload = hostPayload = localPayloadOverride = inlinePayloadBeforeFullscreen = directoryBackPayload = undefined;
        selectionAbortController = dcDisablePacketSelection(selectionAbortController, rpcUpdateContext);
        markdownController.clear();
    };
    const processPreview = dcCreateProcessPreview({
        getToolName: () => app.getHostContext()?.toolInfo?.tool?.name,
        show: (payload) => {
            initialStateResolved = true;
            releaseFileSource();
            renderApp(container, payload, 'rendered', isExpanded);
        },
        unavailable: () => {
            initialStateResolved = true;
            releaseFileSource();
            renderStatusState(container, 'Process output unavailable from this host.');
            onRender?.();
        },
        loading: () => {
            releaseFileSource();
            renderLoadingState(container); onRender?.();
        },
        replay: (result) => handleToolResult(result),
    });""")
    app = replace_once(app,
        "rpcCallTool = (name, args) => (app.callServerTool({ name, arguments: args }));",
        "rpcCallTool = (name, args) => processPreview.allowsFileState() ? app.callServerTool({ name, arguments: args }) : Promise.reject(new Error('No current file invocation.'));")
    app = replace_once(app, "trackUiEvent = (event, params = {}) => filePreviewUiEvent(",
        "trackUiEvent = (event, params = {}) => processPreview.allowsFileState() ? filePreviewUiEvent(")
    app = replace_once(app, "        ...params,\n    });\n    app.ontoolinput",
        "        ...params,\n    }) : undefined;\n    app.ontoolinput")
    app = replace_once(app, "    app.ontoolinput = (params) => {",
        """    app.ontoolinput = (params) => {
        const inputGeneration = ++previewGeneration;
        if (processPreview.input(params.arguments)) return;
        pendingCachedPayload ??= widgetState.read() ?? undefined;""")
    app = replace_once(app, "void pullPayloadByArgs(readArgs, (p) => {",
        """void pullPayloadByArgs(readArgs, (p) => {
                if (inputGeneration !== previewGeneration || !processPreview.allowsFileState()) return;""")
    app = replace_once(app, "    app.ontoolresult = (result) => {",
        """    app.ontoolresult = handleToolResult = (result) => {
        if (processPreview.result(result)) return;
        const resultGeneration = previewGeneration;""")
    app = replace_once(app, "        const deliver = (pulled) => {",
        "        const deliver = (pulled) => {\n            if (resultGeneration !== previewGeneration || !processPreview.allowsFileState()) return;")
    app = replace_once(app, "        const renderMessageFallback = () => {",
        "        const renderMessageFallback = () => {\n            if (resultGeneration !== previewGeneration || !processPreview.allowsFileState()) return;")
    app = replace_once(app, "pendingCachedPayload = widgetState.read() ?? undefined;",
        "pendingCachedPayload = processPreview.allowsFileState() ? widgetState.read() ?? undefined : undefined;")
    app = replace_once(app,
        "    const widgetState = createWidgetStateStorage((value) => isPreviewStructuredContent(value) && typeof value.content === 'string');",
        "    let widgetState;\n    const getWidgetState = () => widgetState ??= createWidgetStateStorage((value) => isPreviewStructuredContent(value) && typeof value.content === 'string');")
    app = app.replace("widgetState.read()", "getWidgetState().read()").replace("widgetState.write(", "getWidgetState().write(")
    app = replace_once(app, "    container.innerHTML = layout.html;",
        "    container.innerHTML = layout.html;\n    dcBindProcessSnapshot(container, payload);")
    source[app_path] = app

    runtime_path = "dist/ui/file-preview/preview-runtime.js"
    runtime = source[runtime_path]
    runtime = replace_once(runtime, old_helper.replace("export function ", "function "),
        helper.replace("export function ", "function "))
    layout_function = bundled_function(layout, "buildDocumentLayout", {
        "buildDocumentLayout": "k3", "renderCompactRow": "pa", "escapeHtml": "gn",
        "parseReadRange": "Gt", "stripReadStatusLine": "tt", "renderMarkdownCopyButton": "m3",
        "renderMarkdownModeToggle": "g3", "buildBreadcrumb": "HC", "countContentLines": "o0",
        "renderCopyIcon": "y3", "renderFolderIcon": "sJ", "renderUndoIcon": "aJ",
        "renderExpandIcon": "lJ", "renderMarkdownSaveStatus": "uJ"})
    runtime = replace_span(runtime, "function k3(options)", "var cJ=", layout_function + "\n")
    runtime = replace_once(runtime, "function E3(e){return",
        "function E3(e){if(dcIsProcessSnapshot(e))return{supportsPreview:true,canCopy:true,canOpenInFolder:false};return")
    runtime = replace_once(runtime, "function $3(e){return",
        "function $3(e){let snapshot=dcProcessSnapshotBody(e.payload,S3);if(snapshot)return snapshot;return")
    runtime = replace_once(runtime, "dcIsPacket(t)?dcDisablePacketSelection",
        "(dcIsPacket(t)||dcIsProcessSnapshot(t))?dcDisablePacketSelection")
    runtime = replace_once(runtime, "await o(tt(e.payload.content))",
        "await o(dcIsProcessSnapshot(e.payload)?e.payload.content:tt(e.payload.content))")
    runtime = replace_once(runtime, '});let l=t("copy-active-markdown");',
        '});if(dcIsProcessSnapshot(e.payload))return;let l=t("copy-active-markdown");')
    runtime = replace_once(runtime, "o=b=>{b&&r.write(b),",
        "o=b=>{if(!dcProcess.allowsFileState())return;b&&r.write(b),")
    runtime = replace_once(runtime, "s=()=>{let b=r.read();",
        "s=()=>{if(!dcProcess.allowsFileState())return;let b=r.read();")
    runtime = replace_once(runtime, "Q3=b=>{r.write(b)}",
        "Q3=b=>{dcProcess.allowsFileState()&&r.write(b)}")
    runtime = replace_once(runtime, "Of=()=>{wl(e,xt,X3,Sn)}",
        "Of=()=>{if(dcProcess.allowsFileState()||dcIsProcessSnapshot(xt))wl(e,xt,X3,Sn)}")
    router = """let dcGeneration=0,dcToolResult;
    const dcReleaseFileSource=()=>{a=xt=oy=Yr=sy=as=undefined;us=dcDisablePacketSelection(us,G3);ln.clear();};
    const dcProcess=dcCreateProcessPreview({
        getToolName:()=>t.getHostContext()?.toolInfo?.tool?.name,
        show:payload=>{d=true;dcReleaseFileSource();wl(e,payload,"rendered",Sn)},
        unavailable:()=>{d=true;dcReleaseFileSource();xl(e,"Process output unavailable from this host.");Sr?.()},
        loading:()=>{dcReleaseFileSource();uy(e);Sr?.()},
        replay:result=>dcToolResult(result)
    });"""
    runtime = replace_once(runtime, ";Sr=()=>{},dy=", ";" + router + "Sr=()=>{},dy=")
    runtime = replace_once(runtime, "dy=(b,v)=>t.callServerTool({name:b,arguments:v})",
        'dy=(b,v)=>dcProcess.allowsFileState()?t.callServerTool({name:b,arguments:v}):Promise.reject(new Error("No current file invocation."))')
    runtime = replace_once(runtime, "ls=(b,v={})=>p(b,{tool_name:MJ(xt??oy),...v})",
        "ls=(b,v={})=>dcProcess.allowsFileState()?p(b,{tool_name:MJ(xt??oy),...v}):undefined")
    runtime = replace_once(runtime, "t.ontoolinput=b=>{let v=",
        "t.ontoolinput=b=>{const dcInputGeneration=++dcGeneration;if(dcProcess.input(b.arguments))return;a??=r.read()??undefined;let v=")
    runtime = replace_once(runtime, "J3(y,x=>{c=!0,",
        "J3(y,x=>{if(dcInputGeneration!==dcGeneration||!dcProcess.allowsFileState())return;c=!0,")
    runtime = replace_once(runtime, "t.ontoolresult=b=>{if(a=void 0,c)",
        "t.ontoolresult=dcToolResult=b=>{if(dcProcess.result(b))return;const dcResultGeneration=dcGeneration;if(a=void 0,c)")
    runtime = replace_once(runtime, "C=D=>{c=!0;",
        "C=D=>{if(dcResultGeneration!==dcGeneration||!dcProcess.allowsFileState())return;c=!0;")
    runtime = replace_once(runtime, "A=()=>{v&&(d?",
        "A=()=>{if(dcResultGeneration!==dcGeneration||!dcProcess.allowsFileState())return;v&&(d?")
    runtime = replace_once(runtime, "a=r.read()??void 0",
        "a=dcProcess.allowsFileState()?r.read()??undefined:undefined")
    runtime = replace_once(runtime, "e.innerHTML=f.html,document.body",
        "e.innerHTML=f.html,dcBindProcessSnapshot(e,t),document.body")
    runtime = replace_once(runtime, "function nD(){", "function nD(){let dcWidgetState;")
    runtime = replace_once(runtime, 'r=W$(b=>kc(b)&&typeof b.content=="string")',
        'r=()=>dcWidgetState??=W$(b=>kc(b)&&typeof b.content=="string")')
    bootstrap = runtime.index("function nD(){")
    runtime = runtime[:bootstrap] + runtime[bootstrap:].replace("r.read()", "r().read()").replace("r.write(", "r().write(")
    source[runtime_path] = runtime
    source["dist/ui/file-preview/styles.css"] += """
.output-preview .code-viewer, .output-preview .code-viewer code {
  white-space: pre-wrap; overflow-wrap: anywhere; word-break: normal;
}
.output-preview .code-viewer { padding: 12px; font-size: 12px; }
"""
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
    """Accept pristine vendor bytes or the exact deployed v1; restore on failure."""
    package = Path(package)
    if json.loads((package / "package.json").read_text())["version"] != VERSION:
        raise RuntimeError("Unsupported Desktop Commander preview package version")
    helper = Path(__file__).with_name("desktop_commander_preview_ui.js").read_text()
    fingerprint = digest(Path(__file__).read_bytes() + helper.encode("utf8"))
    marker = package / MARKER_PATH
    recorded = json.loads(marker.read_text()) if marker.exists() else None
    if recorded and recorded.get("overlay") == OVERLAY:
        if recorded.get("fingerprint") != fingerprint:
            raise RuntimeError("A different Desktop Commander preview overlay is installed")
        if set(recorded.get("sha256", {})) != set(BASE_SHA256) | {HELPER_PATH}:
            raise RuntimeError("Incomplete Desktop Commander preview overlay manifest")
        for name, expected in recorded["sha256"].items():
            if digest((package / name).read_bytes()) != expected:
                raise RuntimeError("Installed Desktop Commander preview overlay has changed: " + name)
        return False
    previous = {name: (package / name).read_bytes() for name in BASE_SHA256}
    if recorded:
        if (recorded.get("overlay") != "compact-file-preview-v1"
                or recorded.get("fingerprint") != V1_FINGERPRINT
                or recorded.get("sha256") != V1_SHA256):
            raise RuntimeError("Unsupported Desktop Commander preview overlay upgrade")
        expected = dict(BASE_SHA256, **V1_SHA256)
        previous[HELPER_PATH] = (package / HELPER_PATH).read_bytes()
        for name, value in previous.items():
            if digest(value) != expected[name]:
                raise RuntimeError("Deployed Desktop Commander preview asset has changed: " + name)
    else:
        for name, expected in BASE_SHA256.items():
            if digest(previous[name]) != expected:
                raise RuntimeError("Unsupported Desktop Commander preview asset: " + name)
        if (package / HELPER_PATH).exists():
            raise RuntimeError("Untracked Desktop Commander preview helper already exists")
        previous = build_file_overlay(previous, helper)
    outputs = build_process_overlay(previous, helper)
    manifest = {
        "overlay": OVERLAY, "fingerprint": fingerprint,
        "sha256": {name: digest(value) for name, value in outputs.items()},
    }
    outputs[MARKER_PATH] = (json.dumps(manifest, indent=2) + "\n").encode("utf8")
    before = {
        name: ((package / name).read_bytes(), stat.S_IMODE((package / name).stat().st_mode))
        if (package / name).exists() else None for name in outputs
    }
    written = []
    try:
        for name, value in outputs.items():
            written.append(name)
            atomic_write(package / name, value, before[name][1] if before[name] else 0o644)
    except BaseException:
        for name in reversed(written):
            if before[name]:
                atomic_write(package / name, *before[name])
            else:
                (package / name).unlink(missing_ok=True)
        raise
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({"overlay": OVERLAY, "changed": apply_overlay(args.package)}))

#!/usr/bin/env node
/** Focused pinned-asset and native widget observer. Private inputs stay outside Git. */
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { Script } from 'node:vm';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { cp, readFile, writeFile, mkdir, mkdtemp, chmod } from 'node:fs/promises';
import { createServer } from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { gzipSync, gunzipSync } from 'node:zlib';

const flags = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
    const key = process.argv[i];
    if (!process.argv[i + 1]) throw new Error('Missing value for ' + key);
    if (!flags.has(key)) flags.set(key, []);
    flags.get(key).push(process.argv[i + 1]);
}
const required = (key) => {
    const value = flags.get(key)?.[0];
    if (!value) throw new Error('Required ' + key);
    return value;
};
const packageRoot = required('--package');
const evidence = required('--evidence-dir');
const python = required('--python');
const playwrightRoot = required('--playwright');
const browserBinary = required('--browser');
const packetPaths = flags.get('--private-packet') ?? [];
if (!packetPaths.length) throw new Error('At least one exact private packet is required');
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const overlay = path.join(root, 'implementation/desktop_commander_preview.py');
const helperPath = path.join(root, 'implementation/desktop_commander_preview_ui.js');
const sha = (value) => createHash('sha256').update(value).digest('hex');
await mkdir(evidence, { recursive: true, mode: 0o700 });
await chmod(evidence, 0o700);
async function copyPreviewPackage(destination) {
    await cp(path.join(packageRoot, 'dist/ui'), path.join(destination, 'dist/ui'), { recursive: true });
    await cp(path.join(packageRoot, 'package.json'), path.join(destination, 'package.json'));
    for (const name of ['dist/server.js', 'dist/handlers/terminal-handlers.js']) {
        await mkdir(path.dirname(path.join(destination, name)), { recursive: true });
        await cp(path.join(packageRoot, name), path.join(destination, name));
    }
}
const stage = await mkdtemp(path.join(evidence, 'candidate-'));
await copyPreviewPackage(stage);
const modelOwner = path.join(packageRoot, 'dist/handlers/filesystem-handlers.js');
const modelHash = sha(await readFile(modelOwner));
const apply = () => JSON.parse(execFileSync(python, [overlay, '--package', stage], { encoding: 'utf8', stdio: 'pipe' }));
assert.equal(apply().changed, true, 'overlay applied');
assert.equal(apply().changed, false, 'overlay idempotent');
const upgradeReport = JSON.parse(execFileSync(python, [path.join(root, 'tests/check_desktop_commander_preview_upgrade.py'), '--installed', packageRoot, '--upgraded', stage], { encoding: 'utf8', stdio: 'pipe' }));
const runtimePath = path.join(stage, 'dist/ui/file-preview/preview-runtime.js');
execFileSync(process.execPath, ['--check', runtimePath], { stdio: 'pipe' });
const manifest = JSON.parse(await readFile(path.join(stage, 'dist/ui/file-preview/.compact-preview-overlay.json'), 'utf8'));
for (const name of Object.keys(manifest.sha256).filter((name) => name.endsWith('.js'))) {
    execFileSync(process.execPath, ['--check', path.join(stage, name)], { stdio: 'pipe' });
}
const runtime = await readFile(runtimePath, 'utf8');
const helper = await readFile(helperPath, 'utf8');
assert(runtime.includes(helper.replaceAll('export function ', 'function ')), 'same helper is served');
assert.equal(sha(await readFile(modelOwner)), modelHash, 'model-facing owner is unchanged');

// Tampered output must be rejected; restoration retains the already-checked stage.
const cssPath = path.join(stage, 'dist/ui/file-preview/styles.css');
const css = await readFile(cssPath);
await writeFile(cssPath, Buffer.concat([css, Buffer.from('\n/* drift */\n')]));
assert.throws(apply, /Command failed/, 'installed drift rejected');
await writeFile(cssPath, css);
assert.equal(apply().changed, false);
const driftStage = await mkdtemp(path.join(evidence, 'drift-'));
await copyPreviewPackage(driftStage);
const driftCss = path.join(driftStage, 'dist/ui/file-preview/styles.css');
await writeFile(driftCss, 'upstream changed');
const untouchedRuntimeHash = sha(await readFile(path.join(driftStage, 'dist/ui/file-preview/preview-runtime.js')));
assert.throws(() => execFileSync(python, [overlay, '--package', driftStage], { stdio: 'pipe' }));
assert.equal(sha(await readFile(path.join(driftStage, 'dist/ui/file-preview/preview-runtime.js'))), untouchedRuntimeHash,
    'all upstream assets validated before any write');

// Execute the native installer's overlay/reporting join against a reused release.
const reportingRelease = await mkdtemp(path.join(evidence, 'installer-'));
const reportingPackage = path.join(reportingRelease, 'node_modules/@wonderwhy-er/desktop-commander');
await mkdir(reportingPackage, { recursive: true });
await copyPreviewPackage(reportingPackage);
const reportingProbe = [
    'import ast,sys',
    'from pathlib import Path',
    'root=Path(sys.argv[1]);sys.path.insert(0,str(root/"implementation"))',
    'from desktop_commander_preview import apply_overlay',
    'main=next(n for n in ast.parse((root/"implementation/install.py").read_text()).body if isinstance(n,ast.FunctionDef) and n.name=="main")',
    'assignments=[n for n in main.body if isinstance(n,ast.Assign)]',
    'call=next(n for n in assignments if any(isinstance(t,ast.Name) and t.id=="preview_changed" for t in n.targets))',
    'report=next(n for n in assignments if any(isinstance(t,ast.Name) and t.id=="changed" for t in n.targets) and any(isinstance(v,ast.Name) and v.id=="preview_changed" for v in ast.walk(n.value)))',
    'emit=next(n for n in main.body if isinstance(n,ast.Expr) and any(isinstance(v,ast.Constant) and v.value=="CLOUD_DEV_CHANGED=" for v in ast.walk(n)))',
    'code=compile(ast.Module(body=[call,report,emit],type_ignores=[]),"<native installer reporting>","exec")',
    'scope={"package_dir":Path(sys.argv[2]),"apply_overlay":apply_overlay,"managed":[],"before":{}}',
    'for _ in range(2):',
    ' scope["changed"]=False;exec(code,scope)',
].join('\n');
assert.deepEqual(execFileSync(python, ['-c', reportingProbe, root, reportingRelease], { encoding: 'utf8', stdio: 'pipe' })
    .trim().split('\n'), ['CLOUD_DEV_CHANGED=1', 'CLOUD_DEV_CHANGED=0'], 'native reused-release reporting');

const api = await import('data:text/javascript;base64,' + Buffer.from(helper).toString('base64'));
const escaped = (text) => text.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
async function helperCase(content, range) {
    const payload = Object.freeze({ fileName: 'fixture.packet', filePath: '/fixture/fixture.packet', fileType: 'unsupported', content });
    const snapshot = JSON.stringify(payload);
    let finished;
    const done = new Promise((resolve) => { finished = resolve; });
    api.dcPreparePacketPreview(payload, content, range, finished);
    let body = api.dcPacketPreviewBody(payload, escaped);
    if (body.notice.startsWith('Preparing')) {
        assert.equal(api.dcPacketFooter(payload, ''), 'PACKET');
        let timeout;
        await Promise.race([done, new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('preview timeout')), 3000); })]);
        clearTimeout(timeout);
        body = api.dcPacketPreviewBody(payload, escaped);
    }
    assert.equal(JSON.stringify(payload), snapshot, 'raw payload retained');
    return body;
}
const synthetic = gzipSync(Buffer.from(JSON.stringify({ safe: '<script>untrusted</script>', answer: 42 }))).toString('base64');
assert((await helperCase(synthetic)).html.includes('&lt;script&gt;'), 'decoded text escaped');
assert((await helperCase(synthetic, { isPartial: true })).notice.includes('Partial read'));
assert((await helperCase('not a packet')).notice.includes('Preview unavailable'));
assert((await helperCase('A'.repeat(1024 * 1024 + 1))).notice.includes('Preview too large'));
const oversized = gzipSync(Buffer.alloc(1024 * 1024 + 1, 65)).toString('base64');
assert((await helperCase(oversized)).notice.includes('Preview too large'));
let deep = {};
for (let i = 0; i < 40; i++) deep = { child: deep };
assert((await helperCase(gzipSync(Buffer.from(JSON.stringify(deep))).toString('base64'))).notice.includes('Preview unavailable'));
assert.equal(api.dcPacketPreviewBody({ fileType: 'text', filePath: '/fixture/code.js' }, escaped), undefined);


const requireFromPackage = createRequire(path.join(packageRoot, 'package.json'));
const zod = await import(pathToFileURL(requireFromPackage.resolve('zod')).href);
const schemaSource = await readFile(path.join(packageRoot, 'dist/tools/schemas.js'), 'utf8');
const schemaStart = schemaSource.indexOf('export const ReadProcessOutputArgsSchema');
const schemaEnd = schemaSource.indexOf('export const ', schemaStart + 1);
const processSchema = new Function('z', schemaSource.slice(schemaStart, schemaEnd).replace('export const ', 'const ')
    + ';return ReadProcessOutputArgsSchema;')(zod.z);
const managerSource = await readFile(path.join(packageRoot, 'dist/terminal-manager.js'), 'utf8');
const managerStart = managerSource.indexOf('export class TerminalManager');
const managerEnd = managerSource.indexOf('export const terminalManager', managerStart);
const NativeManager = new Function(managerSource.slice(managerStart, managerEnd).replace('export class ', 'class ')
    + ';return TerminalManager;')();
const nativeManager = new NativeManager();
const processSource = await readFile(path.join(packageRoot, 'dist/tools/improved-process-tools.js'), 'utf8');
const processStart = processSource.indexOf('export async function readProcessOutput(');
const processEnd = processSource.indexOf('export async function ', processStart + 1);
const nativeRead = new Function('ReadProcessOutputArgsSchema', 'MAX_PROCESS_WAIT_MS', 'MAX_BUFFERED_OUTPUT_CHARS',
    'configManager', 'terminalManager', 'getProcessWaitLimit', 'formatProcessStateMessage',
    processSource.slice(processStart, processEnd).replace('export async function ', 'async function ')
    + ';return readProcessOutput;')(
        processSchema, 30000, 50 * 1024 * 1024, { getConfig: async () => ({ fileReadLineLimit: 1000 }) },
        nativeManager, (timeout, cap) => ({ waitMs: Math.min(timeout, cap) }), () => '');
const handlerSource = await readFile(path.join(stage, 'dist/handlers/terminal-handlers.js'), 'utf8');
const handlerStart = handlerSource.indexOf('export async function handleReadProcessOutput(');
const handlerEnd = handlerSource.indexOf('export async function ', handlerStart + 1);
const nativeHandler = new Function('ReadProcessOutputArgsSchema', 'readProcessOutput',
    handlerSource.slice(handlerStart, handlerEnd).replace('export async function ', 'async function ')
    + ';return handleReadProcessOutput;')(processSchema, nativeRead);
const session = {
    outputLines: Array.from({ length: 400 }, (_, i) => '  \u001b[31mline ' + i + ' <script>untrusted</script> left\u0000right ' + 'x'.repeat(120) + '\r').concat(['']),
    lastReadIndex: 0, lastReadOpenLine: '', evictedLines: 0, startTime: new Date(0),
};
nativeManager.completedSessions.set(4242, { session, exitCode: 0, endTime: new Date(1234) });
const processArgs = { pid: 4242, offset: 0, length: 400, timeout_ms: 0 };
const originalResult = await nativeRead(processArgs);
session.lastReadIndex = 0; session.lastReadOpenLine = '';
const processResult = await nativeHandler(processArgs);
assert.deepEqual(processSchema.parse({ ...processArgs, path: '/fixture/unrelated.js' }), processArgs, 'native schema accepts and strips ambiguous path');
assert.deepEqual(processResult.content, originalResult.content, 'native handler preserves original returned blocks');
assert.equal(session.lastReadIndex, 400, 'native offset0 advances only its original read');
assert.deepEqual(processResult._meta, { 'desktop-commander/preview': { kind: 'process_output', pid: 4242 } });
assert.equal(processResult.structuredContent, undefined, 'stdout is not duplicated into structuredContent');
const expectedProcessText = processResult.content.map((block) => block.text).join('\n');
const processDisplay = expectedProcessText.slice(0, 48 * 1024).split('\n').slice(0, 240).join('\n');

const cases = [];
for (const packetPath of packetPaths) {
    const content = await readFile(packetPath, 'utf8');
    let decoded;
    try { decoded = JSON.stringify(JSON.parse(gunzipSync(Buffer.from(content, 'base64')).toString('utf8')), null, 2); }
    catch { throw new Error('Exact private packet is not gzip/base64 JSON'); }
    cases.push({
        name: path.basename(packetPath), packetPath, type: 'unsupported', content,
        expected: decoded.slice(0, 48 * 1024).split('\n').slice(0, 240).join('\n'),
        decoded: true,
    });
}
cases.push(
    { name: 'ordinary.js', packetPath: '/fixture/ordinary.js', type: 'text', content: 'const actual = 42;\n', ordinary: true },
    { name: 'partial.js', packetPath: '/fixture/partial.js', type: 'text', content: '[Reading 2 lines from line 20 (total: 100 lines, 78 remaining)]\n\nconst before = 1;\nconst after = 2;', partial: true, args: { offset: 20, length: 2 } },
    { name: 'partial.packet', packetPath: '/fixture/partial.packet', type: 'unsupported', content: '[Reading 1 lines from line 2 (total: 3 lines, 1 remaining)]\n\n' + synthetic, partialPacket: true, args: { offset: 2, length: 1 } },
    { name: 'invalid.packet', packetPath: '/fixture/invalid.packet', type: 'unsupported', content: 'not a packet', invalid: true },
    { name: 'limit.packet', packetPath: '/fixture/limit.packet', type: 'unsupported', content: oversized, limited: true },
);

cases.push({ ...cases[0], dark: true });
cases.push({ name: 'file-order.js', packetPath: '/fixture/file-order.js', type: 'text', content: 'const exact = 1;\n', ordinary: true, order: 'file-result-first' });


const snapshotCase = {
    name: 'Process 4242 output', process: true, args: processArgs, result: processResult,
    content: expectedProcessText, expected: processDisplay,
};
cases.push(
    { ...snapshotCase, scenario: 'known-input-first' },
    { ...snapshotCase, scenario: 'generic-host-no-persistence', fallbackHost: true, noToolInfo: true },
    { ...snapshotCase, scenario: 'ambiguous-pid-path', noToolInfo: true, unavailable: true, args: { ...processArgs, path: '/fixture/unrelated.js' } },
    { ...snapshotCase, scenario: 'unknown-input-first', noToolInfo: true },
    { ...snapshotCase, scenario: 'unknown-result-first', noToolInfo: true, order: 'result-first' },
    { ...snapshotCase, scenario: 'metadata-only-result-first', noToolInfo: true, order: 'result-first', args: {} },
    { ...snapshotCase, scenario: 'late-file-race', noToolInfo: true, race: true },
    { ...snapshotCase, scenario: 'rendered-file-context-race', noToolInfo: true, readyFile: true },
    { ...snapshotCase, scenario: 'directory-child-handoff', noToolInfo: true, directoryHandoff: true },
    { ...snapshotCase, scenario: 'missing-identity', unavailable: true, result: { content: processResult.content } },
    { ...snapshotCase, scenario: 'missing-identity-result-first', noToolInfo: true, order: 'result-first', unavailable: true, result: { content: processResult.content } },
    { ...snapshotCase, scenario: 'missing-text', unavailable: true, result: { ...processResult, content: [] } },
    { ...snapshotCase, scenario: 'mismatched-pid', unavailable: true, args: { ...processArgs, pid: 4243 } },
    { ...snapshotCase, scenario: 'unsupported-multiple-blocks', unavailable: true, result: { ...processResult, content: [{ type: 'text', text: 'first' }, { type: 'text', text: 'second' }] } },
    { ...snapshotCase, scenario: 'present-empty-text', content: '', expected: '', result: { ...processResult, content: [{ type: 'text', text: '' }] } },
);

const nativeResources = await import(pathToFileURL(path.join(stage, 'dist/ui/resources.js')).href);
const resource = await nativeResources.getFilePreviewResourceText();
assert(resource.includes('Content-Security-Policy'), 'native CSP/inliner boundary is used');
const HARNESS = String.raw`<!doctype html><meta name="viewport" content="width=device-width, initial-scale=1"><style>
html,body{margin:0;color-scheme:light dark;background:light-dark(#fff,#1e1e2e);font-family:system-ui}main{padding:8px}iframe{display:block;width:100%;height:760px;border:0}
</style><main><iframe id="widget" title="Actual file preview"></iframe></main><script>
(async()=>{
  const fixture=await fetch('/case').then(r=>r.json());
  const widget=document.getElementById('widget');
  widget.dataset.fallbackHost=fixture.fallbackHost?'true':'false';
  window.__reads=[];window.__calls=[];window.__modelUpdates=0;window.__nonemptyModelUpdates=0;
  let raceStarted=false;
  const send=(method,params)=>widget.contentWindow.postMessage({jsonrpc:'2.0',method,params},'*');
  const exerciseContext=()=>{
    send('ui/notifications/host-context-changed',{displayMode:'fullscreen'});
    send('ui/notifications/host-context-changed',{displayMode:'inline'});
    const child=widget.contentWindow;
    child.dispatchEvent(new Event('focus'));
    child.document.dispatchEvent(new Event('visibilitychange'));
  };
  const deliverProcess=()=>{
    if(fixture.readyFile||fixture.directoryHandoff)window.__beforeProcess={
      calls:[...window.__calls],reads:widget.contentWindow.__stateReads,writes:widget.contentWindow.__stateWrites
    };
    if(fixture.order==='result-first'){
      send('ui/notifications/tool-result',fixture.result);
      setTimeout(()=>send('ui/notifications/tool-input',{arguments:fixture.args}),25);
    }else{
      send('ui/notifications/tool-input',{arguments:fixture.args});
      setTimeout(()=>send('ui/notifications/tool-result',fixture.result),fixture.readyFile?150:25);
    }
    setTimeout(exerciseContext,90);
  };
  window.__deliverProcess=deliverProcess;
  window.addEventListener('message',(event)=>{
    if(event.source!==widget.contentWindow)return;
    const m=event.data;if(!m||m.jsonrpc!=='2.0')return;
    const reply=(result)=>event.source.postMessage({jsonrpc:'2.0',id:m.id,result},'*');
    if(m.method==='ui/initialize')reply({
      protocolVersion:m.params.protocolVersion,hostInfo:{name:'offline-preview-review',version:'1'},
      hostCapabilities:{serverTools:{},updateModelContext:{text:{}}},
      hostContext:{theme:fixture.theme,displayMode:'inline',availableDisplayModes:['inline','fullscreen'],
        containerDimensions:{width:374},
        ...(fixture.noToolInfo?{}:{toolInfo:{tool:{name:fixture.process?'read_process_output':'read_file',inputSchema:{type:'object'}}}})}
    });
    else if(m.method==='ui/notifications/initialized'){
      exerciseContext();
      if(fixture.directoryHandoff)send('ui/notifications/tool-input',{arguments:{path:'/fixture/dir'}});
      else if(fixture.race||fixture.readyFile)send('ui/notifications/tool-input',{arguments:{path:fixture.readyFile?'/fixture/ready.md':'/fixture/late-file.js',...(fixture.readyFile?{offset:20,length:2}:{})}});
      else if(fixture.process)setTimeout(deliverProcess,20);
      else if(fixture.order==='file-result-first'){
        send('ui/notifications/tool-result',fixture.result);
        setTimeout(()=>send('ui/notifications/tool-input',{arguments:fixture.args}),25);
      }else send('ui/notifications/tool-input',{arguments:fixture.args});
    }else if(m.method==='tools/call'){
      window.__calls.push(m.params.name);
      if(m.params.name==='read_file'){
        window.__reads.push(m.params.arguments);
        if(fixture.directoryHandoff){
          const directory=m.params.arguments.path==='/fixture/dir';
          reply({content:[{type:'text',text:directory?'[FILE] child.js':'const child = 1;'}],
            structuredContent:{fileName:directory?'dir':'child.js',filePath:directory?'/fixture/dir':'/fixture/dir/child.js',fileType:directory?'directory':'text'}});
        }else if(fixture.readyFile){
          reply({content:[{type:'text',text:'[Reading 2 lines from line 20 (total: 100 lines, 78 remaining)]\n\n# Existing partial file\nbody'}],
            structuredContent:{fileName:'ready.md',filePath:'/fixture/ready.md',fileType:'markdown'}});
          if(!raceStarted){raceStarted=true;setTimeout(deliverProcess,150);}
        }else if(fixture.race&&!raceStarted){
          raceStarted=true;deliverProcess();
          setTimeout(()=>reply({content:[{type:'text',text:'late file must not replace process output'}],
            structuredContent:{fileName:'late-file.js',filePath:'/fixture/late-file.js',fileType:'text'}}),120);
        }else reply(fixture.result);
      }else reply({content:[]});
    }else if(m.method==='ui/update-model-context'){
      window.__modelUpdates++;if(m.params.content?.length)window.__nonemptyModelUpdates++;reply({});
    }else if(m.id!==undefined)reply({});
  });
  widget.srcdoc=await fetch('/resource').then(r=>r.text());
})();
</script>`;
for (const [name, document] of [['native-resource', resource], ['offline-host', HARNESS]]) {
    const start = document.indexOf('<script>') + '<script>'.length;
    const end = document.lastIndexOf('</script>');
    assert(start >= '<script>'.length && end > start, 'inline script exists');
    new Script(document.slice(start, end), { filename: name + '.js' });
}
let current;
const server = createServer((request, response) => {
    response.setHeader('Cache-Control', 'no-store');
    if (request.url.startsWith('/resource')) {
        response.setHeader('Content-Type', 'text/html; charset=utf-8');
        response.end(resource);
    } else if (request.url.startsWith('/case')) {
        response.setHeader('Content-Type', 'application/json');
        response.end(JSON.stringify({
            theme: current.dark ? 'dark' : 'light',
            process: current.process, noToolInfo: current.noToolInfo, fallbackHost: current.fallbackHost, order: current.order, race: current.race, readyFile: current.readyFile, directoryHandoff: current.directoryHandoff,
            args: current.process ? current.args : { path: current.packetPath, ...current.args },
            result: current.process ? current.result : { content: [{ type: 'text', text: current.content }], structuredContent: {
                fileName: current.name, filePath: current.packetPath, fileType: current.type,
            } },
        }));
    } else {
        response.setHeader('Content-Type', 'text/html; charset=utf-8');
        response.end(HARNESS);
    }
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const { chromium } = await import(pathToFileURL(path.join(playwrightRoot, 'index.mjs')).href);
const browser = await chromium.launch({ executablePath: browserBinary, headless: true, args: ['--no-sandbox'] });
const context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true });
await context.addInitScript(() => {
    window.__stateReads = 0; window.__stateWrites = 0;
    const stale = { payload: { fileName: 'stale.js', filePath: '/fixture/stale-saved.js', fileType: 'text', content: 'stale saved file must not activate' } };
    if (window.frameElement?.dataset.fallbackHost !== 'true') {
        window.openai = { setWidgetState: () => { window.__stateWrites++; } };
        Object.defineProperty(window.openai, 'widgetState', { get: () => { window.__stateReads++; return stale; } });
    } else {
        for (const method of ['getItem', 'setItem']) {
            const original = Storage.prototype[method];
            Storage.prototype[method] = function(key, ...args) {
                if (String(key).startsWith('desktop-commander:widget-state')) {
                    if (method === 'getItem') window.__stateReads++;
                    else window.__stateWrites++;
                }
                return original.call(this, key, ...args);
            };
        }
    }
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: {
        writeText: async (text) => { window.__dcCopied = text; },
    } });
});
const report = { stage, upgradeReport, modelFacingOwnerSha256: modelHash, helperSha256: sha(helper), runtimeSha256: sha(runtime), cases: [] };
try {
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (error) => errors.push({ name: error.name, frames: error.stack?.split('\n').slice(1, 4) }));
    for (let index = 0; index < cases.length; index++) {
        current = cases[index];
        await page.emulateMedia({ colorScheme: current.dark ? 'dark' : 'light' });
        await page.goto('http://127.0.0.1:' + server.address().port + '/?case=' + index);
        const frame = page.frameLocator('#widget');
        if (current.directoryHandoff) {
            const before = frame.locator('#compact-toggle');
            await before.waitFor({ state: 'visible' });
            if (await before.getAttribute('aria-expanded') !== 'true') await before.click();
            await frame.locator('.dir-row-file').first().click();
            await before.locator('.compact-label').filter({ hasText: 'child.js' }).waitFor();
            await frame.locator('#dir-back').waitFor({ state: 'visible' });
            await page.evaluate(() => window.__deliverProcess());
            await frame.locator('#compact-toggle .compact-label').filter({ hasText: current.name }).waitFor();
        }
        const assertProcessBoundary = async () => {
            await page.waitForTimeout(220);
            const calls = await page.evaluate(() => window.__calls);
            const baseline = (current.readyFile || current.directoryHandoff) ? await page.evaluate(() => window.__beforeProcess) : null;
            if (baseline) assert(baseline.calls.includes('read_file'), 'real prior file view activated');
            assert.deepEqual(calls, baseline?.calls ?? (current.race ? ['read_file'] : []), 'no further tool calls for process snapshot');
            const state = await frame.locator('body').evaluate(() => ({ reads: window.__stateReads, writes: window.__stateWrites }));
            assert.deepEqual(state, baseline ? { reads: baseline.reads, writes: baseline.writes } : { reads: current.race ? 1 : 0, writes: 0 }, 'no process state restoration or persistence');
            if (current.fallbackHost) assert.equal(await frame.locator('body').evaluate(() => window.name), '', 'generic host does not create a persistent widget id');
            assert.equal(await frame.locator('#open-in-folder,#open-in-editor,#load-before,#load-after,#dir-back,.line-num').count(), 0, 'no filesystem controls or line anchors');
            assert.equal(await page.evaluate((ready) => ready ? window.__nonemptyModelUpdates : window.__modelUpdates, current.readyFile || current.directoryHandoff), 0, 'no process filesystem annotation context');
        };
        if (current.unavailable) {
            await frame.locator('.compact-row').filter({ hasText: 'Process output unavailable from this host.' }).waitFor();
            await assertProcessBoundary();
            assert.equal(await frame.locator('#copy-source,.output-preview').count(), 0, 'unavailable data is not invented');
            report.cases.push({ scenario: current.scenario, passed: true });
            continue;
        }
        const toggle = frame.locator('#compact-toggle');
        try { await toggle.waitFor({ state: 'visible', timeout: 15000 }); }
        catch (error) { console.error(JSON.stringify({ scenario: current.scenario ?? current.name, errors })); throw error; }
        assert.equal(await toggle.locator('.compact-label').textContent(), current.name, 'actual filename first');
        assert((await toggle.getAttribute('aria-label')).startsWith(current.process ? current.name : current.packetPath), 'accessible source identity');
        if (await toggle.getAttribute('aria-expanded') !== 'true') await toggle.click();
        if (current.process) {
            await assertProcessBoundary();
            const body = await frame.locator('.output-preview code').textContent();
            assert.equal(sha(body), sha(current.expected), 'exact native output excerpt including header/whitespace/CRLF/ANSI');
            assert.equal(await frame.locator('.output-preview script').count(), 0, 'stdout is inert escaped text');
        } else if (current.decoded) {
            await frame.locator('.notice').filter({ hasText: 'Decoded JSON preview' }).waitFor();
            const body = await frame.locator('.packet-preview code').textContent();
            assert.equal(sha(body), sha(current.expected), 'exact packet preview body');
            assert.equal(await frame.locator('.packet-preview [data-line]').count(), 0, 'no invented file lines');
        } else if (current.partialPacket) {
            await frame.locator('.notice').filter({ hasText: 'Partial read' }).waitFor();
        } else if (current.invalid) {
            await frame.locator('.notice').filter({ hasText: 'Preview unavailable' }).waitFor();
        } else if (current.limited) {
            await frame.locator('.notice').filter({ hasText: 'Preview too large' }).waitFor();
        } else if (current.partial) {
            assert.equal(await toggle.locator('.compact-filename').textContent(), 'Lines 20–21');
            assert.equal(await frame.locator('.code-line').first().getAttribute('data-line'), '20');
        } else {
            assert.equal(await frame.locator('.code-line').first().getAttribute('data-line'), '1');
        }
        const metrics = await frame.locator('.panel-content-wrapper').evaluate((element) => {
            const rgb = (value) => {
                const parts = value.match(/[0-9.]+/g)?.map(Number);
                if (!parts || parts.length < 3) return null;
                return { color: parts.slice(0, 3).map((n) => value.startsWith('color(srgb') ? n * 255 : n), alpha: parts[3] ?? 1 };
            };
            const background = (node) => {
                for (let current = node; current; current = current.parentElement) {
                    const value = rgb(getComputedStyle(current).backgroundColor);
                    if (value?.alpha === 1) return value.color;
                }
                return rgb(getComputedStyle(parent.document.body).backgroundColor).color;
            };
            const luminance = (color) => color.map((n) => {
                const v = n / 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
            }).reduce((sum, n, i) => sum + n * [0.2126, 0.7152, 0.0722][i], 0);
            const contrast = (node) => {
                if (!node) return null;
                const foreground = luminance(rgb(getComputedStyle(node).color).color);
                const behind = luminance(background(node));
                return (Math.max(foreground, behind) + 0.05) / (Math.min(foreground, behind) + 0.05);
            };
            const text = element.querySelector('code, .line-content') || element;
            return {
                height: element.getBoundingClientRect().height,
                previewHeight: document.getElementById('tool-shell').getBoundingClientRect().height,
                horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 1,
                viewportWidth: innerWidth, viewportHeight: innerHeight,
                fontSize: getComputedStyle(text).fontSize, lineHeight: getComputedStyle(text).lineHeight,
                codeContrast: contrast(text),
                noticeContrast: contrast(document.querySelector('.notice')),
                parentLabelContrast: contrast(document.querySelector('.panel-breadcrumb')),
                footerContrast: contrast(document.querySelector('.panel-footer')),
                compactLabelContrast: contrast(document.querySelector('#compact-toggle .compact-label')),
            };
        });
        assert(metrics.height <= Math.min(metrics.viewportHeight * 0.35, 140) + 0.5, 'bounded mobile content');
        if (current.decoded) assert(metrics.previewHeight <= 280.5, 'compact total mobile preview ' + JSON.stringify(metrics));
        for (const [name, value] of Object.entries(metrics)) {
            if (name.endsWith('Contrast') && value !== null) assert(value >= 4.5, name + ' text contrast');
        }
        assert.equal(metrics.horizontalOverflow, false, 'no mobile page overflow');
        assert.equal(await frame.locator('#copy-source').getAttribute('aria-label'),
            current.process ? 'Copy output snapshot' : current.type === 'unsupported' ? 'Copy original encoded source' : 'Copy source');
        const reads = await page.evaluate(() => window.__reads);
        if (!current.process) {
            assert.equal(reads.length, 1, 'one faithful UI read');
            assert.deepEqual(reads[0], { path: current.packetPath, ...current.args, origin: 'ui' });
        }
        if (current.decoded) {
            const image = path.join(evidence, current.dark ? 'mobile-dark.png' : 'mobile-' + index + '.png');
            await page.screenshot({ path: image });
            await chmod(image, 0o600);
        }
        await frame.locator('#copy-source').click();
        await frame.locator('body').evaluate(async () => {
            for (let i = 0; i < 100 && window.__dcCopied === undefined; i++) await new Promise((resolve) => setTimeout(resolve, 10));
        });
        const copied = await frame.locator('body').evaluate(() => window.__dcCopied);
        const rawSource = current.process ? current.content : current.content.replace(/^\[Reading [^\]]+\]\r?\n(?:\r?\n)?/, '');
        assert.equal(typeof copied, 'string', 'native copy handler called');
        assert.equal(sha(copied), sha(rawSource), 'copy retains original text');
        if (current.process || current.type === 'unsupported') {
            await frame.locator(current.process ? '.output-preview code' : '.packet-preview code').evaluate((element) => {
                const selection = window.getSelection();
                const range = document.createRange();range.selectNodeContents(element);
                selection.removeAllRanges();selection.addRange(range);
                document.dispatchEvent(new Event('selectionchange'));
            });
            await page.waitForTimeout(300);
            assert.equal(await page.evaluate((ready) => ready ? window.__nonemptyModelUpdates : window.__modelUpdates, current.readyFile || current.directoryHandoff), 0, 'projected view has no file selection context');
            if (current.process) await assertProcessBoundary();
        }
        if (current.ordinary) {
            await frame.locator('.line-content').first().evaluate((element) => {
                const selection = window.getSelection();
                const range = document.createRange(); range.selectNodeContents(element);
                selection.removeAllRanges(); selection.addRange(range);
                document.dispatchEvent(new Event('selectionchange'));
            });
            await page.waitForTimeout(300);
            assert((await page.evaluate(() => window.__modelUpdates)) > 0, 'ordinary native selection observer is active');
        }
        report.cases.push({ name: current.name, scenario: current.scenario, theme: current.dark ? 'dark' : 'light', passed: true, sourceSha256: sha(current.content), ...metrics });
    }
    assert.deepEqual(errors, [], 'native widget browser errors');
    report.passed = true;
    await writeFile(path.join(evidence, 'report.json'), JSON.stringify(report, null, 2) + '\n', { mode: 0o600 });
    console.log(JSON.stringify({ passed: true, cases: report.cases.length, report: path.join(evidence, 'report.json'), stage }));
} finally {
    await context.close();
    await browser.close();
    await new Promise((resolve) => server.close(resolve));
}

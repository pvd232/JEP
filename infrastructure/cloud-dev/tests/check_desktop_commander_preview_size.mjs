#!/usr/bin/env node
/** Observe compact resource metadata through the shipped ChatGPT parser and height owner. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdtempSync,rmSync,openSync,readSync,closeSync} from 'node:fs';
import {join,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';

const flags=new Map();
for(let i=2;i<process.argv.length;i+=2){
  assert(process.argv[i+1],'Missing value for '+process.argv[i]);
  flags.set(process.argv[i],process.argv[i+1]);
}
const snapshotPath=flags.get('--snapshot');
assert(snapshotPath,'Expected --snapshot');
const sha=value=>createHash('sha256').update(value).digest('hex');
const packageRoot=flags.get('--package');
if(packageRoot){
  // Generate candidate bytes in memory; the installed package is read-only.
  const python=flags.get('--python');assert(python,'Expected --python');
  const root=dirname(dirname(fileURLToPath(import.meta.url)));
  const build=[
    'import json,sys',
    'from pathlib import Path',
    'root,package=map(Path,sys.argv[1:])',
    'sys.path.insert(0,str(root/"implementation"))',
    'import desktop_commander_preview as p',
    'assert json.loads((package/"package.json").read_text())["version"]==p.VERSION',
    'marker=json.loads((package/p.MARKER_PATH).read_text())',
    'assert marker["fingerprint"]==p.V1_FINGERPRINT',
    'assert marker["sha256"]==p.V1_SHA256',
    'expected=dict(p.BASE_SHA256,**p.V1_SHA256)',
    'previous={name:(package/name).read_bytes() for name in set(p.BASE_SHA256)|{p.HELPER_PATH}}',
    'for name,value in previous.items():',
    '    assert p.digest(value)==expected[name],name',
    'helper=(root/"implementation/desktop_commander_preview_ui.js").read_text()',
    'candidate=p.build_process_overlay(previous,helper)',
    'name="dist/ui/resources.js"',
    'print(json.dumps({"beforeSource":previous[name].decode(),"candidateSource":candidate[name].decode(),',
    ' "sourceSha256":{"overlay":p.digest((root/"implementation/desktop_commander_preview.py").read_bytes()),',
    ' "helper":p.digest(helper.encode()),"beforeResource":p.digest(previous[name]),',
    ' "candidateResource":p.digest(candidate[name]),"candidateRuntime":p.digest(candidate["dist/ui/file-preview/preview-runtime.js"])}}))',
  ].join('\n');
  const generated=JSON.parse(execFileSync(python,['-c',build,root,packageRoot],{encoding:'utf8',stdio:'pipe'}));
  const contracts=await import(pathToFileURL(join(packageRoot,'dist/ui/contracts.js')).href);
  const render=source=>{
    const start=source.indexOf('function getUiResourceMeta()');
    assert(start>=0&&source.includes("const UI_RESOURCE_MIME_TYPE = 'text/html;profile=mcp-app';"));
    const functions=source.slice(start).replaceAll('export function ','function ').replaceAll('export async function ','async function ');
    const resource={mimeType:'text/html;profile=mcp-app'};
    return new Function('UI_RESOURCE_CSP','FILE_PREVIEW_RESOURCE_URI','CONFIG_EDITOR_RESOURCE_URI',
      'FILE_PREVIEW_RESOURCE','CONFIG_EDITOR_RESOURCE','getFilePreviewResourceText','getConfigEditorResourceText',
      functions+';return readUiResource;')(
        contracts.UI_RESOURCE_CSP,contracts.FILE_PREVIEW_RESOURCE_URI,contracts.CONFIG_EDITOR_RESOURCE_URI,
        resource,resource,async()=>'<p>Public fixture</p>',async()=>'<p>Config fixture</p>');
  };
  const before=render(generated.beforeSource),candidate=render(generated.candidateSource);
  const record={sourceSha256:generated.sourceSha256,controlledResourceBody:true,nativeHostVerified:false,
    before:{file:await before(contracts.FILE_PREVIEW_RESOURCE_URI),config:await before(contracts.CONFIG_EDITOR_RESOURCE_URI)},
    candidate:{file:await candidate(contracts.FILE_PREVIEW_RESOURCE_URI),config:await candidate(contracts.CONFIG_EDITOR_RESOURCE_URI)}};
  assert.equal(record.candidate.file.contents[0]._meta['openai/widgetHeightHint'],32);
  assert.equal(record.candidate.file.contents[0]._meta['openai/widgetMinFrameHeight'],32);
  assert.deepEqual(record.candidate.config,record.before.config,'Config resource must retain every original field');
  const {_meta,...fileWithoutMeta}=record.candidate.file.contents[0];
  assert.deepEqual(fileWithoutMeta,Object.fromEntries(Object.entries(record.before.file.contents[0]).filter(([key])=>key!=='_meta')));
  assert.deepEqual(_meta.ui,record.before.file.contents[0]._meta.ui,'Existing CSP retained');
  writeFileSync(snapshotPath,JSON.stringify(record,null,2)+'\n',{mode:0o600});
  console.log(JSON.stringify({resourceMetadata:true,installedPackageModified:false,nativeHostVerified:false,
    sourceSha256:record.sourceSha256,snapshotSha256:sha(readFileSync(snapshotPath))}));
} else {
  const archivePath=flags.get('--native-asar');assert(archivePath,'Expected --native-asar');
  const record=JSON.parse(readFileSync(snapshotPath,'utf8'));
  const fd=openSync(archivePath,'r'),prefix=Buffer.alloc(16);
  readSync(fd,prefix,0,16,0);
  const headerBytes=Buffer.alloc(prefix.readUInt32LE(12));
  readSync(fd,headerBytes,0,headerBytes.length,16);
  const assets=JSON.parse(headerBytes).files.webview.files.assets.files,base=8+prefix.readUInt32LE(4);
  const temporary=mkdtempSync('/tmp/dc-preview-size-native-');
  try{
    const asset=name=>{
      const entry=assets[name];assert(entry&&!entry.unpacked);
      const bytes=Buffer.alloc(entry.size);
      assert.equal(readSync(fd,bytes,0,bytes.length,base+Number(entry.offset)),bytes.length);
      assert.equal(sha(bytes),entry.integrity.hash);return bytes.toString('utf8');
    };
    const one=pattern=>{
      const names=Object.keys(assets).filter(name=>pattern.test(name));
      assert.equal(names.length,1,String(pattern));return names[0];
    };
    const extracted=new Set();
    const extract=name=>{
      assert(/^(resource-|inline-height-|app-shared-|rolldown-runtime-)[\w.-]+\.js$/.test(name));
      if(extracted.has(name))return;extracted.add(name);
      const source=asset(name);writeFileSync(join(temporary,name),source);
      for(const match of source.matchAll(/import\{[^}]+\}from"\.\/([^"]+)"/g))extract(match[1]);
    };
    writeFileSync(join(temporary,'package.json'),'{"type":"module"}');
    const resourceName=one(/^resource-[0-9a-f]+\.js$/),heightName=one(/^inline-height-[0-9a-f]+\.js$/);
    extract(resourceName);extract(heightName);
    const parser=await import(pathToFileURL(join(temporary,resourceName)).href);
    const height=await import(pathToFileURL(join(temporary,heightName)).href);
    parser.r();height.r();
    const cases=[];
    for(const variant of ['before','candidate'])for(const kind of ['file','config']){
      const resource=parser.n(record[variant][kind]);assert.equal(resource.kind,'html');
      const minimum=kind==='file'&&variant==='candidate'?32:200;
      const values=[];
      for(const intrinsic of [null,0,32,42,480,1000]){
        const actual=height.t(intrinsic,resource.heightHint,resource.minFrameHeight,false);
        if(intrinsic!=null)assert.equal(actual,Math.max(intrinsic,minimum));
        else assert.equal(actual,kind==='file'&&variant==='candidate'?32:480);
        values.push({intrinsic,height:actual});
      }
      cases.push({variant,kind,values});
    }
    const report={compactFileMinimumBeforePx:200,compactFileMinimumAfterPx:32,configDefaultUnchanged:true,
      expandedIntrinsicHeightPreserved:true,actualNativeResourceParser:true,actualNativeResourceSchema:true,
      actualNativeInlineHeightOwner:true,controlledResourceBody:true,liveHost:false,headerBottomPositionVerified:false,
      sourceSha256:{...record.sourceSha256,nativeResource:sha(asset(resourceName)),nativeHeight:sha(asset(heightName)),
        snapshot:sha(readFileSync(snapshotPath))},cases};
    if(flags.get('--report'))writeFileSync(flags.get('--report'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{closeSync(fd);rmSync(temporary,{recursive:true,force:true})}
}


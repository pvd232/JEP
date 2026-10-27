// ChatGPT functions.exec controller: keep this async cell running until the full comparison finishes.
// Uses existing own-terminal SSH and connected GitHub tools; credentials stay in their existing stores.
const config = {
  repository: "pvd232/JEP",
  branch: "experiment/csts-proposition-evidence-20261026",
  directory: "training_outputs/proposition_full_20261026",
  runName: "propositions_v41_full_after_indicative",
  sourceCommit: "a6daf0eeea544716d7340f0f24de687e4ba93490",
  validationSha256: "f186e86877e731c96ee9b1c819863b981074bc500dc9aa11c6951ba9fd56e2c9",
  operator: "/home/machina/jep-csts-proposition-indicative-20261026-operator",
  root: "/home/machina/jep-csts-proposition-evidence-20261026",
  pollMilliseconds: 30000
};
const existing = load("proposition_epoch_controller");
if (existing && existing.status === "running" && Date.now() - Date.parse(existing.lastCheckedAt || 0) < 90000)
  throw Error("An epoch controller already holds a recent heartbeat");
const owner = "own-ssh-" + new Date().toISOString().replace(/[^0-9TZ]/g, "");
const state = { owner, status: "starting", pollSeconds: 30, startedAt: new Date().toISOString(),
  checks: 0, publications: 0, failures: 0, sessionId: load("proposition_epoch_initial_ssh_session") || null };
store("proposition_epoch_controller", state);
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
function unpack(result) {
  if (result.isError) throw Error(JSON.stringify(result.structuredContent || result.content));
  const value = result.structuredContent;
  if (typeof value?.content === "string") {
    try { return JSON.parse(value.content); } catch { return value.content; }
  }
  return value;
}
function signature(report) {
  return JSON.stringify({
    identity: report.identity, runStatus: report.run_status, currentStage: report.current_stage,
    stages: Object.fromEntries(Object.entries(report.stages).map(([key, value]) => [key, {
      status: value.status, traceStatus: value.trace_status, epochs: value.epochs,
      stopReason: value.stop_reason, notes: value.notes
    }]))
  });
}
function validate(report) {
  if (report.identity.run_name !== config.runName || report.identity.source_commit !== config.sourceCommit ||
      report.identity.validation_sha256 !== config.validationSha256 || report.validation_rows !== 1572)
    throw Error("Unexpected experiment identity");
}
async function sshRead() {
  if (!state.sessionId) {
    const opened = await tools.exec_command({
      cmd: "ssh -tt -o BatchMode=yes -o ConnectTimeout=15 jep-gpu 'stty -echo; export PS1=\"JEP_GPU> \"; exec bash --noprofile --norc -i'",
      tty: true, yield_time_ms: 1000, max_output_tokens: 1000
    });
    if (!opened.session_id) throw Error("SSH failed: " + opened.output);
    state.sessionId = opened.session_id;
  }
  const marker = "JEP_EPOCH_" + Date.now();
  const script = [
    "import json,subprocess,time",
    "from pathlib import Path",
    "p=Path(" + JSON.stringify(config.operator) + ");out=p/'epoch_publication'",
    "lease=p/'publication_controller_status.json'",
    "old=json.loads(lease.read_text()) if lease.exists() else {}",
    "owner=" + JSON.stringify(owner),
    "if old.get('owner') not in (None,owner) and time.time()-old.get('checked_unix',0)<90:",
    " raise RuntimeError('Another epoch controller owns the live lease')",
    "subprocess.run(['python3',str(p/'export_epoch_scores.py'),'--root'," + JSON.stringify(config.root) +
      ",'--name'," + JSON.stringify(config.runName) + ",'--output',str(out)],check=True,capture_output=True,text=True,timeout=30)",
    "status={'owner':owner,'mode':'own_ssh_connected_github_controller','status':'running','poll_seconds':30,'checked_unix':time.time()}",
    "tmp=lease.with_suffix('.tmp');tmp.write_text(json.dumps(status));tmp.replace(lease)",
    "print('\\n" + marker + ":'+json.dumps({'report':json.loads((out/'epoch_scores.json').read_text()),'markdown':(out/'epoch_scores.md').read_text()})+'\\n" + marker + "_END')"
  ].join("\n");
  const command = "python3 - <<'JEP_READER'\n" + script + "\nJEP_READER\n";
  let output = "";
  try {
    let r = await tools.write_stdin({session_id:state.sessionId,chars:command,yield_time_ms:1000,max_output_tokens:20000});
    output += r.output;
    for (let i = 0; !output.includes(marker + "_END") && i < 10; i++) {
      r = await tools.write_stdin({session_id:state.sessionId,chars:"",yield_time_ms:1000,max_output_tokens:20000});
      output += r.output;
    }
    const begin = output.indexOf(marker + ":");
    const end = output.indexOf("\n" + marker + "_END", begin);
    if (begin < 0 || end < 0) throw Error("Incomplete SSH snapshot: " + output.slice(-1000));
    return JSON.parse(output.slice(begin + marker.length + 1, end).trim());
  } catch (error) {
    state.sessionId = null;
    throw error;
  }
}
async function fetchGithub(path) {
  return unpack(await tools.mcp__codex_apps__github_fetch({url:"https://api.github.com/repos/" + config.repository + path}));
}
async function publish(envelope) {
  const report = envelope.report;
  for (let attempt = 0; attempt < 3; attempt++) {
    const reference = await fetchGithub("/git/ref/heads/" + config.branch);
    const parent = reference.object.sha;
    const commit = await fetchGithub("/git/commits/" + parent);
    const old = unpack(await tools.mcp__codex_apps__github_fetch({
      url:"https://raw.githubusercontent.com/" + config.repository + "/" + parent + "/" + config.directory + "/epoch_scores.json"
    }));
    if (JSON.stringify(old.identity) !== JSON.stringify(report.identity))
      throw Error("Published experiment identity differs");
    for (const [name, phase] of Object.entries(old.stages)) {
      for (const row of phase.epochs) {
        const next = report.stages[name].epochs.find(value => value.epoch === row.epoch);
        if (!next || JSON.stringify(next) !== JSON.stringify(row)) throw Error("Published epoch history must remain intact");
      }
    }
    if (signature(old) === signature(report)) return {published:false,commit:parent};
    const readme = [
      "# Full Qwen proposition comparison", "",
      "[Per-epoch validation scores](epoch_scores.md) · [Raw history](epoch_scores.json)", "",
      "Continuous publication is active through the existing GPU SSH route and connected GitHub tools.",
      "The publisher checks every 30 seconds and appends each newly completed epoch or stage change.",
      "Refresh the GitHub page to see new commits.", "",
      "The active controller keeps a heartbeat outside the training checkout in",
      config.operator + "/publication_controller_status.json.",
      "The hourly completion check provides recovery and final reporting.", "",
      "The experiment starts from pretrained Qwen3-Embedding-8B. The short continuation pilot is stored separately under training_outputs/proposition_indicative_20261026.", ""
    ].join("\n");
    const files = [
      ["epoch_scores.json",JSON.stringify(report,null,2)+"\n"],
      ["epoch_scores.md",envelope.markdown],
      ["README.md",readme]
    ];
    const tree = unpack(await tools.mcp__codex_apps__github_create_tree({
      repository_full_name:config.repository,base_tree_sha:commit.tree.sha,
      tree_elements:files.map(([name,content])=>({path:config.directory+"/"+name,mode:"100644",type:"blob",content}))
    }));
    const created = unpack(await tools.mcp__codex_apps__github_create_commit({
      repository_full_name:config.repository,parent_sha:parent,tree_sha:tree.sha,
      message:"Publish completed Qwen validation epochs"
    }));
    const moved = await tools.mcp__codex_apps__github_update_ref({
      repository_full_name:config.repository,branch_name:config.branch,
      expected_sha:parent,sha:created.sha
    });
    if (!moved.isError && moved.structuredContent?.success) return {published:true,commit:created.sha};
    if (attempt === 2) throw Error("Branch advanced during publication; retry required");
  }
}
let lastSignature = null;
const deadline = Date.now() + 48 * 60 * 60 * 1000;
while (Date.now() < deadline && load("proposition_epoch_controller_stop") !== owner) {
  const started = Date.now();
  try {
    const envelope = await sshRead();
    validate(envelope.report);
    const current = signature(envelope.report);
    if (current !== lastSignature) {
      const result = await publish(envelope);
      state.lastCommit = result.commit;
      if (result.published) {
        state.publications++;
        state.lastPublishedAt = new Date().toISOString();
      }
      lastSignature = current;
    }
    state.status = "running";
    state.lastCheckedAt = new Date().toISOString();
    state.checks++;
    state.failures = 0;
    state.epochs = Object.fromEntries(Object.entries(envelope.report.stages).map(([key,value])=>[key,value.completed_epoch]));
    state.currentStage = envelope.report.current_stage;
    delete state.error;
    store("proposition_epoch_controller",state);
    if (state.checks === 1) {
      notify({epochPublisher:state});
      await yield_control();
    }
    if (["complete","completed","succeeded"].includes(envelope.report.run_status)) {
      state.status = "complete";
      store("proposition_epoch_controller",state);
      break;
    }
  } catch (error) {
    state.status = "retrying";
    state.failures++;
    state.error = String(error);
    state.lastAttemptAt = new Date().toISOString();
    store("proposition_epoch_controller",state);
    if (state.failures === 1) notify({epochPublisherError:state.error});
  }
  await pause(Math.max(0,config.pollMilliseconds - (Date.now() - started)));
}
if (state.status !== "complete") {
  state.status = "stopped";
  store("proposition_epoch_controller",state);
}

#!/bin/bash
# Run on the Mac. Reuse an authenticated VM connector and a private SSH relay.
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export CLOUDSDK_PYTHON_SITEPACKAGES=1
relay_profile=''
relay_port=22022
relay_label=''
while [ "$#" -gt 0 ]; do
  case "$1" in
    --profile|--port|--label)
      if [ "$#" -lt 2 ]; then echo "Missing value for $1" >&2; exit 2; fi
      case "$1" in
        --profile) relay_profile=$2 ;;
        --port) relay_port=$2 ;;
        --label) relay_label=$2 ;;
      esac
      shift 2 ;;
    --help)
      echo 'Usage: start_mac_relay.sh [--profile VM_PROFILE.json] [--port 22022] [--label LABEL]'
      echo 'Without --profile, preserve the established Aether route.'
      exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
if [ "$(uname -s)" != Darwin ]; then
  echo 'Run this setup on your Mac.' >&2
  exit 1
fi
command -v gcloud >/dev/null
command -v python3 >/dev/null
if ! /usr/bin/nc -z -w 2 127.0.0.1 22; then
  echo 'Enable System Settings > General > Sharing > Remote Login, then rerun this script.' >&2
  exit 1
fi

relay_target='peter_aetherlabs_live@aether-dev-peter-vm'
relay_project='aether-dev-peter'
relay_zone='us-central1-a'
relay_account='peter@aetherlabs.live'
relay_helper='/opt/cloud-dev/aether/bin/mac_relay.py'
relay_state='/var/lib/cloud-dev/aether/mac-relay'
if [ -n "$relay_profile" ]; then
  relay_values=()
  relay_profile_values=$(python3 - "$relay_profile" <<'PY'
import json,re,sys
p=json.load(open(sys.argv[1]))
name=p['profile']
if not re.fullmatch(r'[a-z][a-z0-9-]{0,62}',name):
    raise SystemExit('Invalid relay profile name')
t=p['target']; paths=p['paths']
values=[t['linux_user']+'@'+t['vm_name'],t['gcp_project'],t['zone'],t['gcp_account'],paths['install_root']+'/bin/mac_relay.py',paths['state_root']+'/mac-relay','local.chatgpt.mac-relay.'+name]
if any(not isinstance(v,str) or not v or any(ord(c)<32 for c in v) for v in values):
    raise SystemExit('Invalid relay profile values')
if not all(re.fullmatch(r'[A-Za-z0-9_@.+-]+',v) for v in values[:4]):
    raise SystemExit('Invalid relay target')
if any(not v.startswith('/') for v in values[4:6]):
    raise SystemExit('Relay paths must be absolute')
print('\n'.join(values))
PY
  )
  while IFS= read -r relay_value; do relay_values+=("$relay_value"); done <<< "$relay_profile_values"
  relay_target=${relay_values[0]}
  relay_project=${relay_values[1]}
  relay_zone=${relay_values[2]}
  relay_account=${relay_values[3]}
  relay_helper=${relay_values[4]}
  relay_state=${relay_values[5]}
  if [ -z "$relay_label" ]; then relay_label=${relay_values[6]}; fi
fi
relay_label=${relay_label:-live.aetherlabs.chatgpt-mac-relay}
python3 - "$relay_port" "$relay_label" <<'PY'
import re,sys
if not sys.argv[1].isdigit() or not 1024 <= int(sys.argv[1]) <= 65535:
    raise SystemExit('Use an unprivileged relay port between 1024 and 65535')
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]{0,127}',sys.argv[2]):
    raise SystemExit('Invalid LaunchAgent label')
PY
relay_gcloud=$(command -v gcloud)
# Install into the interpreter gcloud actually uses, not the shell's Python.
relay_python=$("$relay_gcloud" info --format='value(basic.python_location)')
if ! "$relay_python" -c 'import numpy' >/dev/null 2>&1; then
  "$relay_python" -m pip install --only-binary=:all: numpy
fi
relay_cloud=(--project="$relay_project" --zone="$relay_zone" --account="$relay_account" --tunnel-through-iap --quiet)
if ! gcloud auth print-access-token --account="$relay_account" >/dev/null 2>&1; then
  gcloud auth login "$relay_account"
fi
printf -v relay_base 'python3 %q --state-root %q' "$relay_helper" "$relay_state"
gcloud compute ssh "$relay_target" "${relay_cloud[@]}" --command="$relay_base check-server"
relay_public_key=$(gcloud compute ssh "$relay_target" "${relay_cloud[@]}" --command="$relay_base public-key")
case "$relay_public_key" in
  'ssh-ed25519 '*) ;;
  *) echo 'Could not retrieve the relay public key.' >&2; exit 1 ;;
esac
relay_authorized_keys="$HOME/.ssh/authorized_keys"
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
touch "$relay_authorized_keys"
chmod 600 "$relay_authorized_keys"
if ! grep -Fq "$relay_public_key" "$relay_authorized_keys"; then
  printf '\nrestrict %s\n' "$relay_public_key" >> "$relay_authorized_keys"
fi
relay_mac_user=$(id -un)
relay_host_key=$(/usr/bin/ssh-keyscan -T 5 -t ed25519 127.0.0.1 2>/dev/null | awk '!/^#/ {print $2 " " $3; exit}')
if [ -z "$relay_host_key" ]; then
  echo 'Could not read the local SSH server public host key.' >&2
  exit 1
fi
printf -v relay_config_command '%s configure --mac-user %q --host-key %q --port %q --gcloud-bin %q' "$relay_base" "$relay_mac_user" "$relay_host_key" "$relay_port" "$relay_gcloud"
gcloud compute ssh "$relay_target" "${relay_cloud[@]}" --command="$relay_config_command"

relay_plist="$HOME/Library/LaunchAgents/$relay_label.plist"
relay_logs="$HOME/Library/Logs/ChatGPTMacRelay/$relay_label"
mkdir -p "$HOME/Library/LaunchAgents" "$relay_logs"
python3 - "$relay_plist" "$relay_label" "$relay_logs" "$relay_gcloud" "$relay_target" "$relay_project" "$relay_zone" "$relay_account" "$relay_port" <<'PY'
import os,plistlib,sys
path,label,logs,gcloud,target,project,zone,account,port=sys.argv[1:]
command=[gcloud,'compute','ssh',target,'--project='+project,'--zone='+zone,'--account='+account,'--tunnel-through-iap','--quiet','--','-N','-T','-o','ExitOnForwardFailure=yes','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3','-R','127.0.0.1:'+port+':127.0.0.1:22']
data={'Label':label,'ProgramArguments':command,'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':15,'StandardOutPath':logs+'/stdout.log','StandardErrorPath':logs+'/stderr.log','EnvironmentVariables':{'PATH':os.environ['PATH'],'CLOUDSDK_PYTHON_SITEPACKAGES':'1'}}
with open(path,'wb') as stream: plistlib.dump(data,stream)
os.chmod(path,0o600)
PY
launchctl bootout "gui/$(id -u)/$relay_label" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$relay_plist"
gcloud compute ssh "$relay_target" "${relay_cloud[@]}" --command="$relay_base verify"
echo "Mac relay installed through $relay_target. LaunchAgent $relay_label reconnects automatically."

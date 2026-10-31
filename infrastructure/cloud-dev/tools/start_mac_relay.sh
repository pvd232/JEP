#!/bin/bash
# Run once on the Mac. Reuse Aether's authenticated connector and private SSH relay.
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
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
relay_cloud=(--project="$relay_project" --zone="$relay_zone" --account="$relay_account" --tunnel-through-iap --quiet)
relay_public_key=$(gcloud compute ssh "$relay_target" "${relay_cloud[@]}" --command="python3 $relay_helper public-key")
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
printf -v relay_config_command 'python3 %q configure --mac-user %q --host-key %q --port 22022' "$relay_helper" "$relay_mac_user" "$relay_host_key"
gcloud compute ssh "$relay_target" "${relay_cloud[@]}" --command="$relay_config_command"

relay_label='live.aetherlabs.chatgpt-mac-relay'
relay_plist="$HOME/Library/LaunchAgents/$relay_label.plist"
relay_logs="$HOME/Library/Logs/ChatGPTMacRelay"
mkdir -p "$HOME/Library/LaunchAgents" "$relay_logs"
relay_gcloud=$(command -v gcloud)
python3 - "$relay_plist" "$relay_label" "$relay_logs" "$relay_gcloud" "$relay_target" "$relay_project" "$relay_zone" "$relay_account" <<'PY'
import os,plistlib,sys
path,label,logs,gcloud,target,project,zone,account=sys.argv[1:]
command=[gcloud,'compute','ssh',target,'--project='+project,'--zone='+zone,'--account='+account,'--tunnel-through-iap','--quiet','--','-N','-T','-o','ExitOnForwardFailure=yes','-o','ServerAliveInterval=30','-o','ServerAliveCountMax=3','-R','127.0.0.1:22022:127.0.0.1:22']
data={'Label':label,'ProgramArguments':command,'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':15,'StandardOutPath':logs+'/stdout.log','StandardErrorPath':logs+'/stderr.log','EnvironmentVariables':{'PATH':os.environ['PATH']}}
with open(path,'wb') as stream: plistlib.dump(data,stream)
os.chmod(path,0o600)
PY
launchctl bootout "gui/$(id -u)/$relay_label" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$relay_plist"
echo 'Mac relay installed. The connection uses the existing Aether VM and reconnects automatically.'

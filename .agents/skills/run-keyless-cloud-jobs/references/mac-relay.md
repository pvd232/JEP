# Mac access through the existing VM

Reuse the already authenticated Aether Dev VM connector and a private reverse
SSH tunnel from the Mac to that VM. This requires no additional VM, public
MCP listener, DNS name or ngrok subscription. The Mac must remain online.

Implementation: `infrastructure/cloud-dev/tools/mac_relay.py` and
`tools/start_mac_relay.sh` in [JEP PR 16](https://github.com/pvd232/JEP/pull/16).
The VM helper and `mac-command` wrapper are installed under
`/opt/cloud-dev/aether/bin/`. Confirm their live availability.

1. On the Mac, enable System Settings > General > Sharing > Remote Login for
   the intended local user. Keep that user's existing GCP administrator login.
2. Run `start_mac_relay.sh` on the Mac. It installs a restricted SSH public
   key, pins the Mac's SSH host key on Aether, and installs a user LaunchAgent
   that reconnects the reverse tunnel. It binds only VM loopback port 22022.
3. Through Aether Dev VM, run `mac-command hostname` and `mac-command id -un`.
   Require the returned host/user to match the Mac before using Mac paths.
4. Use `mac-command COMMAND ARGUMENTS` for Mac CLI work. The underlying
   process runs on macOS. Direct Aether file tools still refer to the VM.

The SSH transport key is distinct from Google service-account credentials.
Google background jobs continue using their VM's keyless workload identity.
IAP still needs its configured GCP firewall rule; an existing working IAP SSH
route supplies this transport without a new public application port.

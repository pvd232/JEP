# Established Mac relay routes

Verify these targets live before changes.

| Route | VM connector | VM identity | Mac command |
| --- | --- | --- | --- |
| Columbia: academic and personal | `columbia-vm` | `dev.c.pvd-dev-232.internal`, user `pvd2112_columbia_edu` | `/opt/cloud-dev/columbia/bin/mac-command` |
| Aether: company | `Aether Dev VM` | `aether-dev-peter-vm.us-central1-a.c.aether-dev-peter.internal`, user `peter_aetherlabs_live` | `/opt/cloud-dev/aether/bin/mac-command` |

Both relay VMs forward their own `127.0.0.1:22022` to the Mac SSH server.
The remote listeners are on different VMs and can use the same port.
Expected Mac identity: `Peters-MacBook-Air-9.local`, user `machina`.

Columbia uses GCP project `pvd-dev-232`, VM `dev`, zone `us-central1-a`,
administrator `pvd2112@columbia.edu`. Its LaunchAgent is
`local.chatgpt.mac-relay.columbia`.

Aether uses project `aether-dev-peter`, VM `aether-dev-peter-vm`, zone
`us-central1-a`, administrator `peter@aetherlabs.live`. Its existing LaunchAgent
is `live.aetherlabs.chatgpt-mac-relay`.

Each VM has its own SSH private key. The Mac authorizes the corresponding
public key with `restrict`; each VM pins the Mac's SSH host key. Neither
relay exposes the Mac SSH server on a public VM listener.

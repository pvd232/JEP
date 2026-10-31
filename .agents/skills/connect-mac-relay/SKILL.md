---
name: connect-mac-relay
description: Run native Mac terminal commands through an existing authenticated VM connector and a private reverse SSH relay over Google IAP. Use for local Mac files, tools, repositories, or apps that require Mac CLI access, and for checking the health of an already configured Aether or Columbia Mac relay. Verify the actual Mac host and user before operating. Keep VM workloads on their intended VM.
---

# Connect Mac Relay

Use the existing authenticated Aether or Columbia connector to execute
`mac-command` on the Mac. Prefer Columbia for academic and personal work;
use Aether for company work. Read [host routes](references/hosts.md) for the
connector and executable paths. Load only the route needed for the task.

## Verify the execution target

1. Confirm the VM's hostname and Linux user through its connector.
2. Run the selected host's `mac-command hostname` and `mac-command id -un`.
3. Require `Peters-MacBook-Air-9.local` and `machina` for the established Mac.
   For another Mac, obtain its expected identity from the authorized setup.
4. Run native Mac commands through `mac-command COMMAND ARGUMENTS`. Use an
   absolute executable and path when available. Quote each argument through
   the VM shell; pass complex work as a quoted Python script or shell argument.
5. Treat the connector's direct file tools as VM file access. Use a Mac-side
   command for Mac reads and writes. Preserve unrelated files and user work.

Use the shortest working route. Once Columbia has verified Mac access,
call its relay directly instead of nesting SSH through Aether. Keep cloud
execution under Run Keyless Cloud Jobs.

## Respect the task and connector boundary

Use only the connected VM plugin and relay already authorized for this
workspace. Resolve the requested command, target machine and file scope from
the user's current task before execution. Treat a working relay as transport;
it grants no additional permission to access files, secrets or other machines.
Honor every platform and connector approval for the underlying operation.

Use read-only identity and listener checks for connection diagnosis. Stop on
an authentication or authorization denial and report the exact required grant.
Keep SSH configuration, IAM, credentials, Remote Login and persistent startup
services outside routine command execution. Perform new relay provisioning
only as a separately explicit user task using the project's reviewed
[cloud development setup](https://github.com/pvd232/JEP/tree/infra/columbia-shared-devbox-20261031/infrastructure/cloud-dev).

## Diagnose connectivity

Check that the Mac is awake, online and accepting local SSH. Inspect only the
selected LaunchAgent and its logs under
`~/Library/Logs/ChatGPTMacRelay/LABEL/`. Check the selected VM's private
listener and run its relay helper's `verify` operation. Preserve the other
working relay while diagnosing a failure. Report a required login through the
user's normal account flow; keep credential values out of output.

## Verify completion

Check the returned Mac identity, a temporary file write/read/delete and the
VM listener's loopback binding. For an explicitly requested installation, verify its documented
reconnection check. Keep secret values out of commands and logs. Report the working connector, actual execution
host and any concrete remaining prerequisite. The Mac must be awake and online.

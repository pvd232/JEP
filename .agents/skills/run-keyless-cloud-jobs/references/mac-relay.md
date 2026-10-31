# Mac relay routing

Apply [Connect Mac Relay](https://github.com/pvd232/agents/blob/main/skills/connect-mac-relay/SKILL.md)
for native Mac commands and connection health checks. Use Columbia for academic
and personal work, and Aether for company work. Both hosts have a private relay
to the same Mac. Verify its hostname and user before operating on Mac paths.

For an explicitly requested new relay installation, use the reviewed
[JEP bootstrap](https://github.com/pvd232/JEP/blob/infra/columbia-shared-devbox-20261031/infrastructure/cloud-dev/tools/start_mac_relay.sh)
with the intended VM profile. The bootstrap handles the Google Cloud CLI's
NumPy dependency and host-specific LaunchAgent configuration.

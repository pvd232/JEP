# Tool rejection: provenance audit and support-ready description

Recorded during the user's November 7, 2026 (New York time) request to identify the tool, safety check, responsible administrator, and resolution path.

## Exact affected integration

- ChatGPT connected app: **Aether Dev VM**.
- Intended action: **`Aether_Dev_VM.start_process`** (remote terminal command on the existing authorized cloud bridge).
- Historical code-mode identifier for that action: **`mcp__Aether_Dev_VM__start_process`**. Some prior turns invoked it through the outer `functions.exec` tool dispatcher.
- Cloud target of the intended deployment: the existing task-owned `jep-full-prompt-spot-2-20261107` L4 instance in GCP project `mantra-477901`, zone `asia-northeast1-b`.
- This is not the local Mac terminal tool, not Google Cloud Shell, and not the native VIPER trainer.

## Reported error and what is actually retained

The contemporaneous assistant-written incident note quotes:

> This tool call was blocked by OpenAI's safety checks. Please double check what you are sending.

The recorded operation would validate completed review receipts and the user's launch authorization, bind worker2 to its currently allocated GPU and shutdown deadline, and copy the launch records over IAP.

**Evidence limitation:** The original rejected tool-call payload, raw transport response, request ID, backend rule identifier, and exact internal component are not retained in the available incident files. The quote above is preserved in the earlier incident note, not independently recovered here from an original transport log. The identifier `start_process` names the intended action; it does not establish that its handler received the rejected request. We cannot locate the rejection more precisely between the outer dispatcher, ChatGPT action checks, and the connector gateway from the retained evidence.

The message attributes the rejection to OpenAI safety checks. That is consistent with OpenAI's documentation of explicit action-safety blocks, but is **not** evidence identifying a specific rule, classifier, team, or human administrator. No Columbia or Google administrator is named in this error. We cannot establish whether this specific decision was a false positive or which input triggered it.

## Incident timing

1. Earlier incident was recorded at 2026-11-08 00:19:57 UTC, i.e. November 7 at 7:19:57 p.m. EST. Exact rejected-call timestamp was not retained.
2. Later incident occurred after the successful worker2 allocation/check around 2026-11-08 03:40 UTC and before its cleanup, verified at 03:42:53 UTC; approximately November 7, 10:40–10:43 p.m. EST. Exact rejected-call timestamp was not retained.

These times must not be represented as backend request IDs or exact denial timestamps.

## Checks performed now

The live `Plugin_Management.get_app_permissions` call for **Aether Dev VM** returned:

- Global default: **Allow low-risk actions**.
- App-specific override: **Allow all actions**.

No permission setting was changed. The missing step is not another user permission toggle or repeated Google reauthentication based on this evidence.

Read-only `Aether_Dev_VM.start_process` diagnostic commands succeeded in this turn. Therefore the tool is not universally disabled. This does not establish that the previously rejected write/deployment action is now permitted.

A bounded read of `aether-remote-device.service` journal windows 00:10–00:25 UTC and 03:35–03:45 UTC returned zero records. This is **not** proof that the rejected request never reached the server: complete request logging has not been established, so the journal cannot independently locate the rejection.

The active Seoul collector remained `active/running` at 2026-11-08 04:08 UTC, and its retained events show successful SHA-verified cloud publication of Arm A seed 7 epoch 1 and epoch 2. That existing execution was not changed. No new GPU was allocated in this provenance audit, no worker2 deployment was retried, and no IAM, organization-policy, tool-safety or app-permission controls were weakened.

## Distinct kinds of approval

`approval.json` and the ten-review receipt checks in this repository are **experiment-level provenance and launch checks** implemented by our own code. They do not grant ChatGPT app permissions, approve a tool call on OpenAI's behalf, or override a platform safety decision.

Google IAM authorization and zone capacity are separate. The earlier record includes a successful Tokyo Spot allocation followed by the reported tool rejection; consequently that allocation does not identify the safety block's cause.

## Supported escalation

OpenAI's official troubleshooting guidance distinguishes an explicit safety block from missing provider authorization or an approval prompt. It states that app-permission changes, reconnecting an account, or a saved approval do not override safety protections. For a persistent unexpected block, contact OpenAI Support with exact tool/app name, message, time and interface, observed destination effects, and any exposed request ID. Do not send passwords, OAuth verification codes, tokens, or private training text.

Support-ready summary:

> An explicitly authorized JEP machine-learning training deployment through the ChatGPT connected app Aether Dev VM, action Aether_Dev_VM.start_process, was reported blocked with: "This tool call was blocked by OpenAI's safety checks. Please double check what you are sending." The app-specific permission is already Allow all actions. Neighboring read-only tool calls succeed, and another previously launched worker is training. The requested operation prepares task-specific launch records and copies them to an existing authorized GPU VM. The most recent incident was approximately 2026-11-08 03:40–03:43 UTC (November 7, 10:40–10:43 p.m. EST). Request/diagnostic ID: not shown in retained evidence. Original blocked transport payload: not retained. Please investigate which action-safety component rejected this request and identify the supported resolution. No safeguard override is requested.

The affected ChatGPT account/workspace, exact conversation URL and a screenshot of the actual rejected tool card should be supplied through the authenticated Support channel, not invented or copied into this repository. **This document is a prepared support brief, not a submitted support ticket.**

## Official documentation

- Troubleshooting plugins and apps: https://help.openai.com/en/articles/20001497-troubleshooting-plugins-and-apps-in-chatgpt
- Managing app permissions: https://help.openai.com/en/articles/20001495-managing-app-permissions-in-chatgpt
- Contacting Support: https://help.openai.com/en/articles/6614161-how-can-i-contact-support

## Existing project evidence

- `capacity-and-launch-diagnosis-20261108T0342Z.md` in this directory: contemporaneous incident narrative, successful allocation, and cleanup status.
- Training source remains `9b163a100362580f99722eecc63895420ecec3b1`; this documentation commit does not change running code or training configuration.

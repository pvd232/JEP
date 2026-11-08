# Independent proposal review

**Review state: not yet completed.** Three independent reviews were requested by the user. Local Codex on Columbia returned `Not logged in`; the Columbia GitHub CLI is unauthenticated and its existing Mac relay is unavailable. Those are access observations, not review results. Aether and cross-host credential copying are excluded.

A hosted GitHub review request, if supported by the repository's existing Codex connection, is the next permitted route. Three requests must be treated as requests until attributable reviewer outputs exist. Do not infer completion from comment submission, an eyes reaction, or a passing mechanical check.

## Shared review contract

Review only this proposal packet and its pinned implementation sources. This is a specification review, not authorization to change IAM, start/stop a VM, read credentials, modify source, or migrate a live collector. Start each assessment independently; do not adopt another reviewer's conclusions as your own. Inspect the same pinned proposal commit and identify it in the result.

Each result must state: reviewer/task identifier when exposed; exact reviewed commit; inspected files; concrete findings with severity and file/section; counterexample; proposed smallest repair and acceptance test; verdict; and unverified runtime assumptions. A no-finding result must explicitly state its inspected scope. Missing provider task identity must be reported as unavailable, not invented. The author records finding dispositions and obtains re-review of material changes.

## Reviewer 1 — security and IAM

Determine whether the proposal really limits Columbia's authority to the intended Mantra operations. Inspect metadata-identity trust, administrator versus runtime authority, IAP versus SSH, public/private SSH key handling, object-prefix versus bucket-list permissions, credential backup/reconstruction and explicit tool-refusal boundaries. Challenge self-granting permissions, blanket admin roles, copied refresh tokens, application allowlists misrepresented as IAM, and host-wide credential exposure. No cloud mutation is permitted.

## Reviewer 2 — reliability and recovery

Trace host authentication, target authorization, CLI/account precedence, IAP network and guest login, artifact round trips, renewal and rebuild evidence. Examine the existing collector's `finally: stop(...)` behavior and ensure the proposed cutover cannot stop a live trainer or advance a checkpoint twice. Distinguish read-only observations from missing real integration tests. Challenge rollback, stale acknowledgements, revoked access and unavailable metadata/network. No running service may be touched.

## Reviewer 3 — minimality and contract traceability

Check that the plan repairs the two diagnosed gaps with existing owners, not a new credential platform. Trace every requirement to a planned code owner and positive/rejection evidence. Check the clean PR baseline and unmerged installed-code dependency. Reject invented skill use, unimplemented typed-contract claims, duplicate configuration authority, vague acceptance gates, speculative scope expansion and unsupported claims of completion.

## Acceptance and evidence

The proposal is independently reviewed only after all three actual results are retained with matching source identity and blocking findings have dispositions. The author may perform syntax, link, scope or counterexample checks, but these do not count as subagent reviews. Static reviewer approval does not establish cloud access, token refresh, guest login or safe live migration.

Review requests and any provider responses will be linked in the PR conversation. Until those responses exist, this file must remain explicit that the review is pending or blocked. The PR remains draft while the required reviews are incomplete.

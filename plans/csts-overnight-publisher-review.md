# Independent overnight status publisher review

Reviewer: `/root/iped_research`. Date: 2026-10-26.

**Verdict: Approve.** No unresolved blocking finding remains for the bounded read-only monitoring and status-publication contract.

Reviewed file: `scripts/publish_overnight_status.py`.

SHA-256: `6193e94f59958873cd00ddeb21dddd09f8d8fb66b753b0c996c100ce26d946f2`.

## Inspected behavior

The GPU command reads controller JSON and event sidecars under two fixed experiment roots. It launches no inference, training, cancellation, or configuration update. The Mac publisher uses the authenticated `gh` executable, without copying a token into command arguments or status content. Its write endpoint is the single declared GitHub status file on the experiment branch. An existing-file GET supplies the blob SHA used by the subsequent PUT; a concurrent modification causes failure, with a fresh GET on the next loop. Publisher exceptions remain local to the independent polling process.

The renderer publishes aggregate metrics, completion/selection events, progress, and controller paths. The inspected training emitters supply no passage or answer text in these rendered fields. The review covers the actual fixed event producers; it does not claim arbitrary future events are safe for unrestricted publication.

## Findings and repairs

| Finding | Consequence | Verified repair |
|---|---|---|
| Validation and test rendering read `mse`, while the experiment emits `mse_0_1`. | Live MSE values appeared missing. | Both lookups now prefer `mse_0_1`, with a legacy `mse` fallback. |
| State parsing ran outside the loop's exception guard, and state writes directly replaced file contents. | An interrupted state write could prevent publisher restart. | Malformed/unreadable state resets to an empty state. A temporary file is written and atomically renamed. |

## Executed checks

- Python compilation succeeded.
- Synthetic event rendering selected the completed best checkpoint over a later worse epoch, displayed its validation MSE, displayed test Spearman and test MSE, and retained the fixed publication endpoint.
- A mocked GitHub interaction verified the exact branch/path, expected existing blob SHA, exact base64 content, checked subprocess execution and 30-second timeouts, and absence of a token argument.
- A temporary malformed state file recovered, published once, and became valid state through replacement. The temporary file was absent afterward.
- A synthetic SSH/snapshot failure emitted `publisher_error`, preserved the previous state, and performed no publication.

These observer checks launched no network request, native stage, or GPU job. Actual remote connectivity and authenticated GitHub publication remain owner-deployment observations. The publisher's fixed deadline and independent process lifetime bound its overnight work.

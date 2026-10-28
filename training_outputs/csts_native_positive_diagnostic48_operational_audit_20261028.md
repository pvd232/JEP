The original frozen diagnostic retains48 records per model,96 total. Each model has31 actual completed responses,10 unsupported routes and7 zero-call empty-input precondition errors. The errors are harness/input-contract failures, not model abstentions or evidence about native extraction capability. No semantic-quality score is supplied by this audit.

Both archives verify against the declared SHA-256 identities:

- KnowCoder: `f01cc8aba5da050e0902afd2bed9028100dfcf4aa7675b30ad7cdb42df6c7189`.
- GoLLIE: `92efafb0154ec7271325801cceb2113f125c756b6b10a311ab6ae3a85904d7d5`.

All146 execution-index hashes per archive verify. The144 request/capture/raw-handler manifest hashes per model also verify; these repeat indexed artifacts. All447 regular TAR-member byte lengths match. Frozen inference jobs contain only source ID, passage and condition, and each request matches its exact job source/model/protocol.

For every one of the62 actual calls, a CPU replay of the pinned tokenizer reproduces its input IDs from the frozen prompt, checks its token budget, reproduces output decoding from the retained output IDs and verifies the declared native payload envelope. All62 responses end on EOS ID2, none is truncated, and every recorded token length agrees. Bridge records retain the raw handler's output, stage records, normalized claims, call count and failure status.

Each empty-input error has an actual zero-length source passage, zero calls, zero bound requests, zero generated stages and no raw response. Original captures were not rewritten or rerun. Any later authorized first generation for those IDs must remain a separately sealed origin/sensitivity result; it cannot become a retrospective pass in this original96-record denominator.

The machine evidence is `report.json`; the reproducible CPU-only verifier is `/tmp/audit_final_native48_20261028.py`. No model calls, gold changes, semantic accuracy judgments or model rankings were made during this review.

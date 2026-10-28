# Color diagnostic run

The preliminary 13-state diagnostic is complete. Read the [report](report.md) for measured contrasts and intervals.

The probe contains 100 families, 400 captions and 520 caption-condition inputs. One model author proposed the color labels; the planned two-human review remains pending.

The run used the existing JEP L4 VM and the saved checkpoints for seeds 7, 8 and 9. Cached decoding passed comparison with full-sequence decoding. All 12 adapter files passed their saved SHA-256 checks.

The [protocol](diagnostic_protocol.json) records the frozen inputs and preliminary labeling. The [metrics](metrics.json), [family measurements](family_metrics.json) and [decoded answers](parsed_answers.json) support inspection of the report.

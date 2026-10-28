# Color diagnostic run

**Complete:** all 6,760 evaluations across 13 model states, covering seeds 7, 8 and 9. The [report](report.md) gives the measured contrasts and corrected intervals.

The proposition arm had a lower implied-color embedding margin in all three seeds. Exact color readout improved by 20 percentage points, and wrong-object answers fell by 3.89 percentage points. The results support weaker use of implied colors as a candidate explanation for the original C-STS color regression. The shared-correct geometry comparison remains unresolved because each seed fell below its minimum family count.

**Label validation:** one model authored the probe and expected color labels. The run omitted the two-person label check specified in the plan. The exploratory run and analysis are complete; the unvalidated labels limit interpretation, especially for implied colors.

The probe contains 100 families, 400 captions and 520 caption-condition inputs. The run used the existing JEP L4 VM and the saved checkpoints. Cached decoding passed comparison with full-sequence decoding. All 12 adapter files passed their saved SHA-256 checks.

The [protocol](diagnostic_protocol.json) records the frozen inputs and labeling. The [metrics](metrics.json), [family measurements](family_metrics.json) and [decoded answers](parsed_answers.json) support inspection of the report.

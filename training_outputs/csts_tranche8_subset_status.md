# Proposition subset trial

Status: **running**. Uses the 2,880 completed training answers and the 30-pair revised-policy development sample. Full answer generation remains stopped; no held-out test is released.

This is a small development triage experiment. Native metrics and training progress are preserved in [the results JSON](csts_tranche8_subset_results.json).

```json
{
  "phase": "native_status",
  "source_commit": "a75fa36a8d709c25d7efccdd5c9dcdcfab3b3ec1",
  "name": "proposition_subset_v2",
  "status": "running",
  "module": "csts_pilot.proposition_subset",
  "started_unix": 1793047781.5107346,
  "supervisor_sha256": "75205868a63afedecb808276d22525b9dc34d6ca86cd6a4deac66d60b8a129cb",
  "supervisor_pid": 97112,
  "native_pid": 97115,
  "summary": {
    "status": "running",
    "in_flight": {
      "name": "fit",
      "experiment_id": "csts_subset_a75fa36a_c1514635_fit"
    },
    "source_commit": "a75fa36a8d709c25d7efccdd5c9dcdcfab3b3ec1"
  },
  "runs": [
    {
      "name": "prepare",
      "status": "succeeded",
      "seconds": 37.01582214399241
    },
    {
      "name": "epoch_zero",
      "status": "succeeded",
      "seconds": 131.57889592298307
    }
  ],
  "publication_counts": {
    "published": 11
  },
  "free_bytes": 4857212928,
  "training": {
    "status": "running",
    "current_epoch": 6,
    "actual_updates": 60,
    "completed_epoch": 6,
    "selected": {
      "epoch": 3,
      "step": 30,
      "sha256": "1513a9dbdd4c77de1d1e8b4adebc7a111d62837ab56dafa60871ec0ec544dd52",
      "validation": {
        "n": 30,
        "mse_0_1": 0.05148419168540155,
        "mse_1_5": 0.8237470669664247,
        "spearman": 0.5261340606350965,
        "prediction_mean": 0.5122741500536601,
        "target_mean": 0.5,
        "prediction_std": 0.22118903314851354,
        "target_std": 0.22360679774997896,
        "mean_prediction_by_rating": {
          "1.0": {
            "n": 2,
            "mean": 0.39090581238269806
          },
          "2.0": {
            "n": 5,
            "mean": 0.351238888502121
          },
          "3.0": {
            "n": 15,
            "mean": 0.4855423629283905
          },
          "4.0": {
            "n": 7,
            "mean": 0.7026978858879634
          },
          "5.0": {
            "n": 1,
            "mean": 0.6281977891921997
          }
        },
        "condition_changes": {
          "n": 0,
          "correct": 0,
          "ties": 0,
          "accuracy_ties_half": null,
          "difference_mse": null,
          "unit": "Within-pair comparisons. These reuse captions and are dependent."
        }
      }
    },
    "epochs_without_improvement": 3,
    "latest_epoch": {
      "epoch": 6,
      "step": 60,
      "training_mse_0_1": 0.017809945538826193,
      "validation": {
        "n": 30,
        "mse_0_1": 0.053342462252401274,
        "mse_1_5": 0.8534793960384204,
        "spearman": 0.4975580892906982,
        "prediction_mean": 0.5133376051982244,
        "target_mean": 0.5,
        "prediction_std": 0.23094414051427034,
        "target_std": 0.22360679774997896,
        "mean_prediction_by_rating": {
          "1.0": {
            "n": 2,
            "mean": 0.3399876654148102
          },
          "2.0": {
            "n": 5,
            "mean": 0.36310950219631194
          },
          "3.0": {
            "n": 15,
            "mean": 0.48822770416736605
          },
          "4.0": {
            "n": 7,
            "mean": 0.7109491143907819
          },
          "5.0": {
            "n": 1,
            "mean": 0.6045459508895874
          }
        },
        "condition_changes": {
          "n": 0,
          "correct": 0,
          "ties": 0,
          "accuracy_ties_half": null,
          "difference_mse": null,
          "unit": "Within-pair comparisons. These reuse captions and are dependent."
        }
      },
      "fit_seconds": 82.68023605900817,
      "validation_seconds": 1.648221695999382,
      "observed_epoch_seconds": 84.33369029598543
    }
  },
  "result": {},
  "preparation": {
    "coverage": {
      "training": {
        "comparisons": 312,
        "accepted_side_occurrences": 542,
        "fallback_side_occurrences": 82,
        "comparison_coverage": {
          "both": 243,
          "one": 56,
          "neither": 13
        },
        "accepted_count_per_row": [
          1,
          2,
          2,
          1,
          1,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          1,
          1,
          1,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          1,
          1,
          1,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          1,
          1,
          1,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          1,
          0,
          1,
          2,
          1,
          1,
          2,
          0,
          2,
          2,
          1,
          2,
          2,
          0,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          0,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          1,
          0,
          2,
          1,
          1,
          2,
          2,
          1,
          2,
          2,
          1,
          2,
          2,
          1,
          2,
          0,
          2,
          2,
          2,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          0,
          2,
          2,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          1,
          2,
          1,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          0,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          0,
          2,
          2,
          2,
          0,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          1,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          0,
          1,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          0,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          0,
          2,
          2
        ]
      },
      "validation": {
        "comparisons": 30,
        "accepted_side_occurrences": 52,
        "fallback_side_occurrences": 8,
        "comparison_coverage": {
          "both": 22,
          "one": 8,
          "neither": 0
        },
        "accepted_count_per_row": [
          1,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          1,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2,
          2,
          1,
          1,
          2,
          2,
          1,
          2,
          2,
          2,
          2,
          2,
          2
        ]
      }
    },
    "source_groups": {
      "training": 291,
      "validation": 30
    },
    "training_available_records": 2880,
    "selected_records": 674,
    "training_selection": "Original comparisons whose two canonical passage-condition identities are in completed capture batches; labels and predictions do not select rows.",
    "validation_selection": "The 30 disjoint source pairs selected before the frozen v2 fidelity audit; no judgment-based answer filtering.",
    "limitations": "This model-assisted audit sample was used during development and is reused for epoch selection. It is a small development triage, not independent confirmation or test eligibility.",
    "test_inputs_opened": false
  },
  "epoch_zero_metrics": {
    "saved_qwen": {
      "n": 30,
      "mse_0_1": 0.04185093042714131,
      "mse_1_5": 0.669614886834261,
      "spearman": 0.5758418427215707,
      "prediction_mean": 0.5015633329749107,
      "target_mean": 0.5,
      "prediction_std": 0.20274980324297884,
      "target_std": 0.22360679774997896,
      "mean_prediction_by_rating": {
        "1.0": {
          "n": 2,
          "mean": 0.3346192240715027
        },
        "2.0": {
          "n": 5,
          "mean": 0.31868474185466766
        },
        "3.0": {
          "n": 15,
          "mean": 0.49986075758934023
        },
        "4.0": {
          "n": 7,
          "mean": 0.6693160789353507
        },
        "5.0": {
          "n": 1,
          "mean": 0.6011139154434204
        }
      },
      "condition_changes": {
        "n": 0,
        "correct": 0,
        "ties": 0,
        "accuracy_ties_half": null,
        "difference_mse": null,
        "unit": "Within-pair comparisons. These reuse captions and are dependent."
      },
      "operating_point": {
        "cutoff": 0.3142477869987488,
        "tp": 8,
        "fn": 0,
        "fp": 3,
        "tn": 4,
        "recall": 1.0,
        "false_negative_rate": 0.0,
        "false_positive_rate": 0.42857142857142855,
        "excluded_middle_rating": 15
      },
      "descriptive_cutoffs": {
        "0.5": {
          "cutoff": 0.5,
          "tp": 6,
          "fn": 2,
          "fp": 1,
          "tn": 6,
          "recall": 0.75,
          "false_negative_rate": 0.25,
          "false_positive_rate": 0.14285714285714285,
          "excluded_middle_rating": 15
        },
        "0.75": {
          "cutoff": 0.75,
          "tp": 3,
          "fn": 5,
          "fp": 0,
          "tn": 7,
          "recall": 0.375,
          "false_negative_rate": 0.625,
          "false_positive_rate": 0.0,
          "excluded_middle_rating": 15
        }
      },
      "errors_by_rating": {
        "1.0": {
          "n": 2,
          "signed_error": 0.3346192240715027,
          "mse": 0.13211550753528645
        },
        "2.0": {
          "n": 5,
          "signed_error": 0.06868474185466766,
          "mse": 0.02653502766189626
        },
        "3.0": {
          "n": 15,
          "signed_error": -0.00013924241065979003,
          "mse": 0.026016990790704318
        },
        "4.0": {
          "n": 7,
          "signed_error": -0.0806839210646493,
          "mse": 0.04417954130296309
        },
        "5.0": {
          "n": 1,
          "signed_error": -0.3988860845565796,
          "mse": 0.15911010845287876
        }
      }
    },
    "propositions": {
      "n": 30,
      "mse_0_1": 0.05753978267137554,
      "mse_1_5": 0.9206365227420087,
      "spearman": 0.486511915493704,
      "prediction_mean": 0.5133678225179513,
      "target_mean": 0.5,
      "prediction_std": 0.22962168324313648,
      "target_std": 0.22360679774997896,
      "mean_prediction_by_rating": {
        "1.0": {
          "n": 2,
          "mean": 0.4151739180088043
        },
        "2.0": {
          "n": 5,
          "mean": 0.34012899547815323
        },
        "3.0": {
          "n": 15,
          "mean": 0.49294862846533455
        },
        "4.0": {
          "n": 7,
          "mean": 0.6954831736428397
        },
        "5.0": {
          "n": 1,
          "mean": 0.6074302196502686
        }
      },
      "condition_changes": {
        "n": 0,
        "correct": 0,
        "ties": 0,
        "accuracy_ties_half": null,
        "difference_mse": null,
        "unit": "Within-pair comparisons. These reuse captions and are dependent."
      },
      "operating_point": {
        "cutoff": 0.2539628744125366,
        "tp": 8,
        "fn": 0,
        "fp": 5,
        "tn": 2,
        "recall": 1.0,
        "false_negative_rate": 0.0,
        "false_positive_rate": 0.7142857142857143,
        "excluded_middle_rating": 15
      },
      "descriptive_cutoffs": {
        "0.5": {
          "cutoff": 0.5,
          "tp": 6,
          "fn": 2,
          "fp": 2,
          "tn": 5,
          "recall": 0.75,
          "false_negative_rate": 0.25,
          "false_positive_rate": 0.2857142857142857,
          "excluded_middle_rating": 15
        },
        "0.75": {
          "cutoff": 0.75,
          "tp": 4,
          "fn": 4,
          "fp": 0,
          "tn": 7,
          "recall": 0.5,
          "false_negative_rate": 0.5,
          "false_positive_rate": 0.0,
          "excluded_middle_rating": 15
        }
      },
      "errors_by_rating": {
        "1.0": {
          "n": 2,
          "signed_error": 0.4151739180088043,
          "mse": 0.20780440595908978
        },
        "2.0": {
          "n": 5,
          "signed_error": 0.09012899547815323,
          "mse": 0.035887134974277854
        },
        "3.0": {
          "n": 15,
          "signed_error": -0.0070513715346654255,
          "mse": 0.03888107849180999
        },
        "4.0": {
          "n": 7,
          "signed_error": -0.0545168263571603,
          "mse": 0.056260254790101626
        },
        "5.0": {
          "n": 1,
          "signed_error": -0.39256978034973145,
          "mse": 0.1541110324438364
        }
      }
    }
  }
}
```

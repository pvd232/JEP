"""Publish C-STS progress and verified results, then stop the authorized VM.

Run with ``python -m csts_pilot.finish_study --root WORKSPACE --shutdown``.
snapshot reads the external observer. aggregate computes seed means and paired
source-group intervals. publish commits generated reports. main waits for the
study and verified storage cleanup, publishes through VIPER, then stops the VM.
"""

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ARMS = ("ratings", "answers", "sequential", "joint", "shuffled")
SEEDS = (7, 8, 9)
BRANCH = "experiment/csts-joint-20261021"
OBSERVER = Path("/home/machina/jep-csts-observer-20261021/progress.py")
STORAGE = Path("/mnt/rico-source-data/jep-storage-cleanup-20261021.state.json")


def read_json(path: Path):
    """Read one complete JSON record."""
    return json.loads(path.read_text())


def alive(pid: int) -> bool:
    """Treat exited and zombie controllers as finished."""
    try:
        return Path(f"/proc/{pid}/stat").read_text().split(") ", 1)[1][0] != "Z"
    except FileNotFoundError:
        return False


def ready(summary: dict, storage: dict) -> bool:
    """Require every arm and seed plus verified storage completion."""
    expected = {(arm, seed) for arm in ARMS for seed in SEEDS}
    actual = [(row["arm"], row["seed"]) for row in summary.get("evaluation", [])]
    if summary.get("status") != "complete":
        return False
    if len(actual) != len(expected) or set(actual) != expected:
        raise ValueError("The complete study lacks one evaluation per arm and seed.")
    for row in summary["evaluation"]:
        scores = row["diagnostics"]
        if scores["n"] != 2620 or not all(
            math.isfinite(scores[k]) for k in ("mse_0_1", "spearman")
        ):
            raise ValueError("Evaluation scores are missing or invalid.")
    return (
        storage.get("status") == "complete"
        and storage.get("files") == 362
        and bool(storage.get("cloud_completion"))
    )


def snapshot(root: Path) -> dict:
    """Use the existing observer to read stage metrics, answers and GPU use."""
    raw = subprocess.check_output(
        [sys.executable, str(OBSERVER), "--root", str(root), "--json"],
        text=True,
        timeout=30,
    )
    return json.loads(raw)


def aggregate(summary: dict) -> dict:
    """Report each seed and paired MSE intervals over connected caption groups."""
    output = {
        "source_commit": summary["source_commit"],
        "data_manifest": summary["data_manifest"],
        "annotation": summary.get("annotation"),
        "selected": summary["selected"],
        "evaluation": summary["evaluation"],
        "runs": summary["runs"],
        "means": {},
    }
    errors, identities, group_ids = {}, None, None
    for arm in ARMS:
        runs = sorted(
            (r for r in summary["evaluation"] if r["arm"] == arm),
            key=lambda r: r["seed"],
        )
        output["means"][arm] = {
            key: float(np.mean([r["diagnostics"][key] for r in runs]))
            for key in ("mse_0_1", "spearman")
        }
        output["means"][arm]["condition_ordering"] = float(
            np.mean(
                [
                    r["diagnostics"]["condition_changes"]["accuracy_ties_half"]
                    for r in runs
                ]
            )
        )
        per_seed = []
        for run in runs:
            predictions = read_json(
                Path(run["path"]).parent / "artifacts/eval/predictions/predictions.json"
            )
            keys = [
                (
                    r["sentence1"],
                    r["sentence2"],
                    r["condition"],
                    r["target"],
                    r["group_id"],
                )
                for r in predictions
            ]
            if identities is None:
                identities = keys
                group_ids = [r["group_id"] for r in predictions]
            if keys != identities:
                raise ValueError(
                    "Evaluation inputs or their order differ between arms."
                )
            per_seed.append(
                np.array([(r["prediction"] - r["target"]) ** 2 for r in predictions])
            )
        errors[arm] = np.mean(per_seed, axis=0)
    _, groups = np.unique(group_ids, return_inverse=True)
    count = np.bincount(groups)
    rng = np.random.default_rng(20261021)
    weights = rng.multinomial(
        len(count), np.full(len(count), 1 / len(count)), size=2000
    )
    output["paired_mse_intervals"] = {}
    for arm in ARMS[1:]:
        difference = errors[arm] - errors["ratings"]
        sums = np.bincount(groups, weights=difference)
        bootstrap = (weights @ sums) / (weights @ count)
        output["paired_mse_intervals"][arm + "_minus_ratings"] = {
            "difference": float(difference.mean()),
            "lower_95": float(np.quantile(bootstrap, 0.025)),
            "upper_95": float(np.quantile(bootstrap, 0.975)),
            "source_groups": len(count),
            "replicates": 2000,
        }
    output["interval_method"] = (
        "Paired resampling of connected caption groups; squared errors average matched seeds within each comparison. Negative differences favor the named arm."
    )
    output["label_provenance"] = (
        "C-STS release mixes original human ratings and LLM reannotations. Answer labels are Qwen3-8B extractions accepted by its second prompt."
    )
    output["scope"] = (
        "Filtered C-STS captions, one FLAN-T5-small backbone, three seeds. Answer-only projection stays at its matched initialization. Sequential training receives an extra training stage."
    )
    return output


def curves(summary: dict, output: Path) -> bool:
    """Plot completed native training traces without reading reserved inputs."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    plotted = False
    for run in summary.get("runs", []):
        trace_path = Path(run["path"]).parent / "artifacts/train/trace/trace.json"
        if not trace_path.exists():
            continue
        trace = read_json(trace_path)
        history = trace["epochs"]
        x = [row["epoch"] for row in history]
        axes[0].plot(
            x,
            [row["development"]["mse_0_1"] for row in history],
            label=run["name"],
            alpha=0.75,
        )
        axes[1].plot(
            x,
            [row["development_answer_ce"] for row in history],
            label=run["name"],
            alpha=0.75,
        )
        plotted = True
    for axis, title in zip(
        axes,
        ("Development similarity MSE", "Development answer cross-entropy"),
        strict=True,
    ):
        axis.set(xlabel="Epoch within stage", title=title)
        axis.grid(alpha=0.2)
    if plotted:
        axes[1].legend(fontsize=6, loc="upper left", bbox_to_anchor=(1.02, 1))
        fig.tight_layout()
        fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return plotted


def publish(
    root: Path, summary: dict, observed: dict, final: dict | None = None
) -> str:
    """Commit generated status and curves in a separate publication checkout."""
    checkout = Path("/mnt/rico-source-data/jep-csts-publication-20261021")

    def git(*args):
        return subprocess.check_output(
            ["git", "-C", str(checkout), *args], text=True
        ).strip()

    subprocess.run(["git", "-C", str(root), "fetch", "origin", BRANCH], check=True)
    if not checkout.exists():
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "worktree",
                "add",
                "--detach",
                str(checkout),
                "origin/" + BRANCH,
            ],
            check=True,
        )
    else:
        git("merge", "--ff-only", "origin/" + BRANCH)
    out = checkout / "training_outputs"
    out.mkdir(exist_ok=True)
    (out / "csts_live_status.json").write_text(json.dumps(observed, indent=2) + "\n")
    (out / "csts_joint_study_status.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    names = [
        "training_outputs/csts_live_status.json",
        "training_outputs/csts_joint_study_status.json",
        "CSTS_PROGRESS.md",
    ]
    if curves(summary, out / "csts_joint_learning_curves.png"):
        names.append("training_outputs/csts_joint_learning_curves.png")
    if final is not None:
        (out / "csts_joint_results.json").write_text(json.dumps(final, indent=2) + "\n")
        names.append("training_outputs/csts_joint_results.json")
    progress = checkout / "CSTS_PROGRESS.md"
    text = progress.read_text()
    start = text.find("\nThe [answer and joint study]")
    if start < 0:
        start = text.find("\n## Answer and joint study")
    end = text.find("\nThe VIPER precision repair", start)
    if start < 0 or end < 0:
        raise ValueError(
            "Progress report markers differ from the publication template."
        )
    lines = [
        "",
        "## Answer and joint study",
        "",
        "Observed at " + observed["observed_at_utc"] + ".",
        "",
    ]
    for trial in observed.get("trials", []):
        if trial.get("annotation"):
            counts = trial["annotation"]
            lines.append(
                f"Annotation: {counts.get('completed')} records completed; {counts.get('accepted')} accepted. Total planned: 17,334."
            )
    lines += [
        "",
        "Study status: " + summary.get("status", "starting") + ".",
        "[Live counts and epoch metrics](training_outputs/csts_live_status.json).",
        "[Completed trial records](training_outputs/csts_joint_study_status.json).",
        "",
    ]
    if final is not None:
        lines += [
            "| Training | MSE | Spearman | Condition ordering |",
            "| --- | ---: | ---: | ---: |",
        ]
        for arm in ARMS:
            m = final["means"][arm]
            lines.append(
                f"| {arm} | {m['mse_0_1']:.4f} | {m['spearman']:.3f} | {m['condition_ordering']:.1%} |"
            )
        lines += [
            "",
            "Scores average seeds 7, 8 and 9 on 2,620 reserved comparisons.",
            "[Results, source-group intervals and label provenance](training_outputs/csts_joint_results.json).",
            "",
        ]
    if "training_outputs/csts_joint_learning_curves.png" in names:
        lines += [
            "![Joint study learning curves](training_outputs/csts_joint_learning_curves.png)",
            "",
        ]
    progress.write_text(text[:start] + "\n".join(lines) + text[end:])
    git("add", "--", *names)
    if (
        subprocess.run(
            ["git", "-C", str(checkout), "diff", "--cached", "--quiet"], check=False
        ).returncode
        == 0
    ):
        return git("rev-parse", "HEAD")
    git(
        "commit",
        "-m",
        "Publish completed C-STS study"
        if final is not None
        else "Stream C-STS annotation and training progress",
    )
    git("push", "origin", "HEAD:refs/heads/" + BRANCH)
    return git("rev-parse", "HEAD")


def main() -> None:
    """Wait for verified outputs and cleanup, publish them, and honor shutdown."""
    import fcntl

    from viper.cloud import GcsRepository, ViperCloud, ViperCloudDestination

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--shutdown", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    with (root / "csts_results/finish.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        published = 0.0
        while True:
            try:
                observed = snapshot(root)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                print(json.dumps({"observer_error": str(error)}), flush=True)
                time.sleep(30)
                continue
            summary_path = root / "csts_results/summary.json"
            summary = (
                read_json(summary_path)
                if summary_path.exists()
                else {"status": "starting", "runs": []}
            )
            storage = read_json(STORAGE) if STORAGE.exists() else {}
            stream_path = root / "csts_results/live_status.json"
            stream_path.write_text(json.dumps(observed, indent=2) + "\n")
            print(
                json.dumps(
                    {
                        "observed_at": observed["observed_at_utc"],
                        "status": summary["status"],
                        "trials": [
                            {
                                "name": t["name"],
                                "annotation": t.get("annotation"),
                                "epochs": t.get("epochs"),
                            }
                            for t in observed.get("trials", [])
                        ],
                    }
                ),
                flush=True,
            )
            controller = read_json(root / "csts_results/launcher.json")["pid"]
            if not alive(controller) and summary.get("status") != "complete":
                raise RuntimeError(
                    "Study controller stopped before completing evaluation; inspect launcher.log."
                )
            if time.monotonic() - published >= 300:
                publish(root, summary, observed)
                published = time.monotonic()
            if (
                ready(summary, storage)
                and not alive(controller)
                and not alive(storage["pid"])
            ):
                final = aggregate(summary)
                final["storage_cleanup"] = storage
                commit = publish(root, summary, observed, final)
                checkout = Path("/mnt/rico-source-data/jep-csts-publication-20261021")
                cloud = ViperCloud(
                    Path("/"),
                    GcsRepository(
                        bucket="mantra-mlfg-prod-uscentral1-8e7a", prefix="viper"
                    ),
                )
                destination = ViperCloudDestination(
                    owner="pvd232", workspace="jep_csts_joint_20261021"
                )
                selected = {
                    "reports/" + name.name: name
                    for name in (checkout / "training_outputs").glob("csts_joint*")
                    if name.is_file()
                }
                refs = cloud.resolved_files(destination, selected)
                state = {
                    "status": "complete",
                    "publication_commit": commit,
                    "cloud_reports": {
                        key: ref.model_dump(mode="json") for key, ref in refs.items()
                    },
                    "shutdown_requested": args.shutdown,
                    "completed_at_utc": time.strftime(
                        "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                    ),
                }
                (root / "csts_results/completion.json").write_text(
                    json.dumps(state, indent=2) + "\n"
                )
                cloud.resolved_files(
                    destination,
                    {
                        "reports/completion.json": (
                            json.dumps(state, indent=2) + "\n"
                        ).encode()
                    },
                )
                print(json.dumps(state), flush=True)
                if args.shutdown:
                    gpu_pids = subprocess.check_output(
                        [
                            "nvidia-smi",
                            "--query-compute-apps=pid",
                            "--format=csv,noheader",
                        ],
                        text=True,
                    ).strip()
                    if gpu_pids:
                        raise RuntimeError(
                            "A GPU process remains active; shutdown requires review."
                        )
                    subprocess.run(["sudo", "-n", "shutdown", "-h", "+1"], check=True)
                return
            time.sleep(30)


if __name__ == "__main__":
    main()

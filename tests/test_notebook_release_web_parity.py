import json

from scripts.validate_notebook_release_parity import validate_parity


def test_parity_validator_matches_notebook_release_and_web(tmp_path):
    snapshot = {
        "analysis_policy_id": "policy",
        "frozen_test": [
            {
                "track": "PRE_LAB",
                "model": "extra_trees",
                "macro_f1": 0.476,
                "macro_pr_auc": 0.539,
                "macro_recall": 0.506,
                "micro_f1": 0.756,
            }
        ],
        "per_label": [],
    }
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [],
                "outputs": [
                    {
                        "output_type": "stream",
                        "name": "stdout",
                        "text": [
                            "VECTRA_X_EVIDENCE_SNAPSHOT="
                            + json.dumps(snapshot)
                            + "\n"
                        ],
                    }
                ],
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    notebook_path = tmp_path / "submission.ipynb"
    notebook_path.write_text(json.dumps(notebook), encoding="utf-8")
    release_path = tmp_path / "release.json"
    release_path.write_text(
        json.dumps(
                {
                    "run_id": "run",
                    "analysis_policy_id": "policy",
                "notebook_sha256": "ignored-in-unit-test",
                "evidence": {
                    "frozen_test": snapshot["frozen_test"],
                    "per_label": [],
                },
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "analysis_policy_id": "policy",
                "notebook_run_id": "run",
            }
        ),
        encoding="utf-8",
    )
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(
        json.dumps(
            {
                "run_id": "run",
                "validation_and_frozen_test": {
                    "frozen_test": snapshot["frozen_test"],
                    "per_label": [],
                },
            }
        ),
        encoding="utf-8",
    )

    report = validate_parity(
        notebook_path,
        release_path,
        manifest_path,
        evidence_path,
        verify_notebook_hash=False,
    )
    assert report["errors"] == []
    assert "aggregate metrics agree" in report["passed_checks"]

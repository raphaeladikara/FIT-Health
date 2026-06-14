# Modeling Summary

*Leaderboard & pre-lab vs lab-aware*

_Generated: 2026-06-14 20:04 — VECTRA-X pipeline_

Best model per track (by OOF macro-PR-AUC): **{'PRE_LAB': 'extra_trees', 'LAB_AWARE': 'hist_gb', 'FULL': 'hist_gb'}**.


## Leaderboard (5-fold OOF on train)

| model_track | macro_f1 | micro_f1 | macro_pr_auc | macro_roc_auc | hamming_loss | subset_accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| FULL:classifier_chain | 0.6861 | 0.9222 | 0.7422 | 0.8716 | 0.0480 | 0.7964 |
| FULL:hist_gb | 0.7022 | 0.9240 | 0.7382 | 0.8702 | 0.0471 | 0.8009 |
| FULL:lightgbm | 0.6890 | 0.9004 | 0.7363 | 0.8609 | 0.0624 | 0.7511 |
| FULL:xgboost | 0.6414 | 0.9215 | 0.7296 | 0.8631 | 0.0480 | 0.7919 |
| FULL:random_forest | 0.6160 | 0.8981 | 0.7118 | 0.8502 | 0.0624 | 0.7557 |
| FULL:extra_trees | 0.6317 | 0.8970 | 0.6985 | 0.8484 | 0.0643 | 0.7557 |
| FULL:logreg | 0.6374 | 0.8218 | 0.6409 | 0.8307 | 0.1186 | 0.5385 |
| LAB_AWARE:hist_gb | 0.4662 | 0.7781 | 0.5350 | 0.7712 | 0.1321 | 0.5023 |
| LAB_AWARE:extra_trees | 0.5034 | 0.7994 | 0.5275 | 0.7572 | 0.1267 | 0.5475 |
| LAB_AWARE:classifier_chain | 0.4662 | 0.7820 | 0.5241 | 0.7721 | 0.1312 | 0.5113 |
| LAB_AWARE:random_forest | 0.4645 | 0.7915 | 0.5230 | 0.7589 | 0.1249 | 0.5294 |
| LAB_AWARE:lightgbm | 0.4860 | 0.7679 | 0.5181 | 0.7595 | 0.1466 | 0.4615 |
| LAB_AWARE:xgboost | 0.4484 | 0.7914 | 0.5069 | 0.7753 | 0.1231 | 0.5204 |
| LAB_AWARE:logreg | 0.4814 | 0.7071 | 0.4640 | 0.7306 | 0.2009 | 0.3529 |
| PRE_LAB:extra_trees | 0.5532 | 0.7854 | 0.5040 | 0.7087 | 0.1385 | 0.5068 |
| PRE_LAB:random_forest | 0.4402 | 0.7809 | 0.4861 | 0.7136 | 0.1330 | 0.5158 |
| PRE_LAB:classifier_chain | 0.4052 | 0.7575 | 0.4724 | 0.6984 | 0.1466 | 0.4842 |
| PRE_LAB:xgboost | 0.3742 | 0.7504 | 0.4702 | 0.6932 | 0.1475 | 0.4751 |
| PRE_LAB:lightgbm | 0.4505 | 0.7373 | 0.4668 | 0.6807 | 0.1683 | 0.4299 |
| PRE_LAB:hist_gb | 0.4020 | 0.7500 | 0.4647 | 0.6926 | 0.1502 | 0.4615 |
| PRE_LAB:logreg | 0.4725 | 0.6712 | 0.4430 | 0.6740 | 0.2208 | 0.3756 |


## Held-out TEST metrics by track

| track | macro_f1 | micro_f1 | macro_pr_auc | macro_recall | hamming_loss | subset_accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| PRE_LAB | 0.4823 | 0.7673 | 0.5247 | 0.5011 | 0.1462 | 0.4487 |
| LAB_AWARE | 0.4439 | 0.7321 | 0.5024 | 0.5217 | 0.1821 | 0.3462 |
| FULL | 0.6436 | 0.8917 | 0.6728 | 0.6286 | 0.0667 | 0.7308 |

**Pre-lab vs lab-aware vs full**: LAB_AWARE does not improve both frozen-test macro-F1 and macro-PR-AUC. This is retained as a negative result; adding laboratory variables is not claimed to improve aggregate performance. FULL remains a research-only leakage demonstration and is never deployable.


## Per-label metrics (held-out test)

| track | label | support_pos | precision | recall | f1 | roc_auc | pr_auc | tp | fp | fn | tn | false_negative_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRE_LAB | malaria | 68 | 0.8718 | 1.0000 | 0.9315 | 0.6779 | 0.9423 | 68 | 10 | 0 | 0 | 0.0000 |
| PRE_LAB | other_diseases | 25 | 0.6207 | 0.7200 | 0.6667 | 0.8536 | 0.7047 | 18 | 11 | 7 | 42 | 0.2800 |
| PRE_LAB | dengue | 14 | 0.4167 | 0.3571 | 0.3846 | 0.7980 | 0.5068 | 5 | 7 | 9 | 57 | 0.6429 |
| PRE_LAB | typhoid | 7 | 0.4286 | 0.4286 | 0.4286 | 0.7525 | 0.3683 | 3 | 4 | 4 | 67 | 0.5714 |
| PRE_LAB | yellow_fever | 3 | 0.0000 | 0.0000 | 0.0000 | 0.7511 | 0.1011 | 0 | 2 | 3 | 73 | 1.0000 |
| LAB_AWARE | malaria | 68 | 0.8718 | 1.0000 | 0.9315 | 0.9706 | 0.9952 | 68 | 10 | 0 | 0 | 0.0000 |
| LAB_AWARE | other_diseases | 25 | 0.6538 | 0.6800 | 0.6667 | 0.7819 | 0.7067 | 17 | 9 | 8 | 44 | 0.3200 |
| LAB_AWARE | dengue | 14 | 0.3438 | 0.7857 | 0.4783 | 0.7690 | 0.5375 | 11 | 21 | 3 | 43 | 0.2143 |
| LAB_AWARE | typhoid | 7 | 0.1429 | 0.1429 | 0.1429 | 0.6901 | 0.1861 | 1 | 6 | 6 | 65 | 0.8571 |
| LAB_AWARE | yellow_fever | 3 | 0.0000 | 0.0000 | 0.0000 | 0.7244 | 0.0867 | 0 | 5 | 3 | 70 | 1.0000 |
| FULL | malaria | 68 | 0.8718 | 1.0000 | 0.9315 | 0.9750 | 0.9960 | 68 | 10 | 0 | 0 | 0.0000 |
| FULL | other_diseases | 25 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 25 | 0 | 0 | 53 | 0.0000 |
| FULL | dengue | 14 | 1.0000 | 0.8571 | 0.9231 | 0.9989 | 0.9952 | 12 | 0 | 2 | 64 | 0.1429 |
| FULL | typhoid | 7 | 0.5000 | 0.2857 | 0.3636 | 0.7606 | 0.2980 | 2 | 2 | 5 | 69 | 0.7143 |
| FULL | yellow_fever | 3 | 0.0000 | 0.0000 | 0.0000 | 0.6800 | 0.0749 | 0 | 4 | 3 | 71 | 1.0000 |


## Co-infection detector (Track 4, cohort OOF)

| model | roc_auc | pr_auc |
| --- | --- | --- |
| extra_trees | 0.7833 | 0.7780 |
| random_forest | 0.7801 | 0.7655 |
| logreg | 0.7696 | 0.8059 |
| xgboost | 0.7495 | 0.7602 |
| hist_gb | 0.7377 | 0.7509 |
| lightgbm | 0.7372 | 0.7561 |


![Leaderboard](../figures/model_leaderboard.png)

*Leaderboard*


![Per-label F1](../figures/per_label_f1.png)

*Per-label F1*


![Recall](../figures/per_label_recall.png)

*Recall*


![Confusion](../figures/confusion_matrices.png)

*Confusion*


![ROC](../figures/roc_curves.png)

*ROC*


![PR](../figures/pr_curves.png)

*PR*

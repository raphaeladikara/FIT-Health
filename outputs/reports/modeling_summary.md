# Modeling Summary

*Leaderboard & pre-lab vs lab-aware*

_Generated: 2026-06-13 13:56 — VECTRA-X pipeline_

Best model per track (by OOF macro-PR-AUC): **{'PRE_LAB': 'extra_trees', 'LAB_AWARE': 'hist_gb', 'FULL': 'hist_gb'}**.


## Leaderboard (5-fold OOF on train)

| model_track | macro_f1 | micro_f1 | macro_pr_auc | macro_roc_auc | hamming_loss | subset_accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| FULL:classifier_chain | 0.6844 | 0.9283 | 0.7153 | 0.8897 | 0.0439 | 0.8027 |
| FULL:hist_gb | 0.6755 | 0.9267 | 0.7093 | 0.8864 | 0.0448 | 0.7982 |
| FULL:extra_trees | 0.6300 | 0.8784 | 0.6960 | 0.8795 | 0.0762 | 0.7040 |
| FULL:logreg | 0.6560 | 0.8489 | 0.6491 | 0.8514 | 0.0987 | 0.6054 |
| LAB_AWARE:classifier_chain | 0.5309 | 0.8589 | 0.5791 | 0.8329 | 0.0843 | 0.6682 |
| LAB_AWARE:hist_gb | 0.5128 | 0.8559 | 0.5748 | 0.8229 | 0.0861 | 0.6592 |
| LAB_AWARE:extra_trees | 0.5552 | 0.8312 | 0.5662 | 0.8311 | 0.1085 | 0.5964 |
| LAB_AWARE:logreg | 0.5514 | 0.7772 | 0.5463 | 0.8044 | 0.1507 | 0.4753 |
| PRE_LAB:extra_trees | 0.5604 | 0.8258 | 0.5580 | 0.7826 | 0.1139 | 0.5785 |
| PRE_LAB:classifier_chain | 0.4934 | 0.8331 | 0.5371 | 0.7474 | 0.1013 | 0.6099 |
| PRE_LAB:hist_gb | 0.4754 | 0.8368 | 0.5301 | 0.7392 | 0.0987 | 0.6009 |
| PRE_LAB:logreg | 0.5233 | 0.7313 | 0.5221 | 0.7259 | 0.1839 | 0.4126 |


## Held-out TEST metrics by track

| track | macro_f1 | micro_f1 | macro_pr_auc | macro_recall | hamming_loss | subset_accuracy |
| --- | --- | --- | --- | --- | --- | --- |
| PRE_LAB | 0.6095 | 0.8240 | 0.6059 | 0.6968 | 0.1143 | 0.6364 |
| LAB_AWARE | 0.5911 | 0.8259 | 0.5549 | 0.6557 | 0.1117 | 0.5844 |
| FULL | 0.7080 | 0.9021 | 0.6829 | 0.7128 | 0.0597 | 0.7532 |

**Pre-lab vs lab-aware vs full**: lab-aware/full score higher because they include diagnostic-test signal; the pre-lab model is the realistic deployable triage model.


## Per-label metrics (held-out test)

| track | label | support_pos | precision | recall | f1 | roc_auc | pr_auc | tp | fp | fn | tn | false_negative_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRE_LAB | malaria | 67 | 0.8701 | 1.0000 | 0.9306 | 0.6612 | 0.9377 | 67 | 10 | 0 | 0 | 0.0000 |
| PRE_LAB | other_diseases | 25 | 0.9600 | 0.9600 | 0.9600 | 0.9938 | 0.9903 | 24 | 1 | 1 | 51 | 0.0400 |
| PRE_LAB | dengue | 14 | 0.4706 | 0.5714 | 0.5161 | 0.7993 | 0.4547 | 8 | 9 | 6 | 54 | 0.4286 |
| PRE_LAB | typhoid | 7 | 0.3333 | 0.2857 | 0.3077 | 0.5939 | 0.3067 | 2 | 4 | 5 | 66 | 0.7143 |
| PRE_LAB | yellow_fever | 3 | 0.2222 | 0.6667 | 0.3333 | 0.8829 | 0.3400 | 2 | 7 | 1 | 67 | 0.3333 |
| LAB_AWARE | malaria | 67 | 0.9565 | 0.9851 | 0.9706 | 0.9642 | 0.9944 | 66 | 3 | 1 | 7 | 0.0149 |
| LAB_AWARE | other_diseases | 25 | 1.0000 | 0.9600 | 0.9796 | 0.9838 | 0.9817 | 24 | 0 | 1 | 52 | 0.0400 |
| LAB_AWARE | dengue | 14 | 0.4000 | 0.5714 | 0.4706 | 0.7778 | 0.5162 | 8 | 12 | 6 | 51 | 0.4286 |
| LAB_AWARE | typhoid | 7 | 0.3000 | 0.4286 | 0.3529 | 0.6469 | 0.2036 | 3 | 7 | 4 | 63 | 0.5714 |
| LAB_AWARE | yellow_fever | 3 | 0.1250 | 0.3333 | 0.1818 | 0.5811 | 0.0786 | 1 | 7 | 2 | 67 | 0.6667 |
| FULL | malaria | 67 | 0.9565 | 0.9851 | 0.9706 | 0.9657 | 0.9946 | 66 | 3 | 1 | 7 | 0.0149 |
| FULL | other_diseases | 25 | 1.0000 | 0.9600 | 0.9796 | 0.9838 | 0.9817 | 24 | 0 | 1 | 52 | 0.0400 |
| FULL | dengue | 14 | 1.0000 | 0.8571 | 0.9231 | 0.9977 | 0.9911 | 12 | 0 | 2 | 63 | 0.1429 |
| FULL | typhoid | 7 | 0.6000 | 0.4286 | 0.5000 | 0.6286 | 0.3652 | 3 | 2 | 4 | 68 | 0.5714 |
| FULL | yellow_fever | 3 | 0.1111 | 0.3333 | 0.1667 | 0.5631 | 0.0821 | 1 | 8 | 2 | 66 | 0.6667 |


## Co-infection detector (Track 4, cohort OOF)

| model | roc_auc | pr_auc |
| --- | --- | --- |
| logreg | 0.8654 | 0.8779 |
| extra_trees | 0.8596 | 0.8668 |
| hist_gb | 0.8470 | 0.8686 |


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

# Explainability Summary

*Permutation importance + linear local*

_Generated: 2026-06-14 20:04 — VECTRA-X pipeline_

Features are anonymised/encoded clinical **signals** — explanations describe model behaviour, not medical causation.


## Global importance (top 15)

| feature | importance_mean |
| --- | --- |
| Pâleur cutanéo muqueuse ou Anémie (Mucosal skin pallor or Anemia) | 0.0256 |
| Diabète | 0.0145 |
| Détresse respiratoire (Respiratory distress) | 0.0130 |
| Douleur abdominale (stomac pain) | 0.0125 |
| Poids (Weight)__missing | 0.0123 |
| Fréquence respiratoire (médiane IQR) / Respiratory rate (median breaths/min IQR)__missing | 0.0081 |
| Troubles de la conscience (Consciousness trouble) | 0.0077 |
| Hypertension artérielle | 0.0065 |
| Température axillaire (médiane IQR) (°C) /Axillary temperature (median IQR) (°C) | 0.0060 |
| Céphalée (Headache) | 0.0055 |
| Fréquence du pouls (battements/m in ± SD)./ Pulse rate (mean beats/min ± SD) - Shock ou Myocarditis | 0.0051 |
| bp__missing | 0.0045 |
| Convulsions multiples (Multiple convulsions) | 0.0039 |
| Oligurie (Oliguria) | 0.0032 |
| Pneumonie (Pneumonia) | 0.0026 |


![Global importance](../figures/feature_importance_global.png)

*Global importance*


![Per-label importance](../figures/feature_importance_per_label.png)

*Per-label importance*


![Local case studies](../figures/local_explanation_examples.png)

*Local case studies*


![SHAP summary (malaria)](../figures/shap_summary.png)

*SHAP summary (malaria)*

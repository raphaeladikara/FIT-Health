# Explainability Summary

*Permutation importance + linear local*

_Generated: 2026-06-13 02:43 — VECTRA-X pipeline_

Features are anonymised/encoded clinical **signals** — explanations describe model behaviour, not medical causation.


## Global importance (top 15)

| feature | importance_mean |
| --- | --- |
| autres_maladies_pr_sent_es_par_le_patien__present | 0.0905 |
| Température axillaire (médiane IQR) (°C) /Axillary temperature (median IQR) (°C)__missing | 0.0184 |
| Diabète | 0.0126 |
| Douleur abdominale (stomac pain) | 0.0122 |
| Pâleur cutanéo muqueuse ou Anémie (Mucosal skin pallor or Anemia) | 0.0110 |
| Vertige (Dizzy) | 0.0095 |
| Douleur articulaire (Joint pain) | 0.0080 |
| Convulsions généralisées ou focales (Generalised or focal convulsion) | 0.0048 |
| Troubles de la conscience (Consciousness trouble) | 0.0039 |
| Haute température.(temperature, Hyperpyrexia) | 0.0029 |
| Céphalée (Headache) | 0.0028 |
| Convulsions multiples (Multiple convulsions) | 0.0020 |
| Distension abdominale (Ventre gonflé) (Abdominal Distension (Swelling Stomach)/ Ascites) | 0.0011 |
| Fièvre depuis 48 heures(Fever 48 hrs) | 0.0007 |
| Saignement/ Manifestations hémorragiques (Bleeding) | 0.0005 |


![Global importance](../figures/feature_importance_global.png)

*Global importance*


![Per-label importance](../figures/feature_importance_per_label.png)

*Per-label importance*


![Local case studies](../figures/local_explanation_examples.png)

*Local case studies*


![SHAP summary (malaria)](../figures/shap_summary.png)

*SHAP summary (malaria)*

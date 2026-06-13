# Explainability Summary

*Permutation importance + linear local*

_Generated: 2026-06-13 13:56 — VECTRA-X pipeline_

Features are anonymised/encoded clinical **signals** — explanations describe model behaviour, not medical causation.


## Global importance (top 15)

| feature | importance_mean |
| --- | --- |
| autres_maladies_pr_sent_es_par_le_patien__present | 0.0886 |
| Température axillaire (médiane IQR) (°C) /Axillary temperature (median IQR) (°C)__missing | 0.0357 |
| Douleur articulaire (Joint pain) | 0.0146 |
| Diabète | 0.0139 |
| type_de_fi_vre__cat_1_r_currente | 0.0125 |
| Pâleur cutanéo muqueuse ou Anémie (Mucosal skin pallor or Anemia) | 0.0104 |
| Haute température.(temperature, Hyperpyrexia) | 0.0102 |
| Céphalée (Headache) | 0.0086 |
| centre_de_sant__cat_0_cma_de_dafra | 0.0085 |
| Vertige (Dizzy) | 0.0076 |
| Fièvre depuis 48 heures(Fever 48 hrs) | 0.0069 |
| Convulsions généralisées ou focales (Generalised or focal convulsion) | 0.0065 |
| centre_de_sant__cat_1_cma_de_do | 0.0063 |
| Convulsions multiples (Multiple convulsions) | 0.0062 |
| Nausée (Nausea) | 0.0046 |


![Global importance](../figures/feature_importance_global.png)

*Global importance*


![Per-label importance](../figures/feature_importance_per_label.png)

*Per-label importance*


![Local case studies](../figures/local_explanation_examples.png)

*Local case studies*


![SHAP summary (malaria)](../figures/shap_summary.png)

*SHAP summary (malaria)*

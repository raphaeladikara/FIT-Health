# Triage Engine Summary

*VECTRA-X decision support*

_Generated: 2026-06-13 13:56 — VECTRA-X pipeline_

Triage score = 0.45·risk + 0.25·severe + 0.15·uncertainty + 0.15·co-infection (all bounded to [0,1]). Tiers assigned by transparent rules on severe-disease probability, uncertainty, co-infection and conformal set.


## Cohort triage distribution

| tier | patients |
| --- | --- |
| Confirmatory Test Priority | 107 |
| Clinical Review | 80 |
| Routine Monitoring | 67 |
| Urgent Response Priority | 46 |


## Sample patient outputs

| uuid | predicted_labels | conformal_set | uncertainty_level | triage_score | triage_category | recommended_action |
| --- | --- | --- | --- | --- | --- | --- |
| df22d899-23a3-4c49-8059-6208c130f57d | {malaria, dengue} | {malaria, dengue, typhoid, yellow_fever} | moderate | 0.4649 | Confirmatory Test Priority | Prioritise confirmatory testing (rapid test / laboratory) and closer observation. |
| 4a7ef2f3-4ff0-4215-8cb5-20ba8c8d4355 | {malaria, dengue, typhoid} | {malaria, dengue, typhoid, yellow_fever} | moderate | 0.4932 | Confirmatory Test Priority | Prioritise confirmatory testing (rapid test / laboratory) and closer observation. |
| 104f6bc8-f39a-482b-b680-7ac1f8cccc86 | {malaria, dengue} | {malaria, dengue, typhoid, yellow_fever} | moderate | 0.5201 | Urgent Response Priority | Flag for urgent clinical evaluation / referral. |
| 26d7d04a-1a1c-4d4b-b64a-606f968e6d9c | {malaria} | {malaria, dengue, typhoid, yellow_fever} | moderate | 0.2114 | Clinical Review | Manual clinician review and symptom monitoring. |
| eb694f52-51ff-488d-9beb-2923a572a4cf | {malaria, dengue, yellow_fever} | {dengue, typhoid, yellow_fever} | high | 0.3590 | Urgent Response Priority | Flag for urgent clinical evaluation / referral. |
| 92fee67e-e41c-41f7-85ad-121df731b37f | {malaria} | {malaria, dengue, typhoid, yellow_fever} | moderate | 0.2138 | Clinical Review | Manual clinician review and symptom monitoring. |
| 25435e6c-0ee8-403a-8916-711a3613e4e3 | {malaria} | {malaria, dengue, typhoid, yellow_fever} | moderate | 0.1786 | Clinical Review | Manual clinician review and symptom monitoring. |
| 3d05f28c-9d33-4b7c-9417-0ff09d462209 | {malaria, other_diseases} | {malaria, other_diseases, typhoid} | low | 0.2602 | Clinical Review | Manual clinician review and symptom monitoring. |
| 95c3917b-1714-4210-8861-21f08d80b561 | {malaria, dengue, yellow_fever} | {dengue, typhoid, yellow_fever} | high | 0.3749 | Urgent Response Priority | Flag for urgent clinical evaluation / referral. |
| 9acf30c2-8ac4-4009-b0de-032ed2eaddf7 | {malaria, other_diseases, yellow_fever} | {malaria, other_diseases, dengue, typhoid, yellow_fever} | moderate | 0.3905 | Confirmatory Test Priority | Prioritise confirmatory testing (rapid test / laboratory) and closer observation. |

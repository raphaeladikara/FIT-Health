# Conformal Prediction Summary

*Recall-oriented prediction sets*

_Generated: 2026-06-13 13:56 — VECTRA-X pipeline_

Target coverage = 90% (alpha=0.1). Avg set size = 2.8052, empty sets 0.0%, ambiguous (≥2) 92.21%.


## Per-label coverage (held-out test)

| label | prob_threshold | test_positives | covered_positives | empirical_coverage | predicted_inclusions |
| --- | --- | --- | --- | --- | --- |
| malaria | 0.6059 | 67 | 66 | 0.9851 | 75 |
| other_diseases | 0.5392 | 25 | 24 | 0.9600 | 24 |
| dengue | 0.1837 | 14 | 13 | 0.9286 | 37 |
| typhoid | 0.1257 | 7 | 4 | 0.5714 | 29 |
| yellow_fever | 0.0222 | 3 | 3 | 1.0000 | 51 |


## Example prediction sets

| uuid | prediction_set | set_size | true_labels | interpretation | max_prob |
| --- | --- | --- | --- | --- | --- |
| eb694f52-51ff-488d-9beb-2923a572a4cf | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.8590 |
| 3f96e3e8-d1ed-4ff4-b945-8088af180529 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.8220 |
| f41c7b5c-d560-4352-82b2-cebfcdf2a68a | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.8570 |
| 83257713-90ef-47db-acb6-f977a4b8ee1a | {malaria, dengue, typhoid, yellow_fever} | 4 | {dengue, yellow_fever} | ambiguous — request confirmatory testing | 0.8300 |
| 76d34d9f-4f0b-4bb3-b610-8f41510b0aab | {malaria, dengue, typhoid, yellow_fever} | 4 | {dengue} | ambiguous — request confirmatory testing | 0.7430 |
| f5c31a1e-6059-44fb-8d10-feb7891a93ea | {malaria, other_diseases, typhoid, yellow_fever} | 4 | {malaria, other_diseases} | ambiguous — request confirmatory testing | 0.9010 |
| 2e80ed76-27fd-467c-b9d8-fa3be6dd72a3 | {malaria} | 1 | {malaria} | confident single diagnosis | 0.9380 |
| 708eccbd-9604-491a-b41c-6026aba3c908 | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {malaria, other_diseases} | ambiguous — request confirmatory testing | 0.7750 |
| 8648cafa-454c-45d1-80e2-afdb5f25fd2b | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {other_diseases, dengue} | ambiguous — request confirmatory testing | 0.7130 |
| cc1f97c7-8bef-484a-9fc5-7ea18c162db5 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.9310 |
| a61731ad-62a0-4edd-a463-f24e3428c1c1 | {malaria, other_diseases, dengue, yellow_fever} | 4 | {malaria, other_diseases, dengue} | ambiguous — request confirmatory testing | 0.7790 |
| f6657bfb-245d-4d5f-be6b-c566dc567f71 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.8910 |
| e8b903b1-bd5c-4543-b1c4-de346742db75 | {malaria, typhoid} | 2 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.9580 |
| 09e9b149-fe95-49f6-8513-7baf734163d4 | {malaria, yellow_fever} | 2 | {malaria} | ambiguous — request confirmatory testing | 0.9860 |
| 3e835e2c-0d50-4d96-b8be-2a4825dcbd9f | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.9450 |

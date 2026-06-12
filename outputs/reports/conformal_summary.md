# Conformal Prediction Summary

*Recall-oriented prediction sets*

_Generated: 2026-06-13 02:43 — VECTRA-X pipeline_

Target coverage = 90% (alpha=0.1). Avg set size = 2.8961, empty sets 0.0%, ambiguous (≥2) 94.81%.


## Per-label coverage (held-out test)

| label | prob_threshold | test_positives | covered_positives | empirical_coverage | predicted_inclusions |
| --- | --- | --- | --- | --- | --- |
| malaria | 0.6212 | 67 | 66 | 0.9851 | 75 |
| other_diseases | 0.6025 | 25 | 24 | 0.9600 | 24 |
| dengue | 0.1610 | 14 | 13 | 0.9286 | 37 |
| typhoid | 0.0775 | 7 | 4 | 0.5714 | 33 |
| yellow_fever | 0.0130 | 3 | 3 | 1.0000 | 54 |


## Example prediction sets

| uuid | prediction_set | set_size | true_labels | interpretation | max_prob |
| --- | --- | --- | --- | --- | --- |
| eb694f52-51ff-488d-9beb-2923a572a4cf | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.8940 |
| 3f96e3e8-d1ed-4ff4-b945-8088af180529 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.8230 |
| f41c7b5c-d560-4352-82b2-cebfcdf2a68a | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.8740 |
| 83257713-90ef-47db-acb6-f977a4b8ee1a | {malaria, dengue, typhoid, yellow_fever} | 4 | {dengue, yellow_fever} | ambiguous — request confirmatory testing | 0.8740 |
| 76d34d9f-4f0b-4bb3-b610-8f41510b0aab | {malaria, dengue, typhoid, yellow_fever} | 4 | {dengue} | ambiguous — request confirmatory testing | 0.7070 |
| f5c31a1e-6059-44fb-8d10-feb7891a93ea | {malaria, other_diseases, typhoid, yellow_fever} | 4 | {malaria, other_diseases} | ambiguous — request confirmatory testing | 0.8810 |
| 2e80ed76-27fd-467c-b9d8-fa3be6dd72a3 | {malaria, typhoid} | 2 | {malaria} | ambiguous — request confirmatory testing | 0.9440 |
| 708eccbd-9604-491a-b41c-6026aba3c908 | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {malaria, other_diseases} | ambiguous — request confirmatory testing | 0.8060 |
| 8648cafa-454c-45d1-80e2-afdb5f25fd2b | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {other_diseases, dengue} | ambiguous — request confirmatory testing | 0.7980 |
| cc1f97c7-8bef-484a-9fc5-7ea18c162db5 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.9340 |
| a61731ad-62a0-4edd-a463-f24e3428c1c1 | {malaria, other_diseases, dengue, yellow_fever} | 4 | {malaria, other_diseases, dengue} | ambiguous — request confirmatory testing | 0.8110 |
| f6657bfb-245d-4d5f-be6b-c566dc567f71 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.9020 |
| e8b903b1-bd5c-4543-b1c4-de346742db75 | {malaria, typhoid} | 2 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.9600 |
| 09e9b149-fe95-49f6-8513-7baf734163d4 | {malaria, typhoid} | 2 | {malaria} | ambiguous — request confirmatory testing | 0.9880 |
| 3e835e2c-0d50-4d96-b8be-2a4825dcbd9f | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.9490 |

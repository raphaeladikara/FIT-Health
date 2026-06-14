# Conformal Prediction Summary

*Recall-oriented prediction sets*

_Generated: 2026-06-14 20:04 — VECTRA-X pipeline_

Exact uncapped empirical inclusion policy with nominal target 90% (alpha=0.1). This small-sample result is reported per label and is not a prospective coverage guarantee. Avg set size = 4.0385, empty sets 0.0%, ambiguous (≥2) 100.0%.


## Per-label coverage (held-out test)

| label | prob_threshold | test_positives | covered_positives | empirical_coverage | predicted_inclusions |
| --- | --- | --- | --- | --- | --- |
| malaria | 0.6573 | 68 | 64 | 0.9412 | 72 |
| other_diseases | 0.2266 | 25 | 24 | 0.9600 | 47 |
| dengue | 0.1177 | 14 | 13 | 0.9286 | 45 |
| typhoid | 0.0088 | 7 | 7 | 1.0000 | 73 |
| yellow_fever | 0.0000 | 3 | 3 | 1.0000 | 78 |


## Example prediction sets

| uuid | prediction_set | set_size | true_labels | interpretation | max_prob |
| --- | --- | --- | --- | --- | --- |
| 26d7d04a-1a1c-4d4b-b64a-606f968e6d9c | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.8660 |
| 3f96e3e8-d1ed-4ff4-b945-8088af180529 | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.8080 |
| f41c7b5c-d560-4352-82b2-cebfcdf2a68a | {dengue, typhoid, yellow_fever} | 3 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.8510 |
| aeb1d26c-a9d3-4081-8b6d-6ed064bd5791 | {malaria, dengue, typhoid, yellow_fever} | 4 | {dengue, yellow_fever} | ambiguous — request confirmatory testing | 0.7760 |
| 76d34d9f-4f0b-4bb3-b610-8f41510b0aab | {malaria, dengue, typhoid, yellow_fever} | 4 | {dengue} | ambiguous — request confirmatory testing | 0.8100 |
| 2e80ed76-27fd-467c-b9d8-fa3be6dd72a3 | {malaria, other_diseases, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.9670 |
| 9c6a66f0-eb73-4139-9d53-cec94117485e | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {malaria} | ambiguous — request confirmatory testing | 0.7530 |
| 741111f9-8be6-4140-b7bb-61c78043e168 | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {malaria, other_diseases} | ambiguous — request confirmatory testing | 0.8810 |
| 8648cafa-454c-45d1-80e2-afdb5f25fd2b | {other_diseases, dengue, typhoid, yellow_fever} | 4 | {other_diseases, dengue} | ambiguous — request confirmatory testing | 0.7030 |
| cc1f97c7-8bef-484a-9fc5-7ea18c162db5 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.9400 |
| f6657bfb-245d-4d5f-be6b-c566dc567f71 | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria} | ambiguous — request confirmatory testing | 0.9080 |
| e8b903b1-bd5c-4543-b1c4-de346742db75 | {malaria, typhoid, yellow_fever} | 3 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.9750 |
| 09e9b149-fe95-49f6-8513-7baf734163d4 | {malaria, typhoid, yellow_fever} | 3 | {malaria} | ambiguous — request confirmatory testing | 0.9590 |
| f3042b8a-7be5-4ae7-a4f9-f89c0adfaba4 | {malaria, other_diseases, dengue, typhoid, yellow_fever} | 5 | {malaria, other_diseases} | ambiguous — request confirmatory testing | 0.9270 |
| 3e835e2c-0d50-4d96-b8be-2a4825dcbd9f | {malaria, dengue, typhoid, yellow_fever} | 4 | {malaria, dengue} | ambiguous — request confirmatory testing | 0.9240 |

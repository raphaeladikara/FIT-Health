# Dashboard Capability Boundaries

| Capability | Public static | Local Streamlit |
|---|---:|---:|
| Landing and guided demo | Yes | No |
| Aggregate model evidence | Yes | Yes |
| Curated anonymized cases | Yes | Yes |
| Upload patient file | No | Local workflow only |
| Run model inference | No | Local workflow only |
| Ground-truth evaluation | Aggregate only | Restricted evaluation mode |
| Resource scenario projection | Yes | Yes |

The public dashboard is a static decision-support prototype. It does not store patient
data, authenticate users, or run live clinical inference.

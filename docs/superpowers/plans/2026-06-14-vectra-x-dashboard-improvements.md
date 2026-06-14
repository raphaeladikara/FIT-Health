# VECTRA-X Dashboard Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengubah dashboard VECTRA-X yang saat ini sudah kuat secara visual menjadi prototype decision-support yang aman untuk dipublikasikan, mudah dipahami dalam 3-5 menit, konsisten secara ilmiah, responsif, dan mampu menonjolkan keunggulan utama project.

**Architecture:** Pertahankan deployment statis tanpa backend sebagai surface publik. Pisahkan pengalaman menjadi landing page, guided demo, dan dashboard analitis; hasil pipeline tetap diekspor oleh Python ke kontrak JSON yang tervalidasi dan bebas identifier pasien. Streamlit dipertahankan sebagai tool lokal/advanced, bukan surface publik.

**Tech Stack:** HTML5, CSS, vanilla JavaScript modules, Chart.js lokal, Python/pandas exporter, JSON Schema, Node built-in test runner, Playwright browser checks, Vercel static hosting.

---

## 1. Ringkasan Evaluasi Terbaru

### Yang sudah meningkat

- Identitas visual dark navy, teal, dan coral sudah kohesif dan terlihat seperti produk riset yang serius.
- Cakupan ilmiah jauh lebih lengkap: EDA, model benchmark, held-out metrics, threshold policy, conformal prediction, explainability, fairness, robustness, resource impact, serta limitations.
- Dashboard sudah jujur tentang leakage: model `FULL` tidak diposisikan sebagai model deployment.
- Nilai utama project sudah mulai tampak: multi-label triage, uncertainty-aware prediction, stage-aware modeling, fairness, dan operational resource impact.
- Informasi per-label seperti support, recall, FNR, dan conformal coverage sudah tersedia.

### Blocker sebelum deployment publik

1. `web/data/patients.json` masih membawa UUID dan `true_labels`.
2. `export_web_data.py` menyalin seluruh tabel prediksi pasien tanpa allowlist kolom.
3. Patient Triage dan Prediction Explorer mengekspos identifier serta ground truth.
4. Warna keputusan di patient chart menggunakan threshold tetap `0.5`, padahal threshold kebijakan berbeda per penyakit.

### Kekurangan pengalaman pengguna

1. Pengguna langsung masuk ke dashboard padat tanpa orientasi tentang problem, workflow, dan arti tiap fitur.
2. Sepuluh menu setara membuat hierarchy datar; pengguna baru tidak tahu jalur utama.
3. Mobile menampilkan seluruh sidebar sebelum konten sehingga membutuhkan scroll panjang hanya untuk mulai membaca.
4. Hash URL berubah, tetapi Back/Forward atau perubahan hash tidak merender view baru karena tidak ada listener `hashchange`/`popstate`.
5. Dropdown 300 UUID tidak cocok untuk demo; pengguna tidak mengenal kasus mana yang menarik.
6. Tabel dapat terpotong diam-diam melalui `maxRows` tanpa memberi tahu bahwa data lain disembunyikan.
7. Resource Simulation saat ini masih berupa laporan statis, belum benar-benar menjadi simulator.
8. Belum ada model-mode selector walaupun stage PRE_LAB, LAB_AWARE, dan FULL merupakan pembeda penting.
9. Belum ada provenance yang jelas: run ID, waktu generate, source artifact, split, dan status canonical.
10. Chart berbasis canvas belum memiliki ringkasan tekstual yang memadai untuk aksesibilitas.

### Kekurangan visual dan accessibility

- Label mono 9-11 px terlalu kecil dan redup untuk sebagian pengguna.
- Delapan KPI dengan bobot setara melemahkan prioritas informasi.
- Grain SVG `feTurbulence`, glow, gradient, dan card treatment digunakan terlalu luas.
- Animasi belum memiliki `prefers-reduced-motion`.
- Label form belum selalu terhubung melalui `for` dan `id`.
- Tidak ada skip link, status region, focus management, dan mobile navigation yang ringkas.
- Google Fonts dan Chart.js bergantung pada CDN, berisiko pada demo offline atau jaringan kompetisi yang tidak stabil.

### Skor usability saat ini

| Area | Skor | Catatan |
|---|---:|---|
| Visibility of system status | 2/4 | Loader ada, tetapi view change dan data provenance lemah |
| Match with real-world workflow | 2/4 | Bahasa decision-support baik, alur pengguna belum dipandu |
| User control and freedom | 1/4 | Back/Forward rusak, tidak ada reset/filter state yang jelas |
| Consistency and standards | 3/4 | Visual konsisten, semantics keputusan belum konsisten |
| Error prevention | 1/4 | Data publik dan threshold mismatch merupakan risiko utama |
| Recognition over recall | 2/4 | Menu jelas, tetapi kasus dan metrik terlalu padat |
| Flexibility and efficiency | 1/4 | Belum ada guided/analyst mode, search, atau saved view |
| Aesthetic and minimalist design | 3/4 | Polished, tetapi terlalu card-heavy dan teks kecil |
| Error recovery | 1/4 | Error state hanya memberi instruksi teknis lokal |
| Help and documentation | 2/4 | Methodology lengkap, onboarding produk belum ada |
| **Total** | **18/40** | Visual kuat, tetapi safety, navigation, dan workflow masih membatasi |

---

## 2. Keputusan Produk dan Information Architecture

### Surface publik

1. **Landing Page** di `web/index.html`
   - Menjawab: masalah apa yang diselesaikan, siapa penggunanya, bagaimana alurnya, apa keunggulannya, dan batasannya.
   - CTA primer: `Start guided demo`.
   - CTA sekunder: `Open analytics dashboard`.

2. **Guided Demo** di `web/demo.html`
   - Alur linear 5 langkah menggunakan kasus sintetis/anonymized.
   - Cocok untuk juri, stakeholder, dan pengguna pertama.
   - Estimasi durasi terlihat: 3-5 menit.

3. **Analytics Dashboard** di `web/dashboard.html`
   - Surface analitis mendalam dengan grouping navigasi yang lebih pendek.
   - Tetap menggunakan data pipeline nyata yang sudah disanitasi.

4. **Local Advanced App** di `app/streamlit_app.py`
   - Untuk eksplorasi lokal, upload/inference, dan analisis tim.
   - Tidak dipublikasikan bersama bundle statis.

### Grouping navigasi dashboard

- **Overview**
  - Executive Overview
- **Model Evidence**
  - Dataset & EDA
  - Model Performance
  - Uncertainty
  - Explainability
- **Decision Support**
  - Case Explorer
  - Patient Triage
  - Resource Simulator
- **Trust & Governance**
  - Fairness & Robustness
  - Methodology & Limitations

Desktop memakai collapsible rail. Mobile memakai top bar dengan tombol menu dan drawer.

### Hero message yang direkomendasikan

> VECTRA-X turns pre-lab patient signals into multi-label triage recommendations, calibrated uncertainty, and resource-aware actions.

Tiga proof point utama:

- **Leakage-aware:** deployable evidence dipisahkan dari research-only features.
- **Uncertainty-aware:** conformal prediction menunjukkan kapan sistem harus abstain atau meminta tes konfirmasi.
- **Operational:** prediksi diterjemahkan menjadi priority tier dan kebutuhan sumber daya.

---

## 3. Target Struktur File

```text
web/
  index.html
  demo.html
  dashboard.html
  assets/
    base.css
    landing.css
    dashboard.css
    responsive.css
    app-shell.js
    router.js
    data-client.js
    formatters.js
    chart-factory.js
    components.js
    landing.js
    demo.js
    dashboard.js
    views/
      overview.js
      evidence.js
      explorer.js
      triage.js
      uncertainty.js
      explainability.js
      fairness.js
      resources.js
      methodology.js
    vendor/
      chart.umd.min.js
  data/
    dashboard.json
    demo-cases.json
    manifest.json
    schemas/
      dashboard.schema.json
      demo-cases.schema.json
      manifest.schema.json
  tests/
    router.test.js
    data-client.test.js
    thresholds.test.js
    privacy.test.js
    resource-simulator.test.js
    smoke.spec.mjs
  package.json
  vercel.json

tests/
  test_export_web_data.py
  test_public_bundle_privacy.py

export_web_data.py
app/streamlit_app.py
```

`web/assets/app.js` dan `web/assets/styles.css` dipecah secara bertahap setelah regression tests tersedia. Jangan melakukan rewrite besar dalam satu commit.

---

## Phase 0: Protect the Public Bundle

### Task 1: Tetapkan kontrak data publik

**Files:**
- Create: `web/data/schemas/dashboard.schema.json`
- Create: `web/data/schemas/demo-cases.schema.json`
- Create: `web/data/schemas/manifest.schema.json`
- Create: `tests/test_public_bundle_privacy.py`
- Modify: `export_web_data.py`

- [ ] **Step 1: Tulis privacy regression test**

Test harus gagal bila key berikut muncul di file publik:

```python
FORBIDDEN_KEYS = {
    "uuid",
    "patient_id",
    "true_labels",
    "ground_truth",
    "name",
    "email",
    "phone",
}
```

Test membaca seluruh JSON di `web/data`, menelusuri dictionary/list secara rekursif, dan memastikan tidak ada forbidden key.

- [ ] **Step 2: Jalankan test untuk membuktikan kondisi sekarang gagal**

Run:

```powershell
pytest tests/test_public_bundle_privacy.py -q
```

Expected: FAIL pada `web/data/patients.json`.

- [ ] **Step 3: Ganti export pasien dengan allowlist**

Exporter hanya boleh menghasilkan:

```python
PUBLIC_CASE_COLUMNS = [
    "case_id",
    "scenario",
    "triage_category",
    "triage_score",
    "uncertainty_category",
    "predicted_labels",
    "conformal_set",
    "calprob_malaria",
    "calprob_other_diseases",
    "calprob_dengue",
    "calprob_typhoid",
    "calprob_yellow_fever",
]
```

`case_id` dibuat deterministik sebagai `CASE-001`, `CASE-002`, dan seterusnya setelah urutan data dikunci. Jangan hash UUID lalu mempublikasikannya.

- [ ] **Step 4: Pindahkan ground truth ke agregat evaluasi**

Ground truth hanya boleh tampil sebagai:

- confusion/metric aggregate,
- per-label support,
- coverage aggregate,
- contoh sintetis yang diberi label jelas sebagai simulated example.

- [ ] **Step 5: Hapus `web/data/patients.json`**

Ganti dengan `web/data/demo-cases.json` yang berisi maksimum 12 kasus terpilih dan aman untuk presentasi.

- [ ] **Step 6: Verifikasi**

```powershell
pytest tests/test_public_bundle_privacy.py -q
```

Expected: PASS.

- [ ] **Step 7: Commit**

```powershell
git add export_web_data.py tests/test_public_bundle_privacy.py web/data
git commit -m "fix: sanitize public dashboard data"
```

### Task 2: Sinkronkan threshold keputusan

**Files:**
- Create: `web/assets/thresholds.js`
- Create: `web/tests/thresholds.test.js`
- Modify: `export_web_data.py`
- Modify: `web/assets/app.js`

- [ ] **Step 1: Tulis failing tests**

Tests harus memastikan:

- Malaria operational threshold `0.05`.
- Dengue operational threshold `0.35`.
- Typhoid operational threshold `0.50`.
- Yellow Fever operational threshold `0.10`.
- Predicted state selalu berasal dari threshold policy aktif, bukan `0.5` global.

- [ ] **Step 2: Export threshold sebagai object keyed by label**

```json
{
  "policy": "operational",
  "values": {
    "malaria": 0.05,
    "other_diseases": 0.5,
    "dengue": 0.35,
    "typhoid": 0.5,
    "yellow_fever": 0.1
  }
}
```

- [ ] **Step 3: Buat pure function**

```javascript
export function isPositive(probability, label, thresholds) {
  const threshold = thresholds.values[label];
  if (!Number.isFinite(threshold)) {
    throw new Error(`Missing operational threshold for ${label}`);
  }
  return probability >= threshold;
}
```

- [ ] **Step 4: Perbaiki chart dan copy**

- Warna bar memakai `isPositive`.
- Tooltip menampilkan `Probability 0.42; operational threshold 0.35`.
- Garis/marker threshold ditampilkan per label.
- Label `Above decision threshold` menggantikan interpretasi warna implisit.

- [ ] **Step 5: Run tests and commit**

```powershell
node --test web/tests/thresholds.test.js
git add web/assets web/tests export_web_data.py
git commit -m "fix: align patient decisions with threshold policy"
```

---

## Phase 1: Reliable Data Contract and Provenance

### Task 3: Tambahkan manifest canonical run

**Files:**
- Create: `web/data/manifest.json`
- Create: `tests/test_export_web_data.py`
- Modify: `export_web_data.py`

Manifest minimum:

```json
{
  "schema_version": "1.0.0",
  "run_id": "2026-06-14T120000Z-prelab-et",
  "generated_at": "2026-06-14T12:00:00Z",
  "canonical": true,
  "model_track": "PRE_LAB",
  "model_name": "Extra Trees",
  "evaluation_split": "held-out test",
  "cohort_size": 300,
  "active_labels": 5,
  "source_commit": "git-sha-or-unknown"
}
```

- [ ] Test bahwa semua field hadir dan tipe datanya valid.
- [ ] Test bahwa metrics yang ditampilkan memiliki `evaluation_source`.
- [ ] Export dilakukan secara atomic melalui temporary file lalu rename.
- [ ] Dashboard menampilkan `Canonical run`, `generated_at`, dan `held-out/OOF` di header atau info popover.
- [ ] Commit: `feat: add dashboard provenance manifest`.

### Task 4: Validasi semua input sebelum publish

**Files:**
- Create: `scripts/validate_web_bundle.py`
- Modify: `export_web_data.py`
- Modify: `README.md`

Validator harus gagal jika:

- JSON invalid.
- Schema mismatch.
- Forbidden identifier ditemukan.
- Nilai probabilitas di luar `[0, 1]`.
- Threshold label hilang.
- File figure yang direferensikan tidak ada.
- Canonical metrics kosong.
- `FULL` track ditandai deployable.

Commands:

```powershell
python export_web_data.py
python scripts/validate_web_bundle.py
```

Expected: keduanya exit `0`.

---

## Phase 2: Navigation, Testing, and Static App Foundation

### Task 5: Tambahkan test harness tanpa mengubah deployment

**Files:**
- Create: `web/package.json`
- Create: `web/tests/router.test.js`
- Create: `web/tests/data-client.test.js`
- Create: `web/tests/smoke.spec.mjs`

Scripts:

```json
{
  "scripts": {
    "test": "node --test tests/*.test.js",
    "check": "node --check assets/*.js",
    "test:browser": "node tests/smoke.spec.mjs"
  }
}
```

Smoke test minimum:

- landing page memuat heading utama,
- guided demo dapat maju dan mundur,
- semua dashboard section dapat dibuka,
- Back/Forward mengubah konten aktif,
- tidak ada uncaught console error,
- mobile menu dapat dibuka dan ditutup,
- Chart.js gagal load menampilkan fallback text.

### Task 6: Perbaiki router dan history

**Files:**
- Create: `web/assets/router.js`
- Modify: `web/assets/app.js`
- Test: `web/tests/router.test.js`

Router contract:

```javascript
export function normalizeRoute(hash, validRoutes, fallback = "overview") {
  const route = hash.replace(/^#/, "");
  return validRoutes.includes(route) ? route : fallback;
}
```

Implementation:

- Klik nav menggunakan `history.pushState`, bukan `replaceState`.
- Initial boot membaca hash.
- `window.addEventListener("hashchange", renderCurrentRoute)`.
- `window.addEventListener("popstate", renderCurrentRoute)`.
- Unknown hash kembali ke overview dan menampilkan non-blocking notice.
- Focus dipindahkan ke `<h1>` setelah perubahan route.
- Active link memakai `aria-current="page"`.

Acceptance:

1. Buka `#models`, heading adalah `Model Performance`.
2. Pindah ke `#fairness`.
3. Browser Back kembali ke `Model Performance`.
4. Refresh mempertahankan view aktif.

### Task 7: Pecah file monolit secara bertahap

**Files:**
- Create: `web/assets/data-client.js`
- Create: `web/assets/formatters.js`
- Create: `web/assets/chart-factory.js`
- Create: `web/assets/components.js`
- Create: `web/assets/views/*.js`
- Modify: `web/assets/app.js`

Urutan ekstraksi:

1. pure formatters,
2. data loader dan validation,
3. table/card helpers,
4. chart factory,
5. satu view per commit,
6. app shell terakhir.

Setiap ekstraksi harus menjaga smoke tests tetap hijau. Hindari framework migration; tidak ada kebutuhan produk yang membenarkan membawa kembali Next.js.

---

## Phase 3: Landing Page

### Task 8: Bangun landing page yang menjelaskan value sebelum detail

**Files:**
- Modify: `web/index.html`
- Create: `web/assets/landing.css`
- Create: `web/assets/landing.js`

Urutan section:

1. **Hero**
   - One-sentence value proposition.
   - CTA `Start guided demo`.
   - CTA `Open analytics`.
   - Badge `Decision support, not diagnosis`.

2. **Problem**
   - Gejala overlap.
   - Multi-label/co-infection.
   - Keterbatasan test dan resource.

3. **How VECTRA-X works**
   - Input pre-lab signals.
   - Multi-label model.
   - Calibration + conformal uncertainty.
   - Triage + resource action.

4. **Why this project is different**
   - Leakage-aware stage gating.
   - Uncertainty-aware abstention.
   - Fairness/robustness audit.
   - Operational simulation.

5. **Evidence**
   - Tampilkan maksimum empat angka:
     - macro-F1,
     - macro-recall,
     - conformal coverage,
     - coinfection AUC.
   - Selalu sertakan cohort, split, dan support caveat.

6. **Limitations**
   - n=300.
   - class imbalance.
   - rare labels.
   - LOCO degradation.

7. **CTA footer**
   - `Start 5-step demo`.
   - `Explore full evidence`.

Visual rules:

- Jangan menyalin seluruh dashboard ke landing.
- Maksimum dua card rows per viewport.
- Tidak ada grain filter.
- Gunakan satu gradient hero saja.
- Body text minimum 16 px; metadata minimum 12 px.
- CTA primer harus paling dominan.

Acceptance:

- Pengguna baru dapat menjawab problem, input, output, differentiator, dan limitation hanya dari landing.
- Tidak ada patient-level data yang dimuat pada landing.
- Lighthouse accessibility target minimal 90.

---

## Phase 4: Guided Demo

### Task 9: Buat alur demo 5 langkah

**Files:**
- Create: `web/demo.html`
- Create: `web/assets/demo.js`
- Create: `web/data/demo-cases.json`
- Test: `web/tests/demo.test.js`

Steps:

1. **Select scenario**
   - `Clear single-label case`
   - `Ambiguous multi-label case`
   - `High-risk rare-label case`
   - `Center-shift stress case`

2. **Review pre-lab signals**
   - Tampilkan kelompok sinyal, bukan 82 feature mentah.
   - Jelaskan bahwa feature names dianonimkan.

3. **See model output**
   - Calibrated probability.
   - Label-specific threshold.
   - Predicted labels.

4. **Understand uncertainty**
   - Conformal set.
   - Set size.
   - Plain-language explanation.
   - Kapan sistem abstain.

5. **Take action**
   - Priority tier.
   - Recommended next step.
   - Resource implication.
   - Link ke evidence terkait.

Interaction requirements:

- Progress `Step 2 of 5`.
- Back dan Next selalu tersedia.
- `Restart demo`.
- URL menyimpan `?case=ambiguous&step=3`.
- Keyboard arrow tidak dipakai sebagai satu-satunya kontrol.
- Tidak menyebut scenario sebagai pasien nyata.

### Task 10: Tambahkan guided annotations

Setiap langkah memiliki satu callout `Why this matters`, misalnya:

- Threshold berbeda per penyakit karena trade-off false negative berbeda.
- Conformal set bukan daftar diagnosis, melainkan batas ketidakpastian model.
- Orange/Red membutuhkan human review.
- `FULL` hanya pembanding leakage, bukan rekomendasi deployment.

---

## Phase 5: Dashboard Shell and Overview

### Task 11: Buat shell dashboard baru

**Files:**
- Create: `web/dashboard.html`
- Create: `web/assets/dashboard.css`
- Create: `web/assets/responsive.css`
- Create: `web/assets/app-shell.js`

Header harus memuat:

- current section,
- model mode,
- evaluation source,
- canonical run status,
- mobile menu,
- link kembali ke landing/demo.

Desktop rail:

- empat group, bukan 10 item tanpa grouping,
- group dapat collapse,
- current route jelas,
- footer limitation ringkas.

Mobile:

- rail berubah menjadi drawer,
- drawer tidak mengambil ruang sebelum konten,
- focus trap aktif,
- Escape menutup drawer,
- body scroll dikunci selama drawer terbuka.

### Task 12: Redesign Executive Overview

Prioritas:

1. Hero insight: `What the system can do`.
2. Primary evidence: macro-F1, recall, coverage.
3. Safety caveat: rare-label support dan LOCO.
4. Workflow: signal → prediction → uncertainty → action.
5. Deep links ke demo, evidence, dan limitations.

Kurangi KPI dari delapan menjadi:

- 3 primary cards,
- 3 secondary inline stats,
- 1 limitations callout.

Setiap metric menampilkan:

- value,
- source (`held-out`, `OOF`, atau simulation),
- denominator/support,
- tooltip plain language.

---

## Phase 6: Improve Every Analytical Page

### Task 13: Dataset & EDA

Tambahkan:

- cohort summary,
- label imbalance callout,
- multi-label frequency,
- center distribution,
- missingness overview,
- `What this means for modeling`.

Perbaikan:

- Jangan hanya menampilkan figure tanpa interpretation.
- Setiap chart memiliki satu kalimat takeaway.
- Rare label warning dekat chart prevalence.
- Figure alt text menjelaskan insight, bukan nama file.

### Task 14: Model Performance

Tambahkan model-mode control:

- `PRE_LAB · deployable evidence`
- `LAB_AWARE · workflow comparison`
- `FULL · leakage demonstration`

Rules:

- Default selalu PRE_LAB.
- FULL memakai warning banner permanen.
- Held-out dan OOF tidak boleh dicampur dalam chart tanpa label.
- Per-label table menampilkan support, F1, recall, FNR, PR-AUC.
- Tambahkan uncertainty interval ketika pipeline menyediakannya.
- Sorting default: lowest recall first, agar risk terlihat.

### Task 15: Prediction Explorer

Ganti disease-only filter dengan:

- disease,
- triage tier,
- uncertainty category,
- predicted label count,
- free-text `CASE-###`.

Tambahkan:

- result count,
- clear filters,
- pagination atau `Load 20 more`,
- empty state dengan cara recovery,
- column explanation,
- link `Open case`.

Jangan menampilkan UUID atau true label.

### Task 16: Patient Triage

Ganti dropdown 300 UUID dengan:

- scenario picker,
- searchable `CASE-###`,
- previous/next case,
- `Why this case is interesting`.

Card structure:

1. Action summary.
2. Priority tier and reason.
3. Predicted labels against operational thresholds.
4. Conformal set and ambiguity.
5. Human next step.
6. Link to methodology.

Jangan menampilkan ground truth di operational view. Bila diperlukan untuk evaluasi, buat tab terpisah `Retrospective evaluation` yang hanya menunjukkan agregat.

### Task 17: Uncertainty & Conformal

Urutan informasi:

1. Apa arti conformal set.
2. Overall coverage dan target coverage.
3. Average set size.
4. Ambiguity rate.
5. Per-label coverage dengan support.
6. Failure/undercoverage callout.

Typhoid coverage rendah harus ditampilkan sebagai risk, bukan terselip di tabel. Yellow Fever coverage `1.0` harus disertai support yang sangat kecil agar tidak dibaca sebagai bukti kuat.

### Task 18: Explainability

Pisahkan:

- global importance,
- per-label importance,
- case-level explanation,
- caveat `association, not causation`.

Jangan menampilkan SHAP image saja. Tambahkan data text/table alternatif dan plain-language interpretation.

### Task 19: Fairness & Robustness

Tampilkan:

- subgroup,
- sample size,
- recall,
- gap,
- reliability state.

Reliability states:

- `Adequate support`
- `Low support`
- `Insufficient evidence`

LOCO performance harus menjadi headline robustness finding karena penurunan ke sekitar `0.38/0.37` merupakan batas generalisasi penting.

### Task 20: Methodology & Limitations

Struktur:

1. Stage gating.
2. Leakage detection.
3. Split and evaluation.
4. Threshold policy.
5. Calibration/conformal method.
6. Known limitations.
7. Intended use and prohibited use.

Tambahkan glossary untuk:

- macro-F1,
- macro-recall,
- PR-AUC,
- OOF,
- conformal coverage,
- set size,
- FNR,
- LOCO.

---

## Phase 7: Make Resource Simulation Truly Interactive

### Task 21: Implement pure simulation engine

**Files:**
- Create: `web/assets/resource-simulator.js`
- Create: `web/tests/resource-simulator.test.js`
- Modify: `web/assets/views/resources.js`

Inputs:

- policy: performance/safety/operational,
- daily cohort size,
- confirmatory test capacity,
- urgent review capacity,
- selected scenario.

Outputs:

- predicted Routine/Review/Priority/Urgent counts,
- confirmatory tests required,
- unmet test demand,
- urgent review overload,
- label-specific demand,
- comparison against baseline.

Pure function:

```javascript
export function simulateResources({
  cohortSize,
  baseCohortSize,
  tierRates,
  testRate,
  testCapacity,
  urgentCapacity
}) {
  const scale = cohortSize / baseCohortSize;
  const testsNeeded = Math.round(testRate * cohortSize);
  const urgentNeeded = Math.round(tierRates.urgent * cohortSize);
  return {
    testsNeeded,
    unmetTests: Math.max(0, testsNeeded - testCapacity),
    urgentNeeded,
    unmetUrgent: Math.max(0, urgentNeeded - urgentCapacity),
    scale
  };
}
```

Tests:

- zero capacity,
- capacity above demand,
- cohort scaling,
- invalid negative input,
- policy switch,
- deterministic rounding.

UI:

- sliders memiliki numeric input companion,
- reset to baseline,
- overload memakai text + icon, bukan warna saja,
- caveat bahwa hasil merupakan scenario projection.

---

## Phase 8: Accessibility, Mobile, and Visual Polish

### Task 22: Accessibility baseline

**Files:**
- Modify: all `web/*.html`
- Modify: `web/assets/base.css`
- Modify: shared components

Checklist:

- `Skip to main content`.
- Landmark `header`, `nav`, `main`, `footer`.
- Setiap label menggunakan `for`.
- Heading hierarchy tidak lompat.
- `aria-current` untuk nav.
- `aria-live="polite"` untuk route/filter status.
- Focus visible minimum 2 px.
- Canvas memiliki accessible summary/table.
- Error tidak hanya disampaikan melalui warna.
- Minimum touch target 44x44 px.
- Contrast WCAG AA.

### Task 23: Motion and visual restraint

- Hapus `feTurbulence`.
- Kurangi gradient ke hero dan active navigation saja.
- Hapus pulse berulang pada urgent state.
- Tambahkan:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
```

- Body text minimum 15-16 px.
- Metadata minimum 12 px.
- Mono uppercase hanya untuk metadata singkat.
- Gunakan accent teal untuk selection/action, coral untuk risk, kuning untuk caution.

### Task 24: Offline-resilient assets

- Simpan Chart.js di `web/assets/vendor`.
- Gunakan system font fallback atau self-host font files berlisensi.
- Tambahkan fallback bila chart library gagal:

```html
<p class="chart-fallback">
  Chart unavailable. The equivalent data remains available in the table below.
</p>
```

- Vercel headers menambahkan CSP yang hanya mengizinkan asset lokal.

---

## Phase 9: Streamlit Parity and Capability Boundaries

### Task 25: Sanitasi Streamlit

**Files:**
- Modify: `app/streamlit_app.py`

- UUID tidak ditampilkan secara default.
- True label hanya tersedia dalam explicit evaluation mode.
- Threshold chart menggunakan policy yang sama dengan exporter.
- Tambahkan badge `Local analytical tool`.
- Jelaskan bahwa public static dashboard tidak menjalankan live inference.

### Task 26: Dokumentasikan capability matrix

**Files:**
- Modify: `README.md`
- Create: `docs/dashboard-capabilities.md`

| Capability | Public static | Local Streamlit |
|---|---:|---:|
| Landing/guided demo | Yes | No |
| Aggregate evidence | Yes | Yes |
| Curated anonymized cases | Yes | Yes |
| Upload patient file | No | Yes |
| Run model inference | No | Yes |
| Ground-truth evaluation | Aggregate only | Restricted mode |
| Resource scenario | Yes | Yes |

Jangan mengklaim fitur live inference pada public dashboard.

---

## Phase 10: Release Verification

### Task 27: Automated quality gate

Commands:

```powershell
pytest tests/test_export_web_data.py tests/test_public_bundle_privacy.py -q
node --test web/tests/*.test.js
node --check web/assets/*.js
python scripts/validate_web_bundle.py
npm --prefix web run test:browser
```

Expected:

- semua exit `0`,
- tidak ada forbidden data,
- tidak ada console error,
- semua route dan history bekerja,
- mobile drawer bekerja,
- semua JSON tervalidasi.

### Task 28: Manual acceptance checklist

- [ ] Landing dapat dipahami tanpa membuka methodology.
- [ ] Guided demo selesai dalam maksimal 5 menit.
- [ ] PRE_LAB jelas sebagai deployable evidence.
- [ ] FULL selalu diberi label research/leakage comparison.
- [ ] Semua patient identifiers hilang dari bundle publik.
- [ ] Threshold yang terlihat sama dengan threshold keputusan.
- [ ] Rare-label caveat tampil dekat metric terkait.
- [ ] Back, Forward, refresh, dan direct hash bekerja.
- [ ] Mobile langsung menampilkan konten, bukan 10 menu penuh.
- [ ] Keyboard dapat mengoperasikan semua kontrol.
- [ ] Reduced motion dihormati.
- [ ] Dashboard tetap dapat menjelaskan data bila chart gagal.
- [ ] Manifest menampilkan canonical run dan waktu generate.
- [ ] Resource simulator menjelaskan bahwa hasilnya scenario projection.

### Task 29: Deployment gate

Urutan:

1. Generate data dari canonical artifacts.
2. Jalankan validator.
3. Jalankan seluruh test.
4. Build/deploy preview.
5. Audit preview desktop dan mobile.
6. Periksa Network tab: tidak ada `patients.json`, UUID, atau true labels.
7. Promosikan preview ke production.

Rollback condition:

- privacy test gagal,
- manifest bukan canonical,
- threshold mismatch,
- route smoke test gagal,
- metrics tanpa source/support,
- console error pada salah satu critical journey.

---

## 4. Urutan Implementasi yang Direkomendasikan

### Milestone A: Safe and scientifically consistent

Tasks 1-4. Dashboard belum boleh dipublikasikan sebelum milestone ini selesai.

### Milestone B: Reliable foundation

Tasks 5-7. Router, tests, dan modularisasi minimum.

### Milestone C: Clear product story

Tasks 8-12. Landing, guided demo, dashboard shell, dan overview.

### Milestone D: Complete analytical experience

Tasks 13-20. Seluruh analytical page direvisi.

### Milestone E: Operational differentiator

Task 21. Resource simulator menjadi fitur aktif, bukan figure statis.

### Milestone F: Production readiness

Tasks 22-29. Accessibility, offline resilience, Streamlit boundary, dan release gate.

---

## 5. Definition of Done

Project dianggap selesai ketika:

1. Tidak ada identifier atau ground truth pasien dalam bundle publik.
2. Semua keputusan UI memakai threshold policy yang sama dengan pipeline.
3. Landing menjelaskan value proposition, workflow, evidence, dan limitation.
4. Guided demo menunjukkan alur signal → prediction → uncertainty → action.
5. Dashboard memiliki hierarchy yang jelas dan navigasi mobile yang ringkas.
6. Semua page memiliki interpretation, caveat, dan source metric.
7. Resource Simulation menerima input pengguna dan menghasilkan projection deterministik.
8. Direct link, refresh, Back, dan Forward bekerja.
9. Accessibility dan responsive smoke tests lulus.
10. Manifest canonical run dan validator mencegah publish artifact yang salah.
11. README tidak mengklaim capability yang hanya tersedia di Streamlit lokal.
12. Seluruh automated release gate exit `0`.

## 6. Batas Scope

Tidak termasuk dalam plan ini:

- clinical deployment nyata,
- penyimpanan data pasien,
- authentication/authorization,
- live backend inference pada Vercel,
- real-time hospital integration,
- perubahan model training kecuali diperlukan untuk export contract,
- klaim diagnosis atau clinical validation.

Keputusan scope ini menjaga prototype tetap aman, dapat didemokan, dan realistis untuk kompetisi.

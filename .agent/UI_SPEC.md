# ZAZAH — UI Design Specification

## Design Direction

**Theme:** Clean, clinical dark interface. Think of a hospital information system that is actually usable — not consumer glossy, not academic ugly.

**Palette:**
```css
:root {
  --bg-primary: #0f1117;        /* near-black background */
  --bg-secondary: #1a1d2e;      /* card/sidebar background */
  --bg-tertiary: #252840;       /* input backgrounds, hover states */
  --accent: #3b82f6;            /* blue — primary action */
  --accent-hover: #2563eb;
  --positive: #ef4444;          /* red — typhoid positive (danger) */
  --positive-bg: rgba(239,68,68,0.1);
  --negative: #22c55e;          /* green — typhoid negative (safe) */
  --negative-bg: rgba(34,197,94,0.1);
  --warning: #f59e0b;           /* amber — uncertain/RF route */
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border: #2d3148;
  --border-light: #3d4166;
  --shadow: 0 4px 20px rgba(0,0,0,0.4);
  --font-body: 'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', 'Fira Code', monospace;
  --radius: 8px;
  --radius-lg: 12px;
}
```

**Typography:**
- Load from Google Fonts: `IBM Plex Sans` (300, 400, 500, 600) + `IBM Plex Mono` (400)
- Body: IBM Plex Sans 14px / line-height 1.6
- Page titles: 24px 600
- Card headings: 16px 600
- Labels: 12px 500 uppercase letter-spacing 0.08em
- Numbers/values: IBM Plex Mono

---

## Layout

**Sidebar + Main Content:**

```
┌─────────────────────────────────────────────────┐
│  TOPBAR: Logo | Page title          User + Logout │
├──────────┬──────────────────────────────────────┤
│          │                                       │
│ SIDEBAR  │   MAIN CONTENT AREA                  │
│ 220px    │   padding 32px                       │
│          │                                       │
│ Nav items│                                       │
│          │                                       │
└──────────┴──────────────────────────────────────┘
```

**Sidebar nav items:**
- 🏠 Dashboard
- ＋ New Diagnosis
- 📋 History
- — (separator, admin only) —
- ⚙️ Rules
- 👥 Users
- 📊 Reports

Active nav item: `background: var(--bg-tertiary); border-left: 3px solid var(--accent);`

---

## Page Designs

### Login Page
Full-screen centered card. No sidebar.

```
┌──────────────────────────────────┐
│                                   │
│    🦠  ZAZAH                      │
│    Clinical Diagnosis Support     │
│                                   │
│  Username ________________________│
│  Password ________________________│
│                                   │
│  [ Sign In ]                      │
│                                   │
│  Veritas University · SE Dept     │
└──────────────────────────────────┘
```

Background: dark with subtle grid pattern. Card: `bg-secondary` with shadow.

---

### Dashboard

**Stats row (4 cards):**
```
[Total Diagnoses Today] [Positive Rate] [Model Accuracy] [AUC Score]
```
Each stat card: large number in `--accent` color, label below in muted text.

**Recent diagnoses table:**
Columns: Case ID | Date | Diagnosis | Confidence | Route | Action (View)

**Model info sidebar widget:**
Shows RF accuracy, F1, AUC from last training. Small green badge "Models Loaded" or red "Models Missing".

---

### New Diagnosis Form (`/diagnosis/new`)

**Layout:** Two-column form with sections separated by subtle headers.

**Section 1: Patient Identification**
- Age (number input, placeholder "Years")
- Sex (select: Male / Female / Other)

**Section 2: Clinical Presentation**
- Fever Duration (number, placeholder "Days", help text "Number of days fever has persisted")
- Fever Pattern (select: Continuous / Step-ladder / Remittent / Intermittent)
- Temperature at Presentation (number, placeholder "°C", e.g. 38.5)
- Headache Severity (range slider 1–5 with labels: None / Mild / Moderate / Severe / Very Severe)

**Section 3: Physical Examination Findings** (checkbox grid)
- [ ] Abdominal Pain
- [ ] Relative Bradycardia (Faget's Sign)
- [ ] Hepatosplenomegaly (Enlarged liver/spleen)
- [ ] Rose Spots
- [ ] Diarrhoea
- [ ] Vomiting
- [ ] Nausea
- [ ] Constipation

**Section 4: Laboratory Results**
- Total Leukocyte Count × 10⁹/L (number, placeholder "e.g. 4.2")
- Platelet Count × 10⁹/L (number, placeholder "e.g. 140")
- Haemoglobin g/dL (number, placeholder "e.g. 11.3")
- Neutrophil % (number, placeholder "e.g. 42")
- Lymphocyte % (number, placeholder "e.g. 38")
- Monocyte % (number, placeholder "e.g. 8")
- ESR mm/hr (number, placeholder "e.g. 45")
- Widal O-Antigen Titre (select: Negative / 1:20 / 1:40 / 1:80 / 1:160 / 1:320 / ≥1:640)

**Submit button:** Full-width, `var(--accent)`, text "Run Diagnostic Engine →"

**Form notes:**
- Required fields: age, sex, fever_duration, fever_pattern, leukocyte_count
- All other fields optional (system handles missing values)
- Inline validation on submit
- Show a small info box: "Fields left blank will be estimated. For best results, provide all laboratory values."

---

### Diagnostic Result Page (`/diagnosis/<id>`)

**Full layout:**

```
┌──────────────────────────────────────────────────────┐
│  ⚠️  DISCLAIMER: Clinical decision support only.      │
│      All results must be reviewed by a clinician.     │
└──────────────────────────────────────────────────────┘

┌─────────────────────┐   ┌──────────────────────────┐
│  DIAGNOSIS RESULT   │   │  CASE SUMMARY            │
│                     │   │                          │
│  ██████████████     │   │  Case ID: CASE-...       │
│  TYPHOID POSITIVE   │   │  Date: 20 Apr 2026       │
│  (in red) or        │   │  Route: Expert System    │
│  TYPHOID NEGATIVE   │   │  ES Score: 0.87          │
│  (in green)         │   │  RF Prob: —              │
│                     │   │                          │
│  Confidence: 87.3%  │   │                          │
│  ████████████░░░░░  │   │                          │
└─────────────────────┘   └──────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  CLINICAL RULES FIRED                                 │
│  ─────────────────────────────────────────────────── │
│  ▶ R-001 · Positive (weight: 0.82)                   │
│    Fever Duration > 7 days AND Leukocyte Count < 4.5  │
│  ▶ R-009 · Positive (weight: 0.79)                   │
│    Relative Bradycardia AND Fever Duration > 7 days   │
│  ... (expandable accordion)                           │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  FEATURE IMPORTANCE (Random Forest Model)             │
│  ─────────────────────────────────────────────────── │
│  [Horizontal bar chart with Chart.js]                 │
│  Fever Duration     ████████████████████  0.187      │
│  Leukocyte Count    ██████████████████    0.164      │
│  Platelet Count     ████████████████      0.142      │
│  ...                                                  │
└──────────────────────────────────────────────────────┘

[ ← New Diagnosis ]   [ Print Result ]   [ View History ]
```

**Positive result:** Red badge, red confidence bar, header tinted red
**Negative result:** Green badge, green confidence bar, header tinted green
**RF route:** Add amber "⚡ Routed to Machine Learning (uncertain zone)" badge

---

### Admin Rules Page

Table with columns:
- Rule ID | Category (badge: green/red/amber) | Conditions | Outcome | Weight | Status | Actions

Actions per row: [Edit] [Toggle Active/Inactive]

Active rules: normal row. Inactive: `opacity: 0.5; text-decoration: line-through on conditions`

"+ Add New Rule" button top right.

---

## Chart.js Feature Importance Chart Config

```javascript
const ctx = document.getElementById('featureChart').getContext('2d');
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: featureLabels,  // passed from Jinja2 as JSON
    datasets: [{
      data: featureScores,
      backgroundColor: 'rgba(59, 130, 246, 0.7)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 1,
      borderRadius: 4,
    }]
  },
  options: {
    indexAxis: 'y',   // horizontal bars
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => ` ${(ctx.raw * 100).toFixed(1)}%`
        }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.05)' },
        ticks: { color: '#94a3b8', callback: v => `${(v*100).toFixed(0)}%` },
        max: 0.25,
      },
      y: {
        grid: { display: false },
        ticks: { color: '#f1f5f9', font: { size: 12 } }
      }
    }
  }
});
```

Pass data from Flask to template:
```python
# In diagnosis route, before rendering result.html
feature_labels_json = json.dumps(list(result.feature_importances.keys()))
feature_scores_json = json.dumps(list(result.feature_importances.values()))
```

---

## Flash Message Styling

```html
{% for category, message in get_flashed_messages(with_categories=true) %}
<div class="alert alert-{{ category }}">
  {{ message }}
  <button class="alert-close">×</button>
</div>
{% endfor %}
```

CSS:
```css
.alert { padding: 12px 16px; border-radius: var(--radius); margin-bottom: 16px; display: flex; justify-content: space-between; }
.alert-success { background: rgba(34,197,94,0.1); border-left: 4px solid var(--negative); color: #86efac; }
.alert-danger  { background: rgba(239,68,68,0.1); border-left: 4px solid var(--positive); color: #fca5a5; }
.alert-warning { background: rgba(245,158,11,0.1); border-left: 4px solid var(--warning); color: #fcd34d; }
```

---

## Responsive Behaviour

- Sidebar collapses to hamburger menu on screens < 768px
- Form goes single-column on mobile
- Result cards stack vertically on mobile
- Table horizontally scrollable on mobile

# Data dictionary — R replication files

One row per column. Every file is written by `export_data.py` from the committed pipeline outputs; the "constructed by" column names the Python script that builds the variable. No raw CRSP or Compustat fields are included: returns enter only as derived event-level outcomes, and accounting data only as three derived ratios.

Common to all four files:

| Column | Definition | Units | Constructed by |
|---|---|---|---|
| `event_id` | Parent CIK and breach date, e.g. `4904_2018-12-09` (unique within each file) | text | `export_data.py` |
| `parent_cik` | SEC CIK of the parent registrant the event is assigned to. **The cluster variable** for all cluster-robust inference | integer | `scripts/150`–`153` (entity resolution and gates); Essay 3 uses the re-parented CIK from `scripts/214` |
| `fcc_form499` | Treatment: 1 if the breached entity was an FCC Form 499 registrant (a telecommunications carrier subject to 47 CFR 64.2011) at the breach date, else 0 | 0/1 | `scripts/154` |
| `firm_size_log` | Natural log of total assets, from the latest fiscal year ending before the breach | ln($ millions) | `scripts/156` (Essay 3: `scripts/219`) |
| `leverage` | Total liabilities / total assets, same fiscal year | ratio | `scripts/156` (Essay 3: `scripts/219`) |
| `roa` | Net income / total assets, same fiscal year | ratio | `scripts/156` (Essay 3: `scripts/219`) |
| `health_breach` | 1 if the notification record describes health or medical information as affected | 0/1 | `scripts/156` |

## `essay1_car.csv` — Essay 1, N = 340 (106 treated events; 83 parent-CIK clusters, 12 treated)

| Column | Definition | Units | Constructed by |
|---|---|---|---|
| `car_30d` | Cumulative market-adjusted abnormal return: the sum of (daily stock return − CRSP value-weighted market return) over the 31 trading days starting at the trading day nearest the breach date | percentage points | `scripts/155` |
| `immediate_disclosure` | H1: 1 if the public notification came within 7 days of the breach date | 0/1 | `scripts/156` |
| `prior_breaches_1yr` | H3: number of earlier breach events at the same parent CIK in the 365 days before this breach | count | `scripts/156` |
| `fcc_form499`, `health_breach` | H2 and H4 (defined above) | 0/1 | |
| `firm_size_log`, `leverage`, `roa` | Controls (defined above) | | |

Sample: events with CRSP returns and no missing value in the outcome or the seven regressors (`scripts/158`, lines 59–60).

## `essay2_volatility.csv` — Essay 2, N = 333 (104 treated events; 82 clusters, 12 treated)

| Column | Definition | Units | Constructed by |
|---|---|---|---|
| `e2_vol_change` | Outcome: post-window minus pre-window volatility, where each is the standard deviation of daily log returns × 100. Pre-window = trading days −25 to −5, post-window = +5 to +25, relative to the public notification date | daily percentage points | `scripts/163` |
| `disclosure_delay_days` | Outcome: days from the breach date to the public notification date | days | `scripts/156` |
| `delay_w` | `disclosure_delay_days` winsorized at its 99th percentile. Outcome in the winsorized delay model; control in the volatility model | days | `scripts/163` |
| `e2_pre_sd` | Pre-window volatility (the baseline level) | daily percentage points | `scripts/163` |
| `prior_events` | Number of earlier breach events at the same parent CIK (all prior years) | count | `scripts/156`, `scripts/163` |

## `essay2_announcement.csv` — announcement sample, N = 331 (104 treated events; 81 clusters, 12 treated)

The two events missing relative to the 333 are control events at recently listed firms (Uber 2019, Zscaler 2018) with too little return history to estimate a market model.

| Column | Definition | Units | Constructed by |
|---|---|---|---|
| `elev` | Outcome: announcement-window elevation = abnormal volatility over trading days −4 to +4 around notification, minus abnormal volatility over the baseline window −25 to −5. Abnormal volatility is the standard deviation of market-model residuals × 100 | daily percentage points | `scripts/169` (windows), `scripts/175` (difference) |
| `abn_pre` | Baseline-window abnormal volatility (days −25 to −5) | daily percentage points | `scripts/169` |
| `delay_w`, `prior_events` | As in `essay2_volatility.csv` | | |

## `essay3_departures.csv` — Essay 3, N = 405 (109 treated events; 119 clusters, 13 treated)

| Column | Definition | Units | Constructed by |
|---|---|---|---|
| `exec_departure_30_rd`, `_90_rd`, `_180_rd` | Outcome: 1 if the firm disclosed at least one executive departure (Form 8-K Item 5.02, coded by the rule-based classifier, one departure per person) within 30 / 90 / 180 days **after** the public notification date | 0/1 | `scripts/220` (classifier), `scripts/224` |
| `placebo_exec_departure_rd` | Placebo outcome: the same indicator for the 180 days **before** notification | 0/1 | `scripts/224` |
| `prior_breaches_1yr` | Earlier breach events at the same parent CIK in the prior 365 days | count | `scripts/156` |
| `baseline_exec_rate_py_rd` | Executive departures per year in the baseline window, 730 to 181 days before notification | departures per year | `scripts/224` |
| `prior12m_mktadj_ret_rd` | Buy-and-hold stock return minus buy-and-hold market return over the 365 days before notification (at least 150 trading days required) | proportion | `scripts/224` |

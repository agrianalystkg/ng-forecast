# Data

This folder ships the derived outputs and the public inputs needed to read and rebuild the model. It does not ship the licensed futures, Brent or UK gas price masters.

## Where it comes from

| Input | Source | Frequency | Used for | In repo |
|---|---|---|---|---|
| NYMEX NG futures, per contract | Barchart, own account | daily | formation-month price, target and base price | No |
| ICE Brent front month and forward curve | Barchart/ICE, own account | daily | Brent YoY and forward path | No |
| ICE UK NBP front month and forward curve | Barchart/ICE, own account | daily | UK gas YoY and forward path | No |
| EIA weekly Lower-48 storage | [EIA](https://www.eia.gov/naturalgas/storage/) | weekly | storage level and YoY | Yes |
| NOAA temperatures | [NOAA/NCEI](https://www.ncei.noaa.gov/) | daily | GWDD and storage nowcast | Yes |
| EIA monthly supply/demand | [EIA](https://www.eia.gov/naturalgas/data.php) | monthly | storage, production, trade and consumption panel | Yes |

## Point-in-time construction

At a run date `d`:

- monthly fundamentals through **M-2**, released on the last business day of month `M`;
- EIA weekly stocks through the **last Thursday ≤ d**;
- weather through the storage nowcast (weekly splice);
- the **current forward curve** for future formation months;
- prices real-time through `d`, so the twelve-month-ago price is known.

EIA storage is used as currently published: later revisions are not reflected in the signal, so there is a small implicit look-ahead. See the limitations in the top-level README.

## Shipped files

### `ffv_brent_model_diagnostics.csv`

One row per formation month with a realised outcome: **237 rows, 2007-01 to 2026-09**.
`fitted_log_yoy` is always one step ahead.

| Column | Unit | Meaning |
|---|---|---|
| `date` | month | formation month |
| `actual_log_yoy` | log change | realised `log P_F − log P_{F−12}` |
| `fitted_log_yoy` | log change | one-step-ahead forecast of the same quantity |
| `storage_yoy` | log change | `log(Storage_F / Storage_{F−12})` |
| `brent_yoy` | log change | `log(Brent_F / Brent_{F−12})` |
| `log_price_12m_ago` | log level | `log P_{F−12}`, the lagged-price regressor |
| `alpha` | — | intercept used for that month's forecast |
| `beta_storage` | — | storage coefficient used for that month's forecast |
| `beta_brent` | — | Brent coefficient used for that month's forecast |
| `beta_lag` | — | lagged-price coefficient used for that month's forecast |
| `r2_expanding` | 0–1 | cumulative R² from the first forecast (available from 2007-11) |
| `residual` | log change | `actual_log_yoy − fitted_log_yoy` |
| `n_obs` | months | training window length (120) |

The file contains **no price levels in $/MMBtu** and no storage or Brent levels. `log_price_12m_ago` is the model's lagged-price regressor, expressed as a log level. The chart `images/ffv_brent_model.png` is generated from this file alone; the CSV is Brent only.

### `FFV_history_natgas_brent_sim.csv`

Point-in-time fair-value history for the Brent anchor: **117,420 rows, 9,785 run dates, 333 formation months, 2000-01-01 to 2026-10-15**.

| Column | Meaning |
|---|---|
| `run_date` | date the forecast was made |
| `contract_date` | delivery month (formation month + 1) |
| `contract_label` | delivery label, e.g. `FEB/26` |
| `ffv_mid` | fair-value mid, $/MMBtu |
| `ffv_lower` | `mid − MAE`, $/MMBtu |
| `ffv_upper` | `mid + MAE`, $/MMBtu |

### `FFV_history_natgas_ukgas_sim.csv`

The UK gas (NBP) anchor with the same schema: **117,432 rows, 9,786 run dates, 333 formation months**. Same point-in-time logic, with NBP instead of Brent.

The simulation starts in 2000. Before 2007 the 120-month window is not yet full, so it uses all available history; the diagnostics sample starts in 2007, the first month with a full window.

The FFV histories are shipped here for the model; `natgas` keeps a mirror so the FFV backtest remains runnable. This repo is the model's home.

### `gas_snd_monthly.xlsx`

The assembled monthly natural-gas supply/demand panel: **643 rows, 1973-01 to 2026-07, 48 columns**, sheet `data`, first column `date`.

It contains EIA monthly production, consumption, imports, exports and storage series, plus derived totals and balances. Key columns:

| Column group | Examples | Used for |
|---|---|---|
| Storage | `stor_total_us`, `stor_lower48`, regional storage | storage level and YoY |
| Production | `prod_dry`, `prod_dry_est`, `prod_total`, state production | balance forward, nowcast |
| Trade | `imp_total`, `imp_lng`, `imp_pipe_canada`, `exp_total`, `exp_lng` | balance forward |
| Consumption | `cons_total`, `cons_power`, `cons_residential`, `cons_industrial` | balance forward |
| Balances | `total_supply`, `total_demand`, `implied_balance`, `balance_dry` | diagnostics |

**It contains no price columns and nothing licensed.** The panel is derived from public EIA monthly series. The last observation is 2026-07; later formation months are model estimates built from the latest available vintage. A rebuild with this panel therefore reproduces the model through 2026-07; the 2026-08 and 2026-09 diagnostics rows come from the later build vintage.

### `eia_weekly_inventory.xlsx`

The raw EIA weekly Lower-48 storage workbook. The simulation reads the week-ending Friday and the total Lower-48 Bcf column; the raw workbook keeps the EIA layout.

### `us_daily_anomaly.parquet`

Daily US temperature anomaly and gas-weighted degree days: **9,709 rows, 2000-01-01 to 2026-07-31**.

| Column | Meaning |
|---|---|
| `date` | calendar day |
| `wtmean` | population-weighted mean temperature |
| `norm_t` | normal temperature |
| `anom_t` | temperature anomaly |
| `gwdd18` | gas-weighted degree days at 18°C |
| `norm_gwdd` | normal GWDD |
| `gwdd_anom` | GWDD anomaly |

### `wx_monthly_exog.parquet`

Monthly weather regressors: **319 rows, 2000-01 to 2026-07**, columns `gwdd_anom` and `gwcdd_anom`. It is the monthly aggregation of the daily NOAA-derived anomalies and is used by the storage nowcast and the balance forward.

## Not shipped

- `nymex_natgas_master.csv`, `ice_brent_master.csv`, `uk_natural_gas_master.csv` — licensed raw price masters.
- `04d_pooled_yoy_brent_model.xlsx`, `04e_pooled_yoy_ukgas_model.xlsx` — model workbooks. They contain price, storage and Brent levels and are not redistributed.
- `natgas_fundamental_history_*.xlsx` — the wide point-in-time storage history.
- Any trading results or equity curves. Those live in [`natgas`](https://github.com/agrianalystkg/natgas).

## Rebuilding

The public inputs are already in `data/`. The only missing inputs are your own Barchart/ICE price masters.

```bash
pip install -r requirements.txt

# put your price masters under data/raw/ and/or set:
#   NG_PRICES_CSV, BRENT_CSV, UKGAS_CSV
python forecasting/04d_gas_yoy_price_model_brent.py
```

The main run uses `store_coefs=True` and writes `data/ffv_brent_model_diagnostics.csv`. To rebuild the simulations, run `09d` (Brent) or `09e` (UK gas); they use the shipped `gas_snd_monthly.xlsx`, `eia_weekly_inventory.xlsx`, `us_daily_anomaly.parquet` and `wx_monthly_exog.parquet`.

Regenerate the exhibit without any raw data:

```bash
python forecasting/plot_model_diagnostics.py
```

## Licensing

Raw futures and gas price data are downloaded from Barchart/ICE through my own account, subject to their terms, and are not redistributed. Reproducing the model requires your own subscription. EIA storage and NOAA weather data are public. The repo ships derived model diagnostics and point-in-time FFV histories, not the raw price data.

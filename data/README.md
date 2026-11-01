# Data

This folder ships the **derived outputs** needed to read and reproduce the model exhibits. It does not ship the raw futures, Brent, UK gas or storage panels.

## Where it comes from

| Input | Source | Frequency | Used for |
|---|---|---|---|
| NYMEX NG futures, per contract | Barchart, own account | daily | formation-month price, target and base price |
| ICE Brent front month and forward curve | Barchart/ICE, own account | daily | Brent YoY and forward path |
| ICE UK NBP front month and forward curve | Barchart/ICE, own account | daily | UK gas YoY and forward path |
| EIA weekly Lower-48 storage | [EIA](https://www.eia.gov/naturalgas/storage/) | weekly | storage level and YoY |
| NOAA temperatures | [NOAA/NCEI](https://www.ncei.noaa.gov/) | daily | GWDD and storage nowcast |
| Assembled monthly fundamentals | built from the above | monthly | point-in-time storage vintage |

## Point-in-time construction

At a run date `d`:

- monthly fundamentals through **M-2**, released on the last business day of month `M`;
- EIA weekly stocks through the **last Thursday ≤ d**;
- weather through the storage nowcast (weekly splice);
- the **current forward curve** for future formation months;
- prices real-time through `d`, so the twelve-month-ago price is known.

No revisions are applied. EIA storage enters as published at the time, which is a small implicit look-ahead; see the limitations in the top-level README.

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

The file contains **no price levels in $/MMBtu** and no storage or Brent levels. `log_price_12m_ago` is the model's lagged-price regressor, expressed as a log level. The chart `images/ffv_brent_model.png` is generated from this file alone.

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

## Not shipped

- `nymex_natgas_master.csv`, `ice_brent_master.csv`, `uk_natural_gas_master.csv` — licensed raw masters.
- `04d_pooled_yoy_brent_model.xlsx`, `04e_pooled_yoy_ukgas_model.xlsx` — model workbooks. They contain price, storage and Brent levels and are not redistributed.
- `gas_snd_monthly.xlsx` — the assembled monthly fundamentals panel. It is required to rebuild the model and may contain licensed prices.
- `eia_weekly_inventory.xlsx`, `us_daily_anomaly.parquet`, `wx_monthly_exog.parquet` — public source data, but not shipped here; download from EIA and NOAA.
- `natgas_fundamental_history_*.xlsx` — the wide point-in-time storage history.
- Any trading results or equity curves. Those live in [`natgas`](https://github.com/agrianalystkg/natgas).

## Rebuilding

```bash
pip install -r requirements.txt

# raw masters: data/raw/ or NG_PRICES_CSV / BRENT_CSV / UKGAS_CSV
# monthly fundamentals: data/gas_snd_monthly.xlsx, sheet "data",
# monthly index, at least `stor_total_us` (Lower-48 storage, Bcf)
python forecasting/04d_gas_yoy_price_model_brent.py
```

The main run uses `store_coefs=True` and writes `data/ffv_brent_model_diagnostics.csv`. The simulations additionally need:

- `data/eia_weekly_inventory.xlsx`
- `data/us_daily_anomaly.parquet`
- `data/wx_monthly_exog.parquet`
- for the balance forward: `prod_dry`, `imp_total`, `exp_total`, `cons_total` in the fundamentals sheet.

Regenerate the exhibit without any raw data:

```bash
python forecasting/plot_model_diagnostics.py
```

## Licensing

Raw futures and gas price data are downloaded from Barchart/ICE through my own account, subject to their terms, and are not redistributed. Reproducing the model requires your own subscription. EIA storage and NOAA weather data are public. The repo ships derived model diagnostics and point-in-time FFV histories, not the raw price data.

# Model statistics

Derived from the model workbooks and reproduced by `data/ffv_brent_model_diagnostics.csv`. The Brent row is the one shown in the README exhibit.

## Fit

| Metric | Brent | UK gas |
|---|---:|---:|
| Sample | 2007-01 to 2026-09 | 2008-02 to 2026-09 |
| Observations | 237 | 224 |
| R² | 0.685 | 0.723 |
| RMSE (log YoY) | 0.235 | 0.226 |
| MAE (log YoY) | 0.183 | 0.177 |
| Directional accuracy | 81.0 % | 80.8 % |
| Expanding R² range | 0.10–0.90 | 0.39–0.95 |
| Latest expanding R² | 0.71 | 0.75 |

In the `natgas` study the two signals are 0.62 correlated monthly. The UK gas model is the same structure with NBP instead of Brent; it is a second anchor, not an independent edge.

## Brent coefficients

Monthly refits, 2007-01 to 2026-09.

| Coefficient | Mean | Min | Max | 2022-12 | 2026-09 |
|---|---:|---:|---:|---:|---:|
| `alpha` | 0.51 | 0.15 | 0.82 | 0.27 | 0.81 |
| `beta_storage` | −3.07 | −4.47 | −1.20 | −1.20 | −4.35 |
| `beta_brent` | 0.33 | −0.02 | 0.56 | 0.55 | 0.07 |
| `beta_lag` | −0.41 | −0.76 | −0.12 | −0.16 | −0.68 |

The 2022 shift is the main instability: the Brent beta peaked at 0.55 and has since fallen to 0.07, while the storage beta moved from −1.20 to −4.35. The 120-month window reallocates weight slowly.

## Residuals

| Metric | Brent |
|---|---:|
| Mean residual | −0.053 |
| Residual standard deviation | 0.230 |
| Largest absolute residual | 0.77 |

The negative mean residual is a small optimistic bias. It is not large relative to the residual spread, but it is reported rather than hidden.

## FFV band

The band is `mid ± MAE`, where `MAE` is the mean absolute error of the price-level prediction on all history available at the run date. Across the point-in-time history the band averages about 50 % of the mid, or roughly ±25 %.

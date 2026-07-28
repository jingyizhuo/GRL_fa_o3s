# Mean-state dependence of the Pacific response to Antarctic ozone depletion

Data and plotting code for Figures 1–4 of

> Zhuo et al., *Muted eastern Pacific cooling response to stratospheric ozone depletion linked to double-ITCZ bias*, submitted to **Geophysical Research Letters**.

Every script is self-contained: it reads only the small NetCDF files under
`data/` and writes a PNG to `figures/`. No access to the raw model output is
required.

## Quick start

```bash
pip install -r requirements.txt
python plot_fig1.py     # -> figures/fig1.png
python plot_fig2.py     # -> figures/fig2.png
python plot_fig3.py     # -> figures/fig3.png
python plot_fig4.py     # -> figures/fig4.png
```

## Experiments

| Name | Description |
|---|---|
| CESM2 | CESM2 as released (large double-ITCZ / equatorial cold-tongue bias) |
| CESM2-FA | CESM2 with flux adjustment, which strongly reduces the tropical mean-state bias |
| hist-o3s | Ozone-only historical experiment, 1950–2021, 9 members (`r1i2, r2i2, r3i2, r4i2, r5i2, r7i2, r8i2, r9i2, r11i2`); all quantities below are ensemble means |
| B1850 | Pre-industrial control, used for the climatological mean state (model years 0051–0150) |

Trends are reported as the **total change over the period**, i.e.
`slope × (N_years − 1)`, unless a variable's `units` attribute says otherwise.

## Repository layout

```
data/
  fig1/  trend_{cesm2,cesm2fa}_{1960-2000,2001-2021}.nc   SST/MSLP/wind-stress trends
         ocean_fraction.nc                                land–sea mask for the vectors
  fig2/  ozone_tco_anom_90S-60S.nc                        SON and annual TCO anomaly
         sam_index_annual.nc                              annual SAM index, ens. mean ± SE
         hov_ep_{cesm2,cesm2fa}_1950-2021.nc              220–290°E zonal-mean anomalies
  fig3/  sst_budget_domain_ens_1960-2000.nc               budget terms, ens. mean ± SE
  fig4/  cesm2_forced_trend_diff_1960-2000.nc             CESM2-FA − CESM2 SST/Z200 trends
         cesm2_picontrol_clim_diff.nc                     CESM2-FA − CESM2 mean state
         amip_minus_cmip6hist_1980-2014.nc                AMIP − CMIP6-hist MMM
plot_fig1.py … plot_fig4.py
figures/
```

Only the fields that the figures actually draw are stored, already reduced to
the plotted region, season and averaging (ensemble means and standard errors
rather than individual members); the full model output is not included, so
`data/` is only ≈ 1.2 MB. `prep/make_data.py` documents how every file in
`data/` was derived from the raw model output — it is for reference only and is
not needed to reproduce the figures.

## Figure-by-figure notes

**Figure 1** — Ensemble-mean linear trends in SST (shading), MSLP (contours) and
surface wind stress (vectors) for 1960–2000 and 2001–2021. `trend_TAUX` and
`trend_TAUY` follow the surface wind-stress convention (sign flipped relative to
the raw CESM output). Fields are stored for 90°S–21°N.

**Figure 2** — (a) Total column ozone anomaly averaged 90°S–60°S (cos-lat
weighted) from the CMIP6 ozone forcing dataset
(`ozone_strataero_WACCM_L70_zm5day_18500101-20150103_CMIP6ensAvg_c180923.nc`),
relative to the 1955–1970 climatology; SON and annual mean. (b) Annual SAM index
= zonal-mean MSLP at 45°S minus 60°S (nearest CESM2 grid latitudes), ensemble
mean with the standard error over the 9 members. (c, d) Hovmöller diagrams:
annual anomalies (relative to the 1955–1970 monthly climatology) zonally
averaged over 220–290°E, 75°S–15°N. The stored fields are annual means; the
10-year centred rolling mean shown in the paper is applied inside
`plot_fig2.py`.

**Figure 3** — Surface energy budget decomposition of the ozone-forced SST trend
(1960–2000), cos(lat)-weighted over three domains:

| Domain | Polygon |
|---|---|
| EEP | 180–280°E, 5°S–5°N |
| SEP | (180, −5) (290, −5) (290, −40) (270, −40) |
| SPP | 180–290°E, 70°S–45°S |

The decomposition follows `ΔSST_X = ∓ΔF_X / (α·LH̄)` with `α = 0.06 K⁻¹`:
`dSST` total SST trend; `dSST_SW`, `dSST_LW`, `dSST_SH` shortwave, longwave and
sensible-heat contributions; `dSST_LH` the latent-heat contribution from wind
and humidity changes with the Newtonian damping term removed; `dSST_OHC` ocean
heat uptake plus residual. The file holds the 9-member ensemble mean and the
standard error of the mean (σ/√N), which is what the bars and error bars show.

**Figure 4** — (a–c) CESM2-FA minus CESM2: ozone-forced SST and Z200 trends
(1960–2000, hist-o3s) and the pre-industrial control climatological differences
in precipitation and MSLP, with the Z200 climatological difference in contours.
(d–f) The same quantities for the CMIP6 multi-model mean, AMIP minus
CMIP6-historical over 1980–2014 (member `r1i1p1f1`, Amon, regridded to a common
2.5° grid; 26 models for SST/precipitation/Z200 and 28 for MSLP — the model
lists are stored in the file's global attributes). Source: the
[Pangeo CMIP6 cloud catalog](https://storage.googleapis.com/cmip6/pangeo-cmip6.json).
Fields are cropped to 105–305°E, 90°S–25°N. The dashed arrows and the
`SPSH+` / `ASL-` labels are schematic annotations of the stationary-wave train
discussed in the text, not derived quantities.

## Requirements

Python ≥ 3.9 with `numpy`, `pandas`, `scipy`, `xarray`, `netCDF4`,
`matplotlib`, `cartopy` and `cmaps` (NCL colour tables). See
`requirements.txt`.

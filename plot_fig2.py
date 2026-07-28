#!/usr/bin/env python
"""
Figure 2 — (a) Column-integrated stratospheric ozone anomaly south of 60°S for
SON (purple) and the annual mean (black); (b) annual SAM index; (c, d)
Hovmoller diagrams of zonally averaged SST (shading), surface wind stress
(vectors) and sea level pressure (contours) over the eastern Pacific-Southern
Ocean sector (220-290°E, 15°N-75°S) for CESM2-FA (c) and CESM2 (d).
All Hovmoller fields are shown as 10-year rolling means.

Input : data/fig2/ozone_tco_anom_90S-60S.nc
        data/fig2/sam_index_annual.nc
        data/fig2/hov_ep_{model}_1950-2021.nc
Output: figures/fig2.png
"""
import warnings; warnings.filterwarnings('ignore')
import os

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from scipy import stats
import cmaps

HERE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(HERE, 'data', 'fig2')
OUTDIR  = os.path.join(HERE, 'figures')
os.makedirs(OUTDIR, exist_ok=True)

N_ROLL_YEAR = 10          # rolling window applied to the Hovmoller panels
COLOR_FA    = '#2878B5'
COLOR_CESM  = '#C44E52'

# ── Load ────────────────────────────────────────────────────────────────────
oz = xr.open_dataset(f'{DATADIR}/ozone_tco_anom_90S-60S.nc')
yr_oz  = oz.year.values.astype(float)
oz_son = oz.TCO_son_anom.values
oz_ann = oz.TCO_ann_anom.values

sam = xr.open_dataset(f'{DATADIR}/sam_index_annual.nc')
yr_sam   = sam.year.values.astype(float)
sam_fa,  se_fa  = sam.sam_cesm2fa.values, sam.sam_cesm2fa_se.values
sam_esm, se_esm = sam.sam_cesm2.values,   sam.sam_cesm2_se.values

def load_hov(model):
    ds = xr.open_dataset(f'{DATADIR}/hov_ep_{model}_1950-2021.nc')
    return ds.rolling(time=N_ROLL_YEAR, center=True).mean()

da_fa  = load_hov('cesm2fa')
da_esm = load_hov('cesm2')

# ── Shared plot settings ────────────────────────────────────────────────────
var_cf_label = 'SST Anomaly [K]'
var_cf_vmax  = 0.4
var_cf_ticks = np.arange(-var_cf_vmax, var_cf_vmax + 0.2, 0.2)
cmap         = cmaps.BlueWhiteOrangeRed
psl_levels   = np.arange(-2, 1.4, 0.2)
psl_colors   = ['b' if l < -1e-5 else 'r' for l in psl_levels]

fig = plt.figure(figsize=(18.5, 9))
gs  = gridspec.GridSpec(2, 2, height_ratios=[1, 2.5], hspace=0.35, wspace=0.1)

ax_oz  = fig.add_subplot(gs[0, 0])
ax_sam = fig.add_subplot(gs[0, 1], sharex=ax_oz)
ax_fa  = fig.add_subplot(gs[1, 0], sharex=ax_oz)
ax_esm = fig.add_subplot(gs[1, 1], sharex=ax_oz, sharey=ax_fa)

# ── Panel (a): Southern Ocean total column ozone ────────────────────────────
oz_son_sm = pd.Series(oz_son, index=yr_oz).rolling(5, center=True, min_periods=1).mean().values
oz_ann_sm = pd.Series(oz_ann, index=yr_oz).rolling(5, center=True, min_periods=1).mean().values
ax_oz.fill_between(yr_oz, oz_ann, alpha=0.15, color='gray', linewidth=0)
ax_oz.plot(yr_oz, oz_ann_sm, color='k', lw=2.0, label='ANN')
ax_oz.fill_between(yr_oz, oz_son, alpha=0.20, color='#8E7AB5', linewidth=0)
ax_oz.plot(yr_oz, oz_son_sm, color='#8E7AB5', lw=2.0, label='SON')
ax_oz.axhline(0, color='k', lw=0.6)
ax_oz.set_ylabel('TCO anom. (DU)', fontsize=11)
ax_oz.set_title(r'$\mathbf{(a)}$  SO O3S (90°S–60°S)', loc='left', fontsize=14, pad=5)
ax_oz.legend(fontsize=10, frameon=False, loc='lower left',
             handlelength=1.5, labelspacing=0.3)
ax_oz.spines[['top', 'right']].set_visible(False)
ax_oz.tick_params(axis='y', labelsize=10)

# ── Panel (b): SAM index with piecewise linear trends ───────────────────────
ax_sam.fill_between(yr_sam, sam_fa - se_fa, sam_fa + se_fa,
                    color=COLOR_FA, alpha=0.20, linewidth=0)
ax_sam.fill_between(yr_sam, sam_esm - se_esm, sam_esm + se_esm,
                    color=COLOR_CESM, alpha=0.20, linewidth=0)
ax_sam.plot(yr_sam, sam_fa,  color=COLOR_FA,   lw=2.0, label='CESM2-FA')
ax_sam.plot(yr_sam, sam_esm, color=COLOR_CESM, lw=2.0, label='CESM2')

def lintrend(yrs, vals, y0, y1):
    sel = (yrs >= y0) & (yrs <= y1)
    x, y = yrs[sel], vals[sel]
    slope, icpt, *_ = stats.linregress(x, y)
    return x, slope * x + icpt

for ts, color in [(sam_fa, COLOR_FA), (sam_esm, COLOR_CESM)]:
    for p0, p1 in [(1960, 2000), (2001, 2021)]:
        xf, yf = lintrend(yr_sam, ts, p0, p1)
        ax_sam.plot(xf, yf, '--', color=color, lw=1.8)

ax_sam.set_ylabel('SAM Index (hPa)', fontsize=11)
ax_sam.set_title(r'$\mathbf{(b)}$  SAM Index (ANN, ensemble mean ± SE)',
                 loc='left', fontsize=14, pad=5)
ax_sam.legend(fontsize=10, loc='upper left', frameon=False,
              handlelength=1.5, labelspacing=0.3)
ax_sam.spines[['top', 'right']].set_visible(False)
ax_sam.tick_params(axis='y', labelsize=10)

# ── Panels (c, d): Hovmoller diagrams ───────────────────────────────────────
def lat_fmt(x, pos):
    if x > 0:
        return f'{abs(x):g}°N'
    if x < 0:
        return f'{abs(x):g}°S'
    return 'EQ'

cf_ref, Q_ref = None, None

for da, mdl, lbl, ax in [(da_fa,  'CESM2-FA', 'c', ax_fa),
                         (da_esm, 'CESM2',    'd', ax_esm)]:
    t_hov   = np.array([float(t.year) for t in da.time.values])
    lat_hov = da.lat.values

    cf = ax.contourf(t_hov, lat_hov, da.SST.values.T,
                     levels=np.linspace(-var_cf_vmax, var_cf_vmax, 19),
                     cmap=cmap, vmax=var_cf_vmax, vmin=-var_cf_vmax,
                     extend='neither')
    if cf_ref is None:
        cf_ref = cf

    cl = ax.contour(t_hov, lat_hov, da.PSL.values.T,
                    colors=psl_colors, levels=psl_levels, linewidths=0.8)
    ax.clabel(cl, inline=True, fontsize=8, fmt='%.1f')

    taux, tauy = da.TAUX.values, da.TAUY.values
    hi_idx = np.where(lat_hov <= -40)[0]
    lo_idx = np.where(lat_hov >  -44)[0]

    ax.quiver(t_hov[::6], lat_hov[hi_idx[::3]],
              taux[::6][:, hi_idx[::3]].T, tauy[::6][:, hi_idx[::3]].T,
              pivot='middle', scale=0.048, width=0.004, color='k')
    Q = ax.quiver(t_hov[::4], lat_hov[lo_idx[::3]],
                  taux[::4][:, lo_idx[::3]].T, tauy[::4][:, lo_idx[::3]].T,
                  pivot='middle', scale=0.048, width=0.004, color='k')
    if Q_ref is None:
        Q_ref = Q

    ax.set_ylim(-70, 15)
    ax.set_yticks([-60, -40, -20, 0])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lat_fmt))
    ax.grid(True, linestyle='--', color='k', lw=0.4, alpha=0.4)
    ax.axhline(0, color='grey', ls='--', lw=1)
    ax.set_xlabel('Year', fontsize=12)
    ax.tick_params(axis='both', labelsize=11)
    ax.set_title(rf'$\mathbf{{({lbl})}}$  {mdl}', loc='left', fontsize=14, pad=5)

ax_fa.set_ylabel('Latitude', fontsize=11)
ax_esm.tick_params(axis='y', labelleft=False)
ax_esm.set_ylabel('')

ax_fa.quiverkey(Q_ref, X=0.88, Y=1.08, U=0.005, label='0.005 N/m²',
                labelpos='E', coordinates='axes', fontproperties={'size': 11})

for ax in [ax_oz, ax_sam]:
    plt.setp(ax.get_xticklabels(), visible=False)
ax_oz.set_xlim(1955, 2016)

# ── Colorbar (placed manually so wspace does not distort it) ────────────────
fig.subplots_adjust(right=0.88)
fig.canvas.draw()
pos  = ax_esm.get_position()
cax  = fig.add_axes([pos.x1 + 0.015, pos.y0, 0.018, pos.height])
cbar = fig.colorbar(cf_ref, cax=cax, orientation='vertical', ticks=var_cf_ticks)
cbar.ax.minorticks_off()
cbar.set_label(var_cf_label, fontsize=14)
cbar.set_ticks([-0.4, -0.2, 0, 0.2, 0.4])
cbar.ax.tick_params(labelsize=12, length=3)

figname = os.path.join(OUTDIR, 'fig2.png')
plt.savefig(figname, dpi=500, bbox_inches='tight')
print(f'Saved: {figname}')

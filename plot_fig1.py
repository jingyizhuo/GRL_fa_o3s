#!/usr/bin/env python
"""
Figure 1 — Linear trends in SST (shading), MSLP (contours) and surface wind
stress (vectors) during the ozone depletion period (1960-2000; a, b) and the
ozone stabilization and recovery period (2001-2021; c, d), for CESM2-FA (a, c)
and CESM2 (b, d).  All fields are 9-member ensemble means of the hist-o3s
(ozone-only) experiments.

Input : data/fig1/trend_{model}_{period}.nc, data/fig1/ocean_fraction.nc
Output: figures/fig1.png
"""
import warnings; warnings.filterwarnings('ignore')
import os

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmaps

HERE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(HERE, 'data', 'fig1')
OUTDIR  = os.path.join(HERE, 'figures')
os.makedirs(OUTDIR, exist_ok=True)

# ── Load ────────────────────────────────────────────────────────────────────
periods = [
    ('1960-2000', '1960–2000 (Ozone depletion)'),
    ('2001-2021', '2001–2021 (Ozone stabilization)'),
]
models        = ['cesm2fa', 'cesm2']
model_display = {'cesm2fa': 'CESM2–FA', 'cesm2': 'CESM2'}

trend = {(m, p): xr.open_dataset(f'{DATADIR}/trend_{m}_{p}.nc')
         for m in models for p, _ in periods}
mask  = xr.open_dataset(f'{DATADIR}/ocean_fraction.nc')['OCNFRAC'] > 0

# ── Plot settings ───────────────────────────────────────────────────────────
plt.rcParams['hatch.linewidth'] = 0.5
plt.rcParams['hatch.color']     = '0.3'

proj    = ccrs.EckertIV(central_longitude=180)
vmax    = 0.5
sst_lev = np.linspace(-vmax, vmax, 21)
psl_lev = np.arange(-2, 1.4, 0.2)
psl_col = ['b' if l < -1e-5 else 'r' for l in psl_lev]

# a/b = left column (CESM2-FA), c/d = right column (CESM2)
# a/c = top row (1960-2000),    b/d = bottom row (2001-2021)
panels = [
    ((0, 0), 'a', 0, 'cesm2fa'),
    ((1, 0), 'b', 1, 'cesm2fa'),
    ((0, 1), 'c', 0, 'cesm2'),
    ((1, 1), 'd', 1, 'cesm2'),
]

fig = plt.figure(figsize=(13, 6), dpi=150)
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.1, wspace=0.05)

pcm_ref, q_ref, last_ax = None, None, None

for (row, col), label, pi, mkey in panels:
    period, period_str = periods[pi]
    ax = fig.add_subplot(gs[row, col], projection=proj)
    da = trend[(mkey, period)]

    # SST shading
    pcm = da['trend_SST'].plot(
        ax=ax, transform=ccrs.PlateCarree(),
        levels=sst_lev, cmap=cmaps.BlueWhiteOrangeRed,
        extend='both', add_colorbar=False, zorder=1,
    )
    if pcm_ref is None:
        pcm_ref = pcm

    # Wind-stress vectors — coarser subsampling at high latitudes
    da_south = da.where(mask).sel(lat=slice(-90, -40), lon=slice(None, None, 11))
    da_south = da_south.sel(lat=slice(None, None, 4))
    da_north = da.where(mask).sel(lat=slice(-39, 21), lon=slice(None, None, 6))
    da_north = da_north.sel(lat=slice(None, None, 3))
    for da_q in [da_south, da_north]:
        q = ax.quiver(
            da_q.lon.values, da_q.lat.values,
            da_q['trend_TAUX'].values, da_q['trend_TAUY'].values,
            transform=ccrs.PlateCarree(), color='k',
            width=0.0033, headwidth=5, headlength=3, headaxislength=2.5,
            scale=0.12, zorder=7,
        )
    q_ref = q

    # MSLP contours (blue = negative, red = positive)
    cl = da['trend_PSL'].plot.contour(
        ax=ax, transform=ccrs.PlateCarree(),
        levels=psl_lev, colors=psl_col,
        linewidths=1.2, alpha=0.6, add_colorbar=False, zorder=6,
    )
    ax.clabel(cl, inline=True, fontsize=5, fmt='%.1f', use_clabeltext=True)

    # Map decorations
    ax.coastlines(linewidth=0.8, color='0.3', zorder=5)
    ax.add_feature(cfeature.LAND, facecolor='0.92', zorder=5)
    ax.set_extent([0, 360, -90, 20.1], ccrs.PlateCarree())

    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color='gray',
                      alpha=0.7, linestyle='--', zorder=5)
    gl.top_labels    = False
    gl.right_labels  = False
    gl.left_labels   = (col == 0)
    gl.bottom_labels = (row == 1)
    gl.xlabel_style  = {'size': 7}
    gl.ylabel_style  = {'size': 7}
    gl.xlocator = plt.FixedLocator(np.arange(-180, 181, 60))
    gl.ylocator = plt.FixedLocator(np.arange(-80, 81, 20))

    mid_disp = model_display[mkey]
    ax.set_title(rf'$\mathbf{{({label})}}$ {period_str},   '
                 rf'$\it{{{mid_disp.replace("-", "")}}}$',
                 loc='left', fontsize=14, pad=3)
    last_ax = ax

# Quiver key below panel (d)
last_ax.quiverkey(q_ref, X=0.8, Y=-0.15, U=0.01,
                  label='0.01 N/m²', labelpos='E',
                  fontproperties={'size': 11})

# Shared colorbar
cbar_ax = fig.add_axes([0.35, 0.04, 0.3, 0.03])
cbar = fig.colorbar(pcm_ref, cax=cbar_ax, orientation='horizontal',
                    extendfrac='auto')
cbar.set_ticks([-0.5, -0.25, 0, 0.25, 0.5])
cbar.set_label('SST trend [K]', fontsize=11)
cbar.ax.tick_params(labelsize=9, length=3)

figname = os.path.join(OUTDIR, 'fig1.png')
plt.savefig(figname, dpi=300, bbox_inches='tight')
print(f'Saved: {figname}')

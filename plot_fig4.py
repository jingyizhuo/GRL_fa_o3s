#!/usr/bin/env python
"""
Figure 4 — Differences in forced responses and climatological mean states
associated with tropical mean-state biases.

(a) Ozone-forced SST trends (shading) and Z200 trends (contours), CESM2-FA
    minus CESM2 (hist-o3s, 1960-2000);
(b, c) their pre-industrial control climatological mean-state differences in
    precipitation and MSLP (contours: Z200 climatology difference);
(d-f) as (a-c) but for the CMIP6 multi-model mean over the historical period
    (1980-2014), AMIP minus CMIP6-historical.

Z200 contours: royalblue = negative, firebrick = positive, zero line omitted.
The dashed arrows and the SPSH+/ASL- labels are schematic annotations
highlighting the stationary-wave train discussed in the text.

Input : data/fig4/cesm2_forced_trend_diff_1960-2000.nc
        data/fig4/cesm2_picontrol_clim_diff.nc
        data/fig4/amip_minus_cmip6hist_1980-2014.nc
Output: figures/fig4.png
"""
import warnings; warnings.filterwarnings('ignore')
import os

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmaps

HERE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(HERE, 'data', 'fig4')
OUTDIR  = os.path.join(HERE, 'figures')
os.makedirs(OUTDIR, exist_ok=True)

# ── Load ────────────────────────────────────────────────────────────────────
tr   = xr.open_dataset(f'{DATADIR}/cesm2_forced_trend_diff_1960-2000.nc')
clim = xr.open_dataset(f'{DATADIR}/cesm2_picontrol_clim_diff.nc')
amip = xr.open_dataset(f'{DATADIR}/amip_minus_cmip6hist_1980-2014.nc')

# ── Panel definitions: (shading, contour, cmap, |shading| limit, cbar ticks,
#                       Z200 contour interval, Z200 contour range) ───────────
panels = [
    # row 1 — CESM2-FA minus CESM2
    dict(label='a', shade=tr.SST_trend_diff,     cont=tr.Z200_trend_diff,
         cmap=cmaps.BlueWhiteOrangeRed, vlim=0.6,  zstep=5, zmax=56),
    dict(label='b', shade=clim.PRECT_clim_diff,  cont=clim.Z200_clim_diff,
         cmap=cmaps.MPL_BrBG,           vlim=3.5,  zstep=6, zmax=56),
    dict(label='c', shade=clim.PSL_clim_diff,    cont=clim.Z200_clim_diff,
         cmap=cmaps.MPL_PuOr_r,         vlim=3.0,  zstep=6, zmax=56),
    # row 2 — AMIP minus CMIP6-historical
    dict(label='d', shade=amip.SST_trend_diff,   cont=amip.Z200_trend_diff,
         cmap=cmaps.BlueWhiteOrangeRed, vlim=0.6,  zstep=3, zmax=50),
    dict(label='e', shade=amip.PR_clim_diff,     cont=amip.Z200_clim_diff,
         cmap=cmaps.MPL_BrBG,           vlim=3.5,  zstep=6, zmax=56),
    dict(label='f', shade=amip.PSL_clim_diff,    cont=amip.Z200_clim_diff,
         cmap=cmaps.MPL_PuOr_r,         vlim=3.0,  zstep=6, zmax=56),
]

col_cbar = [
    ('SST Trend Diff. (K)',                np.arange(-0.5, 0.51, 0.25)),
    ('Precipitation Clim. Diff. (mm/day)', np.arange(-3, 4, 1)),
    ('MSLP Clim. Diff. (hPa)',             np.arange(-3, 4, 1)),
]
row_label = ['CESM2-FA $-$ CESM2', 'AMIP $-$ CMIP']

proj  = ccrs.PlateCarree(central_longitude=180)
trans = ccrs.PlateCarree()

fig, axes = plt.subplots(2, 3, figsize=(19, 7),
                         subplot_kw={'projection': proj})
fig.subplots_adjust(hspace=0.12, wspace=0.08, bottom=0.16, top=0.95)

cf_col = [None, None, None]

for i, p in enumerate(panels):
    row, col = divmod(i, 3)
    ax = axes[row, col]

    levs = np.linspace(-p['vlim'], p['vlim'], 21)
    cf = ax.contourf(p['shade'].lon, p['shade'].lat, p['shade'].values,
                     levels=levs, cmap=p['cmap'], transform=trans, extend='both')
    if cf_col[col] is None:
        cf_col[col] = cf

    levs_z = np.arange(-p['zmax'], p['zmax'] + p['zstep'], p['zstep'])
    levs_z = levs_z[levs_z != 0]
    ax.contour(p['cont'].lon, p['cont'].lat, p['cont'].values,
               levels=levs_z,
               colors=['royalblue' if l < 0 else 'firebrick' for l in levs_z],
               linewidths=1.2, transform=trans, zorder=3)

    ax.coastlines(linewidth=0.8, color='0.3', zorder=2)
    ax.add_feature(cfeature.LAND, facecolor='1', zorder=1)
    ax.set_extent([110, 300.1, -90, 20.1], crs=trans)

    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color='gray',
                      alpha=0.5, linestyle='--',
                      xlocs=range(-180, 181, 60), ylocs=[-60, -30, 0],
                      zorder=4)
    gl.top_labels    = False
    gl.right_labels  = False
    gl.left_labels   = (col == 0)
    gl.bottom_labels = (row == 1)
    gl.xlabel_style   = {'size': 9, 'color': '0.3'}
    gl.ylabel_style   = {'size': 9, 'color': '0.3'}

    ax.set_title(rf'$\mathbf{{({p["label"]})}}$', loc='left', fontsize=14, pad=4)

    # schematic wave-train arrow
    ax.annotate('', xy=(250, -58), xytext=(213, -14), xycoords=trans._as_mpl_transform(ax),
                textcoords=trans._as_mpl_transform(ax),
                arrowprops=dict(arrowstyle='-|>', linestyle='--', linewidth=2.2,
                                color='k', connectionstyle='arc3,rad=0.25',
                                mutation_scale=22), zorder=6)

    if col == 2:   # MSLP panels: label the two centres of action
        for lon_t, lat_t, txt in [(244, -32, 'SPSH+'), (252, -60, 'ASL-')]:
            ax.text(lon_t, lat_t, txt, transform=trans, fontsize=13, color='w',
                    fontweight='bold', ha='left', va='center', zorder=7,
                    path_effects=[pe.withStroke(linewidth=2, foreground='0.25')])

    if col == 0:   # row label
        ax.text(-0.12, 0.5, row_label[row], transform=ax.transAxes,
                rotation='vertical', va='center', ha='center',
                fontsize=14, fontweight='bold')

# ── one horizontal colorbar per column ──────────────────────────────────────
for col, (label, ticks) in enumerate(col_cbar):
    pos = axes[1, col].get_position()
    cax = fig.add_axes([pos.x0 + 0.02, 0.07, pos.width - 0.04, 0.025])
    cb  = fig.colorbar(cf_col[col], cax=cax, orientation='horizontal', ticks=ticks)
    cb.set_label(label, size=11, color='0.2')
    cb.ax.tick_params(labelsize=9, color='0.2', labelcolor='0.2')

figname = os.path.join(OUTDIR, 'fig4.png')
plt.savefig(figname, dpi=300, bbox_inches='tight')
print(f'Saved: {figname}')

#!/usr/bin/env python
"""
Figure 3 — Regional decomposition of the ozone-forced SST trend (1960-2000)
into surface energy budget terms for CESM2-FA (blue) and CESM2 (red) over the
EEP (a), SEP (b) and SPP (c) domains.  Bars show the 9-member ensemble mean;
error bars denote ±1 standard error of the mean.

Input : data/fig3/sst_budget_domain_ens_1960-2000.nc
Output: figures/fig3.png
"""
import warnings; warnings.filterwarnings('ignore')
import os

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

HERE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(HERE, 'data', 'fig3')
OUTDIR  = os.path.join(HERE, 'figures')
os.makedirs(OUTDIR, exist_ok=True)

Y0, YE = 1960, 2000

bud = xr.open_dataset(f'{DATADIR}/sst_budget_domain_ens_{Y0}-{YE}.nc')

bar_labels = [r'$\Delta$SST', r'$\Delta$SST_SW', r'$\Delta$SST_LH$_{\rm wind}$',
              r'$\Delta$SST_LW', r'$\Delta$SST_SH', r'$\Delta$SST_OHC\RSD']
term_order = ['dSST', 'dSST_SW', 'dSST_LH', 'dSST_LW', 'dSST_SH', 'dSST_OHC']
domains    = ['EEP', 'SEP', 'SPP']

# seaborn "muted" palette entries 0 (blue) and 3 (red), hard-coded so that
# seaborn is not a required dependency
COLOR_FA  = (0.2823529411764706, 0.47058823529411764, 0.8156862745098039)
COLOR_ESM = (0.8392156862745098, 0.37254901960784315, 0.37254901960784315)

x     = np.arange(len(term_order))
width = 0.35
panel_abc = list('abc')

fig, axes = plt.subplots(3, 1, figsize=(9, 9), sharex=True, sharey=True)
fig.subplots_adjust(hspace=0.15, left=0.15)

for ai, dname in enumerate(domains):
    ax = axes[ai]

    sel = dict(domain=dname, term=term_order)
    vals_fa  = bud.ens_mean.sel(model='cesm2fa', **sel).values
    vals_esm = bud.ens_mean.sel(model='cesm2',   **sel).values
    se_fa    = bud.ens_se.sel(model='cesm2fa',   **sel).values
    se_esm   = bud.ens_se.sel(model='cesm2',     **sel).values

    ax.bar(x - width / 2, vals_fa, width, label='CESM2-FA',
           color=COLOR_FA, edgecolor='white', linewidth=0.5)
    ax.bar(x + width / 2, vals_esm, width, label='CESM2',
           color=COLOR_ESM, edgecolor='white', linewidth=0.5)

    ax.errorbar(x - width / 2, vals_fa, yerr=se_fa, fmt='none',
                ecolor='#1a3a5c', capsize=3, capthick=1.2, elinewidth=1.2, zorder=5)
    ax.errorbar(x + width / 2, vals_esm, yerr=se_esm, fmt='none',
                ecolor='#7a1f22', capsize=3, capthick=1.2, elinewidth=1.2, zorder=5)

    ax.axhline(0, color='k', linewidth=0.8)
    ax.axvline(x=0.5, color='0.4', linewidth=1.0, linestyle='--', zorder=3)

    ax.set_title(rf'$\mathbf{{({panel_abc[ai]})}}$  {dname}', loc='left', fontsize=12)
    ax.tick_params(labelsize=11)
    if ai == 0:
        ax.legend(fontsize=11, loc='upper right', framealpha=0.8,
                  edgecolor='0.8', fancybox=False)
    ax.grid(axis='y', linewidth=0.4, alpha=0.5, linestyle='--', color='gray')
    ax.spines[['top', 'right']].set_visible(False)

fig.text(0.08, 0.5, r'$\Delta$SST [K]', va='center', ha='center',
         rotation='vertical', fontsize=11)

axes[-1].set_xticks(x)
axes[-1].set_xticklabels(bar_labels, fontsize=10)

figname = os.path.join(OUTDIR, 'fig3.png')
plt.savefig(figname, dpi=300, bbox_inches='tight')
print(f'Saved: {figname}')

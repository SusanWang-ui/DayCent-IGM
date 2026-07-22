#import spotpy 
import os, sys
#import pandas as pd
#import numpy as np
import subprocess
import multiprocessing
#import shutil
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(1, r'D:\comet-farm-daycent-model-source-code-main\Test with exp sites')

from daycentpy import handler
from daycentpy import modules, analyzer

if __name__ == '__main__':
    pwd = os.path.join(r'D:\comet-farm-daycent-model-source-code-main\Test with exp sites', "mt")
    md = os.path.join(r'D:\comet-farm-daycent-model-source-code-main\Test with exp sites', "DayCent_data")
    m1 = handler.MultiInit(pwd, md, overwrite=False)    
   #m1 = handler.MultiInit(pwd, md, overwrite=True)
    sel_pars_df = m1.read_sel_dc_pars() 
    df = m1.all_sim_obd_PBAIS()
    sites = df.site_name.unique()
    for st in sites:  # run all sites
        print(st)
        swd = os.path.join(pwd, "multi_main", st)
        obd = df.loc[df["site_name"] == st, "obd"].tolist()
        # modules.run_fast(swd, obd, sel_pars_df, 5000, dbname="sa", parallel="mpc" ) # Better to run at least 3000 or 5000 repetitions

    # if run for individual site (e.g., added a new site), using the following, otherwise using the above for all sites
    #swd = os.path.join(pwd, "multi_main", 'Ceplac')
    #obd = df.loc[df["site_name"] == 'Ceplac', "obd"].tolist()
    # modules.run_fast(swd, obd, sel_pars_df, 5000, dbname="sa", parallel="mpc" )

    # gather all outputs
    all_sa_rs = m1.all_s1_st(sel_pars_df.name.tolist())
    # # plot KDE for senstivity analysis
    # analyzer.plot_senstivity_KDE(all_sa_rs, num_sen_pars=10, sen_type='ST') # here we can change the numebr of sen pars -> num_sen_pars
    # # draw scatter plot for senstivity analysis
    # analyzer.plot_sensitivity_scatter(all_sa_rs, size=30, alpha=0.7, sen_type='ST', numcols=2)
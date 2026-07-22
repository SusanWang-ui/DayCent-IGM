import os, sys
from spotpy.likelihoods import gaussianLikelihoodMeasErrorOut as GausianLike

sys.path.insert(1, r'D:\comet-farm-daycent-model-source-code-main\Test with exp sites')
from daycentpy import handler
from daycentpy import modules, analyzer

pwd = r'D:\comet-farm-daycent-model-source-code-main\Test with exp sites\mt'
md = r"D:\comet-farm-daycent-model-source-code-main\Test with exp sites\DayCent_data"

if __name__ == '__main__':
    # this creates m1
    # handler object
    m1 = handler.MultiInit(pwd, md, overwrite=False)
    #m1 = handler.MultiInit(pwd, md, overwrite=True)

    # this reads selected_pars.csv, and this
    # also creates daycent_pars.csv from 
    # daycentpy\database
    sel_pars_df = m1.read_sel_dc_pars()
    # print(sel_pars_df)

    # this is to run the models;
    # same thing that is done by Notebook 2.
    # No need to rerun if the sites are run before
    #m1.init_run()
    df = m1.all_sim_obd()
    df = df[['site_name', 'treat_name', 'time', 'obd']]
    # print(df)

    # create folds configuration
    # file k_fold_con.csv and
    # setup the processing fold
    # structure
    m1.create_k_fold_con(df, num_folds=3, mode='c')

    fold_n = 3    
    for fold_n in range(1, fold_n + 1):  #[2]:
        wd = os.path.join(pwd, f"fold0{fold_n}_")

        # read all simulations and observations and store them in dataframe
        df = m1.all_sim_obd_wd(wd)
        df = df[['site_name', 'treat_name', 'time', 'obd']]
        obd = df.obd.tolist()

        # 500 repetitions for testing only
        modules.multi_run_sceua(pwd, wd, obd, sel_pars_df, 5000, dbformat="csv", parallel="mpc")  
        # modules.multi_run_dream(pwd, wd, obd, sel_pars_df, 10000, dbformat="csv", nChains=30, parallel="mpc", obj_func=GausianLike)

        kfa = analyzer.KFoldAnalyzer(pwd)
        kfa.create_kfold_sims_pars(os.path.join(wd, "SCEUA_daycent.csv"), fold_number=fold_n)
        # kfa.create_kfold_sims_pars(os.path.join(wd, "DREAM_daycent.csv"), fold_number=fold_n)

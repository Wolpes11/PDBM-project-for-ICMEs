import numpy as np
import pandas as pd
import  matplotlib.pyplot as plt
import os
#from config import path, earth_cme_path, path_cme_soho, path_helcats, dbm_path
# import requests
# print(path)
# path = '/home/plasmion/CWI_analysis/CME_comparison/'

# earth_cme_path = path + 'cme_dat1/'
# earth_cme = 'table_geoeffective.csv'
def load_dataframes():
  
    CME_dat1 = pd.read_csv('data/' + 'ICME_complete_dataset_v3.csv', header=[0,1])


    # path_cme_soho = path + 'cme_dat2/'
    CME_dat1['LASCO_times'] = pd.to_datetime(CME_dat1[CME_dat1.columns[1]])
    CME_dat1['SOHO_times'] = CME_dat1['LASCO_times'] - pd.Timedelta(hours = 1.5)
  

    CME_dat1.name = 'CME_dat1'
 



    return CME_dat1




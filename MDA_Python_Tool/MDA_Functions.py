# -*- coding: utf-8 -*-
"""
Created Sep 2, 2020

@author: morganbrooks
"""
#%%

###############################################################
# Import required modules
###############################################################
import pathlib
import pandas as pd
from matplotlib import pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import seaborn as sns
import math 
import peakutils

###############################################################
# Functions Required for MDA Calculation Tool 
###############################################################


#Check That the Data Loaded Properly & Review Unique Samples

def check_data_loading(main_byid_df):
    print('First 5 Rows of Dataset:')
    print('')
    print(df.head())
    print('')
    print('The following unique samples were found in your data: ')
    print("")
    sample_array = df["Sample_ID"].unique() 
    print(sample_array)
    sample_amounts_table = df.groupby('Sample_ID').Age.nunique().reset_index()
    sample_amounts_table.rename(columns={
    'Age': 'Sample_Size'},
    inplace=True)
    print('')
    print('Summary of sample size disitrbution in the dataset:')
    print('')
    print(sample_amounts_table)
    return 
 

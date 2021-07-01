import pandas as pd
import numpy as np


def load_data(arrays, column_names, data_type):
    dataSheet = 'Data'
    ID_col = 'Sample_ID'
    obj1 = []
    obj2 = []
    obj3 = []
    obj4 = []
    analyses_df = pd.DataFrame(arrays, columns=column_names)
    main_df = pd.DataFrame(analyses_df['Sample_ID'].unique(), columns=['Sample_ID'])
    samples_df = main_df.copy()
    dfs = {'Samples': samples_df, 'Data': analyses_df}
    for sample_ind in range(main_df.shape[0]):
        active_sample_id = main_df.loc[sample_ind,ID_col]
        active_UPb_data = dfs[dataSheet].loc[dfs[dataSheet][ID_col].isin([active_sample_id]),:]
        for colname in active_UPb_data:
            if colname not in [ID_col]: 
                if colname in samples_df.columns:
                    colname_adj = colname+'_'+dataSheet 
                    if colname_adj not in main_df.columns:
                        main_df[colname_adj] = (np.nan*np.empty(shape=(len(main_df),1))).tolist()
                        main_df[colname_adj] = np.asarray(main_df[colname_adj])                
                    main_df.at[sample_ind,colname_adj] = active_UPb_data[colname].values
                else:
                    if colname not in main_df.columns: 
                        main_df[colname] = (np.nan*np.empty(shape=(len(main_df),1))).tolist()
                        main_df[colname] = np.asarray(main_df[colname])
                    main_df.at[sample_ind,colname] = active_UPb_data[colname].values
    main_byid_df = main_df.copy()
    main_byid_df.set_index(ID_col,inplace=True, drop=False)
    obj1.append(main_df)
    obj2.append(main_byid_df)
    obj3.append(samples_df)
    obj4.append(analyses_df)
    main_df = pd.concat(obj1, sort=False)
    main_byid_df = pd.concat(obj2, sort=False)
    samples_df = pd.concat(obj3, sort=False)
    analyses_df = pd.concat(obj4, sort=False)
    return main_df, main_byid_df, samples_df, analyses_df


def validate_analyses_df(df: pd.DataFrame, data_type: str) -> pd.DataFrame: 
    if data_type == 'Ages':
        amount_of_samples = df.Sample_ID.nunique()
        sample_array = df["Sample_ID"].unique() 
        sample_amounts_table = df.groupby('Sample_ID').Best_Age.count().reset_index()
        sample_amounts_table.rename(columns={'Best_Age': 'Sample_Size'}, inplace=True)
    if data_type == '238U/206Pb_&_207Pb/206Pb':
        amount_of_samples = df.Sample_ID.nunique()
        sample_array = df["Sample_ID"].unique() 
        df.rename(columns={'238U/206Pb': 'eight_six_U_Pb'}, inplace=True)
        sample_amounts_table = df.groupby('Sample_ID').eight_six_U_Pb.count().reset_index()
        sample_amounts_table.rename(columns={'eight_six_U_Pb': 'Sample_Size'}, inplace=True)
    return sample_amounts_table

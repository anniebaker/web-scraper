import pandas as pd
import config
from mini_modules import scratch_csv
#CREATE CLIENT INFO DATAFRAME
def new_client_df(CSV_file_location,reps_file_location,cohort1,cohort2):
    dfcr = pd.read_csv(CSV_file_location, engine='python', index_col=False)
    dfcr = dfcr[dfcr.Title.str.startswith(cohort1) | dfcr.Title.str.startswith(cohort2) ] 
    dfcr = dfcr[["Title","Password","Url"]]
    dfcr.reset_index()
    dfcr.Title = dfcr.Title.astype(str)
    dfcr.Password = dfcr.Password.astype(str)
    dfcr.Url = dfcr.Url.astype(str)
    if config.scratch_csv_needed == False:
        dfrep = pd.read_csv(reps_file_location, engine='python', index_col=False) 
        if config.exact_okta_url == False:
            dfrep = dfrep[["Title","App_label","Group Name","Email"]]
            dfrep[["Oktaurl"]] = None #create empty columns for future data
        if config.exact_okta_url == True:
            dfrep = dfrep[["Title","App_label","Group Name","Email","Oktaurl"]]
        dfrep.reset_index()
        dfrep.Title = dfrep.Title.astype(str)
        dfrep.App_label = dfrep.App_label.astype(str)
        dfrep = dfrep.fillna('')
        print(dfrep.head())
        df=dfrep.merge(dfcr, on='Title', how='left') #merge cred dataframe and our offered info into one
        print(df.head())
        df.set_index("Title", inplace=True) #set index to make sure we get the right subdomain info
        df[["Zenapi","Logouturl","Fingerprint"]] = None #create empty columns for future data
        return df

#testing# tdf = new_client_df(config.CSV_file_location, config.reps_file_location, config.cohort1,config.cohort2)
#testing# print(tdf.head())
    # if config.scratch_csv_needed == True: mini_modules.scratch_csv

def new_scratch_client_df(CSV_file_location,subdomain,app_label,group_name,email):
    dfcr = pd.read_csv(CSV_file_location, engine='python', index_col=False)
    dfcr = dfcr[dfcr.Title.str.startswith(subdomain)] 
    dfcr = dfcr[["Title","Password","Url"]]
    dfcr.reset_index()
    dfcr.Title = dfcr.Title.astype(str)
    dfcr.Password = dfcr.Password.astype(str)
    dfcr.Url = dfcr.Url.astype(str)
    dfrep = scratch_csv(subdomain,app_label,group_name,email)
    dfrep.reset_index()
    #dfrep.set_axis(['name', 'email', 'user_fields.first_name','user_fields.middle_name','user_fields.last_name','user_fields.suffix','user_fields.newsletter_flag','user_fields.no_bulk_mail_flag','user_fields.home_address_phone','tags','user_fields.home_address_line_1','user_fields.home_address_city','user_fields.home_address_state','user_fields.home_address_zip_code','user_fields.date_of_birth'], axis='columns', inplace=True)

    df=dfrep.merge(dfcr, on='Title', how='left') #merge cred dataframe and our offered info into one
    df.set_index("Title", inplace=True) #set index to make sure we get the right subdomain info
    df[["Zenapi","Logouturl","Fingerprint","Oktaurl"]] = None #create empty columns for future data

    return df
import os
import pandas as pd

#QUEUE 
queue = []

#Is the account set up yet?
account_primed = True

#Are we ready to assign groups?
client_groups_ready = True

#CSV FILEPATH LOCATION
CSV_file_location = "../assets/UPDATEDCREDSFILENAME.csv"
reps_file_location = "../assets/UPDATEDTEMPLATEFILE.csv" #MAKE csv with Title, App_label 

#DATAFRAME SETUP
cohort1 = ''
cohort2 = ''
#cohort3 = '' #add more if needed

#ONE-OFF DF CREATION
scratch_csv_needed = False
scratch_subdomain = ''
app_label = 'n'
group_name=''
email=''

#JUST GROUP ASSIGNMENTS
exact_okta_url = False #i.e. do we have a link to edit provisioning directly?
cohort_prefix = ''
organization = "Indigov"
client_organization = "" #change this per client
tz = 'Eastern Time (US & Canada)'

class AssignGroups:
    prefix = "" #prefix to custom group assignments in Okta
    def __init__(self,admin,staff,legislator,intern,light_agent)-> None:
        self.admin = ["Admin", "admin",admin]
        self.staff = ["Staffer","agent",staff]
        self.legislator = ["Legislator","agent",legislator]
        self.intern = ["Intern","agent",intern]
        self.light_agent = ["Light agent","agent",light_agent]

proserv_grp = AssignGroups("Professional Services","","","","")
teamdev_grp = AssignGroups("Team Dev","","","","")

client_grp = AssignGroups(
    "Admin",
    "Full",
    "Legislator",
    "Intern",
    "Lite")

def pull_group_data(grp_class_instance):
    grp_value = []
    for x in dir(client_grp):
        g = getattr(client_grp, x)
        if x.startswith("__"):
            continue
        elif type(g) != list:
            continue
        elif g[2]=="":
            continue
        else:
            grp_value.append(g)
    return grp_value

#STABLE CONFIG VALUES
class GlobalCred:
    new_instance_url = "https://indigov-admin.okta.com/admin/app/zendesk/instance/_new_/"
    okta_login = "https://indigov.okta.com/oauth2/v1/authorize?response_type=code&response_mode=query&client_id=okta.b58d5b75-07d4-5f25-bf59-368a1261a405&redirect_uri=https%3A%2F%2Findigov-admin.okta.com%2Fadmin%2Fsso%2Fcallback&scope=openid&state=6FavTToy_YWCsM14Y652v9tNf3WPamzp&nonce=HLCk5ScpZXdKTx4KyzzVsjm5Ve9Gy8ya&code_challenge=eSAJ4LTHH_fqHXeramNHPqSJlwr3KMfZTAEgW3RxJ10&code_challenge_method=S256"
    admin = 'admin@indigov.us'
    saml = 'SAML'
    logoutUrl = 'https://login.indigov.com'
    zapiUser = 'admin@indigov.us/token'

#PNG Location
indigov_png = "../assets/Indigov.png"

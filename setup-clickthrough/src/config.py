import os
import pandas as pd
#Indigov PNG Location
indigov_png = "/Users/abrazilbaker/Ecosystem/Development/flex-tools-main/sso_integration/universal/Indigov.png"
account_primed = True
client_groups_ready = True

#CSV FILEPATH LOCATION
#CSV_file_location ="../universal/wonring1031.csv"
CSV_file_location = "../clients/wonring122623.csv"
reps_file_location = "../clients/mihouse2.csv" #MAKE csv with Title, App_label 
#nc# reps_file_location = "../clients/ncga/input_ncrep080323.csv" #MAKE csv with Title, App_label 
#rep file name must have these column titles: "Title","App_label","Group Name","Email"

#ONE-OFF-SUBDOMAIN DF CREATION
scratch_csv_needed = False
scratch_subdomain = 'waospi'
app_label = 'Washington Office of Superintendent of Public Instruction'
group_name='TBD'
email='NA'

#DATAFRAME SETUP
cohort1 = 'mirep'
cohort2 = 'misen'
#cohort3 = 'nm' #add more if needed

#ASSIGNMENTS
exact_okta_url = True #i.e. do we have a link to edit provisioning directly?
cohort_prefix = ''
organization = "News"

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
    "",
    "Full 2023",
    "",
    "",
    "Lite 2023")

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
tz = 'Eastern Time (US & Canada)'

"""
DONE: 
'mirepmartin',
'mirepmckinney',

'mireprogers',
'mirepsmit',
'mirepstone',
'mirepaiyash',
'mirepalexander',
'mirepandrews',
'mireparagona',
'mireparbit',
'mirepbeeler',
'mirepbegole',
'mirepbeson',
'mirepbezotte',
'mirepbierlein',
'mirepbollin',
'mirepborton',
'mirepbrabec',
'mirepbreen',
'mirepbrixie',
'mirepbruck',
'mirepbyrnes',
'mirepcarra',
'mireptyronecarter',
'mirepcarter',
'mirepcavitt',
'mirepchurches',
'mirepcoffia',
'mirepcoleman',
'mirepconlin',
'mirepdeboer',
'mirepboyer',
'mirepdesana',
'mirepdievendorf',
'mirepedwards',
'mirepfarhat',
'mirepfiller',
'mirepfink',
'mirepfox',
'mirepfriske',
'mirepglanville',
'mirepgrant',
'mirepgreen',
'mirepgreene',
'mirephaadsma',
'mirephall',
'mirepharris',
'mirephill',
'mirephoadley',
'mirephood',
'mirephope',
'mirephoskins',
'mirepkoleszar',
'mirepkuhn',
'mirepkunse',
'mirepliberati',
'mireplightner',
'mirepmacdonell',
'mirepmaddock',
'mirepmarkkanen',
'mirepmartus',
'mirepmcfall',
'mirepmeerman',
'mirepmentzer',
'mirepmiller',
'mirepmorgan',
'mirepmorse',
'mirepmueller',
'mirepneeley',
'mirepneyer',
'mireponeal',
'mirepoutman',
'mireppaiz',
'mireppaquette',
'mireppohutsky',
'mirepposthumus',
'mirepprestin',
'mirepprice',
'mireppuri',
'mireprheingans',
'mireprigas',
'mireproth',
'mirepschmaltz',
'mirepschriver',
'mirepschuette',
'mirepscott',
'mirepshannon',
'mirepskaggs',
'mirepslagh',
'mirepsnyder',
'mirepstgermaine',
'mirepsteckloff',
'mirepsteele',
'mireptate',
'mirepthompson',
'mireptisdel',
'mireptsernoglou',
'mirepvanderwall',
'mirepvanwoerkom',
'mirepwegela',
'mirepweiss',
'mirepwendzel',
'mirepwhitsett',
'mirepwilson',
'mirepwitwer',
'mirepwozniak',
'mirepyoung',
'mirepzorn'
NOT DONE:

"""


#CLIENT QUEUE 
queue = [
]

#STABLE CONFIG VALUES
class GlobalCred:
    new_instance_url = "https://indigov-admin.okta.com/admin/app/zendesk/instance/_new_/"
    okta_login = "https://indigov.okta.com/oauth2/v1/authorize?response_type=code&response_mode=query&client_id=okta.b58d5b75-07d4-5f25-bf59-368a1261a405&redirect_uri=https%3A%2F%2Findigov-admin.okta.com%2Fadmin%2Fsso%2Fcallback&scope=openid&state=6FavTToy_YWCsM14Y652v9tNf3WPamzp&nonce=HLCk5ScpZXdKTx4KyzzVsjm5Ve9Gy8ya&code_challenge=eSAJ4LTHH_fqHXeramNHPqSJlwr3KMfZTAEgW3RxJ10&code_challenge_method=S256"
    admin = 'admin@indigov.us'
    saml = 'SAML'
    logoutUrl = 'https://login.indigov.com'
    zapiUser = 'admin@indigov.us/token'


import pandas as pd
import config
"""
String.stringContains(user.login, '@indigov.com') OR String.stringContains(user.login, '@indigov.us') ? 'Indigov' : user.firstName
String.stringContains(user.login, '@indigov.com') OR String.stringContains(user.login, '@indigov.us') ? 'Admin' : user.lastName
"""

def sub_creds(sub):
    class Rep: 
        app_login = 'String.stringContains(user.login, "@indigov.com") OR String.stringContains(user.login, "@indigov.us") ? "admin@indigov.us" : user.email'
        map_first = "String.stringContains(user.login, '@indigov.com') OR String.stringContains(user.login, '@indigov.us') ? 'Indigov' : user.firstName"
        map_last = "String.stringContains(user.login, '@indigov.com') OR String.stringContains(user.login, '@indigov.us') ? 'Admin' : user.lastName"
        zen_website = "https://"+sub+".zendesk.com/admin/home"
        sso_url = "https://"+sub+".zendesk.com/admin/account/security/sso"
        team_url = "https://"+sub+".zendesk.com/admin/account/security/team_members"
        zapi_url = "https://"+sub+".zendesk.com/admin/apps-integrations/apis/zendesk-api/settings"
        api_dash_url = "https://"+sub+".zendesk.com/api_dashboard/settings"
        email_link = "https://"+sub+".zendesk.com/settings/email"
        allowlist_link = "https://"+sub+".zendesk.com/settings/customers?location=admin_center"
        def __init__(self, samlssourl, certfinger) -> None:
            self.self = self
            self.samlssourl = samlssourl
            self.certfinger = certfinger
    rep = Rep('','')
    return rep
def scratch_csv(subdomain,app_label,group_name,email):
    sr = pd.DataFrame(columns=["Title","App_label","Group Name","Email"])
    sr = sr.append({'Title':subdomain,'App_label':app_label,'Group Name':group_name,'Email':email}, ignore_index=True)
    sr.set_index("Title", inplace=True) #set index to make sure we get the right subdomain info
    return sr


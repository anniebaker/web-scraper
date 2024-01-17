#TUES 6/6
import os
import mini_modules
import config
from sso_df import new_client_df
from sso_df import new_scratch_client_df
from dotenv import load_dotenv
from pyotp import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import pandas as pd
import numpy as np
#chromeOptions = webdriver.ChromeOptions()
#chromeOptions.binary_location = "/Applications/Google Chrome.app" 
chromeDriver = "/usr/local/bin/chromedriver.exe"
driver = webdriver.Chrome()
#LOGIN CREDS
load_dotenv()
class Login:
    email = os.getenv('EMAIL')
    pwd = os.getenv('PRIVATE_KEY')
    ring = os.getenv('SECRET_KEY')
login = Login()

#CLIENT DATA IMPORT
organization = config.organization
CSV_file_location = config.CSV_file_location

if config.scratch_csv_needed == False:
    cohort1 = config.cohort1 
    cohort2 = config.cohort2 
    reps_file_location = config.reps_file_location
    df = new_client_df(CSV_file_location,reps_file_location,cohort1,cohort2)
    print(df.head())
if config.scratch_csv_needed == True:
    subdomain = config.scratch_subdomain
    app_label = config.app_label
    group_name=config.group_name
    email=config.email
    df = new_scratch_client_df(CSV_file_location,subdomain,app_label,group_name,email)
class DfData:
    def __init__(self, df, sub):
        self.zpass = str(df.loc[sub,'Password'])
        self.grp = str(df.loc[sub,'Group Name'])
        self.label = df.loc[sub,'App_label']
        self.email = str(df.loc[sub,'Email'])

#WEBDRIVER SETUP
wait = WebDriverWait(driver,20)

#WEBDRIVER FUNCTIONS
def focus_new_tab(wrongdle):
    for x in driver.window_handles:
        if x != wrongdle:
            driver.switch_to.window(x)
            break
def focus_orig_tab(origndle):
    for x in driver.window_handles:
        if x == origndle:
            driver.switch_to.window(x)
            break
#CREDENTIALS SETUP
creds = config.GlobalCred()
queue = config.queue
print(queue)

#OKTA APP CREATION FROM SCRATCH
for sub in queue: 
    print("starting " + sub )
    rep = mini_modules.sub_creds(sub) 
    dfdata = DfData(df,sub)
    print(dfdata.label)
    print(dfdata.grp)

    current = driver.current_window_handle
    focus_new_tab(current)
    time.sleep(1)
    ################
    if driver.title != "Indigov - Setup: Zendesk":
        tempdle = driver.current_window_handle
        driver.get("https://indigov-admin.okta.com/admin/app/zendesk/instance/_new_/") #open setup tab
        focus_new_tab(tempdle)
        setupdle = driver.current_window_handle
        if driver.title.__contains__("Indigov - Access Forbidden"):
            #driver.execute_script(f'''window.open("{creds.new_instance_url}");''')
            driver.execute_script("""window.open("https://indigov-admin.okta.com/admin/app/zendesk/instance/_new_/")""") #open setup tab
            time.sleep(3)
            #driver.execute_script(f'''window.open("${creds.new_instance_url}")''') #open setup tab
            time.sleep(4)
            driver.close()
            focus_new_tab(setupdle)
        if driver.title == "indigov_default - Sign In":
            driver.get("https://indigov.okta.com/oauth2/v1/authorize?response_type=code&response_mode=query&client_id=okta.b58d5b75-07d4-5f25-bf59-368a1261a405&redirect_uri=https%3A%2F%2Findigov-admin.okta.com%2Fadmin%2Fsso%2Fcallback&scope=openid&state=6FavTToy_YWCsM14Y652v9tNf3WPamzp&nonce=HLCk5ScpZXdKTx4KyzzVsjm5Ve9Gy8ya&code_challenge=eSAJ4LTHH_fqHXeramNHPqSJlwr3KMfZTAEgW3RxJ10&code_challenge_method=S256")
            original_window = driver.current_window_handle

            email = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='input28']")))
            email.send_keys(login.email)

            time.sleep(2)
            next = driver.find_element(By.XPATH, '//*[@type="submit"]')
            next.click()
            psw = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='input59']")))
            psw.send_keys(login.pwd)
            driver.find_element(by='xpath', value='//*[@type="submit"]').click()
            authField = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='input84']")))
            totp = TOTP(login.ring)
            token = totp.now()
            authField.send_keys(token)
            driver.find_element(by='xpath', value='//input[@type="submit"]').click()
            time.sleep(2)
            driver.execute_script("""window.open("https://indigov-admin.okta.com/admin/app/zendesk/instance/_new_/")""") #open setup tab
            time.sleep(8)
            driver.close() 
            focus_new_tab(original_window)
    if driver.title == "Indigov - Sign In":
        driver.find_element(by='xpath', value='//input[@type="submit"]').click()
        time.sleep(8)

    #NEW OKTA APP FROM SCRATCH
    wait.until(EC.title_is("Indigov - Setup: Zendesk")) #wait until page loads
    time.sleep(4)
    oktandle = driver.current_window_handle #grab current handle

    label = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='settings.label']")))
    label.clear()
    #if group lable already has a prefix# dfdata.label = str(config.cohort_prefix)+ " " + str(dfdata.label)
    label.send_keys(dfdata.label)
    #driver.execute_script(f'''document.getElementById("settings.label").value = "{dfdata.label}"''')
    time.sleep(3)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='settings.companySubDomain']")))
    driver.execute_script(f'''document.getElementById("settings.companySubDomain").value = "{sub}"''')
    time.sleep(2)
    driver.execute_script('''document.querySelectorAll('input[type="button"]').item(1).click()''')
    time.sleep(4)

    #Add login information
    driver.execute_script('''document.querySelectorAll("[name=autofillSetting] > option").item(1).selected = true''')
    time.sleep(2)
    driver.execute_script('''document.querySelectorAll("[name=autofillSetting] > option").item(0).selected = true''')
    time.sleep(2)
    driver.execute_script(f'''document.getElementById("ssoSettings.customRule").value = "String.stringContains(user.login, '@indigov.com') OR String.stringContains(user.login, '@indigov.us') ? 'admin@indigov.us' : user.email"''')
    time.sleep(1.3)

    #Sign on options setup page
    driver.execute_script('''document.getElementById("ssoSettings.mode.SAML_2_0").click()''')
    time.sleep(2)
    driver.execute_script('''document.getElementById("helpInstruction.mode.SAML_2_0").click()''')
    time.sleep(3)

    #Switch to SSO setup tab
    focus_new_tab(oktandle)
    time.sleep(2)
    wait.until(EC.title_is("Setup SSO"))
    suboktimal = driver.current_window_handle
    print(driver.current_window_handle)
    time.sleep(3.4)
    samlssourl = driver.execute_script('''return document.getElementById("signOnUrl").innerText''')
    fingerprint = driver.execute_script('''return document.getElementById("certFingerPrintSha256").innerText''')    
    rep.samlssourl = samlssourl
    rep.certfinger = fingerprint
    print(rep.samlssourl)
    print(rep.certfinger)
    time.sleep(2)
    driver.close()
    focus_orig_tab(oktandle)

    #RETURN TO OKTA SETUP PAGE, CHANGE USER ID FIELD, SAVE
    time.sleep(5)
    print(driver.current_window_handle)
    driver.execute_script('''document.querySelectorAll("div.button-bar > input").item(9).click()''')
    time.sleep(5)

    #OPEN ZENDESK
    driver.execute_script(f'''window.open("{rep.zen_website}");''')
    time.sleep(3)
    focus_new_tab(oktandle)
    time.sleep(8)    
    zen = driver.current_window_handle

    #if this instance redirects you to Okta sign-in again for some reason, that means you need to assign yourself to an application that already exists
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    if driver.title == "Indigov - Sign In":
        lastrepdle = driver.current_window_handle
        driver.get("https://indigov-admin.okta.com/admin/app/zendesk/instance/_new_/") #open setup tab
        time.sleep(10)
        print("okta app exists "+sub)
        driver.close()
        focus_new_tab(lastrepdle)
    else:
        login_input = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='user_email']")))
        login_input.send_keys(creds.admin)
        time.sleep(2)
        #password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='user_password']")))
        #password_input.send_keys(dfdata.zpass)
        driver.execute_script(f'''document.getElementById("user_password").value = "{dfdata.zpass}"''')
        time.sleep(2)
        driver.find_element(by='xpath', value='//*[@id="sign-in-submit-button"]').click()
        admin = "admin"

        wait.until(EC.title_is("Zendesk Admin Center"))

        #account_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='77val-accordion_2.0.4--trigger:0']")))
        #account_button.click()
        #single_sign_on_btn = wait.until(EC.presence_of_element_located((By.ID, "72val-accordion_2.0.4--panel:0")))
        #single_sign_on_btn.click()

        """
        #Experimentally commented out: 
        #last_resort_url = "https://"+sub+".zendesk.com/admin/account/security/sso" #last resort works
        #last_resort_url = str(last_resort_url)
        """


    #SSO SETUP
        
        #commented out to keep on the same page
        driver.execute_script(f'''window.open("{rep.sso_url}");''') #open setup tab
        time.sleep(8)
        driver.close()
        focus_new_tab(zen)
        focus_new_tab(oktandle)
        
        samdle = driver.current_window_handle #preserving this even if not needed 
        #wait.until(EC.title_is("Zendesk Admin Center"))
        driver.switch_to.frame(0)
        time.sleep(6)
        """
        sso_box = wait.until(EC.all_of(EC.presence_of_element_located((By.ID, "admin_center_framework_security-mount-point-id"))))
        if sso_box != True:
            print(sso_box)
            driver.refresh()
            wait.until(EC.title_is("Zendesk Admin Center"))
            driver.switch_to.frame(0)
            print("sso not loading")

        elif sso_box != True:
            driver.refresh()
            wait.until(EC.title_is("Zendesk Admin Center"))
            driver.switch_to.frame(0)
            print("sso not loading twice")
        else: 
        """
        driver.execute_script('''document.querySelector("#admin_center_framework_security-mount-point-id > div > div > div > div.sc-hHLeRK.hDSiSu > div:nth-child(4) > button").click()''')
        time.sleep(1)
        driver.execute_script('''document.querySelectorAll("[data-testid=saml-option").item(0).click()''')
        time.sleep(2)
        loaded = wait.until(EC.presence_of_element_located((By.XPATH, "//div")))
        time.sleep(3)
        
        #SSO FIELD SUBMISSION
        
        config_input = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@name='name']")))
        config_input.send_keys(creds.saml)
        saml_input = driver.find_element(By.XPATH, '//*[@name="remote_login_url"]').send_keys(samlssourl)
        cert_input = driver.find_element(By.XPATH, '//*[@name="fingerprint"]').send_keys(fingerprint)
        lo_input = driver.find_element(By.XPATH, '//*[@name="remote_logout_url"]').send_keys(creds.logoutUrl)
        time.sleep(0.2)
        driver.execute_script("""document.querySelector('.sc-jSMfEi').click()""")
        time.sleep(2)
        driver.switch_to.parent_frame()
        time.sleep(5)

        #TEAM MEMBER AUTHENTICATION
        driver.execute_script(f'''window.open("{rep.team_url}");''')
        time.sleep(8)
        driver.close()
        focus_new_tab(samdle)
        focus_new_tab(oktandle)
        time.sleep(3)

        teamdle = driver.current_window_handle
        time.sleep(3)
        loadin = wait.until(EC.visibility_of_element_located((By.XPATH, "//input")))
        time.sleep(3)
        driver.execute_script('''document.querySelector("[data-test-id=zd-auth-select-dropdown-select] > div > div").click()''') #select dropdown
        time.sleep(2)
        driver.execute_script('''document.querySelector("li#downshift-0-item-4.StyledItem-sc-1xeog7q-0.brUQAa").click()''') #select Custom
        time.sleep(5)
        driver.execute_script('''document.querySelectorAll("div > input").item(3).click()''') # External auth
        time.sleep(4)
        driver.execute_script('''document.querySelectorAll("div > input").item(6).click()''') #select SSO
        time.sleep(3)
        driver.execute_script('''document.querySelectorAll("div > input").item(7).click()''') #select SAML
        time.sleep(3.1)
        driver.execute_script('''document.querySelectorAll("[data-test-id=security-staff-members-footer-save-button]").item(0).click()''')
        time.sleep(1.7)
        #might have to go after switching to parent frame?
        driver.execute_script('''document.querySelector("body span:nth-child(2) > button").click()''')
        driver.switch_to.parent_frame()
        time.sleep(1.7)

        #ZENDESK API TOKEN AUTHENTICATION

        driver.execute_script(f'''window.open("{rep.api_dash_url}");''') #NEW ZENDESK API TOKEN AUTH 07-19-2023
        #OLD ZENDESK API URL driver.execute_script(f'''window.open("{rep.zapi_url}");''')
        time.sleep(8)
        driver.close()

        focus_new_tab(samdle)
        focus_new_tab(oktandle)

        #wait.until(EC.title_is("Zendesk API"))
        zandle = driver.current_window_handle
        time.sleep(4)
        if config.account_primed:
            #driver.execute_script('''document.getElementById("checkbox1").click()''')
            #time.sleep(1)
            driver.execute_script('''document.querySelector("#app > div > div > div > div.OAuthClients_headingContainer_nmBSs > button").click()''') #
            time.sleep(2)
        else: 
            driver.execute_script('''document.getElementById("checkbox2").click()''')
            driver.execute_script('''document.querySelectorAll("#app > div button").item(2).click()''')
            time.sleep(1)
        ##terms_chbx = wait.until(EC.presence_of_element_located((By.XPATH, terms_xpath)))
        ##terms_chbx.click()
        
        ##token_access_toggle = wait.until(EC.presence_of_element_located((By.XPATH, token_access_xpath)))
        ##token_access_toggle.click()    driver.execute_script('''document.getElementById("checkbox2").click()''')
        # END: REQUIRED FOR PREPRIMED ACCOUNTS
        
        
        
        wait.until(EC.visibility_of_element_located((By.XPATH, '//input[contains(@id, "fieldComponent")]')))
        wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="description"]')))
        pwd = driver.find_element(By.XPATH, '//input[@name="description"]')
        pwd.send_keys('okta')

        token = driver.find_element(By.XPATH, '//div[contains(@class, "InputWithButtons_group_2JNoM")]//input').get_dom_attribute('value')
        print(token)
        df.at[sub, "Zenapi"] = token
        sv = driver.find_element(By.XPATH, '//button//span[text()="Save"]')
        
        sv.click()
        print("saved")
        time.sleep(3)
        driver.close()

        #OKTA APP RETURN
        focus_orig_tab(oktandle)
        #navigate to provisioning tab
        time.sleep(4)
        driver.execute_script('''document.querySelectorAll("li.ui-state-default > a").item(2).click()''') #click provisioning tab
        time.sleep(1)
        #driver.execute_script('''document.getElementById("userMgmtSettings.edit_link").click()''')
        time.sleep(1.1)
        driver.execute_script('''document.querySelector('div.page-toolbar > a').click()''') #enable provisioning part 1
        time.sleep(0.5)
        driver.execute_script('''document.querySelectorAll('div.checkbox-wrap label.option').item(5).click()''') #enable api config
        time.sleep(1.01)
        driver.execute_script('''document.getElementById("userMgmtSettings.adminUsername").value = "admin@indigov.us/token"''') #username
        time.sleep(1.02)
        driver.execute_script(f'''document.getElementById("userMgmtSettings.adminPassword").value = "{token}"''') #API token ID: 
        time.sleep(1.1)
        driver.execute_script('''document.getElementById("userMgmtSettings.rolesToImport").item(1).selected = true''') #agends and admins
        time.sleep(2)
        #driver.execute_script('''document.getElementById("m-verify-button").click()''') #verify button ID 
        driver.execute_script('''document.getElementById("userMgmtSettings.button.submit").click()''') #submit button
        time.sleep(7)
        
        #Enable API provisioning
        load_edit = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="userMgmtSettings.edit_link"]')))
        load_edit.click()
        time.sleep(3)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="userMgmtSettings.pushProfile"]')))
        driver.execute_script('''document.getElementById("userMgmtSettings.pushNewAccount").click()''')
        time.sleep(1)
        driver.execute_script('''document.getElementById("userMgmtSettings.pushProfile").click()''')
        time.sleep(1)
        driver.execute_script('''document.getElementById("userMgmtSettings.pushDeactivation").click()''')
        submit = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="userMgmtSettings.button.submit"]')))
        submit.click()
        time.sleep(4) #SLEEP
        focus_orig_tab(oktandle)
        driver.execute_script('''document.querySelector("div.app-logo-wrap > a.app-logo-edit").click()''') #starting logo
        time.sleep(1.1)

        #Add indigov logo
        logo = driver.find_element(By.XPATH, "//input[@type='file']")
        logo.send_keys(config.indigov_png)
        time.sleep(1.1)
        driver.execute_script('''document.querySelector("div.app-logo-file-browse > input.button").click()''')
        time.sleep(1.1)
        close = driver.find_element(By.XPATH, '//input[@id="closeEditLinkLogo"]')
        close.click()
        time.sleep(1.1)
        oktaAppUrl = driver.execute_script('''return window.location.href''')
        df.at[sub, "Oktaurl"] = oktaAppUrl
        oktaurls = df[["Oktaurl"]]
        oktaurls.to_csv("oktaurls.csv")
        print(oktaAppUrl)
        #NAV
        #sign on tab: 
        driver.execute_script('''document.querySelectorAll("li.ui-state-default > a").item(1).click()''')
        print("navigated to sign on tab")
        time.sleep(2)
        #edit_link = wait.until(EC.presence_of_element_located((By.ID, "ssoSettings.edit_link")))
        #edit_link.click()
        driver.execute_script('''document.getElementById("ssoSettings.edit_link").click()''') #Edit to make sure it's create&update 

        print("clicked edit")
        #I think missing an edit feature here
        time.sleep(3)
        driver.execute_script('''document.querySelector("#ssoSettings-customRulePushStatus > [value=PUSH]").selected = true''') #Edit to make sure it's create&update 
        print("set to create & update")
        time.sleep(2)
        driver.execute_script('''document.querySelectorAll('input[name=m-save]').item(2).click()''')
        time.sleep(5)
        print("saved")
        #configure profile mapping: 
        driver.execute_script('''document.querySelector('p.explain-text > a').click()''') #open config change
        focus_new_tab(oktandle)
        print("opening configuration mapping")
        mapdle = driver.current_window_handle
        time.sleep(3.5)
        driver.execute_script('''document.querySelectorAll('li.ui-state-default > a').item(3).click()''') #change mini-tabs:
        time.sleep(2)
        print("changed mini tabs")
        #this is out of date anyways

        firstName = wait.until(EC.presence_of_element_located((By.ID, "input1462")))
        lastName = wait.until(EC.presence_of_element_located((By.ID, "input1475")))

        #firstName = driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div[2]/div[3]/div[1]/div[2]/div/table/tbody/tr[1]/td[1]/div/div[2]/div/span/input[2]")
        #lastName = driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div[2]/div[3]/div[1]/div[2]/div/table/tbody/tr[2]/td[1]/div/div[2]/div/span/input[2]")
        time.sleep(2)
        def config_prof(name,login): 
            for i in range(0,14):
                name.send_keys(Keys.BACKSPACE)
            time.sleep(2)
            name.send_keys(login)

        config_prof(firstName,rep.map_first)
        time.sleep(1)
        config_prof(lastName,rep.map_last)
        time.sleep(2)

        driver.execute_script('''document.querySelector("input.button.button-primary.save").click()''') #save
        time.sleep(2)
        driver.execute_script('''document.querySelector("input.save").click()''') #apply updates
    
        driver.execute_script('''document.querySelector("a.app-button").click()''')#navigate back to profile
        time.sleep(4)
        focus_new_tab(mapdle)
        landle = driver.current_window_handle
        time.sleep(6)

        #GROUP ASSIGNMENTS
        focus_new_tab(mapdle)
        assigndle = driver.current_window_handle
        assign_tab = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabs"]/ul/li[5]')))
        assign_tab.click()   
        time.sleep(1.1)

        assign_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tab-assignments-"]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[1]/a')))
        assign_btn.click()
        grps_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tab-assignments-"]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[1]/div/ul/li[2]/a')))
        grps_btn.click()
        srch = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simplemodal-data"]/div/div[1]/div/span/input')))
        
        srch.send_keys("Team Dev") #search
        time.sleep(2)
        assgn = driver.find_element(By.CSS_SELECTOR, 'input[data-se="00g1hwnxjB9x8cgaU696"]')
        assgn.click()
        time.sleep(2)
        #Time zone
        #tz = wait.until(EC.presence_of_element_located((By.XPATH, '//div[6]/div/div/form/div[1]/div[2]/div[2]/div[2]/span/div/a')))
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'select')))

        driver.execute_script('''document.getElementsByTagName("select").item(0).setAttribute("style","display: block")''')
        driver.execute_script('''document.getElementsByTagName("select").item(1).setAttribute("style","display: block")''')
        
        
        time.sleep(1)
        time_zone = Select(driver.execute_script('''return document.getElementsByTagName("select").item(0)'''))
        zd_role = Select(driver.execute_script('''return document.getElementsByTagName("select").item(1)'''))


        time.sleep(2)
        time_zone.select_by_visible_text(f'{config.tz}')
        time.sleep(2)
        zd_role.select_by_visible_text('admin')
        time.sleep(3)
        if config.account_primed:
            driver.execute_script('''document.getElementsByTagName("select").item(4).setAttribute("style","display: block")''')
            time.sleep(1)
            org_name = Select(driver.execute_script('''return document.getElementsByTagName("select").item(4)'''))
            org_name.select_by_value(config.organization)
            time.sleep(1)
        
        driver.execute_script('''document.querySelectorAll("input.button.button-primary").item(9).click()''')

        #PROFESSIONAL SERVICES
        srch = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simplemodal-data"]/div/div[1]/div/span/input')))
        for i in range(0,25):
            srch.send_keys(Keys.BACKSPACE)
        srch.send_keys("Professional Services") #search
        time.sleep(2)
        assgn = driver.find_element(By.CSS_SELECTOR, 'input[data-se="00g20q1r8chV0bxjg697"]')
        assgn.click()
        time.sleep(2)

        #Time zone
        #tz = wait.until(EC.presence_of_element_located((By.XPATH, '//div[6]/div/div/form/div[1]/div[2]/div[2]/div[2]/span/div/a')))
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'select')))

        driver.execute_script('''document.getElementsByTagName("select").item(0).setAttribute("style","display: block")''')
        time.sleep(1)
        time_zone = Select(driver.execute_script('''return document.getElementsByTagName("select").item(0)'''))
        time.sleep(2)
        time_zone.select_by_visible_text(config.tz)

        #ZENDESK ROLE
        driver.execute_script('''document.getElementsByTagName("select").item(1).setAttribute("style","display: block")''')
        zd_role = Select(driver.execute_script('''return document.getElementsByTagName("select").item(1)'''))
        time.sleep(1)
        zd_role.select_by_visible_text('admin')
        time.sleep(2)

        #ORGANIZATION
        if config.account_primed:
            driver.execute_script('''document.getElementsByTagName("select").item(4).setAttribute("style","display: block")''')
            time.sleep(1)
            org_name = Select(driver.execute_script('''return document.getElementsByTagName("select").item(4)'''))
            org_name.select_by_value(config.organization)
            time.sleep(1)
        
        #BACK TO SEARCH BAR
        driver.execute_script('''document.querySelectorAll("input.button.button-primary").item(9).click()''')
        time.sleep(2)
        srch = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simplemodal-data"]/div/div[1]/div/span/input')))
        for i in range(0,25):
            srch.send_keys(Keys.BACKSPACE)
        
        #CUSTOM ORGS
        if config.client_groups_ready:
            srch.send_keys((str(dfdata.grp))) #search
            time.sleep(3)
            #CALL ON CLASS FROM CONFIG 
            client_grp = config.client_grp
            group_arr = config.pull_group_data(client_grp)
            time.sleep(3)
            def assign_groups(group_key,class_group):
                print(group_key[0],group_key[1],group_key[2],) 
                group = driver.find_element(By.XPATH, f"//*[contains(text(), '{group_key[2]}')]")
                grp_id = group.get_attribute("href")
                print(grp_id)
                grp_datase = grp_id[-20:]
                assgn = driver.find_element(By.CSS_SELECTOR, f'input[data-se="{grp_datase}"]')
                assgn.click()
                time.sleep(2)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
                driver.execute_script('''document.getElementsByTagName("select").item(0).setAttribute("style","display: block")''')
                time.sleep(1)
                time_zone = Select(driver.execute_script('''return document.getElementsByTagName("select").item(0)'''))
                time.sleep(2)
                time_zone.select_by_visible_text(f'{config.tz}')
                driver.execute_script('''document.getElementsByTagName("select").item(1).setAttribute("style","display: block")''')
                zd_role = Select(driver.execute_script('''return document.getElementsByTagName("select").item(1)'''))
                time.sleep(1)
                zd_role.select_by_visible_text(f'{group_key[1]}')
                time.sleep(2)
                driver.execute_script('''document.getElementsByTagName("select").item(2).setAttribute("style","display: block")''')
                cstm_role = Select(driver.execute_script('''return document.getElementsByTagName("select").item(2)'''))
                time.sleep(1)
                cstm_role.select_by_visible_text(f'{group_key[0]}')
                time.sleep(2)
                #org
                driver.execute_script('''document.getElementsByTagName("select").item(4).setAttribute("style","display: block")''')
                org_name = Select(driver.execute_script('''return document.getElementsByTagName("select").item(4)'''))
                org_name.select_by_value(config.organization)
                time.sleep(1)
                driver.execute_script('''document.querySelectorAll("input.button.button-primary").item(9).click()''')
                time.sleep(2)
            for i in group_arr:
                assign_groups(i,client_grp)
        
        lastrepdle = driver.current_window_handle
        driver.get("https://indigov-admin.okta.com/admin/app/zendesk/instance/_new_/") #open setup tab
        time.sleep(10)
        print("ending "+sub)

        driver.close()
        focus_new_tab(lastrepdle)
    #driver.find_element()
#FRI 7/21
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
#LOGIN CREDS
load_dotenv()
class Login:
    email = os.getenv('EMAIL')
    pwd = os.getenv('PRIVATE_KEY')
    ring = os.getenv('SECRET_KEY')
login = Login()

#CLIENT DATA IMPORT
CSV_file_location = config.CSV_file_location

if config.scratch_csv_needed == False:
    cohort1 = config.cohort1 
    cohort2 = config.cohort2 
    reps_file_location = config.reps_file_location
    df = new_client_df(CSV_file_location,reps_file_location,cohort1,cohort2)
if config.scratch_csv_needed == True:
    subdomain = config.scratch_subdomain
    app_label = config.app_label
    group_name=config.group_name
    email=config.email
    df = new_scratch_client_df(CSV_file_location,subdomain,app_label,group_name,email)
class DfData:
    def __init__(self, df, sub):
        self.grp = str(df.loc[sub,'Group Name'])
        self.label = df.loc[sub,'App_label']
        self.oktaurl = str(df.loc[sub,'Oktaurl'])
#WEBDRIVER SETUP
driver = webdriver.Chrome()
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
    rep = mini_modules.sub_creds(sub) 
    dfdata = DfData(df,sub)
    current = driver.current_window_handle
    focus_new_tab(current)
    time.sleep(1)

    ################
    if driver.title != "Indigov - Dashboard":
        driver.get("https://indigov.okta.com/oauth2/v1/authorize?response_type=code&response_mode=query&client_id=okta.b58d5b75-07d4-5f25-bf59-368a1261a405&redirect_uri=https%3A%2F%2Findigov-admin.okta.com%2Fadmin%2Fsso%2Fcallback&scope=openid&state=6FavTToy_YWCsM14Y652v9tNf3WPamzp&nonce=HLCk5ScpZXdKTx4KyzzVsjm5Ve9Gy8ya&code_challenge=eSAJ4LTHH_fqHXeramNHPqSJlwr3KMfZTAEgW3RxJ10&code_challenge_method=S256")
        original_window = driver.current_window_handle
        email = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='input28']")))
        email.send_keys(login.email)
        time.sleep(2)
        next = driver.find_element(By.XPATH, '//input[@type="submit"]')
        next.click()
        psw = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='input59']")))
        psw.send_keys(login.pwd)
        driver.find_element(by='xpath', value='//input[@type="submit"]').click()
        authField = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='input84']")))
        totp = TOTP(login.ring)
        token = totp.now()
        print(token)
        authField.send_keys(token)
        driver.find_element(by='xpath', value='//input[@type="submit"]').click()
        time.sleep(2)

        driver.execute_script("""window.open("https://indigov-admin.okta.com/admin/dashboard")""") #open setup tab
        time.sleep(8) #wait for tab to fully load
        driver.close() #close old tab
        focus_new_tab(original_window) #change tab focus
    if driver.title == "Indigov - Sign In":
        driver.find_element(by='xpath', value='//*[@id="form20"]/div[2]/input').click()
        time.sleep(8)

    wait.until(EC.title_is("Indigov - Dashboard")) #wait until page loads
    time.sleep(4)
    if config.exact_okta_url is True:
        driver.get(dfdata.oktaurl) #open setup tab
        time.sleep(10)
        print(sub+" opened")
    if config.exact_okta_url is False:
        focus_new_tab(lastrepdle)
        search = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='spotlight-search-bar']")))
        search.clear()
        search.send_keys(dfdata.label)
        search.send_keys(Keys.ENTER)
        first_result =wait.until(EC.presence_of_element_located((By.XPATH, '//div[starts-with(@id, "TOP_RESULT-search-result-item")]')))
        first_result.click()
        time.sleep(4)
    wait.until(EC.title_contains("Indigov - Zendesk: ")) #wait until page loads
    assign_tab = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabs"]/ul/li[5]')))
    assign_tab.click()   
    time.sleep(1.1)

    assign_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tab-assignments-"]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[1]/a')))
    assign_btn.click()
    grps_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tab-assignments-"]/div[1]/div[1]/div[2]/div[1]/div/div[1]/div[1]/div/ul/li[2]/a')))
    grps_btn.click()
    srch = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="simplemodal-data"]/div/div[1]/div/span/input')))
    
    #CALL ON CLASS FROM CONFIG 
    client_grp = config.client_grp
    group_arr = config.pull_group_data(client_grp)


    #CUSTOM ORGS
    srch.send_keys((str(dfdata.grp))) #search
    time.sleep(3)
    def assign_groups(group_key,class_group):
        print(group_key[0],group_key[1],group_key[2],) 
        ##
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
        orgzn = config.organization
        driver.execute_script('''document.getElementsByTagName("select").item(4).setAttribute("style","display: block")''')
        org_name = Select(driver.execute_script('''return document.getElementsByTagName("select").item(4)'''))
        options = org_name.options
        for i in options:
            i = i.text
            print(i)
            if "Representative" in i:
                orgzn = i
            elif "Rep" in i:
                orgzn = i
        print(orgzn)
        org_name.select_by_value(orgzn)
        time.sleep(1)
        
        driver.execute_script('''document.querySelectorAll("input.button.button-primary").item(9).click()''')
        time.sleep(2)
    for i in group_arr:
        assign_groups(i,client_grp)
        
    lastrepdle = driver.current_window_handle
    driver.get("https://indigov-admin.okta.com/admin/dashboard") #open setup tab
    time.sleep(10)
    print(sub+" completed")
    focus_new_tab(lastrepdle)
    #driver.find_element()
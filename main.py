from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import re
import pandas as pd

def GetEmails(html, list) :
    soup = BeautifulSoup(html, features='lxml')

    print(">>> Getting emails on page . . .")
    emails = list
    
    for a in soup.find_all('a') :
        links = a.get('href',None),a.get_text()
        for link in links :
            #print(link)
            match = re.search(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", str(link))
            if match :
                emails.append(link)
    
    #get unique results
    #emails = dict.fromkeys(emails)

    return emails


def GetCompanySitebyCompProfile(driver_service, driver_option, company_name) :
    driver = webdriver.Chrome(service=driver_service, options=driver_option)
    url = "https://www.google.com/search?q=" + company_name.replace(' ', '+')
    driver.get(url)

    try :
        company_site = driver.find_element(by=By.CLASS_NAME, value='ab_button').get_attribute('href')
        driver.quit()
        return {'rc' : True, 'result' : company_site}
    except NoSuchElementException :
        driver.quit()
        return {'rc' : False, 'result' : "Company site not found"}

def GetCompanySitebyFirstResult(driver_service, driver_option, company_name) :
    driver = webdriver.Chrome(service=driver_service, options=driver_option)
    url = "https://www.google.com/search?q=" + company_name.replace(' ', '+')
    driver.get(url)

    try :
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        links = soup.find_all('div', class_="yuRUbf")
        company_site = links[0].a.get('href')
        driver.quit()

        if "www.dnb.com" not in company_site :
            return {'rc' : True, 'result' : company_site}
        else :
            return {'rc' : False, 'result' : "First search result from D&B"}
        
    except NoSuchElementException :
        driver.quit()
        return {'rc' : False, 'result' : "Company site not found"}

        
def main(company_name) :
    chrome_service = Service('C:\\Users\\user\\Downloads\\chromedriver_win32\\chromedriver.exe')
    chrome_options = Options()
    chrome_options.binary_location = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    chrome_options.add_argument('headless')

    emails = []

    comp = GetCompanySitebyCompProfile(chrome_service, chrome_options, company_name)

    if comp['rc']==False :
        comp = GetCompanySitebyFirstResult(chrome_service, chrome_options, company_name)

    if comp['rc']==True :
        company_site = comp['result']
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        print(">>> Accessing company site at " + company_site + " . . .")
        driver.get(str(company_site))
        
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        emails = GetEmails(driver.page_source, emails)

        driver.quit()
        print(emails)
    else :
        print("<<< Not found the company website.")


if __name__ == "__main__" :
    main("alba pcb")

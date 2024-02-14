from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import time
import logging
import firebase_admin
from firebase_admin import credentials, db
import settings
import json
import retrying


'''
NOTES

'''

class Scraper():
    def __init__(self, url, usr, pwd, flashcardSetName):
        self.driver = self.setup_driver()
        self.url = url
        self.usr = usr
        self.pwd = pwd
        self.flashcardSetName = flashcardSetName

        #Connect to firebase
        self.cred = credentials.Certificate('cred.json')
        firebase_admin.initialize_app(self.cred, {'databaseURL': settings.db_url})

    def setup_driver(self):
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        self.start_time = time.time()

        self.options = webdriver.ChromeOptions()
        
        # self.options.add_argument(f"user-agent={self.user_agent}")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage

        # self.options.add_argument('--headless')

        self.options.page_load_strategy = 'eager'

        try: 
            return uc.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        except:
            pass

    def login_process(self):
        self.driver.get("https://quizlet.com/login")

        # Get elements for username and password
        userElement = self.driver.find_element(By.ID, "username")
        pwdElement = self.driver.find_element(By.ID, "password")

        #Create Mouse Object 
        action = ActionChains(self.driver)
        time.sleep(0.5)

        action.move_to_element(userElement).perform()
        for char in self.usr:
            userElement.send_keys(char)

        print("typed email")
        time.sleep(1)

        action.move_to_element(pwdElement).perform()
        for char in self.pwd:
            pwdElement.send_keys(char)
        
        time.sleep(1)
        pwdElement.send_keys(Keys.ENTER)
        print("pressed enter")

    def query(self):
        print("time @ query method: " + str(time.time()-self.start_time))

        #load page
        time.sleep(2)
        self.driver.set_page_load_timeout(15)
        try:
            self.driver.get(self.url)
        except TimeoutException:
            self.driver.execute_script("window.stop();")

        print("went to url")
        print("time " + str(time.time()-self.start_time))

        self.results = {}
        
        time.sleep(5)
        print("before it tries to get terms and definations \n")
        try:           
            root = self.driver.find_elements(By.XPATH, "//div[@class='SetPageTerms-term']")
           
            count = 0
            for x in root:
                stem = x.find_elements(By.XPATH, "//span[@class='TermText notranslate lang-en']")
                term = stem[count].text
                defination = stem[count+1].text

                count+=2
                
                self.results[str(term)] = str(defination)
            
            print("Results1: " + str(self.results))
            print("")

            self.sendtoDB(self.flashcardSetName, self.results)
            print("pushed all terms!")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

        finally:
            print("closing")
            for window_handle in self.driver.window_handles:
                self.driver.switch_to.window(window_handle)
                self.driver.close()

            self.driver.quit() #clsoe window
            print("total time" + str(time.time() - self.start_time))
            time.sleep(1)

    @retrying.retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def sendtoDB(self, ref, data):
        try:
            json_data = json.dumps(data)
            db.reference(ref).set(json_data)
        except firebase_admin.exceptions.FirebaseError as e:
            logging.error(f"Failed to send data to Firebase: {e}")
     

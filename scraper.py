from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import time
import logging
import firebase_admin
from firebase_admin import credentials, db
import settings

'''
NOTES
try inscepting the cloudflare message and tell the bot to click the checkbox

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
        self.options = webdriver.ChromeOptions()
        
        self.options.add_argument(f"user-agent={self.user_agent}")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage

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
        time.sleep(10)

    def query(self):
        print("started query method")
        time.sleep(3)

        self.driver.get(self.url)
        print("went to url")

        self.results = []
        self.results2 = []
        
        time.sleep(5)
        print("before it tries to get terms and definations \n")
        try:
            # Get the actual terms and definitions
            all = self.driver.find_elements(By.CLASS_NAME, "TermText notranslate lang-en")
            self.results.append(all)

            
            root = self.driver.find_elements(By.XPATH, "//div[@class='SetPageTerms-term']")
            print(root)
            print(len(root))
            for x in root:
                term = x.find_element(By.XPATH, "//div[@class='s1etjelq']//div[1]//div//div//span").text
                defination = x.find_element(By.XPATH, "//div[@class='s1etjelq']//div[2]//div//div//span").text

                self.results2.append({str(term):str(defination)})
            
            # Create a dictionary

            print("Results1: " + self.results)
            print("")
            print("Results2: " + self.results2)

            db.reference(str(self.flashcardSetName)).push(self.results)
            print("pushed all terms!")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

        finally:
            print("closing")
            for window_handle in self.driver.window_handles:
                self.driver.switch_to.window(window_handle)
                self.driver.close()

            self.driver.quit() #clsoe window
            time.sleep(1)

#sets up drivers

# get future quizlets
# def get_quizlet_data(driver):
#     quizlet_data = []
#     new_quizlets = driver.find_elements(By.CLASS_NAME, "chzmmzj")

#     for element in new_quizlets:
#         data = {
#             'title': element.find_element(By.CLASS_NAME, "SetPreviewCard-title").text,
#             'author': element.find_element(By.CLASS_NAME, "UserLink-username").text,
#             'link': element.find_element(By.CSS_SELECTOR, "a").get_attribute('href'),
#         }
#         quizlet_data.append(data)

#     return quizlet_data

# def main(url, filename, USR, PWD):

#     def time_checker():
#         start_time = time.time()

#         while not terminate_event.is_set():
#             elapsed_time = time.time() - start_time
#             if elapsed_time >= 60:
#                 print("60 seconds have passed.")
#                 terminate_event.set()  # Signal termination
#                 break
#             time.sleep(1)  # Adjust the sleep duration as needed


#     time_thread = threading.Thread(target=time_checker)
#     main_thread = threading.Thread(target=inner_main)
#     # Start both threads
#     time_thread.start()
#     main_thread.start()

#     # Wait for the main thread to finish (if needed)
#     main_thread.join()

#     # Optionally wait for the time thread to finish (if needed)
#     time_thread.join()
    



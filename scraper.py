from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import threading
import logging
import firebase_admin
from firebase_admin import credentials, db
import settings

#Connect to firebase
cred = credentials.Certificate('cred.json')
firebase_admin.initialize_app(cred, {'databaseURL': settings.db_url})




def test():
    return "testing"

#sets up drivers
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.page_load_strategy = 'normal'
  
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#get future quizlets
def get_quizlet_data(driver):
    quizlet_data = []
    new_quizlets = driver.find_elements(By.CLASS_NAME, "chzmmzj")

    for element in new_quizlets:
        data = {
            'title': element.find_element(By.CLASS_NAME, "SetPreviewCard-title").text,
            'author': element.find_element(By.CLASS_NAME, "UserLink-username").text,
            'link': element.find_element(By.CSS_SELECTOR, "a").get_attribute('href'),
        }
        quizlet_data.append(data)

    return quizlet_data


def main(url, filename, USR, PWD):
    driver = setup_driver()

    #Go to login page
    driver.get("https://quizlet.com/login")

    # Get elements for username and password
    user = driver.find_element(By.ID, "username")
    pwd = driver.find_element(By.ID, "password")

    #Create Mouse Object 
    action = ActionChains(driver)
    time.sleep(2)
    action.move_to_element(user).perform()
    time.sleep(90)

    for char in USR:
        user.send_keys(char)
    time.sleep(2)
    pwd.send_keys(PWD)
    time.sleep(2)
    pwd.send_keys(Keys.ENTER)

    time.sleep(50)

    # driver.get(url)

    # Event to signal threads to terminate
    terminate_event = threading.Event()

    def inner_main():
        start_time = time.time()
        results = {}
        logging.basicConfig(level=logging.INFO)

        #Actual scraping logic
        try:
            # Get the actual terms and definitions
            terms = driver.find_elements(By.CLASS_NAME, "SetPageTerm-wordText")
            definitions = driver.find_elements(By.CLASS_NAME, "SetPageTerm-definitionText")

            # Create a dictionary
            for x in range(len(terms)):
                results[str(terms[x].text)] = str(definitions[x].text)


            end_time = time.time()
            total_time = end_time - start_time
            logging.info(f'Total time taken: {total_time} seconds')

            db.reference(str(filename)).push(results)

            # return name_of_file

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

        finally:
            terminate_event.set()  # Signal termination
            driver.quit() #clsoe window

    def time_checker():
        start_time = time.time()

        while not terminate_event.is_set():
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60:
                print("60 seconds have passed.")
                terminate_event.set()  # Signal termination
                break
            time.sleep(1)  # Adjust the sleep duration as needed


    time_thread = threading.Thread(target=time_checker)
    main_thread = threading.Thread(target=inner_main)
    # Start both threads
    time_thread.start()
    main_thread.start()

    # Wait for the main thread to finish (if needed)
    main_thread.join()

    # Optionally wait for the time thread to finish (if needed)
    time_thread.join()
    



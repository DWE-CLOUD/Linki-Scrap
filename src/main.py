import sys

from fastapi import FastAPI, HTTPException
from fastapi.openapi.models import License
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from selenium import webdriver
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
from pathlib import Path
import uuid
from dotenv import load_dotenv
from urllib.parse import urlparse
import logging

load_dotenv()

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('profile_scraper.log'),
                        logging.StreamHandler(sys.stdout)
                    ])

class ProfileURL(BaseModel):
    url: str


class OTP(BaseModel):
    otp: str


class LoginResponse(BaseModel):
    message: str
    logged_in: bool


class LinkedInScraper:
    def __init__(self):
        self.driver = None
        self.output_dir = Path("profile_sources")
        self.output_dir.mkdir(exist_ok=True)
        self.otp_needed = False

    def initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--headless')  # Comment this out to test in main env .. To test in head mode
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument(
            f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        chrome_options.add_argument("--user-data-dir=/tmp/user-data")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        service = Service(executable_path='/usr/local/bin/chromedriver')
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(random.uniform(2, 6))
            #logging.info("Driver initialized successfully.")
        except Exception as e:
            #logging.error(f"Driver initialization error: {str(e)}")
            raise e

    def login(self, otp=None):
        logging.info("Attempting login...")
        if not self.driver:
            self.initialize_driver()

        try:
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(random.uniform(2, 4))

            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

            username_field.send_keys(os.getenv('LINKEDIN_USERNAME'))
            password_field.send_keys(os.getenv('LINKEDIN_PASSWORD'))
            submit_button.click()

            time.sleep(random.uniform(3, 5))

            if self.needs_otp():
                if otp:
                    if self.submit_otp(otp):
                        logging.info("Logged in with OTP successfully.")
                        return LoginResponse(message="Logged in with OTP", logged_in=True)
                    else:
                        logging.warning("OTP submission failed.")
                        return LoginResponse(message="OTP submission failed", logged_in=False)
                else:
                    logging.warning("OTP Required")
                    return LoginResponse(message="OTP Required", logged_in=False)
            elif self.is_logged_in_check():
                logging.info("Logged in successfully.")
                return LoginResponse(message="Logged in successfully", logged_in=True)
            else:
                logging.warning("Login failed, check credentials")
                return LoginResponse(message="Login failed, check credentials", logged_in=False)

        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            return LoginResponse(message="Login failed, check credentials", logged_in=False)

    def is_logged_in_check(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav")))
            return True
        except:
            return False

    def needs_otp(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='input__phone_verification_pin']"))
            )
            return True
        except:
            return False

    def submit_otp(self, otp):
        try:
            logging.info("Attempting to submit OTP...")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='input__phone_verification_pin']"))
            )
            otp_field = self.driver.find_element(By.XPATH, "//*[@id='input__phone_verification_pin']")
            if otp_field:
                logging.info("OTP field found.")
            else:
                logging.warning("OTP field NOT found.")
                return False
            otp_field.send_keys(otp)
            logging.info("OTP entered.")

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            if submit_button:
                logging.info("Submit button found.")
            else:
                logging.warning("Submit button NOT found.")
                return False
            submit_button.click()
            logging.info("Submit button clicked.")

            time.sleep(random.uniform(3, 5))

            if self.is_logged_in_check():
                logging.info("OTP submission successful")
                return True
            logging.warning("OTP submission not successful.")
            return False

        except Exception as e:
            logging.error(f"OTP submission failed: {str(e)}")
            return False

    def is_linkedin_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc == "www.linkedin.com"

    def has_scheme(self, url):
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme)

    def get_base_url(self, url):
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    import re
    def get_profile_source(self, profile_url):
        try:
            logging.info(f"Attempting to open profile URL: {profile_url}")

            # Building url
            if self.is_linkedin_url(profile_url):
                logging.info(f"It's a LinkedIn URL, navigating to: {profile_url}")
                url_to_navigate = profile_url
            else:
                if not self.has_scheme(profile_url):
                    logging.info(f"Adding https:// scheme to: {profile_url}")
                    profile_url = f"https://{profile_url}"

                logging.info(f"Not a LinkedIn URL, navigating to: {profile_url}")
                url_to_navigate = profile_url

            logging.info(f"Navigating to: {url_to_navigate}")

            # nav to given url
            self.driver.get(url_to_navigate)
            time.sleep(random.uniform(1, 2))

            logging.info(f"Navigated to {self.driver.current_url}")

            # current url
            current_url = self.driver.current_url
            current_base_url = self.get_base_url(current_url)

            # profile url
            profile_base_url = self.get_base_url(url_to_navigate)

            # re check current with base
            if current_base_url != profile_base_url:
                logging.warning(f"Profile URL doesn't match, Expected: {profile_base_url}, Actual: {current_url}")
                raise HTTPException(status_code=500, detail="Profile URL doesn't match")

            # Begin Scraping
            profile_data = {}

            # Extract name using XPath
            try:
                name_element = self.driver.find_element(By.XPATH, '//*[@id="profile-content"]//h1')
                profile_data['name'] = name_element.text.strip()
            except:
                profile_data['name'] = 'Not Found'

            # Extract about using xpath
            try:
                about_element = self.driver.find_element(By.XPATH,
                                                         '//*[@id="profile-content"]/div/div[2]/div/div/main/section[2]/div[3]/div/div/div/span[1]')
                profile_data['about'] = about_element.text.strip()
            except:
                profile_data['about'] = 'Not Found'

            # Extract work experience
            profile_data['work_experience'] = []
            try:
                experience_section = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[5]'))
                )
                experience_elements = experience_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
                for index, exp_element in enumerate(experience_elements):
                    try:
                        title_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[5]/div[3]/ul/li[{index + 1}]/div/div[2]/div[1]/div/div/div/div/div/span[1]'
                        company_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[5]/div[3]/ul/li[{index + 1}]/div/div[2]/div[1]/div/span[1]/span[1]'
                        duration_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[5]/div[3]/ul/li[{index + 1}]/div/div[2]/div[1]/div/span[2]/span[1]'
                        location_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[5]/div[3]/ul/li[{index + 1}]/div/div[2]/div[1]/div/span[3]/span[1]'
                        about_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[5]/div[3]/ul/li[{index + 1}]/div/div[2]/div[2]/ul/li[1]/div'

                        title_element = exp_element.find_element(By.XPATH, title_xpath) if exp_element.find_elements(
                            By.XPATH, title_xpath) else None
                        company_element = exp_element.find_element(By.XPATH,
                                                                   company_xpath) if exp_element.find_elements(By.XPATH,
                                                                                                               company_xpath) else None
                        duration_element = exp_element.find_element(By.XPATH,
                                                                    duration_xpath) if exp_element.find_elements(
                            By.XPATH, duration_xpath) else None
                        location_element = exp_element.find_element(By.XPATH,
                                                                    location_xpath) if exp_element.find_elements(
                            By.XPATH, location_xpath) else None
                        about_element = exp_element.find_element(By.XPATH, about_xpath) if exp_element.find_elements(
                            By.XPATH, about_xpath) else None

                        experience_entry = {}
                        if title_element:
                            experience_entry['title'] = title_element.text.strip()
                        if company_element:
                            experience_entry['company'] = company_element.text.strip()
                        if duration_element:
                            experience_entry['duration'] = duration_element.text.strip()
                        if location_element:
                            experience_entry['location'] = location_element.text.strip()
                        if about_element:
                            experience_entry['about'] = about_element.text.strip()

                        profile_data['work_experience'].append(experience_entry)

                    except Exception as e:
                        logging.warning(
                            f"Could not extract data from work experience element at index {index}: {exp_element.text} because of {e}")
            except:
                logging.warning("No Work experience found")

            # Extract education
            profile_data['education'] = []
            try:
                education_section = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[6]'))
                )
                education_elements = education_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
                for index, edu_element in enumerate(education_elements):
                    try:
                        institution_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[6]/div[3]/ul/li[{index + 1}]/div/div[2]/div[1]/a/div/div/div/div/span[1]'
                        degree_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[6]/div[3]/ul/li[{index + 1}]/div/div[2]/div[1]/a/span[1]/span[1]'
                        duration_xpath = f'//*[@id="profile-content"]/div/div[2]/div/div/main/section[6]/div[3]/ul/li[{index + 1}]/div/div[2]/div[1]/a/span[2]/span[1]'

                        institution_element = edu_element.find_element(By.XPATH,
                                                                       institution_xpath) if edu_element.find_elements(
                            By.XPATH, institution_xpath) else None
                        degree_element = edu_element.find_element(By.XPATH, degree_xpath) if edu_element.find_elements(
                            By.XPATH, degree_xpath) else None
                        duration_element = edu_element.find_element(By.XPATH,
                                                                    duration_xpath) if edu_element.find_elements(
                            By.XPATH, duration_xpath) else None

                        education_entry = {}
                        if institution_element:
                            education_entry['institution'] = institution_element.text.strip()

                        if degree_element:
                            education_entry['degree'] = degree_element.text.strip()
                            if duration_element:
                                education_entry['duration'] = duration_element.text.strip()
                        else:
                            education_entry['degree'] = "NA"
                            if duration_element:
                                education_entry['duration'] = duration_element.text.strip()

                        profile_data['education'].append(education_entry)
                    except Exception as e:
                        logging.warning(
                            f"Could not extract data from education element at index {index}: {edu_element.text} because of {e}")
            except:
                logging.warning("No Education found")

            # Extract Skills
            profile_data['skills'] = []
            try:
                # Scroll to the bottom of the page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))  # add a small time out

                button_container = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[9]/div[3]/div/div/div'))
                )

                show_all_skills_button = button_container.find_element(By.CSS_SELECTOR, 'a')

                # Scroll the button to view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all_skills_button)
                self.driver.execute_script("arguments[0].click();", show_all_skills_button)
                time.sleep(1)
                if 'skills' not in self.driver.current_url.lower():
                    self.driver.back()
                    button_container = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             '//*[@id="profile-content"]/div/div[2]/div/div/main/section[8]/div[3]/div/div/div'))
                    )
                    show_all_skills_button = button_container.find_element(By.CSS_SELECTOR, 'a')

                    # Viewport
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all_skills_button)
                    self.driver.execute_script("arguments[0].click();", show_all_skills_button)

                # wait for 1 skill
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                         "li.pvs-list__paged-list-item.artdeco-list__item.pvs-list__item--line-separated.pvs-list__item--one-column"))
                )
                # comb class
                skill_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                           "li.pvs-list__paged-list-item.artdeco-list__item.pvs-list__item--line-separated.pvs-list__item--one-column")
                for skill_element in skill_elements:
                    try:
                        span_elements = skill_element.find_elements(By.CSS_SELECTOR, 'span')
                        if span_elements and span_elements[0].text.strip():
                            profile_data['skills'].append(span_elements[0].text.strip())
                    except Exception as e:
                        logging.warning(
                            f"Could not extract data from skill element: {skill_element.text} because of: {e}")
            except Exception as e:
                logging.warning(f"No Skills found because of: {e}")

            #Licenses

            profile_data['license'] = []
            self.driver.back()
            time.sleep(2)
            button_containl = WebDriverWait(self.driver, 4).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[8]/div[3]/div/div/div'))
            )

            show_all_license_button = button_containl.find_element(By.CSS_SELECTOR, 'a')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all_license_button)
            self.driver.execute_script("arguments[0].click();", show_all_license_button)
            time.sleep(1)
            if 'certifications' not in self.driver.current_url.lower():
                self.driver.back()
                button_containl = WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '//*[@id="profile-content"]/div/div[2]/div/div/main/section[7]/div[3]/div/div/div'))
                )
                show_all_license_button = button_containl.find_element(By.CSS_SELECTOR, 'a')

                self.driver.execute_script("arguments[0].scrollIntoView(true);", show_all_license_button)
                self.driver.execute_script("arguments[0].click();", show_all_license_button)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     "li.pvs-list__paged-list-item.artdeco-list__item.pvs-list__item--line-separated.pvs-list__item--one-column"))
            )
            # Find the license
            license_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                       "li.pvs-list__paged-list-item.artdeco-list__item.pvs-list__item--line-separated.pvs-list__item--one-column")
            for license_element in license_elements:
                try:
                    span_elements = license_element.find_elements(By.CSS_SELECTOR, 'span')
                    if span_elements and span_elements[0].text.strip():
                        profile_data['license'].append(span_elements[0].text.strip())
                except Exception as e:
                    logging.warning(
                        f"Could not extract data from license element: {license_element.text} because of: {e}")

            logging.info("Successfully scraped profile data")
            return profile_data

        except Exception as e:
            logging.error(f"Error opening profile URL: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to open profile URL: {str(e)}")

scraper = LinkedInScraper()


@app.post("/login", response_model=LoginResponse)
async def login(otp: OTP = None):
    if otp:
        login_response = scraper.login(otp.otp)
    else:
        login_response = scraper.login()
    return login_response


@app.get("/health")
async def health_check():
    return {"status": "healthy", "logged_in": True}


@app.post("/profile/download")
async def get_profile(profile: ProfileURL):
    try:
        response = scraper.get_profile_source(profile.url)
        return JSONResponse(content=response)

    except HTTPException as e:
        raise e


@app.on_event("startup")
async def startup_event():
    scraper.initialize_driver()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
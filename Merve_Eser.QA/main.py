import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

class InsiderTestAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None

    def setup_browser(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        service = Service("chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 15)

        # Ensure the screenshots directory exists
    def take_screenshot(self, test_name):
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{test_name}_{timestamp}.png"
        self.driver.save_screenshot(filename)

    # Scroll slowly to ensure all elements load
    def scroll_slowly(self, pixels=2000):
        current = 0
        while current < pixels:
            self.driver.execute_script(f"window.scrollTo(0, {current});")
            time.sleep(0.5)
            current += 200
   
   #test home page
    def test_homepage(self):
        try:
            self.driver.get("https://useinsider.com/")
            time.sleep(3)

            current_url = self.driver.current_url
            return "useinsider.com" in current_url
        except Exception:
            self.take_screenshot("homepage_error")
            return False
    
    # Test careers navigation
    def test_careers_navigation(self):
        try:
            company_menu = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Company')]"))
            )
            company_menu.click()
            time.sleep(5)

            careers_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Careers')]"))
            )
            careers_link.click()
            time.sleep(10)

            # Scroll slowly to ensure all sections are visible
            self.scroll_slowly(2500)

            sections = {
                'teams': "//a[contains(text(), 'See all teams') or contains(text(), 'Find your calling')]",
                'locations': "//*[contains(text(), 'Our Locations')]",
                'life': "//*[contains(text(), 'Life at Insider')]"
            }

            results = {}
            for key, xpath in sections.items():
                try:
                    self.driver.find_element(By.XPATH, xpath)
                    results[key] = True
                except:
                    results[key] = False

            return all(results.values())
        except Exception:
            self.take_screenshot("careers_error")
            return False

    def test_qa_jobs(self):
        try:
            # Go to QA landing page
            self.driver.get("https://useinsider.com/careers/quality-assurance/")
            time.sleep(5)

            # Go to open positions page (with QA department filter in URL)
            self.driver.get("https://useinsider.com/careers/open-positions/?department=qualityassurance")
            time.sleep(12)  # wait longer to ensure all content loads

            # Apply Location filter - Istanbul, Turkiye
            location_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "filter-by-location"))
            )
            Select(location_dropdown).select_by_visible_text("Istanbul, Turkiye")
            time.sleep(10)

            # Apply Department filter - Quality Assurance
            department_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "filter-by-department"))
            )
            Select(department_dropdown).select_by_visible_text("Quality Assurance")
            time.sleep(10)

            # Scroll slowly
            self.scroll_slowly(1000)
            time.sleep(12)

            # Get job listings
            job_list = self.driver.find_elements(By.CSS_SELECTOR, ".position-list-item")

            if not job_list:
                return False

            first_job = job_list[0]
            actions = ActionChains(self.driver)
            actions.move_to_element(first_job).perform()
            time.sleep(2)

            view_role_btn = first_job.find_element(By.XPATH, ".//a[contains(text(), 'View Role')]")
            self.driver.execute_script("arguments[0].scrollIntoView();", view_role_btn)
            time.sleep(2)
            view_role_btn.click()
            time.sleep(5)

            return True

        except Exception as e:
            print(f"Error in test_qa_jobs: {e}")
            return False

    def run_all_tests(self):
        test_results = {}

        try:
            self.setup_browser()

            test_results['homepage'] = self.test_homepage()
            test_results['careers'] = self.test_careers_navigation()
            test_results['qa_jobs'] = self.test_qa_jobs()
            
        except Exception:
            pass
        finally:
            if self.driver:
                self.driver.quit()

        self.show_results(test_results)

    def show_results(self, results):
        total = len(results)
        passed = sum(1 for r in results.values() if r)

        for test_name, result in results.items():
            print(f"{test_name}: {'PASSED' if result else 'FAILED'}")

        print(f"Total: {total}, Passed: {passed}, Failed: {total - passed}")

if __name__ == "__main__":
    if not os.path.exists("chromedriver.exe"):
        print("chromedriver.exe not found.")
        print("Download it and place it in this folder: https://chromedriver.chromium.org/")
        exit()

    tester = InsiderTestAutomation()
    tester.run_all_tests()

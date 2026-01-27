import time
from datetime import datetime
from typing import Optional, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from .utils import handle_popups

def ensure_on_diary_page(driver, data: Optional[Dict] = None, wait_for_user=True):
    target_url = "https://vtu.internyet.in/dashboard/student/student-diary"
    
    if target_url in driver.current_url:
         if is_selection_page(driver):
             handle_selection_page(driver, data, wait_for_user)
         return

    try:
        handle_popups(driver)
        driver.get(target_url)
        time.sleep(4)
        handle_popups(driver)
        
        if is_selection_page(driver):
            handle_selection_page(driver, data, wait_for_user)
            
    except Exception as e:
        print(f"[VTU] Navigation failed: {e}")

def is_selection_page(driver):
    return len(driver.find_elements(By.NAME, "internship_id")) > 0

def handle_selection_page(driver, data: Optional[Dict] = None, wait_for_user=True):
    print("[VTU] Filling selection form...")
    wait = WebDriverWait(driver, 10)
    
    # 1. Select Internship
    try:
        # Try finding the internship select button/input
        intern_btn = None
        for selector in [(By.ID, "internship_id"), (By.NAME, "internship_id")]:
            try:
                intern_btn = driver.find_element(*selector)
                break
            except:
                continue
        
        if intern_btn:
            intern_btn.click()
            time.sleep(1)
            
            # Select first available option
            options = driver.find_elements(By.XPATH, "//div[@role='option'] | //*[contains(@class, 'select-item')]")
            if options:
                options[0].click()
            else:
                # Fallback JS
                driver.execute_script("document.getElementsByName('internship_id')[0].selectedIndex = 1;")
                driver.execute_script("document.getElementsByName('internship_id')[0].dispatchEvent(new Event('change'));")
    except Exception as e:
        print(f"[VTU] Internship select warning: {e}")
        try:
            driver.execute_script("document.getElementsByName('internship_id')[0].selectedIndex = 1;")
        except:
            pass
    
    # 2. Select Date
    target_date = data.get("date") if data else None
    day = str(datetime.now().day)
    
    if target_date:
        try:
            day = str(int(target_date.split('-')[2]))
        except:
            pass

    try:
        # Open calendar
        date_btn = driver.find_element(By.XPATH, "//button[contains(., 'Pick a Date') or contains(., 'Date')]")
        driver.execute_script("arguments[0].click();", date_btn)
        time.sleep(1) # Wait for popover
        
        # Pick Day
        day_found = False
        # Improved selectors from original working codebase
        day_selectors = [
            (By.XPATH, f"//button[text()='{day}']"),
            (By.XPATH, f"//div[contains(@class, 'day') and text()='{day}']"),
            (By.XPATH, f"//*[not(self::script) and text()='{day}']")
        ]
        
        for by, sel in day_selectors:
            try:
                # Find visible elements only
                elements = driver.find_elements(by, sel)
                for el in elements:
                    if el.is_displayed():
                        el.click()
                        day_found = True
                        break
                if day_found: break
            except:
                continue
                
        if not day_found:
             print(f"[VTU] ⚠ Could not auto-select day {day}. Please select manually.")
             
    except Exception as e:
        print(f"[VTU] Date selection warning: {e}")
        
    # 3. Continue
    try:
        btn = driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Continue')]")
        driver.execute_script("arguments[0].removeAttribute('disabled');", btn)
        if not wait_for_user:
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
    except Exception:
        pass

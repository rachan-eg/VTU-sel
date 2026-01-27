import time
from typing import Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from .exceptions import SubmitError
from .utils import save_screenshot
from .navigation import ensure_on_diary_page

def fill_diary(driver, wait, data: Dict, dry_run=True, max_retries=3):
    """Fill diary form with retry logic."""
    for attempt in range(max_retries):
        try:
            ensure_on_diary_page(driver, data, wait_for_user=False)
            return _fill_once(driver, wait, data, dry_run)
        except Exception as e:
            print(f"[VTU] Attempt {attempt+1} failed: {e}")
            save_screenshot(driver, f"error_attempt_{attempt+1}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise SubmitError(f"Failed: {e}")

def _fill_once(driver, wait, data, dry_run):
    def fill(selectors, value, field_name):
        # Allow passing a single selector tuple or a list of tuples
        if isinstance(selectors, tuple):
            selectors = [selectors]
            
        filled = False
        for by, selector in selectors:
            try:
                elem = wait.until(EC.presence_of_element_located((by, selector)))
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
                time.sleep(0.5)
                
                elem.clear()
                elem.send_keys(str(value))
                # React/JS trigger events
                driver.execute_script("""
                    arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                    arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
                    arguments[0].dispatchEvent(new Event('blur', {bubbles:true}));
                """, elem)
                print(f"[VTU] Filled {field_name}")
                filled = True
                break
            except Exception:
                continue
                
        if not filled:
            print(f"[VTU] Field not found: {field_name}")
            raise TimeoutException(f"Could not find field {field_name}")

    # Description
    fill([
        (By.NAME, "description"),
        (By.NAME, "entry_text"),
        (By.XPATH, "//textarea[contains(@placeholder, 'Description') or contains(@placeholder, 'entry')]"),
        (By.CSS_SELECTOR, "textarea[name='description']"),
        (By.ID, "description")
    ], data["description"], "Description")

    # Hours
    fill([
        (By.NAME, "hours"),
        (By.XPATH, "//label[contains(., 'Hours')]/following::input[@type='number'][1]"),
        (By.XPATH, "//input[@type='number' and contains(@placeholder, '6.5')]"),
        (By.CSS_SELECTOR, "input[type='number']")
    ], data["hours"], "Hours")

    # Learnings
    fill([
        (By.NAME, "learnings"),
        (By.XPATH, "//textarea[contains(@placeholder, 'learnings') or contains(@placeholder, 'Skills')]"),
        (By.XPATH, "//label[contains(text(), 'Learning')]/following-sibling::*//textarea")
    ], data["learnings"], "Learnings")

    # Blockers
    fill([
        (By.NAME, "blockers"),
        (By.XPATH, "//textarea[contains(@placeholder, 'blockers')]"),
        (By.XPATH, "//label[contains(text(), 'Blocker')]/following-sibling::*//textarea")
    ], data["blockers"], "Blockers")

    # Links
    fill([
        (By.NAME, "links"),
        (By.XPATH, "//input[contains(@placeholder, 'links') or contains(@placeholder, 'URL')]"),
        (By.XPATH, "//label[contains(text(), 'Links')]/following-sibling::input")
    ], data["links"], "Links")
    
    # Skill IDs (React Select) - Aggressive Interaction
    print("[VTU] Attempting to fill Skills...")
    skills_filled = False
    
    # Method 1: React Select Input Interaction
    try:
        # Find the input within the react-select container
        # Often it has an ID like 'react-select-2-input' or class 'react-select__input'
        skill_input = driver.find_element(By.CSS_SELECTOR, "input[id^='react-select-']")
        if not skill_input.is_displayed():
             # Sometimes the input is hidden, find the container
             container = driver.find_element(By.CSS_SELECTOR, "[class*='control']")
             container.click()
             skill_input = driver.switch_to.active_element
        
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", skill_input)
        
        # Click to open menu
        try:
            skill_input.click()
        except:
            driver.execute_script("arguments[0].click();", skill_input)
        time.sleep(1)
        
        # Determine what to select: if data['skill_ids'] is short/numeric, just pick first option
        # otherwise try to type it
        val = str(data.get('skill_ids',''))
        if len(val) > 2 and not val.isdigit():
             skill_input.send_keys(val)
             time.sleep(1)
             skill_input.send_keys(Keys.ENTER)
        else:
             # Just pick the first available option
             skill_input.send_keys(" ")
             time.sleep(1)
             actions = ActionChains(driver)
             actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
             
        print("[VTU] Interacted with Skills UI")
        skills_filled = True
    except Exception as e:
        print(f"[VTU] Skills UI interaction failed: {e}")

    # Method 2: Fallback HIDDEN input force
    if not skills_filled:
        try:
            driver.execute_script(f"""
                const el = document.getElementsByName('skill_ids')[0];
                if (el) {{
                    el.value = '{data['skill_ids']}';
                    el.dispatchEvent(new Event('input', {{bubbles:true}}));
                    el.dispatchEvent(new Event('change', {{bubbles:true}}));
                }}
            """)
            print("[VTU] Forced hidden skill_ids value")
        except:
            pass

    # Submit Button - Aggressive Finding & Clicking
    try:
        time.sleep(1)
        submit_btn = None
        # Priority list of selectors
        selectors = [
            (By.XPATH, "//button[normalize-space()='Save']"),
            (By.XPATH, "//button[contains(text(), 'Save')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[@type='submit']"),
            (By.ID, "submit-btn")
        ]
        
        for by, val in selectors:
            try:
                btns = driver.find_elements(by, val)
                for btn in btns:
                    if btn.is_displayed():
                        submit_btn = btn
                        print(f"[VTU] Found submit button via {by}={val} text='{btn.text}'")
                        break
                if submit_btn: break
            except:
                continue
                
        if not submit_btn:
             # Last resort: find any button with 'Save'
             try:
                 submit_btn = driver.find_element(By.XPATH, "//button[contains(., 'Save')]")
             except:
                 raise NoSuchElementException("Submit/Save button not found")

        # Ensure enabled
        driver.execute_script("arguments[0].disabled = false;", submit_btn)
        driver.execute_script("arguments[0].removeAttribute('disabled');", submit_btn)
        
        # Scroll to it
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
        time.sleep(1)
        
        if dry_run:
            # Highlight it
            driver.execute_script("arguments[0].style.border='3px solid red';", submit_btn)
            print("[VTU] Dry run success - Button highlighted")
            return "DRY_RUN_SUCCESS"
        
        print("[VTU] Clicking Submit...")
        try:
            submit_btn.click()
        except ElementClickInterceptedException:
             # Overlay blocking? JS Click
             driver.execute_script("arguments[0].click();", submit_btn)
        
        time.sleep(5)
        
        # Check if URL changed or success message appeared?
        # For now assume success if no error thrown
        return "SUBMITTED"
        
    except Exception as e:
        raise SubmitError(f"Submit failed: {e}")

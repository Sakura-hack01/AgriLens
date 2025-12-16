import time
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
download_folder = r"C:\Users\Saket Dixit\Downloads\Agro Sentinel\data\raw"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)
  
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": download_folder}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

BASE_URL = "https://fcainfoweb.nic.in/Reports/Report_Menu_Web.aspx"

try:
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 30) # Increased wait time
    print(">>> Website Opened.")

    for i in range(365):
        target_date = datetime.now() - timedelta(days=i+1)
        date_str = target_date.strftime("%d/%m/%Y")
        print(f"\n==========================================")
        print(f"Processing Date: {date_str}")
        print(f"==========================================")
        try:
            print("  1. Filling form...")
            report_type_dd = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_Ddl_Rpt_type")))
            Select(report_type_dd).select_by_visible_text("Retail")
            time.sleep(3)
          
            lang_dd_elem = wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ddl_Language")))
            Select(lang_dd_elem).select_by_visible_text("English")
            time.sleep(3) 
          
            price_rpt_radio = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_Rbl_Rpt_type_0")))
            price_rpt_radio.click()
            time.sleep(3)
          
            rpt_option_dd = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_Ddl_Rpt_Option0")))
            Select(rpt_option_dd).select_by_visible_text("Daily Prices")
            print("     > Selected 'Daily Prices'. Waiting 5s for page reload...")
            time.sleep(5)
            # Enter Date
            date_input = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_Txt_FrmDate")))
            date_input.clear()
            date_input.send_keys(date_str)
            driver.find_element(By.TAG_NAME, 'body').click() 
            time.sleep(2)

        except Exception as e:
            print(f"  !!! Error filling form: {e}")
            driver.refresh()
            time.sleep(5)
            continue
          
        max_retries = 5
        success = False
        
        for attempt in range(max_retries):
            try:
                print(f"  --- Captcha Attempt {attempt+1}/{max_retries} ---")
                
                captcha_elem = wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_captchalogin")))
                screenshot = captcha_elem.screenshot_as_png
                image = Image.open(io.BytesIO(screenshot))

                image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
                image = image.convert('L')
                image = image.point(lambda x: 0 if x < 140 else 255, '1')
                custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
                captcha_text = pytesseract.image_to_string(image, config=custom_config).strip().replace(" ", "")
                
                print(f"      > Read Code: '{captcha_text}'")
                
                if len(captcha_text) < 3: 
                    continue
                  
                input_box = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_MainContent_Captcha")))
                input_box.click()
                input_box.clear()
                input_box.send_keys(captcha_text)
                time.sleep(1)

                # Click Get Data
                get_data_btn = driver.find_element(By.ID, "ctl00_MainContent_btn_getdata1")
                driver.execute_script("arguments[0].scrollIntoView(true);", get_data_btn)
                time.sleep(0.5)
                get_data_btn.click()
              
                try:
                     excel_btn = WebDriverWait(driver, 5).until(
                        EC.any_of(
                            EC.element_to_be_clickable((By.ID, "btnsave")),
                            EC.element_to_be_clickable((By.XPATH, "//input[contains(@src, 'Excel')]")),
                            EC.element_to_be_clickable((By.XPATH, "//input[contains(@src, 'xls')]"))
                        )
                    )
                     excel_btn.click()
                     print(f"      >>> SUCCESS: Downloading data for {date_str}")
                     time.sleep(5) 
                     success = True
                     break 

                except TimeoutException:
                    # Check for Alert (Wrong Captcha)
                    try:
                        alert = driver.switch_to.alert
                        print(f"      ! Alert: {alert.text}")
                        alert.accept()
                    except:
                        pass
                    print("      ! Retrying...")
                    continue

            except Exception as e:
                print(f"      ! Error: {e}")
                continue

        if not success:
            print(f"  !!! Failed {date_str}")

        try:
            print("  6. Going Back...")
            back_btn = WebDriverWait(driver, 10).until(
                EC.any_of(
                     EC.element_to_be_clickable((By.ID, "btn_back")),
                     EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Back')]")),
                     EC.element_to_be_clickable((By.XPATH, "//input[@value='Back']"))
                )
            )
            driver.execute_script("arguments[0].click();", back_btn)
            
            wait.until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_Ddl_Rpt_type")))
            print("  > Returned to menu.")
            time.sleep(3)
            
        except:
            print("  ! Could not go back. Refreshing page.")
            driver.get(BASE_URL)

finally:
    print("Done.")
    driver.quit()

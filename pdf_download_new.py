from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import requests

driver = webdriver.Chrome()
driver.get("https://ceoelection.maharashtra.gov.in/searchlist/")

# Find the district dropdown element
district_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ctl00_Content_DistrictList"))
)
district_select = Select(district_dropdown)
time.sleep(5)

# Select Assembly Constituency
assembly_dropdown = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ctl00_Content_AssemblyList"))
)
# Get the number of assembly options
assembly_options = driver.find_elements(By.CSS_SELECTOR, "#ctl00_Content_AssemblyList option")
num_assemblies = len(assembly_options)
print(num_assemblies)

# Iterate through the assembly options
for i in range(1, num_assemblies):

    assembly_dropdown = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "ctl00_Content_AssemblyList"))
    )
    assembly_dropdown.send_keys(str(i))
    # Wait for the assembly selection to be applied
    time.sleep(3)
    # Get the number of part options within the current assembly
    part_options = driver.find_elements(By.CSS_SELECTOR, "#ctl00_Content_PartList option")
    num_parts = len(part_options)
    #print('##########################################################')
    #print(num_parts)

    # Iterate through the part options and download the PDFs
    for j in range(1, num_parts):

        part_dropdown = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "ctl00_Content_PartList"))
        )
        part_dropdown.send_keys(str(j))
        # Wait for the part selection to be applied
        time.sleep(8)

        captcha_image = driver.find_element(By.CSS_SELECTOR, "img[src='Captcha.aspx']")

        captcha_image_src = captcha_image.get_attribute("src")

        #request to 2Captcha to solve the captcha
        response = requests.get(f"http://2captcha.com/in.php?key=ffc80214c668abe8e99e9508309c830b&method=base64&body={captcha_image_src}")
        response_json = response.json()
        captcha_id = response_json["request"]

        # Poll 2Captcha for the solved captcha
        while True:
            response = requests.get(f"http://2captcha.com/res.php?key=ffc80214c668abe8e99e9508309c830b&action=get&id={captcha_id}")
            response_json = response.json()
            if response_json["status"] == 1:
                captcha_solution = response_json["text"]
                break
            time.sleep(5)

        captcha_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_Content_txtcaptcha"))
        )
        captcha_input.send_keys(captcha_solution)
        print(captcha_solution)

        open_pdf_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_Content_OpenButton"))
        )
        open_pdf_button.click()

        WebDriverWait(driver, 10).until(
            lambda d: len(driver.window_handles) == 2  
        )

        driver.switch_to.window(driver.window_handles[1])

        pdf_url = driver.current_url

        save_path = f"voter_list_downloaded_pdf\_Assembly_{i}_Part_{j}.pdf"

        # Download the PDF
        response = requests.get(pdf_url)
        with open(save_path, "wb") as file:
            file.write(response.content)

        time.sleep(10)

        driver.close()

        driver.switch_to.window(driver.window_handles[0])

driver.quit()

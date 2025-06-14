from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import json
import re
import random
from bs4 import BeautifulSoup
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from proxies_extraction import extract_valid_proxies
import os

class get_papers(extract_valid_proxies):
    def __init__(self):
        driver_path='/Users/drago/Documents/chromedriver-mac-arm64_V137/chromedriver'
        # self.service = Service(ChromeDriverManager().install())
        valid_proxies=self.check_proxies()
        self.download_dir=f'/Users/drago/Documents/Practicefiles/Data_files/Scihub_papers'

        # Make sure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)

        # Setup Chrome options for download_directory
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            "download.default_directory": self.download_dir,  # ✅ Set your desired path
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True  # ✅ Ensures it doesn't open in-browser
        })
        service = Service(driver_path)
        if len(valid_proxies)==0:
            print ("No valid proxies")
            
            self.driver = webdriver.Chrome(service=service,options=chrome_options)
        else:
            print(f'Number of valid proxies is {len(valid_proxies)}')
            proxy = random.choice(valid_proxies)
            ip, port, username, password = proxy.split(':')
            # Create the extension
            self.plugin_file_path = self.create_proxy_extension(ip, port, username, password)
            chrome_options.add_extension(self.plugin_file_path)
            
            self.driver = webdriver.Chrome(service=service,options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
    
    def open_mainpage(self):
        self.driver.get('https://sci-hub.se/')
    
    def search_doi(self,doi):
        # Find the textarea by XPath
        textArea_xpath='/html/body/div[2]/div[1]/form/div/textarea'
        textarea=self.wait.until(EC.presence_of_element_located((By.XPATH,textArea_xpath)))
        # Enter the DOI
        textarea.send_keys(doi)                
        # Optional: Click the submit button
        time.sleep(random.randint(2,5))
        submit_btn_xpath='/html/body/div[2]/div[1]/form/div/button'
        submit_button = self.driver.find_element(By.XPATH,submit_btn_xpath)
        submit_button.click()
    
    def get_file_details(self):
        seconds = 0
        timeout=120
        while seconds < timeout:
            # List all PDF files
            pdf_files = [f for f in os.listdir(self.download_dir) if f.endswith('.pdf')]
            crdownload_files = [f for f in os.listdir(self.download_dir) if f.endswith('.crdownload')]

            if pdf_files:
                # Get the latest PDF based on creation time
                full_paths = [os.path.join(self.download_dir, f) for f in pdf_files]
                latest_pdf = max(full_paths, key=os.path.getctime)

                # Check if a corresponding .crdownload file exists
                if not crdownload_files:
                    # Download is complete
                    pdf_file = os.path.basename(latest_pdf)
                    return pdf_file,latest_pdf

            time.sleep(5)
            seconds += 5
        return None
    def is_save_button_present(self):
        save_btn_xpath='/html/body/div[3]/div[1]/button'
        buttons = self.driver.find_elements(By.XPATH, save_btn_xpath)
        if len(buttons) > 0:
            return True
        else:
            return False

    def save_pdf(self,doi):
        # check_paper=self.check_for_paper()
        try:
            save_btn_xpath='/html/body/div[3]/div[1]/button'
            save_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, save_btn_xpath)))
            save_button.click()
            # print(save_button)
            check_save_btn=self.is_save_button_present()
            if check_save_btn==False:
                return False
            return True
        except:
            return False
        finally:
            time.sleep(random.randint(2,5))
            self.driver.back()

    def main(self,doi_list):
        output_dict={}
        for doi in doi_list:
            try:
                self.open_mainpage()
                self.search_doi(doi)
                output=self.save_pdf(doi)
                print(output)
                if output==True:
                    pdf_name,pdf_path=self.get_file_details()
                    if pdf_name is not None:
                        output_dict[doi]= f"The pdf of reasearch paper is saved in the directory 'Scihub_paper' at location '{pdf_path}'. The name of the pdf is '{pdf_name}'"
                elif output==False:
                    output_dict[doi]='Cannot download research paper'
            except:
                return json.dumps({'error':'Cannot download research paper'})
        self.driver.quit()
        return json.dumps(output_dict)
        

class download_paper_tools_input(BaseModel):
    doi_list:list=Field(required=True,description="The list of doi of research papers that needs to be downloaded from Sci-hub website")

def download_paper_tool(doi_list:list)->dict:
    getPapers=get_papers()
    getPapers_output=getPapers.main(doi_list)
    return getPapers_output

downloadPaper_tool=StructuredTool.from_function(
    func=download_paper_tool,
    description="""
    This tool accepts a list of DOIs (Digital Object Identifiers) corresponding to research papers as input. For each DOI, it attempts to automatically download the associated research paper from Sci-Hub.

    If the download is successful, the tool returns a message in the following format: "The PDF of the research paper is saved in the 'Scihub_paper' directory at location '<download directory path>'. The name of the PDF is '<Name of pdf>'."
    If the download fails, it returns: "Cannot download research paper"

    At the end of execution, the tool provides a JSON-formatted dictionary, where:
    Each DOI is a key
    The corresponding value is either the success message or a failure notice

    If the output dictionary is {"error": "Cannot download research paper"}, it may indicate:
    Sci-Hub server issues
    CAPTCHA/bot protection blocking the download

    The final output is a structured dictionary in JSON format, making it easy to parse and integrate into downstream workflows.
    """,
    args_schema=download_paper_tools_input)

# print(downloadPaper_tool.invoke({'doi_list':['10.1038/s41586-020-2649-2','10.1002/wat2.1605','10.1007/s12665-011-1229-z']}))

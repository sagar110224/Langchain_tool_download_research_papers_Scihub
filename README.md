# Langchain_tool_download_research_papers_Scihub
This tools uses Selenium to download research papers from Scihub

It takes list of DOI as input and download all the available research papers from Scihub. It also returns a dictionary which will tell the status as to whether the paper is downloaded or not. If downloaded it will also return the corresponding file name, download directory name and file path. 

Input: ['10.1038/s41586-020-2649-2','10.1002/wat2.1605','10.1007/s12665-011-1229-z']

Eg of output is:
{"10.1038/s41586-020-2649-2": "The pdf of reasearch paper is saved in the directory 'Scihub_paper' at location /Users/drago/Documents/Practicefiles/Data_files/Scihub_papers/10.1038@s41586-020-2649-2.pdf. The name of the pdf is '10.1038@s41586-020-2649-2.pdf'",
"10.1002/wat2.1605": "Cannot download research paper",
"10.1007/s12665-011-1229-z": "The pdf of reasearch paper is saved in the directory 'Scihub_paper' at location /Users/drago/Documents/Practicefiles/Data_files/Scihub_papers/tabari2011.pdf. The name of the pdf is 'tabari2011.pdf'"}

Change the path of ChromeWebdriver at line number 17
ChromeWebdriver can be downloaded from website: https://googlechromelabs.github.io/chrome-for-testing/#stable
You can get free proxies from the website: www.webshare.io Copy the proxy list in a .txt file. Copy this .txt file path at line 15 in proxy_extraction.py file

**P.S.: Since, Scihub website checks it you are a bot or not. So, you need to manually verify that you are not a bot by typing the capcha once. You will have 30 seconds to type the capcha**

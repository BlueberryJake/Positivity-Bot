from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth

def getTextData(URL):
    request = requests.get(URL)
    html_content = BeautifulSoup(request.content, 'html.parser')
    return html_content.get_text()
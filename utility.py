from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth

import sys
import os
directory = os.getcwd()
sys.path.append(directory + '/test_import')

import red


def getTextData(URL):
    request = requests.get(URL)
    html_content = BeautifulSoup(request.content, 'html.parser')
    return html_content.get_text()
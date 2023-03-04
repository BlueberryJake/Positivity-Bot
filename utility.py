from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth

import sys
import os
directory = os.getcwd()
sys.path.append(directory + '/test_import')


def getTextData(URL):
    request = requests.get(URL)
    html_content = BeautifulSoup(request.content, 'html.parser')
    return html_content.get_text()


def calculateSum(nums):
    totalSum = 0
    try:
        for num in nums:
            totalSum += float(num)
        return "The sum is " + str(totalSum)
    except ValueError:
        return "Error: Invalid Syntax\nSyntax: +add <num1> <num2> ..."


def calculateProduct(nums):
    totalProduct = 1
    try:
        for num in nums:
            totalProduct *= float(num)
        return "The product is " + str(totalProduct)
    except ValueError:
        return "Error: Invalid Syntax\nSyntax: +multiply <num1> <num2> ..."


def calculateMean(nums):
    totalAverage = 0
    try:
        for num in nums:
            totalAverage += float(num)
        return "The mean is " + str(totalAverage / len(nums))
    except ValueError:
        return "Error: Invalid Syntax\nSyntax: +mean <num1> <num2> ..."


import requests
from bs4 import BeautifulSoup
import argparse
import re
from urllib.parse import urljoin
import sys
import os

emailReg = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'ul', 'ol', 'li', 'span', 'a', 'strong', 'em', 'b', 'i', 'mark', 
        'small', 'sub', 'sup', 'code', 'samp', 'kbd', 'var', 'cite', 'del', 'ins', 'q', 'abbr', 'bdi', 'bdo', 'ruby', 'rt', 
        'rp', 'blockquote', 'pre', 'address', 'hr', 'form', 'label', 'input', 'textarea', 'button', 'select', 'option', 
        'fieldset', 'legend', 'table', 'caption', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'article', 'section', 'nav', 
        'aside', 'header', 'footer', 'main', 'figure', 'figcaption', 'details', 'summary', 'dialog']
allEmails = []
line = "=================================================="
header = """
                    _                  
  _  ._ _   _. o | |_ o ._   _|  _  ._ 
 (/_ | | | (_| | | |  | | | (_| (/_ |  
        """

def getHrefRoutes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  #stop if 4xx/5xx errors

        soup = BeautifulSoup(response.text, 'html.parser')

        routes = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            routes.append(href)

        return routes

    except requests.exceptions.RequestException as e:
        print(f"The given URL ({url}) is not reachable, see errors ===> \033[91m{e}\033[0m")
        return []
        

def findEmails(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as x:
        print(f"URL \033[91m{url}\033[0m is not valid: {x}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    #replace all tags by a space to avoid fusion
    websiteContent = []
    for element in soup.descendants:
        if isinstance(element, str):  
            websiteContent.append(element)
        elif element.name in tags: 
            websiteContent.append(' ')

    dataFormated = ''.join(websiteContent)
    emails = re.findall(emailReg, dataFormated)
    
    if emails:
        print(f"Found emails in {url}:")
        for email in set(emails):  
            print(f"\033[92m" + email + "\033[0m")
            allEmails.append(email)  
    #else:
        #print(f"\033[91mNo emails found in {url}.\033[0m")

def process_url(url):
    routes = getHrefRoutes(url)

    if routes:
        print(f"{line}\n - Found {len(routes)} routes.\n - Scanning each for emails on \033[0;33m{url}\033[0m ...\n{line}")
        for route in routes:
            full_url = urljoin(url, route)
            findEmails(full_url)
    else:
        print(f"No routes found on the provided URL: {url}.")

def process_urls_from_file(file_path):
    if not os.path.isfile(file_path):
        print(f"\033[91mThe file '\033[0;33m{file_path}\033[0m' does not exist.\033[0m")
        sys.exit(1)

    with open(file_path, 'r') as f:
        urls = f.read().splitlines()

    for url in urls:
        if url.strip():
            print(f"{line}\n - Scanning \033[0;33m{url}\033[0m ...")
            process_url(url)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Find email addresses from a given website or a file with multiple URLs.")
    parser.add_argument('input', help="The website URL or the file path containing a list of URLs.")
    args = parser.parse_args()

    input_value = args.input

    # Check if input is a file or a URL
    if os.path.isfile(input_value):
        print(f"{header}")
        print(f"{line}\n - Provided target file with URLs ==> \033[0;33m{input_value}\033[0m")
        process_urls_from_file(input_value)
    else:
        print(f"{header}")
        print(f"{line}\n - Provided URL ==> \033[0;33m{input_value}\033[0m")
        process_url(input_value)

    print(f"{line}\n - All collected emails:\n{line}")
    for email in set(allEmails):  #set() to remove duplicates from the final list
        print("\033[92m" + email + "\033[0m")

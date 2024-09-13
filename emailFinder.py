import requests
from bs4 import BeautifulSoup
import argparse
import re
from urllib.parse import urljoin
import sys

emailReg = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'ul', 'ol', 'li', 'span', 'a', 'strong', 'em', 'b', 'i', 'mark', 
        'small', 'sub', 'sup', 'code', 'samp', 'kbd', 'var', 'cite', 'del', 'ins', 'q', 'abbr', 'bdi', 'bdo', 'ruby', 'rt', 
        'rp', 'blockquote', 'pre', 'address', 'hr', 'form', 'label', 'input', 'textarea', 'button', 'select', 'option', 
        'fieldset', 'legend', 'table', 'caption', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'article', 'section', 'nav', 
        'aside', 'header', 'footer', 'main', 'figure', 'figcaption', 'details', 'summary', 'dialog']
allEmails = []
line = "=================================================="

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
        sys.exit(1)
        

def find_emails(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as x:
        #print(f"URL \033[91m{url}\033[0m is not valid: {x}")
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Find email addresses from a given website.")
    parser.add_argument('url', help="The main URL of the website. e.g.: python emailFinder https://example.com ")
    args = parser.parse_args()

    base_url = args.url
    routes = getHrefRoutes(base_url)

    if routes:
        print("""
                    _                  
  _  ._ _   _. o | |_ o ._   _|  _  ._ 
 (/_ | | | (_| | | |  | | | (_| (/_ |  
        """)
        print(f"{line}\n - Found {len(routes)} routes. Scanning each for emails ...\n{line}")
        
        for route in routes:
            full_url = urljoin(base_url, route)
            find_emails(full_url)
    else:
        print("No routes found on the provided URL.")

    print(f"{line}\n - All collected emails:\n{line}")
    for email in set(allEmails):  #set() to remove duplicates from the final list
        print("\033[92m" + email + "\033[0m")

import requests
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
import argparse
import re
from urllib.parse import urljoin, urlparse
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import itertools
import threading

emailReg = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
secondReg = r'^(?!.*\.(png|jpg|jpeg|gif|php|js|css|html|mp4)$)(?=.{2,25}@)(?!.*@.*@)(?!.*\..*\..*\.)(?!.*@.{1,1}\.)(?!.*@.{26,}@).+@[^.]+?\.[^.]+$'
tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'ul', 'ol', 'li', 'span', 'a', 'strong', 'em', 'b', 'i', 'mark', 
        'small', 'sub', 'sup', 'code', 'samp', 'kbd', 'var', 'cite', 'del', 'ins', 'q', 'abbr', 'bdi', 'bdo', 'ruby', 'rt', 
        'rp', 'blockquote', 'pre', 'address', 'hr', 'form', 'label', 'input', 'textarea', 'button', 'select', 'option', 
        'fieldset', 'legend', 'table', 'caption', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'article', 'section', 'nav', 
        'aside', 'header', 'footer', 'main', 'figure', 'figcaption', 'details', 'summary', 'dialog']

allEmails = []
color = ["\033[1;35m", "\033[92m", "\033[33m", "\033[0m"]
line = "=============================================================="

header = f"""{color[0]}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                         •┓┏┓•   ┓                        ║
║                  ┏┓┏┳┓┏┓┓┃┣ ┓┏┓┏┫┏┓┏┓                    ║
║                  ┗ ┛┗┗┗┻┗┗┻ ┗┛┗┗┻┗ ┛                     ║
║                                                          ║
║        {color[3]}Automate your email discovery effortlessly{color[0]}        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝                                                          
{color[3]}"""

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)#(ugly?)way to avoid xml/html error during parsing

#loader for fun
def loader(stopLoader):
    spinner = itertools.cycle(['⠋', '⠙', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stopLoader.is_set():
        sys.stdout.write(f'\r - [ {color[1]}{next(spinner)}{color[3]} Collecting emails, please wait {color[1]}{next(spinner)}{color[3]} ]')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f'\r\n - {color[0]}Done !{color[3]}\n')

#get domain from url
def getDomain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

#check if a URL belongs to the same domain
def checkIfSameDomain(base_url, target_url):
    return getDomain(base_url) == getDomain(target_url)

#search routes in url based on href(could be better?)
def getHrefRoutes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        base_domain = urlparse(url).netloc

        routes = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            full_url = urljoin(url, href)
            
            link_domain = urlparse(full_url).netloc
            link_domain = link_domain.replace("www.", "")

            if link_domain == base_domain:
                routes.append(href)

        return routes

    except requests.exceptions.RequestException as e:
        return []

#scrap emails with regex 
def findEmails(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as x:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    websiteContent = []

    #weird tricks to avoid unwanted concatenation 
    for element in soup.descendants:
        if isinstance(element, str):
            websiteContent.append(element)
        elif element.name in tags:
            websiteContent.append(' ')

    dataFormated = ''.join(websiteContent)
    emails = re.findall(emailReg, dataFormated)

    #second regex filter to avoid wrong email
    if emails:
        for email in set(emails):
            if re.match(secondReg, email):
                allEmails.append(email)

#url process
def processUrl(url):
    routes = getHrefRoutes(url)

    if routes:
        urls_to_scan = [urljoin(url, route) for route in routes]
        with ThreadPoolExecutor(max_workers=500) as executor:
            futures = [executor.submit(findEmails, full_url) for full_url in urls_to_scan]
            for future in as_completed(futures):
                future.result()
    else:
        print(f"\n - [{color[2]}warning{color[3]}] Can't find urls/routes from : {url}")

#urls process
def processUrlsFromFile(file_path):
    if not os.path.isfile(file_path):
        print(f"\033[91mThe file '\033[0;33m{file_path}{color[3]}' does not exist.{color[3]}")
        sys.exit(1)
    with open(file_path, 'r') as f:
        urls = f.read().splitlines()

    with ThreadPoolExecutor(max_workers=500) as executor:
        futures = [executor.submit(processUrl, url) for url in urls if url.strip()]
        for future in as_completed(futures):
            future.result()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find email addresses from a given website or a file with multiple URLs.")
    parser.add_argument('input', help="The website URL or the file path containing a list of URLs.")
    args = parser.parse_args()
    input_value = args.input


    try:
        startTimer = time.time()  
        stopLoader = threading.Event()
        startLoader = threading.Thread(target=loader, args=(stopLoader,))

        if os.path.isfile(input_value):
            print(f"{header}")
            print(f"{line}\n - Provided target file with URLs ==> {color[0]}{input_value}{color[3]}\n{line}")
            startLoader.start()
            processUrlsFromFile(input_value)
        else:
            print(f"{header}")
            print(f"{line}\n - Provided URL ==> {color[0]}{input_value}{color[3]}")
            startLoader.start()
            processUrl(input_value)

        stopLoader.set()  
        startLoader.join()

        lastTime = time.time()
        timerResult = lastTime - startTimer
        convMin = int(timerResult // 60)
        convSec = int(timerResult % 60)

        allEmailsLength = len(set(allEmails))
        print(f"{line}\n - Took {color[1]}{convMin}m{convSec}s{color[3]} to find {color[1]}{allEmailsLength}{color[3]} emails from {color[0]}{input_value}{color[3]}")
        print(f" - All collected emails :\n{line}")
        for email in set(allEmails):
            print(f"{color[1]}" + email + f"{color[3]}")

    #not working very well with multithreading
    except KeyboardInterrupt:
        print("\nemailFinder stopped with Ctrl + C, adios!")
        sys.exit(0)

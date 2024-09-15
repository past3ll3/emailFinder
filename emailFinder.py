import requests
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings
import argparse
import re
from urllib.parse import urljoin
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import itertools
import threading

# Email regex
emailReg = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
secondReg = r'^(?!.*\.(png|jpg|jpeg|gif|php|js|css|html|mp4)$)(?=.{2,25}@)(?!.*@.*@)(?!.*\..*\..*\.)(?!.*@.{1,1}\.)(?!.*@.{26,}@).+@[^.]+?\.[^.]+$'

tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'ul', 'ol', 'li', 'span', 'a', 'strong', 'em', 'b', 'i', 'mark', 
        'small', 'sub', 'sup', 'code', 'samp', 'kbd', 'var', 'cite', 'del', 'ins', 'q', 'abbr', 'bdi', 'bdo', 'ruby', 'rt', 
        'rp', 'blockquote', 'pre', 'address', 'hr', 'form', 'label', 'input', 'textarea', 'button', 'select', 'option', 
        'fieldset', 'legend', 'table', 'caption', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'article', 'section', 'nav', 
        'aside', 'header', 'footer', 'main', 'figure', 'figcaption', 'details', 'summary', 'dialog']

allEmails = []
line = "=================================================="

header = """\033[1;35m
                    _                  
  _  ._ _   _. o | |_ o ._   _|  _  ._ 
 (/_ | | | (_| | | |  | | | (_| (/_ |  
                                       \033[0m"""

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def loader(stopLoader):
    spinner = itertools.cycle(['⠋', '⠙', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stopLoader.is_set():
        sys.stdout.write(f'\r - [ \033[92m{next(spinner)}\033[0m Collecting emails, please wait \033[92m{next(spinner)}\033[0m ]')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r\n - Done !\n')

def getHrefRoutes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        routes = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            routes.append(href)

        return routes

    except requests.exceptions.RequestException as e:
        return []

def findEmails(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as x:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    websiteContent = []

    for element in soup.descendants:
        if isinstance(element, str):
            websiteContent.append(element)
        elif element.name in tags:
            websiteContent.append(' ')

    dataFormated = ''.join(websiteContent)
    emails = re.findall(emailReg, dataFormated)

    if emails:
        for email in set(emails):
            if re.match(secondReg, email):
                allEmails.append(email)

def process_url(url):
    routes = getHrefRoutes(url)

    if routes:
        urls_to_scan = [urljoin(url, route) for route in routes]
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(findEmails, full_url) for full_url in urls_to_scan]
            for future in as_completed(futures):
                future.result()
    else:
        print(f"\n - [\033[91merror\033[0m] Can't find urls/routes from : {url}")

def process_urls_from_file(file_path):
    if not os.path.isfile(file_path):
        print(f"\033[91mThe file '\033[0;33m{file_path}\033[0m' does not exist.\033[0m")
        sys.exit(1)
    with open(file_path, 'r') as f:
        urls = f.read().splitlines()

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_url, url) for url in urls if url.strip()]
        for future in as_completed(futures):
            future.result()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find email addresses from a given website or a file with multiple URLs.")
    parser.add_argument('input', help="The website URL or the file path containing a list of URLs.")
    args = parser.parse_args()
    input_value = args.input

    try:
        startTimer = time.time()  # Start the timer
        stopLoader = threading.Event()
        startLoader = threading.Thread(target=loader, args=(stopLoader,))

        # Display the header
        if os.path.isfile(input_value):
            print(f"{header}")
            print(f"{line}\n - Provided target file with URLs ==> \033[1;35m{input_value}\033[0m\n{line}")
            startLoader.start()
            process_urls_from_file(input_value)
        else:
            print(f"{header}")
            print(f"{line}\n - Provided URL ==> \033[0;33m{input_value}\033[0m")
            startLoader.start()
            process_url(input_value)

        stopLoader.set()  
        startLoader.join()

        lastTime = time.time()
        timerResult = lastTime - startTimer
        convMin = int(timerResult // 60)
        convSec = int(timerResult % 60)

        allEmailsLength = len(set(allEmails))
        print(f"{line}\n - Took \033[92m{convMin}m{convSec}s\033[0m to find \033[92m{allEmailsLength}\033[0m emails from \033[0;33m{input_value}\033[0m")
        print(f" - All collected emails :\n{line}")
        for email in set(allEmails):
            print("\033[92m" + email + "\033[0m")

    except KeyboardInterrupt:
        print("\nemailFinder stopped with Ctrl + C, adios!")
        sys.exit(0)

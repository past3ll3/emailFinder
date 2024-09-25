import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import itertools
import threading
import argparse  # Add this import

# Email regular expressions
email_reg = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
second_reg = r'^(?!.*\.(png|jpg|jpeg|gif|php|js|css|html|mp4)$)(?=.{2,25}@)(?!.*@.*@)(?!.*\..*\..*\.)(?!.*@.{1,1}\.)(?!.*@.{26,}@).+@[^.]+?\.[^.]+$'

# HTML tags to extract text from
tags = set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'ul', 'ol', 'li', 'span', 'a', 'strong', 'em', 'b', 'i', 'mark', 
            'small', 'sub', 'sup', 'code', 'samp', 'kbd', 'var', 'cite', 'del', 'ins', 'q', 'abbr', 'bdi', 'bdo', 'ruby', 'rt', 
            'rp', 'blockquote', 'pre', 'address', 'hr', 'form', 'label', 'input', 'textarea', 'button', 'select', 'option', 
            'fieldset', 'legend', 'table', 'caption', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'article', 'section', 'nav', 
            'aside', 'header', 'footer', 'main', 'figure', 'figcaption', 'details', 'summary', 'dialog'])

all_emails = []
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

# Loader spinner
def loader(stop_loader):
    spinner = itertools.cycle(['⠋', '⠙', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    while not stop_loader.is_set():
        sys.stdout.write(f'\r - [ {color[1]}{next(spinner)}{color[3]} Collecting emails, please wait {color[1]}{next(spinner)}{color[3]} ]')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f'\r\n - {color[0]}Done !{color[3]}\n')

# Get domain from URL
def get_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Check if a URL belongs to the same domain
def check_if_same_domain(base_url, target_url):
    return get_domain(base_url) == get_domain(target_url)

# Get href routes from URL
def get_href_routes(url):
    try:
        response = requests.get(url, timeout=5)  # Reduced timeout for faster response
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')  # Ensure lxml is used for faster parsing
        routes = {urljoin(url, a_tag['href']) for a_tag in soup.find_all('a', href=True) if check_if_same_domain(url, urljoin(url, a_tag['href']))}
        return routes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching routes from {url}: {e}")
        return set()

# Find emails using regex
def find_emails(url):
    try:
        response = requests.get(url, timeout=5)  # Reduced timeout for faster response
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')  # Ensure lxml is used for faster parsing
        website_content = []

        # Extract text from specified tags
        for tag in tags:
            for element in soup.find_all(tag):
                website_content.append(element.get_text())

        data_formatted = ' '.join(website_content)
        emails = set(re.findall(email_reg, data_formatted))

        # Filter out invalid emails
        valid_emails = {email for email in emails if re.match(second_reg, email)}
        all_emails.extend(valid_emails)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching emails from {url}: {e}")

# Process URL to extract email addresses
def process_url(url):
    routes = get_href_routes(url)
    if routes:
        with ThreadPoolExecutor(max_workers=50) as executor:  # Increased number of workers
            futures = [executor.submit(find_emails, full_url) for full_url in routes]
            for future in as_completed(futures):
                future.result()
    else:
        print(f"\n - [{color[2]}warning{color[3]}] Can't find URLs/routes from: {url}")

# Process URLs from a file
def process_urls_from_file(file_path):
    if not os.path.isfile(file_path):
        print(f"\033[91mThe file '\033[0;33m{file_path}{color[3]}' does not exist.{color[3]}")
        sys.exit(1)
    with open(file_path, 'r') as f:
        urls = [url.strip() for url in f if url.strip()]

    with ThreadPoolExecutor(max_workers=50) as executor:  # Increased number of workers
        futures = [executor.submit(process_url, url) for url in urls]
        for future in as_completed(futures):
            future.result()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find email addresses from a given website or a file with multiple URLs.")
    parser.add_argument('input', help="The website URL or the file path containing a list of URLs.")
    args = parser.parse_args()
    input_value = args.input

    try:
        start_timer = time.time()
        stop_loader = threading.Event()
        start_loader = threading.Thread(target=loader, args=(stop_loader,))

        if os.path.isfile(input_value):
            print(f"{header}")
            print(f"{line}\n - Provided target file with URLs ==> {color[0]}{input_value}{color[3]}\n{line}")
            start_loader.start()
            process_urls_from_file(input_value)
        else:
            print(f"{header}")
            print(f"{line}\n - Provided URL ==> {color[0]}{input_value}{color[3]}")
            start_loader.start()
            process_url(input_value)

        stop_loader.set()
        start_loader.join()

        last_time = time.time()
        timer_result = last_time - start_timer
        conv_min = int(timer_result // 60)
        conv_sec = int(timer_result % 60)

        all_emails_length = len(set(all_emails))
        print(f"{line}\n - Took {color[1]}{conv_min}m{conv_sec}s{color[3]} to find {color[1]}{all_emails_length}{color[3]} emails from {color[0]}{input_value}{color[3]}")

        # Print all collected emails
        print(f" - All collected emails:\n{line}")
        for email in set(all_emails):
            print(f"{color[1]}" + email + f"{color[3]}")

    except KeyboardInterrupt:
        print("\nemailFinder stopped with Ctrl + C, adios!")
        sys.exit(0)

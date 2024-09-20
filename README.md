# emailFinder - Email Extraction Tool
emailFinder is a Python-based web scraping tool designed to extract email addresses from websites or multiple URLs listed in a file. 

This email scraper crawls through website pages, parses content, and efficiently extracts email addresses.

## Features
- Automatically crawls through all page routes.
- Finds and displays email addresses.
- Input URLs directly or through a text file.

## Prerequisites
- Python 3.x installed on your machine.
- Venv (Virtual environment support).

  
## How to Install and Run

Follow these simple steps to clone the repository, install dependencies, and run the tool:

### Clone the repository
```
git clone git@github.com:AyraStelmaszewski/emailFinder.git
```

### Navigate to the project directory
```
cd emailFinder
```

### Set up a virtual environment

```
python3 -m venv venv
```

### Activate the virtual environment
```
source venv/bin/activate
```

### Install dependencies
```
pip install -r requirements
```
### Run the email extraction tool
```
python3 emailFinder.py urls.txt 
```


## Usage Example
To extract emails from a website or multiple URLs:

- Add URLs to a file.
- Run the tool as shown in the above command.


This tool will scan all routes of the URLs provided and extract all email addresses found.

## Contribution
Contributions, issues, and feature requests are welcome! Feel free to check out the issues page.

## License
This project is licensed under the GLPv3 License.

## Disclaimer
There is no filter on type of emails collected. 
Business email addresses is considered personal data if they are associated with an individual (e.g. alice.doe@example), but generic email addresses are fine (e.g. sales@example).

## Demo 
![alt text](https://github.com/past3ll3/emailFinder/blob/main/demo.gif)
![image](https://github.com/user-attachments/assets/73892d0c-7f4b-4d2f-8454-1f96151215a9)
![image](https://github.com/user-attachments/assets/6db660e4-8930-44a4-a1ee-42a37d8da15e)
![image](https://github.com/user-attachments/assets/cc790f66-12e9-4459-84e7-68530da62553)
![image](https://github.com/user-attachments/assets/fd9b3c3f-17fa-436d-8843-0a4099d0f81f)


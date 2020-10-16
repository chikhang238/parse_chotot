# Crawling HTML of chotot.com
This code is only used for crawling HTML of chotot and simulating a mouse to click to a button that is required to show a phone number.

## Pre-conditions:
- Install Python 3, pip
- Install successfully elasticsearch.
- Install successfully rabbitmq.
- If you are not familiar with them or have not installed them yet, please follow many public tutorials.
- Virtualenv (optional)

## Installation
```bash
pip install requirements.txt
```

## Usage
- Firstly, you need to run worker.py first for waiting:
```bash
python worker.py
```

- You can control the number of urls you would like to crawl by modify NUM_URLS in line 50.
- Or can comment lines 162-163 for unlimited number of urls.
- Then run send to send links to queue:
```bash
python send.py
```

- phone_number.py is just used for retreiving phone number which is hidden in chotot.com, you may run it by:
```bash
python phone_number.py
```
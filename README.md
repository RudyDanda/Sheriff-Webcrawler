# Ohio Sheriff Sales Web Crawler + Map Interface

## About:

This project was built with the purpose of aggregating the data released by the Ohio government on the different sheriff sales (foreclosures) across its counties. Currently, there is an issue where all the data for each county are on different websites. This application aims to pull this data from these sources and display them on a map interface through a web crawling pipeline. 

## Getting Started

To get started, install the minimum requirements by typing the following into the terminal:
`pip install -r minreq.txt`
`npm install -r minreq_react.txt`

To activate the web crawler to scrape from all counties, type the following into the terminal:

Enter the correct pathway:
`cd sheriff_scraper/sheriff_scraper`

Scrapy Crawler Activation:
`scrapy crawl county_crawler`

After the web crawler finishes, then please enter into the Flask backend pathway
`cd`
`cd sheriff/flask_backend`

Activate the Flask server:
`python -m app`

Activate the React App by entering into the frontend and then launching the app:
`cd`
`cd sheriff/react_frontend`
`npm start`
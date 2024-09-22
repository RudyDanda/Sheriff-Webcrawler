# Ohio Sheriff Sales Web Crawler + Map Interface

## About

This project was created to aggregate data released by the Ohio government on sheriff sales (foreclosures) across its counties. Currently, each county's data is hosted on different websites.

<div style="display: flex; justify-content: space-between;">
    <div style="margin-right: 10px;">
        <p><strong>Cuyahoga Sheriff Sales Page</strong></p>
        <img width="400" alt="Cuyahoga Sheriff Sales Page" src="https://github.com/user-attachments/assets/06e2b5dd-3a66-407c-ac73-5b98898cac6f">
    </div>
    <div>
        <p><strong>Sandusky Sheriff Sales Page</strong></p>
        <img width="400" alt="Sandusky Sheriff Sales Page" src="https://github.com/user-attachments/assets/d0b8fabd-71b7-47a9-8c97-a73c5a6b262c">
    </div>
</div>


All 88 counties of Ohio have a similar web page, which makes access of data on a wider scale difficult. This application aims to pull data from these sources using a web crawler and display them on a map interface. Accomplishing this can help analysts work with Ohio sheriff sales data in an easier way.

## Getting Started

Follow the steps below to install the necessary requirements and start the application.

### Prerequisites

1. **Install Python and npm dependencies**  
   Run the following commands in your terminal to install the required Python and npm packages:
   ```bash
   pip install -r minreq_pip.txt
   npm install -r minreq_npm.txt
   ```

### Running the Web Crawler

1. **Navigate to the web crawler directory**  
   Enter the correct directory by running:
   ```bash
   cd sheriff_scraper/sheriff_scraper
   ```

2. **Activate the Scrapy crawler**  
   Run the following command to start scraping data from all Ohio counties:
   ```bash
   scrapy crawl county_crawler
   ```

### Running the Flask Backend

1. **Navigate to the Flask backend directory**  
   After the web crawler finishes, navigate to the Flask backend directory:
   ```bash
   cd sheriff/flask_backend
   ```

2. **Activate the Flask server**  
   Run the following command to start the Flask backend server:
   ```bash
   python -m app
   ```

### Running the React Frontend

1. **Navigate to the React frontend directory**  
   Change into the frontend directory:
   ```bash
   cd sheriff/react_frontend
   ```

2. **Start the React app**  
   Launch the React frontend with the following command:
   ```bash
   npm start
   ```

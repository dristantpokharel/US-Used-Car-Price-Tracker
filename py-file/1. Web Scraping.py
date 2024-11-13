#!/opt/anaconda3/bin/python
# %% [markdown]
# ### Step 0: Import the required libraries:

# %%
import requests                         # Requests the HTTP to fetch the web pages.
from bs4 import BeautifulSoup           # For web scraping, or parsing HTML and XML documents.
import pandas as pd                     # Data manipulation in tabular form.
import math                             # Quick mathematical functions for calculations.
from sqlalchemy import create_engine    # To create connection to the SQL database.
import pyodbc                           # For connecting to databases using ODBC driver.
import concurrent.futures               # Makes the web scraping process faster.
import logging                          # To log web scrap.
import os

# %% [markdown]
# ### Step 1: Scrap the car links

# %%
# We are extracting used car data from Truecar.com. 
# I configured the car brand, model as per my requirement. 
# If you don't know what model you want, we can leave that space blank too as ' '. 
# Setting a realistic search radius like 100 will show limited but easy to check listings.
# Blank radius will show within 75 miles of the zip code. 

car_brand = 'honda'
car_model = 'pilot'
zip_code = '78701'
radius = '100'
base_url = f'https://www.truecar.com/used-cars-for-sale/listings/{car_brand}/{car_model}/location-{zip_code}/?searchRadius={radius}&page='

# %%
# HEADERS helps to avoid any kind of blocks from the website. It mimics a typical browser request.
# User_Agent for a computer can be found on: https://www.whatsmyua.info/
# Accept-Language used here is English.

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

# %%
# After the above web page is loaded, the website displays available cars in blocks.
# Clicking each block will open a new link that has details about the car. 
# Now, extrating each link from the listings.

# Fetch car links from each listing.
# Function is used here to avoid duplication, and let the code fetch all the links listed in the page.
# New links are stored as 'url' which will be used later. 

def fetch_page(page, session): # Each car link is retrieved from individual listing blocks.
    try:
        url = f"{base_url}{page}"
        response = session.get(url, headers=HEADERS) # Sends request to the website
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser') # 'Soup' Parses the above response to extract the html contents
        return [f"https://www.truecar.com{car['href']}" for car in soup.find_all('a', class_='linkable card-overlay order-2')]
        # By inspecting the web page, <a> tags were specified to the car lisiting, so this was used. 

    except requests.exceptions.RequestException:
        return []

# Sends a GET request to the specified URL using session-level connections to reuse settings like headers, 
# improving performance and ensuring consistency across multiple requests.

# %% [markdown]
# ### Step 2: Scrap data from each car listing link

# %%
# Each url was extracted in the above step.
# Now, each url is inspected, and the key data points are extracted like Title, price, miles, date listed, and so on.  
# Class, tags, strings are inspected to extract the key data points and divided for easier readability.

def scrape_car_details(url, session):
    try:
        response = session.get(url)
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Title
            title = soup.find('h1', {'data-test': "marketplaceVdpHeader"}).text.strip()
            # Mileage  
            mileage = soup.find('span', class_='shrink-0 flex items-center').text.strip()
            # Price  
            price = soup.find('div', {'data-test': 'unifiedPricingInfoPrice'}).text.strip()  
            # VIN
            vin_element = soup.find(string="VIN:")
            VIN = vin_element.find_parent("div").get_text(strip=True).replace("VIN:", "") if vin_element else "N/A"
            # Color
            color = soup.find(string="Exterior:")
            color = color.find_parent("div").get_text(strip=True).replace("Exterior:", "") if color else "N/A"
            # Location using the <p> tag
            location_element = soup.find('p', class_='mr-1')
            location = location_element.get_text(strip=True) if location_element else "N/A"
            # Listed Date
            listed_element = soup.find(string=lambda text: text and "Listed" in text)
            listed_date = listed_element.strip().replace("Listed ", "") if listed_element else "N/A"
            # AWD
            awd_element = soup.find('div', class_='flex items-center')
            awd = awd_element.get_text(strip=True) if awd_element else "N/A"
            # Number of accidents   
            accident_element = soup.find(string=lambda text: text and "Accident" in text)
            accident = accident_element.get_text(strip=True) if accident_element else "N/A"
            # Number of owners
            owner_element = soup.find(string=lambda text: text and "Owner" in text)
            owner = owner_element.get_text(strip=True) if owner_element else "N/A"
            # Car Title type
            clean_element = soup.find(string=lambda text: text and "Title" in text)
            title_type = clean_element.get_text(strip=True) if clean_element else "N/A"
            # Fuel type
            fuel = soup.find(string="Fuel Type:")
            fuel = fuel.find_parent("div").get_text(strip=True).replace("Fuel Type:", "") if fuel else "N/A"
            # Fuel Efficiency
            eff_element = soup.find(string=lambda text: text and "city / " in text)
            efficiency = eff_element.get_text(strip=True) if eff_element else "N/A"
                
            # Return the extracted data
            return {
                'Title': title,
                'Mileage': mileage,
                'Price': price,
                'URL': url,
                'VIN': VIN,
                'Color': color,
                'Location': location,
                'Listed': listed_date,
                'Accidents': accident,
                'Owners': owner,
                'Fuel_Type': fuel,
                'Fuel Efficiency': efficiency,
                'Car_Title': title_type
            }
    except requests.exceptions.RequestException:
        return None

# %%
# This establishes stable connection for repeated and consistent requests.
session = requests.Session()

# %%
# This step is to calculate the number of listings, which is displayed in the initial web link in step 1.
# Number of listing is shown before it starts to fetch data from each link.
# It is useful to see how many links and listing are being fetched.
# If the listing is more than 10,000, it takes time so we can cancel the operation without wasting time.
# Concurrent is for optimized and faster web scarping, used to simultaneouly fetch data from multiple car links.
# Main data scraping, that takes time, happens in this step.

# Counts the total number of listing here
try:
    initial_response = session.get(f'{base_url}1', headers=HEADERS)
    initial_response.raise_for_status()
    soup = BeautifulSoup(initial_response.content, 'html.parser')
    total_listings = int(soup.find('span', {'data-test': 'marketplaceSrpListingsTotalCount'}).text.replace(',', '').strip())
    total_pages = math.ceil(total_listings / 30)

    print(f"Total listings: {total_listings}, Pages: {total_pages}")

    # Fetch car links concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        car_links = [link for result in executor.map(fetch_page, range(1, total_pages + 1), [session]*total_pages) for link in result]

except requests.exceptions.RequestException as e:
    print(f"Error fetching initial page: {e}")

# Scraps each link here
with concurrent.futures.ThreadPoolExecutor() as executor:
    car_data_list = [result for result in executor.map(scrape_car_details, car_links, [session]*len(car_links)) if result]

# Panda package to convert the above extracted data to a dataframe for further manipulation
car_data_df = pd.DataFrame(car_data_list)

# %%
# To log the web scraping time.

# Defining a log file
log_file_path = '/path/to/log/file/web_scraping.log'

# If the directory doesn't exists, this creates it.
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Logging setup
logging.basicConfig(
    filename='/path/to/log/file/web_scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logging.info(f"Script ran. Total listings: {total_listings}, Pages: {total_pages}")

# %% [markdown]
# ### Step 3: Data Manipulation

# %%
# Drop duplicates for VIN, 
# As each car has a unique VIN, this step removes all the duplicate entries
car_data_df = car_data_df.drop_duplicates(subset='VIN')

# car_data_df.dtypes # use this to explore the data type which will be needed for manipulation

# Extracting the needed information, like adding new columns, extracting model details, miles, fuel efficiency,
# converting price to float variable, splitting the strings, keeping only the needed word or numbers and so on.
# Example: Keeping only numeric form. Before the entry had '55340 miles', converting it to '55340'.
car_data_df.insert(0, 'SNum', range(1, len(car_data_df) + 1))
car_data_df[['Status', 'Miles']] = car_data_df['Mileage'].str.split('·', expand=True)
car_data_df['Miles'] = car_data_df['Miles'].str.replace('miles', '').str.replace(',', '').str.strip().astype(int)
car_data_df['Year'] = car_data_df['Title'].str.split().str[0]
car_data_df['Brand'] = car_data_df['Title'].str.split().str[1]
car_data_df['AWD'] = car_data_df['Title'].str.split().str[-1].apply(lambda x: 'Yes' if x == 'AWD' else 'No')
car_data_df['Model'] = car_data_df['Title'].str.split().str[2:3].str.join(' ')
car_data_df['Adv_Model'] = car_data_df['Title'].str.split().str[3:].apply(lambda x: ' '.join(x))
car_data_df[['City', 'State']] = car_data_df['Location'].str.split(', ', expand=True)
car_data_df['Accidents'] = car_data_df['Accidents'].str.split().str[0]
car_data_df['Owners'] = car_data_df['Owners'].str.split().str[0]
car_data_df[['City_Eff', 'Highway_Eff']] = car_data_df['Fuel Efficiency'].str.split(' / ', expand=True)
car_data_df['City_Eff'] = car_data_df['City_Eff'].str.split().str[0]
car_data_df['Highway_Eff'] = car_data_df['Highway_Eff'].str.split().str[0]
car_data_df['List_Date_Ago'] = car_data_df['Listed'].str.split().str[0]

# Removing the comma and dollar sign from price to change it to float fom object
# For listings with no Price, keeping the entry as NaN for numeric consistency.
car_data_df['Price'] = car_data_df['Price'].replace('No Estimate Available', None).str.replace('[\$,]', '', regex=True).astype(float)

# Arrange the Column for easier readability
car_data_df = car_data_df[['SNum','Year', 'Brand', 'Model', 'Adv_Model', 'AWD', 'Miles', 'Price', 'Color', 'City', 'State', 
                               'List_Date_Ago', 'Accidents', 'Owners', 'Fuel_Type', 'City_Eff', 'Highway_Eff', 'Car_Title', 'VIN', 'URL']]

# %% [markdown]
# ### Step 4: Exporting to SQL Server

# %%
# Exporting the final table to SQL on a local server, contained on Docker.
# A database needs to be created on SQL before runnning it.
# Create engine establishes the connection to write data on the specified database.

engine = create_engine ("mssql+pyodbc://SA:YourPasswordHere@localhost/DatabaseNameHere?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes")
car_data_df.to_sql(f"{car_brand}_{car_model}".replace("-", "_"), engine, if_exists='replace', index=False)
engine.dispose()

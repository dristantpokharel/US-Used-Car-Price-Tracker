# US Used Car Price Tracker
From Truecar.com

## Overview
The Car Price Tracker Project helps users filter and find the best car options based on criteria like price and mileage. By scraping real-time data from TrueCar and storing it in an SQL database, this project enables users to make informed decisions when purchasing a vehicle.

## Use Case

### Problem Statement
Finding the right car can be overwhelming with numerous options online. Buyers often struggle to compare prices, mileage, and conditions, leading to frustration and missed deals.

### Solution
This project provides an automated system that:
- Scrapes data from TrueCar to obtain the latest car listings.
- Stores the data in an SQL database for easy querying and analysis.
- Checks every 5 minutes for new entries that meet user-defined criteria.
- Sends email notifications for new listings that match specified criteria.

## User Scenario
**User Requirements**: A user wants to buy a Honda Pilot that is under $28,000 and has fewer than 30,000 miles.  
**Automation**: The system scrapes data from TrueCar every 5 minutes, updating the SQL database.  
**Notifications**: When a new listing meets the user's requirements, an email notification is sent.

## Technologies Used
- **Python**: For web scraping and automation.
- **Beautiful Soup**: Parses HTML and extracts data.
- **SQL**: Stores and queries data.
- **SMTP**: Sends email notifications.
- **Docker**: Hosts SQL Database.
- **Crontab**: Schedules scripts to run automatically every 5 minutes.

## Notebooks
- **1. Web Scraping and Transformation.py**: Scrapes data from TrueCar, transforms it, and stores it in SQL.
- **2. Email Notification.py**: Sends an email if a new listing meets the defined criteria.

## Log Files
- **web_scraping.log**: Logs each time the web scraping script runs.
- **previous_vins.txt**: Stores all unique VINs processed.
- **vin_check.log**: Logs information about new listings, email notifications, or absence of new listings.

## Limitations
- **Data Source**: Only scrapes data from TrueCar, limiting the scope to listings available there.
- **Performance with Large Listings**: Large datasets may slow down the scraping process.
- **HTML Structure Changes**: Changes to TrueCar’s layout may affect scraping and require updates to the code.
- **Data Accuracy**: Dependent on the reliability and structure of TrueCar’s website.
- **Rate Limiting**: Frequent requests may trigger rate limits or IP blocking.
- - **Performance**: Approx 2.5 seconds to scrap 1 page i.e. 30 car listing.

## Setup Instructions for Automated 5-Minute Updates

### For Mac:
0. Save each script as a `.py` file.
1. Open Terminal.
2. Type `crontab -e` to open the crontab editor.
3. Add the line `*/5 * * * * /opt/anaconda3/bin/python "Your_file_path"` for each `.py` file to schedule it to run every 5 minutes.
4. Save and exit the crontab (`:wq`).
5. Confirm it's running by typing `crontab -l` to list all active cron jobs.

## Additional Notes
1. When defining car brand and model, use a hyphen (`-`) for multi-word entries (e.g., brand `Toyota`, model `Land-Cruiser`).
2. Ensure your SQL database is configured and accessible.
3. Double-check database names in SQL and Python for consistency.
4. Keep the main server running (e.g., using Docker on Mac).
5. Automating the main server if it is on the Cloud will be easier. For this project, I just hosted on localhost.
6. Adjust the frequency of cron jobs by modifying the `5` in the crontab (e.g., `0 */2 * * *` for every 2 hours).
7. Use logging to track errors and aid in troubleshooting.
8. Test email settings to ensure notifications are sent successfully.
9. Monitor CPU and memory usage when running frequent scripts to optimize system performance.
10. Run each script manually first to confirm it works before scheduling with crontab.

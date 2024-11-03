# US Used Car Price Tracker
From Truecar.com

## Overview
The Car Price Tracker Project aims to help users filter and find the best car options based on specific criteria, such as price and mileage. This project leverages web scraping to gather real-time data from TrueCar and stores it in a SQL database, allowing users to make informed decisions when purchasing a vehicle.

## Use Case

### Problem Statement
Finding the right car can be overwhelming due to the vast number of options available online. Buyers often struggle with comparing prices, mileage, and vehicle conditions, leading to potential frustration and missed opportunities for great deals.

### Solution
This project provides an automated system that:
- Scrapes data from TrueCar to obtain the latest car listings.
- Stores the data in a SQL database for easy querying and analysis.
- Checks every 5 minutes for new entries that meet user-defined criteria.
- Sends email notifications when new cars that fit the specified criteria are found.

## User Scenario
**User Requirements:** A user wants to buy a Toyota RAV4 under $40,000, with fewer than 30,000 miles.  
**Automation:** The system automatically scrapes data from TrueCar every 5 minutes to update the SQL database.  
**Notifications:** If a new listing appears that meets the user’s requirements, the system sends an email notification, ensuring the user never misses a great deal.

## Technologies Used
- **Python:** Programming language used for web scraping and automation.
- **Beautiful Soup:** Library for parsing HTML and extracting data.
- **SQL:** Database language used for storing and querying data.
- **SMTP:** Protocol for sending email notifications.
- **Crontab:** Tool for scheduling scripts to run automatically every 5 minutes.

## Notebooks
- **1. Web Scraping and Transformation.py:** Scraping the website, manipulating the data, and storing it to the SQL server.
- **2. Email Notification.py:** Sends an email if a car with the defined criteria is listed on the website.

## Limitations
- **Specific Website:** The current implementation only scrapes data from TrueCar. This limits the breadth of available car listings, as other platforms may have different inventories.
- **Performance with Large Listings:** Scraping a large number of listings can take considerable time, potentially delaying the availability of the most up-to-date data for users.
- **HTML Structure Variability:** TrueCar's website structure is suitable for scraping; however, other websites may have different HTML layouts or anti-scraping measures that could complicate data extraction, requiring modifications to the scraping logic.
- **Data Accuracy:** The accuracy of scraped data is dependent on the website's reliability. Any changes in TrueCar’s structure or data presentation may affect the scraping process and result in incomplete or inaccurate listings.
- **Rate Limiting and Blocking:** Frequent requests to the TrueCar website might trigger rate limiting or IP blocking. Proper handling and respect for the website's terms of service are essential to avoid disruptions.

## Instructions to Automate the process every 5 minutes.

**Instructions for Mac:**
0. Save the final script to a 'py' file.
1. Open Terminal.
2. Type `crontab -e` to open the crontab editor.
3. Type `*/5 * * * * /opt/anaconda3/bin/python "Your_file_path"` for both the py files to schedule the script to run every 5 minutes.
4. Type `:wq` and hit return to exit the crontab.
5. To check if it is running, type `crontab -l`. This shows all running crontab functions.

### Some additional things to consider:
1. Ensure your SQL database is properly configured and accessible from the script.
2. Recheck the database name of SQL and Python to be sure what needs to be the same or not.
3. Keep the main server running at all times. Example: As I am using Docker on the Mac to keep the schedule running.
4. Change the frequency by modifying the `5` in the crontab command to your desired number of minutes. For example, `0 */2 * * * /` for every 2 hours.
5. Add logging to your scripts to track errors and aid in troubleshooting.
6. Verify that your email settings are correct and test the functionality to ensure notifications are sent.
7. Monitor CPU and memory usage when running scripts frequently to manage system resources effectively.
8. Run your script manually before adding it to crontab to ensure it executes without errors.

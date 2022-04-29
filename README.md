# Predicting Apartment Rental Prices

Finding the perfect apartment is a challenge; searching through endless apartment listings to compare multiple listings is even more challenging. This app is meant to simplify that process and help you identify the right price and location that fits your budget and needs. 

# Introduction 
Nearly 100 million people within 45 million households are active renters. Since housing prices in major cities across the country are on the rise, the number of people renting, and the longevity that they will have to rent, is only going to increase. Needless to say, the rental market in the US impacts the lives of so many people.  

Many useful sites (e.g. Apartments.com or Craigslist) host thousands of active listings every day for prospective renters to filter through. Rather than displaying active listings to evaluate, this app will aim to predict the rental prices on a per neighborhood basis given a set of user inputs (beds, baths, sqft, amenities, etc.). 

## Project Overview
* Scraped apartment listing data from Apartments.com to build a database for multiple US cities. Current data has been obtained for Seattle, New York City (Manhattan, Brooklyn, and Queens), and the Bay Area.
* Performed simple cleaning operations as data is scraped. This allows for normalization of the scraped data for a consistent format in the database.
* Feature engineering
* Deploying

# Data Acquisition  
Description in progress

# Data Visualization
Description in progress

# Predictive Modeling
Description in progress

# Future Work

- [ ] Migrate SQLite database to PostgreSQL hosted on AWS
- [ ] Deploy the web scraper to an AWS EC2 instance and automate routine web scraping
- [ ] Set up pipeline to routinely re-train the models as new data becomes available
- [ ] Investigate a potential time series model to predict future rental prices (needs a full year of data)
- [ ] Add app functionality to analyze a specific apartments.com listing specified by the user and output if its within market value or not
- [ ] Add app functionality to compare two cities side-by-side
- [ ] Add more cities to the database

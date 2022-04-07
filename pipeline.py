#%%
from sys import argv
import numpy as np
import time
from src.scraper import make_request, generate_page_URL
import src.unit_parser
import src.property_parser
import src.database as db
import pickle as pkl

db_file = "../data/apartments.db"


class ApartmentsPipeline:
    """A class for extracting raw HTML from Apartments.com, parsing, and saving to a db

    Methods:
        get_property_urls: Extracts the general information for each listing
        get_property_urls_details: Extract the listing details for each listing
    """

    def __init__(
        self,
        city_name: str,
        state_abbv: str,
        db_file: str,
        start_price: int = 500,
        end_price: int = 6000,
        price_step: int = 200,
    ):
        """Constructs the attributes to use for web scraping apartments

        Args:
            city_name (str): City name to be scraped.
            state_abbv (str): Abbreviated state name to be scraped.
            db_file (str): Location of db for connection
            start_price (int, optional): Price to begin scraping. Defaults to 500.
            end_price (int, optional): Price to stop scraping. Defaults to 5000.
            price_step (int, optional): Sets the min and max price range. Defaults to 500.
        """

        self.start_price = start_price
        self.end_price = end_price
        self.price_step = price_step
        self.city_name = city_name
        self.state_abbv = state_abbv
        self.conn = db.create_connection(db_file)
        self.BASE_URL = f"https://www.apartments.com/{city_name.lower().replace(' ', '-')}-{state_abbv.lower()}/"  # "/price range/page"
        self.price_range = list(np.arange(start_price, end_price, price_step))
        self.page_range = list(np.arange(1, 29, 1))
        self.property_urls = []
        self.scrape_count = 0

    def sleep_crawler(self):

        if self.scrape_count > 0:
            if self.scrape_count % 100 == 0:
                time.sleep(round(np.random.uniform(15, 30)))

    def get_property_urls(self):

        # Loop through all price ranges
        for min_price in self.price_range:

            for page_num in self.page_range:
                self.sleep_crawler()
                url = generate_page_URL(
                    self.BASE_URL, min_price, min_price + self.price_step, page_num
                )
                soup, res_status = make_request(url)
                # If URL was redirected then end of page range was reached
                if res_status == 301:
                    break
                # If soup is None, skip iteration
                if soup == None:
                    continue

                listings = soup.find_all("li", {"class": "mortar-wrapper"})
                for listing in listings:
                    url = listing.find("a", {"class": "property-link"})["href"]
                    self.property_urls.append(url)
                # Add to the scraping counter
                self.scrape_count += 1

        # Remove any duplicate property URLs
        self.property_urls = list(set(self.property_urls))

    def scrape_property_urls(self):

        for url in self.property_urls:
            soup, res_status = make_request(url)
            # If soup is None, skip iteration
            if soup == None:
                continue
            try:
                property_name = soup.find("h1", {"class": "propertyName"}).get_text(
                    strip=True
                )
                # Extract all property details and save to the db
                property_data = ApartmentsPipeline.save_property_data(
                    self.conn, soup, property_name, self.city_name, url
                )
                # Find all of the current unit listings
                ApartmentsPipeline.save_units_data(
                    self.conn, soup, property_name, property_data["zipcode"]
                )

            except Exception as e:
                print(f"The exception, {e}, occured at the following URL: {url}")
                continue
            # Add to the scraping counter
            self.scrape_count += 1

        # Close db connection after all information is saved
        self.conn.close()

    @staticmethod
    def save_property_data(conn, soup, property_name, city_name, url):
        property_data = property_parser.Property(
            property_name, url
        ).parse_property_page(soup)

        property_data["city_name"] = city_name
        if (
            db.property_exists(
                conn, property_data["property_name"], property_data["zipcode"]
            )
            != 1
        ):
            db.insert_data(conn, property_data, "properties")
        else:
            db.update_data(conn, property_data)

        return property_data

    @staticmethod
    def save_units_data(conn, soup, property_name, zipcode):

        units = ApartmentsPipeline.get_all_units(soup)

        # Extract each unit from the listing and save to the db
        for unit in units:
            current_unit = unit_parser.Single_Unit(property_name, zipcode).parse_unit(
                unit
            )
            if current_unit["date_available"] != "Not Available":
                db.insert_data(conn, current_unit, "units")
            else:
                pass

    @staticmethod
    def get_all_units(soup):
        """Grab all units from a listing URl"""

        # Normal HTML layout for units
        units_html_1 = soup.find("div", {"data-tab-content-id": "all"}).find_all(
            "li", {"class": "unitContainer js-unitContainer"}
        )

        # Alternate HTML layout for units
        units_html_2 = soup.find("div", {"data-tab-content-id": "all"}).find_all(
            "div", {"class": "pricingGridItem multiFamily"},
        )
        units_html_3 = soup.find_all(
            "div", {"class": "priceGridModelWrapper js-unitContainer mortar-wrapper"},
        )
        if len(units_html_1) != 0:
            return units_html_1
        elif len(units_html_2) != 0:
            return units_html_2
        else:
            return units_html_3

    def run(self):
        print("Begin scraping...")
        self.get_property_urls()
        print("All property urls extracted")
        print(f"The total number of listings is {len(self.property_urls)}")
        try:
            with open("../data/raw/nyc_property_urls.pkl", "wb") as f:
                pkl.dump(self.property_urls, f)
        except:
            pass

        self.scrape_property_urls()
        print("Done!")


#%%
seattle_counties = ["King County"]

bay_area_counties = [
    "San Francisco",
    "Alameda County",
    "San Mateo County",
    "Santa Clara County",
]

nyc_counties = [
    "Manhattan County",
    "Bronx County",
    "Brooklyn",
    "Queens County",
    "Staten Island",
]

chicago_counties = ["Chicago"]

for county in chicago_counties:
    print(f"Starting {county}")
    pipeline = ApartmentsPipeline(county, "IL", db_file, end_price=10000)
    pipeline.run()
    print(f"Done with {county}")
    time.sleep(500)

# %%
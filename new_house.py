import os
import json
import re
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def append_sheet(house_data):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    # creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    json_creds = os.environ["GOOGLE_SHEETS_CREDS_JSON"]

    creds_dict = json.loads(json_creds)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)
    sheet = client.open("Houses2").sheet1

    data = sheet.append_row(values=house_data, value_input_option="USER_ENTERED", table_range='A1')
    print(f"updated {data['updates']['updatedCells']} cells")


class HouseScraper:
    def __init__(self, message):
        self.data = []
        self.full_link = ''
        find_full_link = re.search('https://www\.[a-zA-Z]+\.com.+', message)
        was_exception = False
        try:
            full_link = find_full_link.group()
            print(full_link)
            self.full_link = full_link

            headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                       'accept-encoding': 'gzip, deflate, sdch, br',
                       'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
                       'cache-control': 'max-age=0',
                       'upgrade-insecure-requests': '1',
                       'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}

            # headers = {}
            # headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
            page = requests.get(full_link, headers=headers)
            print(page)
            soup = BeautifulSoup(page.content, 'lxml')

        except:
            was_exception = True
            print('message does not have a valid link')

        if not was_exception:
            self.scrape_site(full_link, soup)

    def scrape_site(self, full_link, soup):
        # column order =
        data = {
            'Price': '',
            'Town': '',
            'Address': '',
            'Sq_feet': '',
            'Bedrooms': '',
            'Bathrooms': '',
            'Lot_size': '',
            'Link': '',
        }
        if 'realtor.com' in full_link:
            try:
                price = soup.find('span', attrs={'class': 'price'})
                data['Price'] = price.text

                address = soup.find('h1', attrs={'class': 'address'})
                data['Address'] = address.text

                town = address.find('span')
                data['Town'] = town.text

                beds = soup.find('li', attrs={'data-label': 'pc-meta-beds'})
                beds = beds.find('span', attrs={'data-label': 'meta-value'})
                data['Bedrooms'] = beds.text

                baths = soup.find('li', attrs={'data-label': 'pc-meta-baths'})
                baths = baths.find('span', attrs={'data-label': 'meta-value'})
                data['Bathrooms'] = baths.text

                sq_feet = soup.find('li', attrs={'data-label': 'pc-meta-sqft'})
                sq_feet = sq_feet.find('span', attrs={'data-label': 'meta-value'})
                data['Sq_feet'] = sq_feet.text

                lot_info = soup.find('li', attrs={'data-label': 'pc-meta-sqftlot'})
                lot_size = lot_info.find('span', attrs={'data-label': 'meta-value'})
                lot_size_units = lot_info.find('span', attrs={'data-label': 'meta-label'})
                data['Lot_size'] = lot_size.text + ' ' + lot_size_units.text

                data['Link'] = full_link
            except:
                address = full_link.replace('https://www.realtor.com/realestateandhomes-detail/', '')
                address = address.split('?')[0]

                data['Address'] = address
                data['Link'] = full_link
                print('Could not retrieve all data')

        elif 'trulia.com' in full_link:
            try:
                data['Price'] = soup.find('h3', attrs={'data-testid': 'on-market-price-details'}).text

                data['Address'] = soup.find('span', attrs={'data-testid': 'home-details-summary-headline'}).text

                data['Town'] = soup.find('span', attrs={'data-testid': 'home-details-summary-city-state'}).text

                data['Bedrooms'] = soup.find('li', attrs={'data-testid': 'bed'}).text

                data['Bathrooms'] = soup.find('li', attrs={'data-testid': 'bath'}).text

                data['Sq_feet'] = soup.find('li', attrs={'data-testid': 'floor'}).text

                home_features = soup.find('ul', attrs={'data-testid': 'home-features'})
                home_features = home_features.findChildren()
                for feature in home_features:
                    if "Lot Size: " in feature.text:
                        data['Lot_size'] = feature.text.replace('Lot Size: ', '')

                data['Link'] = full_link


            except:
                address = full_link.replace('https://www.trulia.com/p/', '')
                split_link = address.split('/')
                town = split_link[1]
                address = split_link[2]

                data['Town'] = town
                data['Address'] = address
                data['Link'] = full_link
                print('Could not retrieve all data')

        elif 'zillow.com' in full_link:
            try:
                price = soup.find('h3', attrs={'class': 'ds_price'})
                data['Price'] = price.find('span').text

                address = soup.find('h1', attrs={'class': 'ds-address-container'})
                address = address.find_all('span')
                data['Address'] = address[0].text

                data['Town'] = address[1].text

                bed_bath_living = soup.find_all('span', attrs={'class': 'ds-bed-bath-living-area'})
                for item in bed_bath_living:
                    item_value = item.find_all('span')[0].text
                    item_label = item.find('span', attrs={'class': 'ds-summary-row-label-secondary'}).text
                    if item_label == 'bd':
                        data['Bedrooms'] = item_value
                    elif item_label == 'ba':
                        data['Bathrooms'] = item_value
                    elif item_label == 'sqft':
                        data['Bathrooms'] = item_value

                home_fact_labels = soup.find_all('span', attrs={'class': 'ds-home-fact-label'})
                home_fact_values = soup.find_all('span', attrs={'class': 'ds-home-fact-value'})

                for label, value in zip(home_fact_labels, home_fact_values):
                    if label.text == 'Lot:':
                        data['Lot_size'] = value.text

                data['Link'] = full_link
            except:
                address = full_link.replace('https://www.zillow.com/homedetails/', '')
                address = address.split('/')[0]

                data['Address'] = address
                data['Link'] = full_link
                print('Zillow not supported')

        self.data = data


def scrape_house(message):
    new_house = HouseScraper(message)
    house_data = list(new_house.data.values())
    if len(house_data) > 0:
        append_sheet(house_data)
    return new_house


if __name__ == '__main__':
    try:
        # wayscript variables
        message = variables['Discord_Message']['message']
    except:
        message = 'add house https://www.realtor.com/realestateandhomes-detail/28-1-2-Crowley-Ave_Milford_CT_06461_M32167-69847?view=qv'

    new_house = HouseScraper(message)
    house_data = new_house.data
    if len(house_data) > 0:
        append_sheet(house_data)

import new_house
from new_house import HouseScraper

def should_scrape_realtor():
    #msg = 'https://www.realtor.com/realestateandhomes-detail/28-1-2-Crowley-Ave_Milford_CT_06461_M32167-69847?view=qv'
    msg = 'https://www.realtor.com/realestateandhomes-detail/117-Hillside-Ave_West-Haven_CT_06516_M30507-10302'

    new_scraper = HouseScraper(msg)
    print(new_scraper.data)


if __name__ == '__main__':
    should_scrape_realtor()
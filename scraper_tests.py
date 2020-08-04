import new_house
import requests
from bs4 import BeautifulSoup
from new_house import HouseScraper


def should_scrape_realtor():
    # msg = 'https://www.realtor.com/realestateandhomes-detail/28-1-2-Crowley-Ave_Milford_CT_06461_M32167-69847?view=qv'
    msg = 'https://www.realtor.com/realestateandhomes-detail/125-Winter-St_Stratford_CT_06614_M46460-70069?cid=other_shares_core_ldp'

    new_scraper = HouseScraper(msg)
    print(new_scraper.data)

def should_search_google_then_scrape():
    link = '''Homes for sale in 46 Elaine Rd, Milford, CT

       https://b1iw.app.link/juaTqc0UE8

       https://www.realtor.com/realestateandhomes-search/46-Elaine-Rd_Milford_CT?cid=other_shares_core_srp'''

    if '-search' in link:
        site = 'realtor.com'
        split_link = link.split('/')
        address = split_link[len(split_link) - 1].split('?')[0]

    page = requests.get(f'https://www.google.com/search?q={site}+{address}')
    soup = BeautifulSoup(page.content, 'lxml')
    all_links = soup.findAll('a')
    for link in all_links:
        if 'https://www.realtor.com/realestateandhomes-detail/' in link['href'] and address in link[
            'href'] and 'google.com' not in link['href']:
            correct_link = link['href']
            print(link['href'])

    correct_link = correct_link.replace('/url?q=', '')
    correct_link = correct_link.split('&')[0]

    new_scraper = HouseScraper(correct_link)
    print(new_scraper.data)


if __name__ == '__main__':
    #should_scrape_realtor()
    should_search_google_then_scrape()






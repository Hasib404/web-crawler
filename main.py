import datetime
import logging
import re

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

from database import db_connect, add_events_table, insert_events_info, fetch_events_info


logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)


class Crawler:
    def __init__(self, url):
        self.url_to_visit = url
        self.path_to_visit = []


    def download_url(self, url):
        return requests.get(url).text


    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for a_tag in soup.find_all('a', class_="event-image-link"):
            path_tag = a_tag['href']
            if path_tag and path_tag.startswith('/'):
                path = urljoin(url, path_tag)
                self.path_to_visit.append(path)
    

    def get_page_info(self, url):
        for path in tqdm(self.path_to_visit):
            page_html = self.download_url(path)
            
            # Removes white space
            html = "".join(line.strip() for line in page_html.split("\n"))
            soup = BeautifulSoup(html, 'html.parser')

            # Artists
            artists_list = []
            ul_tag = soup.find_all('ul', attrs={'class':'performers-list'})

            for content in ul_tag:
                strong_tag = content.find_all('strong')
                for artist in strong_tag:
                    title = artist.text
                    artists_list.append(title)

            artists = ",".join(artists_list)

            # Date
            time_tag = soup.find('time')
            day_date = time_tag.text
            extract_date = day_date.split(" ")[1]
            split_date = extract_date.split(".")
            date = '2022' + '-' + split_date[1] + '-' + split_date[0]

            # Title
            h1_tag = soup.find("h1")
            title = h1_tag.text

            # Image
            picture_tag = soup.find("picture")
            img_src = picture_tag.img["src"]

            if img_src and img_src.startswith('/'):
                img_link = urljoin(url, img_src)

            # Price
            try:
                price_class = soup.find(class_ = "prices")
                ticket_price = price_class.text
            except:
                ticket_price = "N/A"

            # Time
            date_time_tag = soup.find(class_ = 'cell large-6 subtitle')
            date_time = date_time_tag.find('br').next_sibling

            time_pattern = r"^.*\| (.*)\|.*$"
            time_re = re.search(time_pattern, date_time)
            time = time_re.group(1)
            
            # Location
            loc_pattern = r"^.*\| (.*).*$"
            loc_re = re.search(loc_pattern, date_time)
            location = loc_re.group(1)

            insert_events_info(path, title, location, date, time, ticket_price, artists, img_link)


    def draw_plot(self):
        event_occurrence_with_date = fetch_events_info()
        date, events = map(list, zip(*event_occurrence_with_date))
        sorted_date = sorted(date, key=lambda x: datetime.datetime.strptime(x, '%d/%m'))
        
        # Create data
        x_pos = np.arange(len(sorted_date))
        
        # Create bars
        plt.bar(x_pos, events)

        # Add labels
        plt.xlabel('Date')
        plt.ylabel('Number of events')
        plt.title('Event Occurrence')

        plt.yticks(np.arange(min(events), max(events)+1, 1))
        
        # Rotation of the bar names
        plt.xticks(x_pos, sorted_date, rotation=90)

        # Save figure
        plt.savefig('plot.png', dpi=300, bbox_inches='tight')


    def crawl(self, url):
        html = self.download_url(url)
        self.get_linked_urls(url, html)
        self.get_page_info(url)
        self.draw_plot()
        db_connect.close()


    def run(self):
        logging.info(f'Crawling: {self.url_to_visit}')
        try:
            add_events_table()
            self.crawl(self.url_to_visit)
        except Exception:
            logging.exception(f'Failed to crawl: {self.url_to_visit}')


if __name__ == '__main__':
    Crawler(url='https://www.lucernefestival.ch/en/program/summer-festival-22').run()
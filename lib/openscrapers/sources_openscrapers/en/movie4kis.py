# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 05-06-2019 by JewBMX in Scrubs.

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import urlparse

from bs4 import BeautifulSoup
from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['movie4k.is']  # Old  movie4k.ws
        self.base_link = 'https://www1.movie4k.is'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            hostDict = hostprDict + hostDict
            if url == None:
                return sources
            h = {'User-Agent': client.randomagent()}
            title = cleantitle.geturl(url['title']).replace('-', '+')
            url = urlparse.urljoin(self.base_link, self.search_link % title)
            r = self.scraper.get(url, headers=h)
            r = BeautifulSoup(r.text, 'html.parser').find('div', {'class': 'item'})
            r = r.find('a')['href']
            r = self.scraper.get(r, headers=h)
            r = BeautifulSoup(r.content, 'html.parser')
            quality = r.find('span', {'class': 'calidad2'}).text
            url = r.find('div', {'class': 'movieplay'}).find('iframe')['src']
            if not quality in ['1080p', '720p']:
                quality = 'SD'
            valid, host = source_utils.is_host_valid(url, hostDict)
            if valid:
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
                                'debridonly': False})
            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            return url
        except:
            return

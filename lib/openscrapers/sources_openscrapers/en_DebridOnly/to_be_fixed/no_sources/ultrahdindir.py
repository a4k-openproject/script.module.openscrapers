# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from resources.lib.modules import log_utils
from openscrapers.modules import source_utils

from bs4 import BeautifulSoup

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        # List of base urls
        self.domains = ['ultrahdindir.com']
        # Base URL
        self.base_link = 'https://ultrahdindir.com'
        # part of link on search results page, with %s on any portion where you need to insert title, year, etc.
        self.search_link = '/index.php?do=search'
                                                                                                                # Example: '/s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            log_utils.log('Ran into problems making the "url" (dict of things)')

    def sources(self, url, hostDict, hostprDict):
        #log_utils.log('URLS GIVE: '+str(url))
        #EXAMPLE: URLS GIVE: year=2015&imdb=tt2395427&title=Avengers%3A+Age+of+Ultron
        try:
            sources = []
            # if no link returned in movie and tvshow searches, nothing to do here, return out.
            if url == None or len(url) == 0:
                return sources
            if debrid.status() is False: raise Exception()
            #            log_utils.log('Scraper Template - Sources - url: ' + str(url))

            #Lets get scraping.
            url = urlparse.parse_qs(url)
            title = url['title'][0]
            imdb = url['imdb'][0]
            year = url['year'][0]
            #Create the string of post data to send.
            post = 'do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=' + urllib.quote_plus(title) + ' ' + urllib.quote_plus(imdb)
            #Join site links
            site_link = urlparse.urljoin(self.base_link, self.search_link)
            # Pulls the webpage HTML for search results
            search_results = client.request(site_link, post=post)
            search_soup = BeautifulSoup(search_results, "html.parser")
            # Find all the results in the html
            results = search_soup.findAll("div", {"class": "news-title"})
            result_links = []
            for result in results:
                # Gets the link from that results
                link = result.find("a", href=True)['href']
                result_links.append(link)  # Put said link into the list
            for link in result_links:
                link_result = client.request(link.encode('ascii'))
                link_soup = BeautifulSoup(link_result, "html.parser")
                dl_links = link_soup.findAll("div", {"class": "quote"})
                nonvip_dl_links = []
                for dl_link in dl_links:
                    if "vip" in str(dl_link).lower():
                        continue
                    else:
                        nonvip_dl_links.append(dl_link)    #For loop filters out the "VIP" links we don't need
                actual_links = []
                for nonvip_dl_link in nonvip_dl_links:
                    the_link = nonvip_dl_link.find('a', href=True)['href']
                    actual_links.append(the_link.encode('ascii'))

            for link in actual_links:
                quality,info = source_utils.get_release_quality(link, url)                                      # Run two strings through this to try to pull Quality and info on the file (such as 1080p, etc)
                host = link.replace('https://', '').split('/')[0].split('.')[0]    # By splitting the URL repeatedly we end up with the host.
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': False, 'debridonly': False})
            return sources
        except Exception as e:
            log_utils.log('EXCEPTION MSG: '+str(e))
            return sources

    def resolve(self, url):
        return url

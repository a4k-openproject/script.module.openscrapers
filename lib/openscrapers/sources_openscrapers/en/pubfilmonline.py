# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re,urllib,urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from resources.lib.modules import log_utils
from openscrapers.modules import source_utils
from openscrapers.modules import cfscrape

from bs4 import BeautifulSoup
import json

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['pubfilmonline.ws']                                                                   # List of base urls, such as 'filmfrantic.com'
        self.base_link = 'https://pubfilmonline.ws'                                                                      # Base URL, such as 'http://filmfrantic.com'
        self.search_link = '/?s='                                                           # part of link on search results page, with %s on any portion where you need to insert title, year, etc.
                                                                                                                # Example: '/s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            log_utils.log('Ran into problems making the "url" (dict of things)')

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None or len(url) == 0:                                                                      # if no link returned in movie and tvshow searches, nothing to do here, return out.
                log_utils.log('inif?')
                return sources

            #Grab title and year (cant use imdb code here)
            url = urlparse.parse_qs(url)
            title = url['title'][0]
            year = url['year'][0]
            
            #Create search link
            searchlink = self.search_link = self.search_link + title + ' ' + year
            url = urlparse.urljoin(self.base_link, searchlink)
            
            scraper = cfscrape.create_scraper()
            html = scraper.get(url).content                                                                          # Get the HTML for the page
            soup = BeautifulSoup(html)
            #Find all search results and add to array
            results = soup.findAll("div", {"class": "result-item"})
            result_links = []
            for result in results:
                result_links.append(result.find("a", href=True)['href'])
            
            #Go over search results and find their sources
            for result_link in result_links:
                html = scraper.get(result_link).content
                soup = BeautifulSoup(html)
                javascripts = soup.findAll("script", {"type": "text/javascript"})
                #Lets keep going until we find the one we need
                ids_b64s = []
                for javascript in javascripts:
                    javascript = str(javascript)
                    if "var Player" in javascript and "LoadPlayer" in javascript:
                        #This is the right script
                        #Get the jwplayer-id
                        jw_id = 'jwplayer-' + re.search('jwplayer-(\d+)', javascript).groups(0)[0]
                        #Get weird b64 string
                        b64_string = re.search('(?<=jwplayer)(.*)(?="\);)', javascript).groups(0)[0]
                        #Parse into just the b64
                        b64_string = b64_string.split('","')[1]
                        ids_b64s.append([jw_id,b64_string])
                        break
            #Go get the video links
            for id_b64 in ids_b64s:
                the_id = id_b64[0]
                the_b64 = id_b64[1]
                post = {
                    'id': the_id,
                    'data': b64_string
                }
                html = scraper.post(urlparse.urljoin(self.base_link, '/wp-content/plugins/apiplayer/load.php'), data=post).content
                soup = BeautifulSoup(html)
                javascripts = soup.findAll("script", {"type": "text/javascript"})
                links_qual = []
                for javascript in javascripts:
                    javascript = str(javascript)
                    if ").setup({" in javascript:
                        #This script contains the stuff
                        files = re.search('(?<=sources: \[)(.*)(?=])', javascript).groups()[0]
                        files = "[" + files + "]"
                        files = json.loads(files)
                        for f in files:
                            quality = f['label']
                            link = f['file']
                            links_qual.append([link, quality])

            for l_q in links_qual:
                link = l_q[0]
                quality = l_q[1]
                host = link.split('//')[1].replace('www.','').split('/')[0]
                info = ''
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'info': info, 'direct': True, 'debridonly': False})
            return sources
        except Exception as e:
            log_utils.log('EXCEPTION MSG: '+str(e))
            return sources

    def resolve(self, url):
        return url

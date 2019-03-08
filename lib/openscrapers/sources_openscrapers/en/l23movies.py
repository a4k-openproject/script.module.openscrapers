# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @tantrumdev wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# -Cleaned and Checked on 10-27-2018 by JewBMX

import re
import urllib
import urlparse
import json
import base64

from openscrapers.modules import client, cleantitle, directstream, dom_parser2
from openscrapers.modules import debrid
from openscrapers.modules import cfscrape

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['l23movies.com']
        self.base_link = 'http://l23movies.com'
        self.movies_search_path = ('search-movies/%s.html')
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title).replace('-','+')
            url = urlparse.urljoin(self.base_link, (self.movies_search_path % clean_title))
            r = self.scraper.get(url).content

            r = dom_parser2.parse_dom(r, 'div', {'id': 'movie-featured'})
            r = [dom_parser2.parse_dom(i, 'a', req=['href']) for i in r if i]
            r = [(i[0].attrs['href'], re.search('Release:\s*(\d+)', i[0].content)) for i in r if i]
            r = [(i[0], i[1].groups()[0]) for i in r if i[0] and i[1]]
            r = [(i[0], i[1]) for i in r if i[1] == year]
            if r[0]: 
                url = r[0][0]
                return url
            else: return
        except Exception:
            return
            
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = self.scraper.get(url).content
            r = dom_parser2.parse_dom(r, 'p', {'class': 'server_play'})
            r = [dom_parser2.parse_dom(i, 'a', req=['href']) for i in r if i]
            r = [(i[0].attrs['href'], re.search('/(\w+).html', i[0].attrs['href'])) for i in r if i]
            r = [(i[0], i[1].groups()[0]) for i in r if i[0] and i[1]]
            for i in r:
                try:
                    host = i[1]
                    if str(host) in str(hostDict):
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        sources.append({
                            'source': host,
                            'quality': 'SD',
                            'language': 'en',
                            'url': i[0].replace('\/','/'),
                            'direct': False,
                            'debridonly': False
                        })
                except: pass
            return sources
        except Exception:
            return
            
    def resolve(self, url):
        try:
            r = self.scraper.get(url).content
            url = re.findall('document.write.+?"([^"]*)', r)[0]
            url = base64.b64decode(url)
            url = re.findall('src="([^"]*)', url)[0]
            return url
        except Exception:
            return

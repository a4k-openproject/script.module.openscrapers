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
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo

import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['movie2k.ac']
        self.base_link = 'http://www.movie2k.ac'
        self.search_link = '/search/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'id': 'tab-plot_german'})
            r = dom_parser.parse_dom(r, 'tbody')
            r = dom_parser.parse_dom(r, 'tr')

            for i in r:
                if re.search('(?<=">)(\n.*?)(?=<\/a>)', i[1]).group().strip():
                    hoster = re.search('(?<=">)(\n.*?)(?=<\/a>)', i[1]).group().strip()
                    link = re.search('(?<=href=\")(.*?)(?=\")', i[1]).group()
                    rel = re.search('(?<=oddCell qualityCell">)(\n.*?)(?=<\/td>)', i[1]).group().strip()
                    quality, info = source_utils.get_release_quality(rel)
                    if not quality:
                        quality = 'SD'

                    valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                    if not valid: continue

                    sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles):
        try:
            query = self.search_link % (urllib.quote_plus(urllib.quote_plus(cleantitle.query(titles[0]))))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'ul', attrs={'class': 'coverBox'})
            r = dom_parser.parse_dom(r, 'li')
            r = dom_parser.parse_dom(r, 'span', attrs={'class': 'name'})
            r = dom_parser.parse_dom(r, 'a')

            title = r[0][1]
            title = cleantitle.get(title)

            if title in t:
                return source_utils.strip_domain(r[0][0]['href'])
            else:
                return
        except:
            return

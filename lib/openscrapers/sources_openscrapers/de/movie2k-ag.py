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
        self.domains = ['movie2k.ag']
        self.base_link = 'https://www.movie2k.ag'
        self.search_link = '?c=movie&m=filter&keyword=%s'
        self.get_link = 'http://www.vodlocker.to/embed/movieStreams?lang=2&e=&id=%s&links=%s&cat=movie'

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
            r = dom_parser.parse_dom(r, 'div', attrs={'id': 'player'})
            r = dom_parser.parse_dom(r, 'iframe', req='src')
            r = client.request(r[0][0]['src'])
            r = dom_parser.parse_dom(r, 'a', attrs={'class': 'play_container'}, req='href')
            r = client.request(r[0][0]['href'])
            url = self.get_link % (re.search('(?<=var id = \")(.*?)(?=\")', r).group(), re.search('(?<=var links = \")(.*?)(?=\")', r).group())
            r = client.request(url)
            r = dom_parser.parse_dom(r, 'ul', attrs={'id': 'articleList'})
            r = dom_parser.parse_dom(r, 'a')

            for i in r:
                if 'http' in i[0]['href']:
                    link = i[0]['href']
                elif 'http' in i[0]['onclick']:
                    link = re.search('http(.*?)(?=\")', i[0]['onclick']).group()
                else:
                    return sources

                valid, hoster = source_utils.is_host_valid(link, hostDict)
                if not valid: continue

                sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'nag'})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'item-video'})
            r = dom_parser.parse_dom(r, 'h2', attrs={'class': 'entry-title'})
            r = dom_parser.parse_dom(r, 'a', req='href')

                           
                                         

            for i in r:
                title = i[1]
                if re.search('\*(?:.*?)\*', title) is not None:
                    title = re.sub('\*(?:.*?)\*', '', title)
                title = cleantitle.get(title)
                if title in t:
                    return source_utils.strip_domain(i[0]['href'])
                else:
                    return
        except:
            return

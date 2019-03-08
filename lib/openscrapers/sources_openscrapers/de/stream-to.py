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
import itertools
import HTMLParser
import json

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['stream.to']
        self.base_link = 'https://stream.to'
        self.search_link = '/ajax/suggest_search'
        self.get_player = '/ajax/load_player/%s'
        self.get_link = '/ajax/load_video/%s'

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

            url = url.replace('/en/', '/de/')

            video_id = re.search('(?<=\/)(\d*?)(?=-)', url).group()
            if not video_id:
                return sources

            # load player
            query = self.get_player % (video_id)
            query = urlparse.urljoin(self.base_link, query)
            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'le-server'})

            # for each hoster
            for i in r:
                hoster = dom_parser.parse_dom(i, 'div', attrs={'class': 'les-title'})
                hoster = dom_parser.parse_dom(hoster, 'strong')
                hoster = hoster[0][1]

                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue

                links = dom_parser.parse_dom(i, 'a', attrs={'class': 'ep-item'})

                # for each link
                for i in links:
                    if '1080p' in i[0]['title']:
                        quality = '1080p'
                    elif 'HD' in i[0]['title']:
                        quality = 'HD'
                    else:
                        quality = 'SD'

                    url = i[0]['id']
                    if not url: continue

                    sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': url, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            query = self.get_link % (url)
            query = urlparse.urljoin(self.base_link, query)
            r = client.request(query)

            url = dom_parser.parse_dom(r, 'iframe', req='src')
            url = url[0][0]['src']

            return url
        except:
            return url

    def __search(self, titles):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link)
            post = urllib.urlencode({'keyword': titles[0]})

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query, post=post)
            r = json.loads(r)
            r = r['content']

            r = dom_parser.parse_dom(r, 'li')

            for i in r:
                title = dom_parser.parse_dom(i[1], 'a', attrs={'class': 'ss-title'})
                if cleantitle.get(title[0][1]) in t:
                    return source_utils.strip_domain(title[0][0]['href'])
        except:
            return

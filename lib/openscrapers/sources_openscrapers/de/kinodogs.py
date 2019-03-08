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
        self.domains = ['kinodogs.to']
        self.base_link = 'http://kinodogs.to'
        self.search_link = '/search?q=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year, imdb)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year, imdb)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year, imdb)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year, imdb)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            r = client.request(urlparse.urljoin(self.base_link, url))
            r = dom_parser.parse_dom(r, 'table', attrs={'class': 'episodes'})
            r = dom_parser.parse_dom(r, 'tr', attrs={'class': ['episode', 'season_%s' % season]})
            r = dom_parser.parse_dom(r, 'span', attrs={'class': 'normal'})
            r = [(dom_parser.parse_dom(i, 'a', req='href'), dom_parser.parse_dom(i, 'b')) for i in r]
            r = [(i[0][0].attrs['href'], i[1][0].content) for i in r if i[0] and i[1]]
            r = [i[0] for i in r if i[1].upper() == 'E%s' % episode]

            if len(r) >= 1:
                return source_utils.strip_domain(r[0])
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            r = client.request(urlparse.urljoin(self.base_link, url))
            r = dom_parser.parse_dom(r, 'table', attrs={'class': 'stream_links'})
            r = dom_parser.parse_dom(r, 'tr')
            r = [(dom_parser.parse_dom(i, 'td'), dom_parser.parse_dom(i, 'td', attrs={'class': 'hide-for-small-only'})) for i in r]
            r = [(dom_parser.parse_dom(i[0][0], 'a', req='href'), i[1][0].content.lower()) for i in r if i[0] and i[1]]
            r = [(i[0][0].attrs['href'], i[1]) for i in r if i[0]]

            for link, hoster in r:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue

                sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            if not url.startswith('http'):
                url = urlparse.urljoin(self.base_link, url)
                url = client.request(url, output='geturl')

            if self.base_link not in url:
                return url
        except:
            return url

    def __search(self, titles, year, imdb):
        try:
            query = self.search_link % urllib.quote_plus(cleantitle.query(titles[0]))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'movie_cell'})
            r = [(dom_parser.parse_dom(i, 'div', attrs={'class': 'bottom'}), dom_parser.parse_dom(i, 'div', attrs={'class': 'year'})) for i in r]
            r = [(dom_parser.parse_dom(i[0], 'a', req=['href', 'title']), re.findall('[(](\d{4})[)]', i[1][0].content)) for i in r if i[0] and i[1]]
            r = [(i[0][0].attrs['href'], i[0][0].content, i[1][0]) for i in r if i[0] and i[1]]
            r = [(i[0], i[1].lower(), i[2]) for i in r if i[2] in y]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t]

            if len(r) > 1:
                for i in r:
                    data = client.request(urlparse.urljoin(self.base_link, i))
                    data = dom_parser.parse_dom(data, 'a', attrs={'name': re.compile('.*/tt\d+.*')}, req='name')
                    data = [re.findall('.+?(tt\d+).*?', d.attrs['name']) for d in data]
                    data = [d[0] for d in data if len(d) > 0 and d[0] == imdb]

                    if len(data) >= 1:
                        url = i
            else:
                url = r[0]

            if url:
                return source_utils.strip_domain(url)
        except:
            return

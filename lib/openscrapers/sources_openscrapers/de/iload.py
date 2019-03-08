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
        self.domains = ['iload.to']
        self.base_link = 'http://iload.to'
        self.search_link_mv = '/suche/%s/Filme'
        self.search_link_tv = '/suche/%s/Serien'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(self.search_link_mv, imdb, [localtitle] + source_utils.aliases_to_array(aliases))
            if not url and title != localtitle: url = self.__search(self.search_link_mv, imdb, [title] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search(self.search_link_tv, imdb, [localtvshowtitle] + source_utils.aliases_to_array(aliases))
            if not url and tvshowtitle != localtvshowtitle: url = self.__search(self.search_link_tv, imdb, [tvshowtitle] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            query = urlparse.urljoin(self.base_link, url)

            r = client.request(query)
            r = dom_parser.parse_dom(r, 'td', attrs={'data-title-name': re.compile('Season %02d' % int(season))})
            r = dom_parser.parse_dom(r, 'a', req='href')[0].attrs['href']
            r = client.request(urlparse.urljoin(self.base_link, r))
            r = dom_parser.parse_dom(r, 'td', attrs={'data-title-name': re.compile('Episode %02d' % int(episode))})
            r = dom_parser.parse_dom(r, 'a', req='href')[0].attrs['href']

            return source_utils.strip_domain(r)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            query = urlparse.urljoin(self.base_link, url)

            r = client.request(query)
            r = dom_parser.parse_dom(r, 'div', attrs={'id': 'Module'})
            r = [(r, dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('[^\'"]*xrel_search_query[^\'"]*')}, req='href'))]
            r = [(i[0], i[1][0].attrs['href'] if i[1] else '') for i in r]

            rels = dom_parser.parse_dom(r[0][0], 'a', attrs={'href': re.compile('[^\'"]*ReleaseList[^\'"]*')}, req='href')
            if rels and len(rels) > 1:
                r = []
                for rel in rels:
                    relData = client.request(urlparse.urljoin(self.base_link, rel.attrs['href']))
                    relData = dom_parser.parse_dom(relData, 'table', attrs={'class': 'release-list'})
                    relData = dom_parser.parse_dom(relData, 'tr', attrs={'class': 'row'})
                    relData = [(dom_parser.parse_dom(i, 'td', attrs={'class': re.compile('[^\'"]*list-name[^\'"]*')}),
                                dom_parser.parse_dom(i, 'img', attrs={'class': 'countryflag'}, req='alt'),
                                dom_parser.parse_dom(i, 'td', attrs={'class': 'release-types'})) for i in relData]
                    relData = [(i[0][0].content, i[1][0].attrs['alt'].lower(), i[2][0].content) for i in relData if i[0] and i[1] and i[2]]
                    relData = [(i[0], i[2]) for i in relData if i[1] == 'deutsch']
                    relData = [(i[0], dom_parser.parse_dom(i[1], 'img', attrs={'class': 'release-type-stream'})) for i in relData]
                    relData = [i[0] for i in relData if i[1]]
                    #relData = dom_parser.parse_dom(relData, 'a', req='href')[:3]
                    relData = dom_parser.parse_dom(relData, 'a', req='href')

                    for i in relData:
                        i = client.request(urlparse.urljoin(self.base_link, i.attrs['href']))
                        i = dom_parser.parse_dom(i, 'div', attrs={'id': 'Module'})
                        i = [(i, dom_parser.parse_dom(i, 'a', attrs={'href': re.compile('[^\'"]*xrel_search_query[^\'"]*')}, req='href'))]
                        r += [(x[0], x[1][0].attrs['href'] if x[1] else '') for x in i]

            r = [(dom_parser.parse_dom(i[0], 'div', attrs={'id': 'ModuleReleaseDownloads'}), i[1]) for i in r]
            r = [(dom_parser.parse_dom(i[0][0], 'a', attrs={'class': re.compile('.*-stream.*')}, req='href'), i[1]) for i in r if len(i[0]) > 0]

            for items, rel in r:
                rel = urlparse.urlparse(rel).query
                rel = urlparse.parse_qs(rel)['xrel_search_query'][0]

                quality, info = source_utils.get_release_quality(rel)

                items = [(i.attrs['href'], i.content) for i in items]
                items = [(i[0], dom_parser.parse_dom(i[1], 'img', req='src')) for i in items]
                items = [(i[0], i[1][0].attrs['src']) for i in items if i[1]]
                items = [(i[0], re.findall('.+/(.+\.\w+)\.\w+', i[1])) for i in items]
                items = [(i[0], i[1][0]) for i in items if i[1]]

                info = ' | '.join(info)

                for link, hoster in items:
                    valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                    if not valid: continue

                    sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': link, 'info': info, 'direct': False, 'debridonly': False, 'checkquality': True})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            url = client.request(urlparse.urljoin(self.base_link, url), output='geturl')
            return url if self.base_link not in url else None
        except:
            return

    def __search(self, search_link, imdb, titles):
        try:
            query = search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'big-list'})
            r = dom_parser.parse_dom(r, 'table', attrs={'class': 'row'})
            r = dom_parser.parse_dom(r, 'td', attrs={'class': 'list-name'})
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [i.attrs['href']for i in r if i and cleantitle.get(i.content) in t][0]

            url = source_utils.strip_domain(r)

            r = client.request(urlparse.urljoin(self.base_link, url))
            r = dom_parser.parse_dom(r, 'a', attrs={'href': re.compile('.*/tt\d+.*')}, req='href')
            r = [re.findall('.+?(tt\d+).*?', i.attrs['href']) for i in r]
            r = [i[0] for i in r if i]

            return url if imdb in r else None
        except:
            return

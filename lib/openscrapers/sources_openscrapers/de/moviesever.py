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

import base64
import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['moviesever.com/']
        self.base_link = 'http://moviesever.com/'
        self.search_link = '/?s=%s'

        self.get_link = 'http://play.seriesever.net/me/moviesever.php'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            rels = dom_parser.parse_dom(r, 'nav', attrs={'class': 'player'})
            rels = dom_parser.parse_dom(rels, 'ul', attrs={'class': 'idTabs'})
            rels = dom_parser.parse_dom(rels, 'li')
            rels = [(dom_parser.parse_dom(i, 'a', attrs={'class': 'options'}, req='href'), dom_parser.parse_dom(i, 'img', req='src')) for i in rels]
            rels = [(i[0][0].attrs['href'][1:], re.findall('/flags/(\w+)\.png$', i[1][0].attrs['src'])) for i in rels if i[0] and i[1]]
            rels = [i[0] for i in rels if len(i[1]) > 0 and i[1][0].lower() == 'de']

            r = [dom_parser.parse_dom(r, 'div', attrs={'id': i}) for i in rels]
            r = [(re.findall('link"?\s*:\s*"(.+?)"', ''.join([x.content for x in i])), dom_parser.parse_dom(i, 'iframe', attrs={'class': 'metaframe'}, req='src')) for i in r]
            r = [i[0][0] if i[0] else i[1][0].attrs['src'] for i in r if i[0] or i[1]]

            for i in r:
                try:
                    i = re.sub('\[.+?\]|\[/.+?\]', '', i)
                    i = client.replaceHTMLCodes(i)
                    if not i.startswith('http'): i = self.__decode_hash(i)
                    if 'play.seriesever' in i:
                        i = client.request(i)
                        i = dom_parser.parse_dom(i, 'iframe', req='src')
                        if len(i) < 1: continue
                        i = i[0].attrs['src']

                    valid, host = source_utils.is_host_valid(i, hostDict)
                    if not valid: continue

                    urls, host, direct = source_utils.check_directstreams(i, host)

                    for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'de', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        if url.startswith('/'): url = 'http:%s' % url
        return url

    def __decode_hash(self, hash):
        hash = hash.replace("!BeF", "R")
        hash = hash.replace("@jkp", "Ax")
        hash += '=' * (-len(hash) % 4)
        try: return base64.b64decode(hash)
        except: return

    def __search(self, titles, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'details'})
            r = [(dom_parser.parse_dom(i, 'div', attrs={'class': 'title'}), dom_parser.parse_dom(i, 'span', attrs={'class': 'year'})) for i in r]
            r = [(dom_parser.parse_dom(i[0][0], 'a', req='href'), i[1][0].content) for i in r if i[0] and i[1]]
            r = [(i[0][0].attrs['href'], client.replaceHTMLCodes(i[0][0].content), i[1]) for i in r if i[0]]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return

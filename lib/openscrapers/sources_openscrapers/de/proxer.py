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
import json

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import tvmaze
from openscrapers.modules import anilist
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.genre_filter = ['animation', 'anime']
        self.domains = ['proxer.me']
        self.base_link = 'http://proxer.me'
        self.search_link = '/search?s=search&name=%s&sprache=alle&typ=%s&format=raw'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            alt_title = anilist.getAlternativTitle(title)
            aliases = source_utils.aliases_to_array(aliases)

            url = self.__search([alt_title] + aliases, year, 'movie')
            if not url and localtitle != alt_title: url = self.__search([localtitle] + aliases, year, 'movie')
            if not url and title != localtitle: url = self.__search([title] + aliases, year, 'movie')
            return urllib.urlencode({'url': url, 'episode': '1'}) if url else None
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            alt_title = anilist.getAlternativTitle(tvshowtitle)
            aliases = source_utils.aliases_to_array(aliases)

            url = self.__search([alt_title] + aliases, year, 'animeseries')
            if not url and localtvshowtitle != alt_title: url = self.__search([localtvshowtitle] + aliases, year, 'animeseries')
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + aliases, year, 'animeseries')
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            return urllib.urlencode({'url': url, 'episode': tvmaze.tvMaze().episodeAbsoluteNumber(tvdb, int(season), int(episode))})
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            for item_id, episode, content_type in self.__get_episode(data.get('url'), data.get('episode')):
                stream_link = urlparse.urljoin(self.base_link, '/watch/%s/%s/%s' % (item_id, episode, content_type))

                info = 'subbed' if content_type.endswith('sub') else ''

                r = client.request(stream_link)

                r = dom_parser.parse_dom(r, 'script')
                r = ' '.join([i.content for i in r if i.content])
                r = json.loads(re.findall('var\s*streams\s*=\s*(\[.*?\])\s*;', r)[0])
                r = [(i.get('replace'), i.get('code')) for i in r]
                r = [(i[0].replace('#', i[1])) for i in r if i[0] and i[1]]

                for stream_link in r:
                    if stream_link.startswith('/'): stream_link = 'http:%s' % stream_link

                    if self.domains[0] in stream_link:
                        stream_link = client.request(stream_link, cookie=urllib.urlencode({'proxerstream_player': 'flash'}))

                        i = [(match[0], match[1]) for match in re.findall('''["']?\s*file\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)(?:[^}>\]]+)["']?\s*width\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)''', stream_link, re.DOTALL)]
                        i = [(x[0].replace('\/', '/'), source_utils.label_to_quality(x[1])) for x in i]

                        for url, quality in i:
                            sources.append({'source': 'cdn', 'quality': quality, 'language': 'de', 'url': url, 'info': info, 'direct': True, 'debridonly': False})
                    else:
                        valid, host = source_utils.is_host_valid(stream_link, hostDict)
                        if not valid: continue

                        sources.append({'source': host, 'quality': 'SD', 'language': 'de', 'url': stream_link, 'info': info, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __get_episode(self, url, episode='1'):
        try:
            if not url:
                return []

            item_id = re.findall('info/(\d+)', url)[0]
            url = urlparse.urljoin(self.base_link, '/info/%s/list?format=json' % item_id)

            r = client.request(url)
            r = json.loads(r).get('data', [])
            return [(item_id, episode, i.get('typ')) for i in r if int(i.get('no', '0')) == int(episode) and 'ger' in i.get('typ')]
        except:
            return []

    def __search(self, titles, year, content_type):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])), content_type)
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'div', attrs={'id': 'search'})
            r = dom_parser.parse_dom(r, 'table')
            r = dom_parser.parse_dom(r, 'tr', attrs={'class': re.compile('entry\d+')})
            r = [(dom_parser.parse_dom(i, 'a'), dom_parser.parse_dom(i, 'img', attrs={'class': 'flag', 'alt': 'de'})) for i in r]
            r = [i[0] for i in r if i[0] and i[1]]
            r = [(i[0].attrs['href'], i[0].content) for i in r]
            r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return

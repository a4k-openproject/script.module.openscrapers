# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    Covenant Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib, urlparse, re

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import trakt
from openscrapers.modules import tvmaze


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['gr']
        self.domains = ['liomenoi.com']
        self.base_link = 'http://liomenoi.com'
        self.search_link = '?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(
                aliases),year)
            if not url: url = self.__search(trakt.getMovieTranslation(imdb, 'el'), year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search(
                [tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url: url = self.__search(tvmaze.tvMaze().getTVShowTranslation(tvdb, 'el'), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = url[:-1] if url.endswith('/') else url
            url += '/season/%d/episode/%d' % (int(season), int(episode))

            return url
        except:
            return

    def __search(self, titles, year):
        try:

            query = self.search_link % (urllib.quote_plus(cleantitle.getsearch(titles[0]+' '+year)))

            query = urlparse.urljoin(self.base_link, query)

            t =  cleantitle.get(titles[0])

            r = client.request(query)

            r = client.parseDOM(r, 'div', attrs={'class': 'card'})

            r = client.parseDOM(r, 'h3')

            for i in r:
                data = re.findall('<span.*?>(.+?)</span>.+?date">\s*\((\d{4}).*?</span>', i, re.DOTALL)
                for title, year in data:
                    title = cleantitle.get(title)
                    y = year
                    if title in t and year == y:
                        url = client.parseDOM(i, 'a', ret='href')[0]
                        return source_utils.strip_domain(url)

            return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            query = urlparse.urljoin(self.base_link, url)
            r = client.request(query)
            links = client.parseDOM(r, 'tbody')
            links = client.parseDOM(links, 'a',  ret='href')
            for i in range(len(links)):

                url = links[i]
                if 'target' in url: continue
                data = client.request(url)
                url = client.parseDOM(data, 'iframe', ret='src')[0]
                if url.startswith('/go'): url = re.findall('go\?(.+?)-', url)[0]
                if 'crypt' in url: continue
                if 'redvid' in url:
                    data = client.request(url)
                    url = client.parseDOM(data, 'iframe', ret='src')[0]

                if any(x in url for x in ['.online', 'xrysoi.se', 'filmer', '.bp', '.blogger', 'youtu']):
                    continue
                quality = 'SD'
                lang, info = 'gr', 'SUB'
                valid, host = source_utils.is_host_valid(url, hostDict)
                if 'hdvid' in host: valid = True
                if not valid: continue

                sources.append({'source': host, 'quality': quality, 'language': lang, 'url': url, 'info': info,
                                'direct':False,'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
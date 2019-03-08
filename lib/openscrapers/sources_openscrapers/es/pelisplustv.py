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

import re
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['es']
        self.domains = ['pelisplus.tv']
        self.base_link = 'http://pelisplus.tv'
        self.search_link = '/busqueda/?s=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),
                                                                    year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = url[:-1] if url.endswith('/') else url
            url += '/temporada/%d/capitulo/%d/' % (int(season), int(episode))
            return url
        except:
            return

    def __search(self, titles, year):
        try:
            query = self.search_link % (cleantitle.getsearch(titles[0].replace(' ','%20')))

            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i][0]

            r = client.request(query)

            r = client.parseDOM(r, 'li', attrs={'class': 'item everyone-item over_online haveTooltip'})

            for i in r:
                title = client.parseDOM(i, 'a', ret='title')[0]
                url = client.parseDOM(i, 'a', ret='href')[0]
                data = client.request(url)
                y = re.findall('<p><span>Año:</span>(\d{4})',data)[0]
                original_t = re.findall('movie-text">.+?h2.+?">\((.+?)\)</h2>',data, re.DOTALL)[0]
                original_t, title = cleantitle.get(original_t), cleantitle.get(title)

                if (t in title or t in original_t) and y == year :
                    x = dom_parser.parse_dom(i, 'a', req='href')
                    return source_utils.strip_domain(x[0][0]['href'])

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
            q = re.findall("'(http://www.elreyxhd.+?)'",r, re.DOTALL)[0]
            links = client.request(q)
            links = client.parseDOM(links, 'a', ret='href')

            for url in links:
                lang, info = 'es', 'LAT'
                qual = 'HD'
                if not 'http' in url: continue
                if 'elrey' in url :continue

                valid, host = source_utils.is_host_valid(url, hostDict)
                if not valid: continue

                sources.append({'source': host, 'quality': qual, 'language': lang, 'url': url, 'info': info, 'direct':
                    False,'debridonly': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        return url
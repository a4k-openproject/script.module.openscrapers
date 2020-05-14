# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    OpenScrapers Project
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
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 31
        self.language = ['en']
        self.domains = ['watchseries.movie', 'watch-series.co']
        self.base_link = 'https://www5.watchseries.movie'
        self.search_link = '/series/%s-season-%s-episode-%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle.replace(" ", "-").lower()
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link % (url, season, episode))
            print url
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url is None:
                return

            hostDict =  hostDict + hostprDict
            result = client.request(url)
            print result

            dom = dom_parser.parse_dom(result, 'a', req='data-video')
            urls = [i.attrs['data-video'] if i.attrs['data-video'].startswith('https') else 'https:' + i.attrs['data-video'] for i in dom]
            print urls

            for url in urls:
                valid, hoster = source_utils.is_host_valid(url, hostDict)
                if not valid: continue
                try:
                    url.decode('utf-8')
                    sources.append({'source': hoster, 'quality': 'SD', 'info': '', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            return sources

    def resolve(self, url):
        return url

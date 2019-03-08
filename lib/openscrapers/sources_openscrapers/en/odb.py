# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

"""
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
"""

import re
import traceback

from openscrapers.modules import client, log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['odb.to']
        self.base_link = 'https://api.odb.to'
        self.movie_link = '/embed?imdb_id=%s'
        self.tv_link = '/embed?imdb_id=%s&s=%s&e=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.base_link + self.movie_link % imdb
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ODB - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = imdb
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ODB - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            imdb = url
            url = self.base_link + self.tv_link % (imdb, season, episode)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ODB - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            r = client.request(url)
            try:
                match = re.compile('iframe id="odbIframe" src="(.+?)"').findall(r)
                for url in match:
                    host = url.split('//')[1].replace('www.', '')
                    host = host.split('/')[0].lower()
                    sources.append({
                        'source': host,
                        'quality': 'HD',
                        'language': 'en',
                        'url': url,
                        'direct': False,
                        'debridonly': False
                    })
            except Exception:
                failure = traceback.format_exc()
                log_utils.log('ODB - Exception: \n' + str(failure))
                return sources
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ODB - Exception: \n' + str(failure))
            return sources
        return sources

    def resolve(self, url):
        return url

# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
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

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ganool.ws', 'ganol.si', 'ganool123.com']
        self.base_link = 'https://www4.ganool.ws'
        self.search_link = '/search/?q=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None:
                return sources
            if debrid.status() is False:
                raise Exception()
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            q = '%s' % cleantitle.get_gan_url(data['title'])
            url = self.base_link + self.search_link % q
            r = self.scraper.get(url).content
            v = re.compile(
                '<a href="(.+?)" class="ml-mask jt" title="(.+?)">\r\n\t\t\t\t\t\t\t\t\t\t\t\t<span class=".+?">(.+?)</span>').findall(
                r)
            for url, check, quality in v:
                t = '%s (%s)' % (data['title'], data['year'])
                if t not in check:
                    raise Exception()
                key = url.split('-hd')[1]
                r = self.scraper.get('https://ganool.ws/moviedownload.php?q=' + key).content
                r = re.compile('<a rel=".+?" href="(.+?)" target=".+?">').findall(r)
                for url in r:
                    if any(x in url for x in ['.rar']):
                        continue
                    quality = source_utils.check_url(quality)
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid:
                        continue
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False,
                                    'debridonly': True})
            return sources
        except:
            return sources

    def resolve(self, url):
        return url

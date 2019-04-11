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
import requests

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cmovieshd.bz']
        self.base_link = 'http://w1.cmovieshd.bz'
        self.search_link = '/film/%s/watching.html?ep=0'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title).replace('--', '-')
            url = {'title': title, 'year': year}
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            queries = [url['title'], '%s-%s' % (url['title'], url['year'])]

            r = requests.get('%s%s' % (self.base_link, self.search_link % queries[0]))
            if not r.ok:
                r = requests.get('%s%s' % (self.base_link, self.search_link % queries[1]))
            if not r.ok:
                return

            r = r.content
            qual = re.compile('class="quality">(.+?)<').findall(r)

            for i in qual:
                if '1080' in i:
                    quality = '1080p'
                elif '720' in i:
                    quality = '720p'
                else:
                    quality = 'SD'
            u = client.parseDOM(r, "div", attrs={"class": "pa-main anime_muti_link"})

            for t in u:
                urls = re.findall('<li class=".+?" data-video="(.+?)"', t)
                for url in urls:
                    if 'vidcloud' in url:
                        url = 'https:' + url
                        r = requests.get(url).content
                        t = re.findall('li data-status=".+?" data-video="(.+?)"', r)
                        for url in t:
                            if 'vidcloud' in url:
                                continue
                            valid, host = source_utils.is_host_valid(url, hostDict)
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    if 'vidcloud' in url:
                        continue
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                return sources
        except:
            import traceback
            traceback.print_exc()
            return

    def resolve(self, url):
        return url

    def unit_test(self, test_type, hosts):

        if test_type == 'movie':
           url = self.movie('', 'Holiday', '', [], '2018')
           url = self.sources(url, hosts, [])
        else:
            raise Exception("No Episode Calls Available")
        return url

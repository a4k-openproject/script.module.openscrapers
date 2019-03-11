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
import urlparse

from openscrapers.modules import cleantitle

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['iwaatch.com']
        self.base_link = 'https://iwaatch.com/'
        self.search_link = 'https://iwaatch.com/?q=%s'
        self.sources2 = []

    def movie(self, imdb, title, localtitle, aliases, year):
        if 1:  # try:
            clean_title = cleantitle.geturl(title).replace('-', '%20')
            url = urlparse.urljoin(self.base_link, (
            self.search_link % (clean_title))) + '$$$$$' + title + '$$$$$' + year + '$$$$$' + 'movie'
            return url
            # except:
            #    return

    def sources(self, url, hostDict, hostprDict):
        import requests
        self.sources2 = []

        if url is None:
            return self.sources2

        data = url.split('$$$$$')

        url = data[0]
        title = data[1]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',

            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers',
        }

        response = requests.get(url, headers=headers).content
        regex = '<div class="col-xs-.+?a href="(.+?)".+?div class="post-title">(.+?)<'
        match2 = re.compile(regex, re.DOTALL).findall(response)

        for link_in, title_in in match2:
            if title in title_in:
                x = requests.get(link_in.replace('movie', 'view'), headers=headers).content
                regex = "file: '(.+?)'.+?label: '(.+?)'"
                match3 = re.compile(regex, re.DOTALL).findall(x)

                for url, q in match3:
                    self.sources2.append(
                        {'source': 'Direct', 'quality': q, 'language': 'en', 'url': url, 'direct': True,
                         'debridonly': False})

        return self.sources2

    def resolve(self, url):
        return url

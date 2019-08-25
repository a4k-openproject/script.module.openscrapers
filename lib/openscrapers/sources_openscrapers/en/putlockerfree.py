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

from openscrapers.modules import cleantitle
from openscrapers.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['putlockerfree.sc']
        self.base_link = 'https://www.putlockerfree.sc'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            tvshowtitle = cleantitle.geturl(tvshowtitle)
            url = tvshowtitle
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            http = self.base_link + '/tv_series/%s-season-%s/' % (url, season)
            url = http + 'watching.html/'
            url = 'url="' + url + '"&episode="' + episode + '"'
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            match = re.compile('url="(.+?)"&episode="(.+?)"').findall(url)
            for url, episode in match:
                url = url
                episode = episode
                r = client.request(url)
                try:
                    match = re.compile('<a title="Episode ' + episode + '.+?" data-openload="(.+?)"').findall(r)
                    for url in match:
                        if '2160' in url:
                            quality = '4K'
                        elif '1080' in url:
                            quality = '1080p'
                        elif '720' in url:
                            quality = 'HD'
                        elif '480' in url:
                            quality = 'SD'
                        else:
                            quality = 'SD'
                        url = url
                        sources.append({
                            'source': 'Openload.co',
                            'quality': quality,
                            'language': 'en',
                            'url': url,
                            'direct': False,
                            'debridonly': False
                        })
                except:
                    return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url

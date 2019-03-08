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
        self.domains = ['xrysoi.se']
        self.base_link = 'http://xrysoi.se/'
        self.search_link = 'search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'aliases': aliases,'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']
            year = data['year']
            query = '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)
            posts = client.parseDOM(r, 'item')

            for post in posts:
                try:
                    name = client.parseDOM(post, 'title')

                    links = client.parseDOM(post, 'a', ret='href')

                    t = re.sub('(\.|\(|\[|\s|)(\d{4})(\.|\)|\]|\s|)(.+|)', '',name[0])
                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()

                    y = re.findall('\(\s*(\d{4})\s*\)', name[0])[0]
                    if not y == year: raise Exception()

                    for url in links:
                        if any(x in url for x in ['.online', 'xrysoi.se', 'filmer', '.bp', '.blogger']): continue

                        url = client.replaceHTMLCodes(url)
                        url = url.encode('utf-8')
                        valid, host = source_utils.is_host_valid(url,hostDict)
                        if 'hdvid' in host: valid = True
                        if not valid: continue
                        quality = 'SD'
                        info = 'SUB'

                        sources.append({'source': host, 'quality': quality, 'language': 'gr', 'url': url, 'info': info, 'direct': False, 'debridonly': False})

                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url
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

import json
import re
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['wannahd.us']
        self.base_link = 'http://www.wannahd.one'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']
            year = data['year']

            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', title)

            query = self.search_link % urllib.quote_plus(query)
            query = urlparse.urljoin(self.base_link, query)
            r = self.scraper.get(query).content
            posts = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            posts = [(client.parseDOM(i, 'a', ret='href')[0],
                      client.parseDOM(i, 'h2')[0],
                      client.parseDOM(i, 'a', attrs={'rel': 'tag'})[0]) for i in posts if i]
            posts = [(i[0], i[1]) for i in posts if year == i[2]]
            post = [i[0] for i in posts if cleantitle.get(title) == cleantitle.get(i[1])][0]

            url = urlparse.urljoin(self.base_link, post) if post.startswith('/') else post
            r = self.scraper.get(url).content

            frames = client.parseDOM(r, 'iframe', ret='src')
            for frame in frames:
                if 'wannahd' in frame:
                    try:
                        r = self.scraper.get(frame).content
                        links = re.findall('sources:\s*(\[.+?\])', r, re.DOTALL)[0]
                        links = json.loads(links)
                        links = [(i['label'], i['file']) for i in links if i['file']]
                        for qual, link in links:
                            quality, info = source_utils.get_release_quality(qual, qual)
                            link = urllib.quote(link, ':?/;.,%@#$^&!')
                            sources.append(
                                {'source': 'GVIDEO', 'quality': quality, 'language': 'en', 'url': link, 'direct': True,
                                 'debridonly': False})

                    except Exception:
                        pass

                elif 'movienight' in frame:
                    pass

                else:
                    valid, host = source_utils.is_host_valid(frame, hostDict)
                    if valid:
                        sources.append(
                            {'source': host, 'quality': 'HD', 'language': 'en', 'url': frame, 'direct': False,
                             'debridonly': False})

            return sources
        except Exception:
            return sources

    def resolve(self, url):
        return url

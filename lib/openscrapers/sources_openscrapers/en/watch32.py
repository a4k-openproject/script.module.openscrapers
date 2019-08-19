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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import jsunpack
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watch32hd.co']
        self.base_link = 'https://watch32hd.co/'
        self.search_link = 'results?q=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']

            hdlr = data['year']

            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', title)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)
            r = client.request(url)

            posts = client.parseDOM(r, 'div', attrs={'class': 'video_title'})

            items = []

            for post in posts:
                try:
                    data = dom_parser.parse_dom(post, 'a', req=['href', 'title'])[0]
                    t = data.content
                    y = re.findall('\((\d{4})\)', data.attrs['title'])[0]
                    qual = data.attrs['title'].split('-')[1]
                    link = data.attrs['href']

                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()
                    if not y == hdlr: raise Exception()

                    items += [(link, qual)]

                except BaseException:
                    pass
            for item in items:
                try:
                    r = client.request(item[0]) if item[0].startswith('http') else client.request(
                        urlparse.urljoin(self.base_link, item[0]))

                    qual = client.parseDOM(r, 'h1')[0]
                    quality = source_utils.get_release_quality(item[1], qual)[0]

                    url = re.findall('''frame_url\s*=\s*["']([^']+)['"]\;''', r, re.DOTALL)[0]
                    url = url if url.startswith('http') else urlparse.urljoin('https://', url)

                    sources.append({'source': 'GVIDEO', 'quality': quality, 'language': 'en', 'url': url,
                                    'direct': False, 'debridonly': False})

                except BaseException:
                    pass

            return sources
        except BaseException:
            return sources

    def resolve(self, url):
        try:
            if 'vidlink' in url:
                ua = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1'}
                html = client.request(url, headers=ua)
                postID = re.findall("postID\s*=\s*'([^']+)", html)[0]

                rid = client.request('https://vidlink.org/embed/update_views', post=None, headers=ua, referer=url)
                id_view = re.findall('''id_view['"]\s*:\s*['"]([^'"]+)['"]''', rid)[0]

                plink = 'https://vidlink.org/streamdrive/info'
                data = {'browserName': 'Firefox',
                        'platform': 'Win32',
                        'postID': postID,
                        'id_view': id_view}
                headers = ua
                headers['X-Requested-With'] = 'XMLHttpRequest'
                headers['Referer'] = url
                ihtml = client.request(plink, post=data, headers=headers)
                linkcode = jsunpack.unpack(ihtml).replace('\\', '')
                sources = json.loads(re.findall('window\.srcs\s*=\s*([^;]+)', linkcode, re.DOTALL)[0])
                for src in sources:
                    link = src['url']
                    return link
            else:
                return url
        except BaseException:
            return url

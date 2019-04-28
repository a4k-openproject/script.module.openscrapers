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
import urlparse
import unicodedata

from openscrapers.modules import cache
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils
from openscrapers.modules import directstream

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['sezonlukdizi.org/']
        self.base_link = 'https://sezonlukdizi.org/'
        self.search_link = '/js/series1.js'
        self.video_link = '/ajax/dataEmbed.asp'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            t = [tvshowtitle] + source_utils.aliases_to_array(aliases)
            t = [cleantitle.get(i) for i in set(t) if i]

            url = [i[0] for i in cache.get(self.sezonlukdizi_tvcache, 120) if cleantitle.get(i[1]) in t][0]

            return source_utils.strip_domain(url)
        except:
            return

    def sezonlukdizi_tvcache(self):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)

            result = client.request(url, redirect=False)

            if not result:
                r = client.request(self.base_link)
                r = dom_parser.parse_dom(r, 'script', attrs={'type': 'text/javascript', 'src': re.compile('.*/js/dizi.*')}, req='src')[0]
                url = urlparse.urljoin(self.base_link, r.attrs['src'])
                result = client.request(url)

            result = re.compile('{(.+?)}').findall(result)
            result = [(re.findall('u\s*:\s*(?:\'|\")(.+?)(?:\'|\")', i), re.findall('d\s*:\s*(?:\'|\")(.+?)(?:\',|\")', i)) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [(re.compile('/diziler(/.+?)(?://|\.|$)').findall(i[0]), re.sub('&#\d*;', '', i[1])) for i in result]
            result = [(i[0][0] + '/', cleantitle.query(self.lat2asc(i[1]))) for i in result if len(i[0]) > 0]

            return result
        except:
            return []

    def lat2asc(self, title):
        title = title.decode('iso8859-1')
        return unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = '%s%01d-sezon-%01d-bolum.html' % (url.replace('.html', ''), int(season), int(episode))
            return source_utils.strip_domain(url)
        except:
            return []

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)
            c = client.request(url, output='cookie')
            result = client.request(url)

            result = re.sub(r'[^\x00-\x7F]+', ' ', result)

            pages = dom_parser.parse_dom(result, 'div', attrs={'class': 'item'}, req='data-id')
            pages = [i.attrs['data-id'] for i in pages]

            for page in pages:
                try:
                    url = urlparse.urljoin(self.base_link, self.video_link)

                    result = client.request(url, post={'id': page}, cookie=c)
                    if not result: continue

                    url = dom_parser.parse_dom(result, 'iframe', req='src')[0].attrs['src']
                    if url.startswith('//'): url = 'http:' + url
                    if url.startswith('/'): url = urlparse.urljoin(self.base_link, url)

                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if valid: sources.append({'source': host, 'quality': 'HD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})

                    if '.asp' not in url: continue

                    result = client.request(url, cookie=c)

                    try:
                        url = dom_parser.parse_dom(result, 'iframe', req='src')[0].attrs['src']
                        url = url.replace('https://href.li/?', '')
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            if host == 'gvideo':
                                ginfo = directstream.google(url)
                                for g in ginfo: sources.append({'source': host, 'quality': g['quality'], 'language': 'en', 'url': g['url'], 'direct': True, 'debridonly': False})
                            else: sources.append({'source': host, 'quality': 'HD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    except: pass

                    captions = re.search('''["']?kind["']?\s*:\s*(?:\'|\")captions(?:\'|\")''', result)
                    if not captions: continue

                    matches = [(match[0], match[1]) for match in re.findall('''["']?label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)["']?(?:[^}\]]+)["']?\s*file\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)''', result, re.DOTALL | re.I)]
                    matches += [(match[1], match[0]) for match in re.findall('''["']?\s*file\s*["']?\s*[:=,]?\s*["'](?P<url>[^"']+)(?:[^}>\]]+)["']?\s*label\s*["']?\s*[:=]\s*["']?(?P<label>[^"',]+)''', result, re.DOTALL | re.I)]

                    result = [(source_utils.label_to_quality(x[0]), x[1].replace('\/', '/')) for x in matches]
                    result = [(i[0], i[1]) for i in result if not i[1].endswith('.vtt')]

                    for quality, url in result: sources.append({'source': 'gvideo', 'quality': quality, 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            if url.startswith('//'): url = 'http:' + url
            if url.startswith('/'): url = urlparse.urljoin(self.base_link, url)
            return url
        except:
            pass

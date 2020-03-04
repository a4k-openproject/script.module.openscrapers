# -*- coding: UTF-8 -*-

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

import requests
import urllib
import urlparse
import json

from openscrapers.modules import cfscrape
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.base_link = 'https://api.filepursuit.com/'
        self.search_link = '?type=video&q=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            if 'tvshowtitle' in data: query = '%s S%02dE%02d' %(data['tvshowtitle'], int(data['season']), int(data['episode']))
            else: query = '%s %s' % (data['title'], data['year'])
            url = self.search_link % urllib.quote(query)
            url = self.base_link + self.search_link % query
            url = urlparse.urljoin(self.base_link, url).replace('%20', '-')
            r = self.scraper.get(url).content
            r = r.split('Array')[0]
            r = json.loads(r)
            if not r.get('paired', False):
                return sources
            results = r['files_found']
            for item in results:
                try: size = item['file_size_bytes']
                except: size = None
                try: name = item['file_name']
                except: name = item['file_link'].split('/')[-1]
                url = item['file_link']
                details = self.details(name, size)
                details = '%s | %s' % (details, name)
                quality = source_utils.get_release_quality(name, url)
                sources.append({'source': 'DL',
                                'quality': quality[0],
                                'language': "en",
                                'url': url,
                                'info': details,
                                'direct': True,
                                'debridonly': False})
            return sources
        except:
            return sources

    def details(self, name, size):
        import HTMLParser, re
        name = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", name)
        name = HTMLParser.HTMLParser().unescape(name)
        name = name.replace("&quot;", "\"")
        name = name.replace("&amp;", "&")
        if size: size = float(size) / 1073741824
        fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*)(\.|\)|\]|\s)', '', name)
        fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
        fmt = [x.lower() for x in fmt]
        if '3d' in fmt:
            q = '  | 3D'
        else:
            q = ''
        try:
            if any(i in ['hevc', 'h265', 'x265'] for i in fmt): v = 'HEVC'
            else: v = 'h264'
            if size: info = '%.2f GB%s | %s' % (size, q, v)
            else: '%s | %s' % (q, v)
            return info
        except: pass
        try:
            if size: info = '%.2f GB | %s' % (size, name.replace('.', ' '))
            else: info = '| %s' % (name.replace('.', ' '))
            return info
        except: pass

    def resolve(self, url):
        return url

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

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['warezmovies.info']
        self.base_link = 'http://warezmovies.info/'
        self.search_link = 'search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
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
            if url is None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            self._sources = []

            if url is None: return self._sources

            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            self.title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            self.hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data[
                'year']

            self.hostDict = hostprDict + hostDict

            items = []
            urls = []
            posts = []
            links = []

            if 'tvshowtitle' not in data:
                url = urlparse.urljoin(self.base_link, self.search_link % data['imdb'])
                r = client.request(url, headers={'User-Agent': client.agent()})
                posts = client.parseDOM(r, 'item')
            else:
                url = urlparse.urljoin(self.base_link, self.search_link % (
                        cleantitle.geturl(self.title).replace('-', '+') + '+' + self.hdlr))
                r = client.request(url, headers={'User-Agent': client.agent()})
                posts = client.parseDOM(r, 'item')

            if not posts: return self._sources

            for post in posts:
                try:
                    t = client.parseDOM(post, 'title')[0]
                    u = client.parseDOM(post, 'link')[0]
                    s = re.search('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', post)
                    s = s.groups()[0] if s else '0'
                    items += [(t, u, s)]
                except BaseException:
                    pass

            items = set(items)

            threads = []
            for i in items: threads.append(workers.Thread(self._get_sources, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            return self._sources
        except BaseException:
            return self._sources

    def _get_sources(self, i):
        try:
            name = i[0]
            name = client.replaceHTMLCodes(name)
            r = client.request(i[1].strip())
            r = client.parseDOM(r, 'p')
            r = [e for e in r if all(x in e.lower() for x in ['single', 'link'])]
            links = client.parseDOM(r[0], 'a', ret='href')
            for url in links:
                try:
                    if any(x in url for x in ['.rar.', '.zip.', '.iso.']) or any(
                            url.endswith(x) for x in ['.rar', '.zip', '.iso']): raise Exception()
                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d+E\d+|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', name, flags=re.I)
                    if not cleantitle.get(t) == cleantitle.get(self.title): raise Exception()
                    try:
                        y = re.findall('(?:\.|\(|\[|\s*|)(S\d+E\d+|S\d+)(?:\.|\)|\]|\s*|)', name, re.I)[-1].upper()
                    except BaseException:
                        y = re.findall('(?:\.|\(|\[|\s*|)(\d{4})(?:\.|\)|\]|\s*|)', name, re.I)[0].upper()
                    if not y == self.hdlr: raise Exception()

                    valid, host = source_utils.is_host_valid(url, self.hostDict)
                    if not valid: continue
                    if host in ['1fichier.com', 'uptobox.com']: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    info = []
                    quality, info = source_utils.get_release_quality(name, url)
                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', i[2])[0]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except BaseException:
                        pass

                    info = ' | '.join(info)
                    self._sources.append(
                        {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                         'direct': False, 'debridonly': True})
                except BaseException:
                    pass
        except BaseException:
            pass

    def resolve(self, url):
        return url

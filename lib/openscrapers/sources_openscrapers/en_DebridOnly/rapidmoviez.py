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
import time
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import dom_parser2
from openscrapers.modules import source_utils
from openscrapers.modules import workers


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['rmz.cr']
        self.base_link = 'http://rmz.cr/'
        self.search_link = 'search/%s'
        self.scraper = cfscrape.create_scraper()

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
        except Exception:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def search(self, title, year):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link % (urllib.quote_plus(title)))
            headers = {'User-Agent': client.agent()}
            r = self.scraper.get(url, headers=headers).content
            r = dom_parser2.parse_dom(r, 'div', {'class': 'list_items'})[0]
            r = dom_parser2.parse_dom(r.content, 'li')
            r = [(dom_parser2.parse_dom(i, 'a', {'class': 'title'})) for i in r]
            r = [(i[0].attrs['href'], i[0].content) for i in r]
            r = [(urlparse.urljoin(self.base_link, i[0])) for i in r if
                 cleantitle.get(title) in cleantitle.get(i[1]) and year in i[1]]
            if r:
                return r[0]
            else:
                return
        except:
            return

    def sources(self, url, hostDict, hostprDict):

        self.sources = []

        try:
            if url is None:
                return self.sources

            if debrid.status() is False:
                raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = data['year']
            hdlr2 = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else ''
            imdb = data['imdb']

            url = self.search(title, hdlr)
            headers = {'User-Agent': client.agent()}
            r = self.scraper.get(url, headers=headers).content
            if hdlr2 == '':
                r = dom_parser2.parse_dom(r, 'ul', {'id': 'releases'})[0]
            else:
                r = dom_parser2.parse_dom(r, 'ul', {'id': 'episodes'})[0]
            r = dom_parser2.parse_dom(r.content, 'a', req=['href'])
            r = [(i.content, urlparse.urljoin(self.base_link, i.attrs['href'])) for i in r if
                 i and i.content != 'Watch']
            if hdlr2 != '':
                r = [(i[0], i[1]) for i in r if hdlr2.lower() in i[0].lower()]

            self.hostDict = hostDict + hostprDict
            threads = []

            for i in r:
                threads.append(workers.Thread(self._get_sources, i[0], i[1]))
            [i.start() for i in threads]

            alive = [x for x in threads if x.is_alive() is True]
            while alive:
                alive = [x for x in threads if x.is_alive() is True]
                time.sleep(0.1)
            return self.sources
        except:
            return self.sources

    def _get_sources(self, name, url):
        try:
            headers = {'User-Agent': client.agent()}
            r = self.scraper.get(url, headers=headers).content
            name = client.replaceHTMLCodes(name)
            l = dom_parser2.parse_dom(r, 'div', {'class': 'ppu2h'})
            s = ''
            for i in l:
                s += i.content
            urls = re.findall(r'''((?:http|ftp|https)://[\w_-]+(?:(?:\.[\w_-]+)+)[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])''',
                              i.content, flags=re.MULTILINE | re.DOTALL)
            urls = [i for i in urls if
                    '.rar' not in i or '.zip' not in i or '.iso' not in i or '.idx' not in i or '.sub' not in i]
            for url in urls:
                if url in str(self.sources):
                    continue

                valid, host = source_utils.is_host_valid(url, self.hostDict)
                if not valid:
                    continue
                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')
                quality, info = source_utils.get_release_quality(name, url)
                try:
                    size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', name)[0]
                    div = 1 if size.endswith(('GB', 'GiB')) else 1024
                    size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                    size = '%.2f GB' % size
                    info.append(size)
                except BaseException:
                    pass
                info = ' | '.join(info)
                self.sources.append(
                    {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False,
                     'debridonly': True})
        except:
            pass

    def resolve(self, url):
        return url

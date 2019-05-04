# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

"""
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
"""

import re
import urllib
import urlparse

from openscrapers.modules import client
from openscrapers.modules import control
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = ['1337x.to', '1337x.is', '1337x.st', '1337x.ws', '1337x.eu', '1337x.se']
        self.base_link = 'https://1337x.to'
        self.search_link = '/search/%s/1/'
        self.min_seeders = int(control.setting('torrent.min.seeders'))

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
        except:
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

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None: return sources
            if debrid.status() is False: raise Exception()
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
            query = '%s s%02de%02d' % (
                data['tvshowtitle'], int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
                data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)
            r = client.request(url)
            try:
                posts = client.parseDOM(r, 'div', attrs={'class': 'box-info'})
                for post in posts:
                    data = client.parseDOM(post, 'a', ret='href')
                    u = [i for i in data if '/torrent/' in i]
                    for u in u:
                        match = '%s %s' % (title, hdlr)
                        match = match.replace('+', '-').replace(' ', '-').replace(':-', '-').replace('---', '-')
                        if not match in u: continue
                        u = self.base_link + u
                        r = client.request(u)
                        r = client.parseDOM(r, 'div', attrs={'class': 'torrent-category-detail clearfix'})
                        for t in r:
                            link = re.findall('href="magnet:(.+?)" onclick=".+?"', t)[0]
                            link = 'magnet:%s' % link
                            link = str(client.replaceHTMLCodes(link).split('&tr')[0])
                            seeds = int(re.compile('<span class="seeds">(.+?)</span>').findall(t)[0])
                            if self.min_seeders > seeds:
                                continue
                            quality, info = source_utils.get_release_quality(link, link)
                            try:
                                size = re.findall('<strong>Total size</strong> <span>(.+?)</span>', t)
                                for size in size:
                                    size = '%s' % size
                                    info.append(size)
                            except BaseException:
                                pass
                            info = ' | '.join(info)
                            sources.append(
                                {'source': 'Torrent', 'quality': quality, 'language': 'en', 'url': link, 'info': info,
                                 'direct': False, 'debridonly': True})
            except:
                return
            return sources
        except:
            return sources

    def resolve(self, url):
        return url

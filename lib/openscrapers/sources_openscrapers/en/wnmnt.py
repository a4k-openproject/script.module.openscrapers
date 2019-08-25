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

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchnewmovienet.com']
        self.base_link = 'http://watchnewmovienet.com/'
        self.search_link = '/search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
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

    def searchShow(self, title, season):
        try:
            sea = '%s season %d' % (title, int(season))
            query = self.search_link % urllib.quote_plus(cleantitle.getsearch(sea))
            url = urlparse.urljoin(self.base_link, query)
            headers = {'User-Agent': client.agent(),
                       'Referer': self.base_link}
            scraper = cfscrape.create_scraper()
            r = scraper.get(url, headers=headers).content
            # r = client.request(url)
            r = client.parseDOM(r, 'item')
            r = [(client.parseDOM(i, 'title')[0], i) for i in r if i]
            r = [i[1] for i in r if sea.lower() in i[0].replace('  ', ' ').lower()]
            links = re.findall('''<h4>(EP\d+)</h4>.+?src="(.+?)"''', r[0], re.I | re.DOTALL)
            links = [(i[0], i[1].lstrip()) for i in links if i]
            return links
        except BaseException:
            return

    def searchMovie(self, title, year):
        try:
            query = self.search_link % urllib.quote_plus(cleantitle.getsearch(title + ' ' + year))
            url = urlparse.urljoin(self.base_link, query)
            headers = {'User-Agent': client.agent(),
                       'Referer': self.base_link}
            scraper = cfscrape.create_scraper()
            r = scraper.get(url, headers=headers).content
            r = client.parseDOM(r, 'item')
            r = [(client.parseDOM(i, 'title')[0], i) for i in r if i]
            r = [i[1] for i in r if cleantitle.get(title) in cleantitle.get(i[0]) and year in i[0]]
            return r[0]
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            try:
                if 'tvshowtitle' in data:
                    epi = 'EP%d' % int(data['episode'])
                    links = self.searchShow(data['tvshowtitle'], data['season'])
                    url = [i[1] for i in links if epi.lower() == i[0].lower()]
                else:

                    url = self.searchMovie(data['title'], data['year'])

                    try:
                        url = re.findall('''src=['"]\s*(.+?)['"]''', url, re.DOTALL)
                    except BaseException:
                        url = client.parseDOM(url, 'iframe', ret='src')

            except BaseException:
                pass
            for u in url:
                u = u.lstrip()
                if 'entervideo' in u:
                    r = client.request(u)
                    url = client.parseDOM(r, 'source', ret='src')[0]
                    quality, info = source_utils.get_release_quality(url, url)
                    sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': url,
                                    'direct': True, 'debridonly': False})
                elif 'vidnode' in u:
                    headers = {'Host': 'vidnode.net',
                               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                               'Upgrade-Insecure-Requests': '1',
                               'Accept-Language': 'en-US,en;q=0.9'}
                    r = client.request(u, headers=headers)
                    links = re.findall('''\{file:\s*['"]([^'"]+).*?label:\s*['"](\d+\s*P)['"]''', r, re.DOTALL | re.I)
                    for u, qual in links:
                        quality, info = source_utils.get_release_quality(qual, u)
                        url = u
                        sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': url,
                                        'direct': True, 'debridonly': False})

            return sources
        except BaseException:
            return sources

    def resolve(self, url):
        return

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
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import dom_parser2
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['scnsrc.me', 'scenesource.me']
        self.base_link = 'http://www.scnsrc.me/'
        self.search_link = '?s=%s&x=0&y=0'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title).replace('-', '+').replace(': ', '+')
            url = urlparse.urljoin(self.base_link, self.search_link % clean_title).lower()
            url = {'url': url, 'title': title, 'year': year}
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
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url is None:
                return sources
            if debrid.status() is False:
                raise Exception()

            hostDict = hostprDict + hostDict

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if \
                'tvshowtitle' in data else '%s' % (data['title'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)
            headers = {'Referer': self.base_link}
            r = self.scraper.get(url, headers=headers).content

            search_results = dom_parser2.parse_dom(r, 'h2')
            search_results = [dom_parser2.parse_dom(i.content, 'a', req=['href']) for i in search_results]
            search_results = [(i[0].content, i[0].attrs['href']) for i in search_results]

            items = []
            for search_result in search_results:
                try:
                    headers = {'Referer': url}
                    r = self.scraper.get(search_result[1], headers=headers).content
                    links = dom_parser2.parse_dom(r, 'a', req=['href', 'rel', ])
                    links = [i.attrs['href'] for i in links]
                    for url in links:
                        try:
                            if hdlr in url.upper() and cleantitle.get(title) in cleantitle.get(url):
                                items.append(url)
                        except:
                            pass
                except:
                    pass

            seen_urls = set()
            for item in items:
                try:
                    url = str(item)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    if any(x in url for x in
                           ['.part', 'extras', 'subs', 'dubbed', 'dub', 'MULTISUBS', 'sample', 'youtube', 'trailer']) \
                            or any(url.endswith(x) for x in ['.rar', '.zip', '.iso', '.sub', '.idx', '.srt']):
                        raise Exception()
                    quality, info = source_utils.get_release_quality(url, url)
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if host in hostDict:
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        sources.append(
                            {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                             'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

# -*- coding: utf-8 -*-

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
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['yifymovies.org']
        self.base_link = 'https://yifymovies.org/'
        self.search_link = '/search/%s/feed/rss2/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def searchMovie(self, title, year):
        try:
            query = self.search_link % urllib.quote_plus(cleantitle.getsearch(title))
            url = urlparse.urljoin(self.base_link, query)
            r = client.request(url)
            r = client.parseDOM(r, 'item')
            r = [(client.parseDOM(i, 'title')[0], client.parseDOM(i, 'link')[0]) for i in r if i]
            r = [i[1] for i in r if cleantitle.get(title) == cleantitle.get(i[0])]
            return r[0]
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url is None: return sources
            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            url = self.searchMovie(data['title'], data['year'])
            if url is None: return sources

            r = client.request(url)
            data = client.parseDOM(r, 'div', attrs={'class': 'playex'})[0]
            frames = client.parseDOM(data, 'iframe', ret='src')
            frames += re.compile('''<iframe\s*src=['"](.+?)['"]''', re.DOTALL).findall(data)
            quality = client.parseDOM(r, 'span', attrs={'class': 'qualityx'})[0]
            for frame in frames:
                url = frame.split('=')[1] if frame.startswith('<') else frame
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                valid, host = source_utils.is_host_valid(url, hostDict)

                if valid:
                    quality, info = source_utils.get_release_quality(quality, url)
                    info = ' | '.join(info)
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                    'direct': False, 'debridonly': False})

                elif url.endswith('mp4'):
                    url += '|User-Agent=%s' % urllib.quote_plus(client.agent())
                    sources.append({'source': 'MP4', 'quality': quality, 'language': 'en', 'url': url,
                                    'direct': True, 'debridonly': False})

                elif 'mystream' in url:
                    data = client.request(url)
                    links = dom_parser.parse_dom(data, 'source', req=['src', 'label'])
                    for link in links:
                        label = link.attrs['label']
                        url = link.attrs['src'] + '|User-Agent=%s' % urllib.quote_plus(client.agent())

                        sources.append({'source': 'MYSTREAM', 'quality': label, 'language': 'en', 'url': url,
                                        'direct': True, 'debridonly': False})

                else:
                    continue
            return sources
        except Exception:
            return sources

    def resolve(self, url):
        try:
            if not '|Us' in url:
                return client.request(url, output='geturl')
        except Exception:
            return url

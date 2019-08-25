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
import time
import urllib
import urlparse

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
        self.domains = ['onlineseries.ucoz.com']
        self.base_link = 'https://onlineseries.ucoz.com'
        self.search_link = 'search/?q=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except Exception:
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
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            self._sources = []
            if url is None: return self._sources
            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (
                data['tvshowtitle'], int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
                data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            query = self.search_link % cleantitle.geturl(query)
            url = urlparse.urljoin(self.base_link, query)
            r = client.request(url)
            posts = dom_parser2.parse_dom(r, 'div', {'class': 'eTitle'})
            posts = [dom_parser2.parse_dom(i.content, 'a', req='href') for i in posts if i]
            posts = [(i[0].attrs['href'], re.sub('<.+?>', '', i[0].content)) for i in posts if i]
            posts = [(i[0], i[1]) for i in posts if (
                        cleantitle.get_simple(i[1].split(hdlr)[0]) == cleantitle.get(title) and hdlr.lower() in i[
                    1].lower())]
            self.hostDict = hostDict + hostprDict
            threads = []

            for i in posts: threads.append(workers.Thread(self._get_sources, i))
            [i.start() for i in threads]
            [i.join() for i in threads]

            alive = [x for x in threads if x.is_alive() == True]
            while alive:
                alive = [x for x in threads if x.is_alive() == True]
                time.sleep(0.1)
            return self._sources
        except Exception:
            return self._sources

    def _get_sources(self, url):
        try:
            item = client.request(url[0])
            title = url[1]
            links = dom_parser2.parse_dom(item, 'a', req='href')
            links = [i.attrs['href'] for i in links]
            info = []
            try:
                size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GiB|MiB|GB|MB))', item)[0]
                div = 1 if size.endswith(('GB', 'GiB')) else 1024
                size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                size = '%.2f GB' % size
                info.append(size)
            except Exception:
                pass
            info = ' | '.join(info)
            for url in links:
                if 'youtube' in url: continue
                if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.']) or any(
                        url.lower().endswith(x) for x in ['.rar', '.zip', '.iso']): raise Exception()

                if any(x in url.lower() for x in ['youtube', 'sample', 'trailer']): raise Exception()
                valid, host = source_utils.is_host_valid(url, self.hostDict)
                if not valid: continue

                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')
                quality, info2 = source_utils.get_release_quality(title, url)
                if url in str(self._sources): continue

                self._sources.append(
                    {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False,
                     'debridonly': True})
        except Exception:
            pass

    def resolve(self, url):
        return url

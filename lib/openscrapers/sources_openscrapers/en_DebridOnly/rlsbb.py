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

import json
import re
import urllib

import urlparse
from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source(object):
    def __init__(self):
        self.priority = 1
        self.language = [u'en']
        self.domains = ['rlsbb.ru']
        self.base_link = 'http://search.rlsbb.ru'
        self.search_link = '/Home/GetPost?phrase=%s&pindex=1&type=Simple&rand=0.2317716259235285'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        url = {u'imdb': imdb, u'title': cleantitle.getsearch(title), u'year': year}
        url = urllib.urlencode(url)
        return url

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = {u'imdb': imdb, u'tvdb': tvdb, u'tvshowtitle': cleantitle.getsearch(tvshowtitle), u'year': year}
        url = urllib.urlencode(url)
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if url is None:
            return

        url = urlparse.parse_qs(url)
        url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
        url[u'title'], url[u'premiered'], url[u'season'], url[u'episode'] = title, premiered, season, episode
        url = urllib.urlencode(url)
        return url

    def sources(self, url, hostDict, hostprDict):
        sources = []

        if url is None:
            return sources

        if debrid.status() is False:
            raise Exception()

        data = urlparse.parse_qs(url)
        data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

        title = (data[u'tvshowtitle'] if u'tvshowtitle' in data else data[u'title'])
        hdlr = 'S%02dE%02d' % (int(data[u'season']), int(data[u'episode'])) if u'tvshowtitle' in data else data[u'year']

        query = '%s S%02dE%02d' % (
            data[u'tvshowtitle'], int(data[u'season']),
            int(data[u'episode'])) if u'tvshowtitle' in data else '%s' % (
            data[u'title'])
        query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

        query = query.replace("&", u'and')
        query = query.replace("  ", " ")
        query = query.replace(" ", "-")

        query = urllib.quote_plus(query).encode('utf-8')

        url = '%s%s' % (self.base_link, self.search_link % query)

        r = self.scraper.get(url).content

        results = json.loads(r)[u'results']

        if u'tvshowtitle' in data:
            regex = r'.*?(%s) .*?(s%se%s)' % (data[u'tvshowtitle'].lower(),
                                              str(data[u'season']).zfill(2),
                                              str(data[u'episode']).zfill(2))
        else:
            regex = r'.*?(%s) .*?(%s)' % (data[u'title'], data[u'year'])

        post_urls = []

        for post in results:
            capture = re.findall(regex, post['post_title'].lower())
            capture = [i for i in capture if len(i) > 1]
            if len(capture) >= 1:
                post_urls.append('http://%s/%s' % (post[u'domain'], post['post_name']))

        if len(post_urls) == 0:
            return None

        items = []
        for url in post_urls:
            r = self.scraper.get(url).content
            posts = client.parseDOM(r, u'div', attrs={u'class': u'content'})
            hostDict = hostprDict + hostDict
            for post in posts:
                u = client.parseDOM(post, u'a', ret=u'href')
                for i in u:
                    if hdlr in i.upper() and cleantitle.get(title) in cleantitle.get(i):
                        items.append(i)

        seen_urls = set()

        for item in items:
            url = str(item)
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            if url in seen_urls:
                continue
            seen_urls.add(url)

            host = url.replace("\\", "")
            host2 = host.strip('"')
            host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(host2.strip().lower()).netloc)[0]

            if host not in hostDict:
                continue

            if any(x in host2 for x in ['.rar', '.zip', '.iso']):
                continue

            quality, info = source_utils.get_release_quality(url)

            info = ' | '.join(info)
            host = client.replaceHTMLCodes(host)
            host = host.encode('utf-8')
            sources.append({u'source': host, u'quality': quality, u'language': u'en', u'url': host2, u'info': info,
                            u'direct': False, u'debridonly': False})
        return sources

    def resolve(self, url):
        return url

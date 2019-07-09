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

from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['300mbfilms.co']
        self.base_link = 'https://www.300mbfilms.co'
        self.search_link = '/?s=%s'

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
            if url is None:
                return

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

            posts = client.parseDOM(r, 'h2')

            hostDict = hostprDict + hostDict

            urls = []
            for item in posts:

                try:
                    item = re.compile('a href="(.+?)"').findall(item)
                    name = item[0]
                    query = query.replace(" ", "-").lower()
                    if query not in name:
                        continue
                    name = client.replaceHTMLCodes(name)

                    quality, info = source_utils.get_release_quality(name, item[0])
                    if any(x in quality for x in ['CAM', 'SD']):
                        continue

                    url = item
                    links = self.links(url)
                    urls += [(i, quality, info) for i in links]

                except:
                    pass

            for item in urls:
                if 'earn-money' in item[0]:
                    continue
                if any(x in item[0] for x in ['.rar', '.zip', '.iso']):
                    continue
                url = client.replaceHTMLCodes(item[0])
                url = url.encode('utf-8')

                valid, host = source_utils.is_host_valid(url, hostDict)
                if not valid:
                    continue
                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')

                sources.append({'source': host, 'quality': item[1], 'language': 'en', 'url': url, 'direct': False,
                                'debridonly': True})

            return sources
        except:
            return sources

    def links(self, url):
        urls = []
        try:
            if url is None:
                return
            for url in url:
                r = client.request(url)
                r = client.parseDOM(r, 'div', attrs={'class': 'entry'})
                r = client.parseDOM(r, 'a', ret='href')
                r1 = [i for i in r if 'money' in i][0]
                r = client.request(r1)
                r = client.parseDOM(r, 'div', attrs={'id': 'post-\d+'})[0]

                if 'enter the password' in r:
                    plink = client.parseDOM(r, 'form', ret='action')[0]

                    post = {'post_password': '300mbfilms', 'Submit': 'Submit'}
                    send_post = client.request(plink, post=post, output='cookie')
                    link = client.request(r1, cookie=send_post)
                else:
                    link = client.request(r1)

                link = re.findall('<strong>Single(.+?)</tr', link, re.DOTALL)[0]
                link = client.parseDOM(link, 'a', ret='href')
                link = [(i.split('=')[-1]) for i in link]
                for i in link:
                    urls.append(i)

                return urls
        except:
            pass

    def resolve(self, url):
        return url

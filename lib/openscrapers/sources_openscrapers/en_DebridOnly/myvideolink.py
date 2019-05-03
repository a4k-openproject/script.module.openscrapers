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
from openscrapers.modules import debrid
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['myvideolinks.net', 'iwantmyshow.tk']
        self.base_link = 'http://myvideolinks.net'
        self.search_link = '/?s=%s'
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

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']
            query = '%s S%02dE%02d' % (
                data['tvshowtitle'], int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s' % (data['imdb'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            s = self.scraper.get(self.base_link).content
            s = re.findall('\'(http.+?)\'', s) + re.findall('\"(http.+?)\"', s)
            s = [i for i in s if urlparse.urlparse(self.base_link).netloc in i and len(i.strip('/').split('/')) > 3]
            s = s[0] if s else urlparse.urljoin(self.base_link, 'vv')
            s = s.strip('/')
            url = s + self.search_link % urllib.quote_plus(query)
            r = self.scraper.get(url).content
            r = client.parseDOM(r, 'h2')
            l = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
            r = [(i[0], i[1], re.sub('(\.|\(|\[|\s)(\d{4}|3D)(\.|\)|\]|\s|)(.+|)', '', i[1]),
                  re.findall('[\.|\(|\[|\s](\d{4}|)([\.|\)|\]|\s|].+)', i[1])) for i in l]
            r = [(i[0], i[1], i[2], i[3][0][0], i[3][0][1]) for i in r if i[3]]
            r = [(i[0], i[1], i[2], i[3], re.split('\.|\(|\)|\[|\]|\s|\-', i[4])) for i in r]
            r = [i for i in r if cleantitle.get(title) == cleantitle.get(i[2]) and data['year'] == i[3]]
            r = [i for i in r if
                 not any(x in i[4] for x in ['HDCAM', 'CAM', 'DVDR', 'DVDRip', 'DVDSCR', 'HDTS', 'TS', '3D'])]
            r = [i for i in r if '1080p' in i[4]][:1] + [i for i in r if '720p' in i[4]][:1]
            if 'tvshowtitle' in data:
                posts = [(i[1], i[0]) for i in l]
            else:
                posts = [(i[1], i[0]) for i in l]
            hostDict = hostprDict + hostDict
            items = []
            for post in posts:
                try:
                    t = post[0]
                    u = self.scraper.get(post[1]).content
                    u = re.findall('"(http.+?)"', u) + re.findall('"(http.+?)"', u)
                    u = [i for i in u if not '/embed/' in i]
                    u = [i for i in u if not 'youtube' in i]
                    items += [(t, i) for i in u]
                except:
                    pass

            seen_urls = set()
            for item in items:
                try:
                    name = item[0]
                    name = client.replaceHTMLCodes(name)
                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)
                    if not cleantitle.get(t) == cleantitle.get(title):
                        raise Exception()
                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()
                    if not y == hdlr:
                        raise Exception()
                    url = item[1]

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    quality, info = source_utils.get_release_quality(url, name)
                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', item[2])[-1]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                        info.append(size)
                    except:
                        pass
                    info = ' | '.join(info)
                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                                    'direct': False, 'debridonly': True})
                except:
                    pass
            check = [i for i in sources if not i['quality'] == 'CAM']
            if check:
                sources = check
            return sources
        except:
            return

    def resolve(self, url):
        return url

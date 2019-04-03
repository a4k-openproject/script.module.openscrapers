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

import re, urllib, urlparse

from openscrapers.modules import cleantitle, client, debrid, source_utils, cfscrape, dom_parser2, workers

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['300mbmoviesdl.com', 'moviesleak.net/', 'hevcbluray.net']
        self.base_link = 'https://moviesleak.net/'
        self.search_link = '?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except Exception:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            self._sources = []

            if url is None:
                return self._sources

            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (
            data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
            data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            posts = client.parseDOM(r, 'div', attrs={'class': 'item'})

            hostDict = hostprDict + hostDict

            items = []

            for post in posts:
                try:
                    tit = client.parseDOM(post, 'img', ret='alt')[0]
                    c = client.parseDOM(post, 'a', ret='href')[0]
                    name = tit
                    name = client.replaceHTMLCodes(name)

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d+E\d+|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', name, flags=re.I)

                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()

                    try:
                        y = re.findall('(?:\.|\(|\[|\s*|)(S\d+E\d+|S\d+)(?:\.|\)|\]|\s*|)', name, re.I)[-1].upper()
                    except Exception:
                        y = re.findall('(?:\.|\(|\[|\s*|)(\d{4})(?:\.|\)|\]|\s*|)', name, re.I)[0].upper()

                    if not y == hdlr: raise Exception()

                    try:
                        s = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', t)[0]
                    except BaseException:
                        s = '0'

                    items += [(tit, c, s)]
                except Exception:
                    pass
            threads = []
            for item in items:
                threads.append(workers.Thread(self._get_sources, item, hostDict))
            [i.start() for i in threads]
            [i.join() for i in threads]

            return self._sources
        except Exception:
            return self._sources


    def _get_sources(self, item, hostDict):
        try:
            quality, info = source_utils.get_release_quality(item[0], item[1])
            size = item[2] if item[2] != '0'else item[0]

            try:
                size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', size)[-1]
                div = 1 if size.endswith(('GB', 'GiB')) else 1024
                size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
                size = '%.2f GB' % size
                info.append(size)

            except Exception:
                pass

            data = self.scraper.get(item[1]).content

            try:
                r = client.parseDOM(data, 'li', attrs={'class': 'elemento'})
                r = [(dom_parser2.parse_dom(i, 'a', req='href')[0],
                      dom_parser2.parse_dom(i, 'img', req='alt')[0],
                      dom_parser2.parse_dom(i, 'span', {'class': 'd'})[0]) for i in r]
                urls = [('http:' + i[0].attrs['href'] if not i[0].attrs['href'].startswith('http') else
                         i[0].attrs['href'], i[1].attrs['alt'], i[2].content) for i in r if i[0] and i[1]]

                for url, host, qual in urls:

                    try:
                        if any(x in url for x in ['.rar', '.zip', '.iso', ':Upcoming']): raise Exception()
                        url = client.replaceHTMLCodes(url)
                        url = url.encode('utf-8')

                        valid, host = source_utils.is_host_valid(host, hostDict)
                        if not valid: continue
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        quality, info = source_utils.get_release_quality(qual, quality)
                        info.append('HEVC')
                        info = ' | '.join(info)
                        self._sources.append(
                            {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                             'direct': False, 'debridonly': True})
                    except Exception:
                        pass
            except Exception:
                pass

        except BaseException:
            return

    def resolve(self, url):
        if 'hideurl' in url:
            data = self.scraper.get(url).content
            data = client.parseDOM(data, 'div', attrs={'class': 'row'})
            url = [dom_parser2.parse_dom(i, 'a', req='href')[0] for i in data]
            url = [i.attrs['href'] for i in url if 'direct me' in i.content][0]
            return url
        else:
            return url
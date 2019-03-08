# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

#######################################################################
 # ----------------------------------------------------------------------------
 # "THE BEER-WARE LICENSE" (Revision 42):
 # @Daddy_Blamo wrote this file.  As long as you retain this notice you
 # can do whatever you want with this stuff. If we meet some day, and you think
 # this stuff is worth it, you can buy me a beer in return. - Muad'Dib
 # ----------------------------------------------------------------------------
#######################################################################

# Addon Name: Placenta
# Addon id: plugin.video.placenta
# Addon Provider: Mr.Blamo

import re
import urllib
import urlparse

from openscrapers.modules import cache
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['movie4k.org']
        self._base_link = None
        self.search_link = '/movies.php?list=search&search=%s'

    @property
    def base_link(self):
        if not self._base_link:
            self._base_link = cache.get(self.__get_base_url, 120, 'http://%s' % self.domains[0])
        return self._base_link

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(imdb, [localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search(imdb, [title] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)
            r = r.replace('\\"', '"')

            links = dom_parser.parse_dom(r, 'tr', attrs={'id': 'tablemoviesindex2'})

            for i in links:
                try:
                    host = dom_parser.parse_dom(i, 'img', req='alt')[0].attrs['alt']
                    host = host.split()[0].rsplit('.', 1)[0].strip().lower()
                    host = host.encode('utf-8')

                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if not valid: continue

                    url = dom_parser.parse_dom(i, 'a', req='href')[0].attrs['href']
                    url = client.replaceHTMLCodes(url)
                    url = urlparse.urljoin(self.base_link, url)
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': 'SD', 'language': 'de', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            h = urlparse.urlparse(url.strip().lower()).netloc

            r = client.request(url)
            r = r.rsplit('"underplayer"')[0].rsplit("'underplayer'")[0]

            u = re.findall('\'(.+?)\'', r) + re.findall('\"(.+?)\"', r)
            u = [client.replaceHTMLCodes(i) for i in u]
            u = [i for i in u if i.startswith('http') and not h in i]

            url = u[-1].encode('utf-8')
            return url
        except:
            return

    def __search(self, imdb, titles, year):
        try:
            q = self.search_link % urllib.quote_plus(cleantitle.query(titles[0]))
            q = urlparse.urljoin(self.base_link, q)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(q)

            r = dom_parser.parse_dom(r, 'tr', attrs={'id': re.compile('coverPreview.+?')})
            r = [(dom_parser.parse_dom(i, 'a', req='href'), dom_parser.parse_dom(i, 'div', attrs={'style': re.compile('.+?')}), dom_parser.parse_dom(i, 'img', req='src')) for i in r]
            r = [(i[0][0].attrs['href'].strip(), i[0][0].content.strip(), i[1], i[2]) for i in r if i[0] and i[2]]
            r = [(i[0], i[1], [x.content for x in i[2] if x.content.isdigit() and len(x.content) == 4], i[3]) for i in r]
            r = [(i[0], i[1], i[2][0] if i[2] else '0', i[3]) for i in r]
            r = [i for i in r if any('us_ger_' in x.attrs['src'] for x in i[3])]
            r = [(i[0], i[1], i[2], [re.findall('(\d+)', x.attrs['src']) for x in i[3] if 'smileys' in x.attrs['src']]) for i in r]
            r = [(i[0], i[1], i[2], [x[0] for x in i[3] if x]) for i in r]
            r = [(i[0], i[1], i[2], int(i[3][0]) if i[3] else 0) for i in r]
            r = sorted(r, key=lambda x: x[3])[::-1]
            r = [(i[0], i[1], i[2], re.findall('\((.+?)\)$', i[1])) for i in r]
            r = [(i[0], i[1], i[2]) for i in r if not i[3]]
            r = [i for i in r if i[2] in y]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year

            r = [(client.replaceHTMLCodes(i[0]), i[1], i[2]) for i in r]

            match = [i[0] for i in r if cleantitle.get(i[1]) in t and year == i[2]]

            match2 = [i[0] for i in r]
            match2 = [x for y, x in enumerate(match2) if x not in match2[:y]]
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if match: url = match[0]; break
                    r = client.request(urlparse.urljoin(self.base_link, i))
                    r = re.findall('(tt\d+)', r)
                    if imdb in r: url = i; break
                except:
                    pass

            return source_utils.strip_domain(url)
        except:
            return

    def __get_base_url(self, fallback):
        try:
            for domain in self.domains:
                try:
                    url = 'http://%s' % domain
                    r = client.request(url, limit=1, timeout='10')
                    r = dom_parser.parse_dom(r, 'meta', attrs={'name': 'author'}, req='content')
                    if r and 'movie4k.to' in r[0].attrs.get('content').lower():
                        return url
                except:
                    pass
        except:
            pass

        return fallback

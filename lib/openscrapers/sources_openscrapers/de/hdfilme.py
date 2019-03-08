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

import base64
import re
import urllib
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hdfilme.tv']
        self.base_link = 'http://hdfilme.tv'
        self.search_link = '/movie-search?key=%s'
        self.get_link = '/movie/getlink/%s/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'aliases': aliases, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            tvshowtitle = data['tvshowtitle']
            localtvshowtitle = data['localtvshowtitle']
            aliases = source_utils.aliases_to_array(eval(data['aliases']))

            url = self.__search([localtvshowtitle] + aliases, data['year'], season)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + aliases, data['year'], season)
            if not url: return

            r = client.request(urlparse.urljoin(self.base_link, url))

            r = dom_parser.parse_dom(r, 'ul', attrs={'class': ['list-inline', 'list-film']})
            r = dom_parser.parse_dom(r, 'li')
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href'], i.content) for i in r if i]
            r = [(i[0], i[1] if re.compile("^(\d+)$").match(i[1]) else '0') for i in r]
            r = [i[0] for i in r if int(i[1]) == int(episode)][0]

            return source_utils.strip_domain(r)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            r = re.findall('(\d+)-stream(?:\?episode=(\d+))?', url)
            r = [(i[0], i[1] if i[1] else '1') for i in r][0]

            r = client.request(urlparse.urljoin(self.base_link, self.get_link % r), output='extended')

            headers = r[3]
            headers.update({'Cookie': r[2].get('Set-Cookie'), 'Referer': self.base_link})
            r = r[0]

            r += '=' * (-len(r) % 4)
            r = base64.b64decode(r)

            i = [(match[1], match[0]) for match in re.findall('''["']?label\s*["']?\s*[:=]\s*["']?([^"',]+)["']?(?:[^}\]]+)["']?\s*file\s*["']?\s*[:=,]?\s*["']([^"']+)''', r, re.DOTALL)]
            i += [(match[0], match[1]) for match in re.findall('''["']?\s*file\s*["']?\s*[:=,]?\s*["']([^"']+)(?:[^}>\]]+)["']?\s*label\s*["']?\s*[:=]\s*["']?([^"',]+)''', r, re.DOTALL)]
            r = [(x[0].replace('\/', '/'), source_utils.label_to_quality(x[1])) for x in i]

            for u, q in r:
                try:
                    tag = directstream.googletag(u)

                    if tag:
                        sources.append({'source': 'gvideo', 'quality': tag[0].get('quality', 'SD'), 'language': 'de', 'url': u, 'direct': True, 'debridonly': False})
                    else:
                        sources.append({'source': 'CDN', 'quality': q, 'language': 'de', 'url': u + '|%s' % urllib.urlencode(headers), 'direct': True, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, year, season='0'):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))
            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = dom_parser.parse_dom(r, 'ul', attrs={'class': ['products', 'row']})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': ['box-product', 'clearfix']})
            if int(season) > 0:
                r = [i for i in r if dom_parser.parse_dom(i, 'div', attrs={'class': 'episode'})]
            else:
                r = [i for i in r if not dom_parser.parse_dom(i, 'div', attrs={'class': 'episode'})]
            r = dom_parser.parse_dom(r, 'h3', attrs={'class': 'title-product'})
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href'], i.content.lower()) for i in r if i]
            r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
            r = [(i[0], i[1], i[2], re.findall('(.+?)\s+(?:staf+el|s)\s+(\d+)', i[1])) for i in r]
            r = [(i[0], i[3][0][0] if len(i[3]) > 0 else i[1], i[2], i[3][0][1] if len(i[3]) > 0 else '0') for i in r]
            r = [(i[0], i[1].replace(' hd', ''), i[2], '1' if int(season) > 0 and i[3] == '0' else i[3]) for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0]for i in r if cleantitle.get(i[1]) in t and i[2] in y and int(i[3]) == int(season)][0]

            url = source_utils.strip_domain(r)
            url = url.replace('-info', '-stream')
            return url
        except:
            return

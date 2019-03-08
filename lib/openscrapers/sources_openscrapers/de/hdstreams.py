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

import json
import urllib
import urlparse
import re
import base64

from openscrapers.modules import cache
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hd-streams.org']
        self.base_link = 'https://hd-streams.org'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return urllib.urlencode({'url': url}) if url else None
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'aliases': aliases}
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

            year = re.findall('(\d{4})', premiered)
            year = year[0] if year else data['year']

            url = self.__search([localtvshowtitle] + aliases, year, season)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + aliases,year, season)
            if not url: return

            return urllib.urlencode({'url': url, 'episode': episode})
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            url = urlparse.urljoin(self.base_link, data.get('url'))
            episode = data.get('episode')

            r = client.request(url)

            aj = self.__get_ajax_object(r)

            b = dom_parser.parse_dom(r, 'img', attrs={'class': 'dgvaup'}, req='data-img')[0].attrs['data-img']

            if episode:
                r = dom_parser.parse_dom(r, 'a', attrs={'class': 'btn-stream-ep', 'data-episode': episode}, req=['data-episode', 'data-server'])
            else:
                r = dom_parser.parse_dom(r, 'div', attrs={'id': 'lang-de'})
                r = dom_parser.parse_dom(r, 'div', attrs={'class': 'movie'})
                r = dom_parser.parse_dom(r, 'a', attrs={'class': 'btn-stream'}, req=['data-episode', 'data-server'])

            r = [(i.attrs['data-episode'], i.attrs['data-server']) for i in r]

            for epi, server in r:
                try:
                    x = {'action': aj.get('load_episodes'), 'episode': epi, 'pid': aj.get('postid'), 'server': server, 'nonce': aj.get('nonce'), 'b': b}
                    x = client.request(aj.get('ajax_url'), post=x, XHR=True, referer=url)
                    x = json.loads(x)

                    q = source_utils.label_to_quality(x.get('q'))
                    x = json.loads(base64.decodestring(x.get('u')))

                    u = source_utils.evp_decode(x.get('ct'), base64.decodestring(b), x.get('s').decode("hex"))
                    u = u.replace('\/', '/').strip('"')

                    valid, host = source_utils.is_host_valid(u, hostDict)
                    if not valid: continue

                    sources.append({'source': host, 'quality': q, 'language': 'de', 'url': u, 'direct': False, 'debridonly': False, 'checkquality': True})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, titles, year, season='0'):
        try:
            aj = cache.get(self.__get_ajax_object, 24)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(aj.get('ajax_url'), post={'action': aj.get('search'), 'nonce': aj.get('snonce'), 'query': cleantitle.query(titles[0])})

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'search-result'})
            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'search-item-content'})
            r = dom_parser.parse_dom(r, 'a', req='href')
            r = [(i.attrs['href'], i.content.lower()) for i in r if i]
            r = [(i[0], i[1], re.findall('(.+?) \(*(\d{4})', i[1])) for i in r]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
            r = [(i[0], i[1], i[2], re.findall('(.+?)\s+(?:staf+el|s)\s+(\d+)', i[1])) for i in r]
            r = [(i[0], i[3][0][0] if len(i[3]) > 0 else i[1], i[2], i[3][0][1] if len(i[3]) > 0 else '0') for i in r]
            r = [(i[0], i[1].replace(' hd', ''), i[2], '1' if int(season) > 0 and i[3] == '0' else i[3]) for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y and int(i[3]) == int(season)][0]

            return source_utils.strip_domain(r)
        except:
            return

    def __get_ajax_object(self, html=None):
        try:
            r = client.request(self.base_link) if not html else html
            r = re.findall('ajax_object\s*=\s*({.*?});', r)[0]
            r = json.loads(r)
            return r
        except:
            return {}

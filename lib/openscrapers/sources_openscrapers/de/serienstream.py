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
import re
import urllib

import urlparse
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils

from openscrapers.modules import control


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['serienstream.to']
        self.base_link = 'https://serienstream.to'
        self.search_link = '/ajax/search'
        self.login = control.setting('serienstream.user')
        self.password = control.setting('serienstream.pass')
        self.cookie = ''
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = url[:-1] if url.endswith('/') else url
            url += '/staffel-%d/episode-%d/' % (int(season), int(episode))
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            r = client.request(urlparse.urljoin(self.base_link, url))

            r = dom_parser.parse_dom(r, 'div', attrs={'class': 'hosterSiteVideo'})
            r = dom_parser.parse_dom(r, 'li', attrs={'data-lang-key': re.compile('[1|3]')})
            r = [(dom_parser.parse_dom(i, 'a', req='href'), dom_parser.parse_dom(i, 'h4'), 'subbed' if i.attrs['data-lang-key'] == '3' else '') for i in r]
            r = [(i[0][0].attrs['href'], i[1][0].content.lower(), i[2]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(i[0], i[1], re.findall('(.+?)\s*<br\s*/?>(.+?)$', i[1], re.DOTALL), i[2]) for i in r]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '', i[3]) for i in r]
            r = [(i[0], i[1], 'HD' if 'hosterhdvideo' in i[2] else 'SD', i[3]) for i in r]

            for link, host, quality, info in r:
                valid, host = source_utils.is_host_valid(host, hostDict)
                if not valid: continue

                sources.append({'source': host, 'quality': quality, 'language': 'de', 'url': link, 'info': info, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            url = client.request(urlparse.urljoin(self.base_link, url), output='geturl')
            if self.base_link not in url:
                return url

            header = {'User-Agent': self.user_agent, 'Accept': 'text/html'}
            
            self.__login()
            cookie = self.cookie

            try:
                res = client.request(url, headers=header, cookie=cookie, redirect=False, output='geturl')
                if self.base_link not in res:
                    url = res
                else:
                    control.infoDialog(control.lang(32572).encode('utf-8'), sound=True, icon='WARNING')
            except:
                return

            return url
        except:
            return

    def __search(self, titles, year):
        try:
            r = urllib.urlencode({'keyword': titles[0]})
            r = client.request(urlparse.urljoin(self.base_link, self.search_link), XHR=True, post=r)
            if r is None:
                r = urllib.urlencode({'keyword': cleantitle.query(titles[0])})
                r = client.request(urlparse.urljoin(self.base_link, self.search_link), XHR=True, post=r)

            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = json.loads(r)
            r = [(i['link'], re.sub('<.+?>|</.+?>', '', i['title'])) for i in r if 'title' in i and 'link' in i]
            r = [(i[0], i[1], re.findall('(.+?)\s*Movie \d+:.+?$', i[1], re.DOTALL)) for i in r]
            r = [(i[0], i[2][0] if len(i[2]) > 0 else i[1]) for i in r]
            r = [(i[0], i[1], re.findall('(.+?) \((\d{4})\)?', i[1])) for i in r]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if cleantitle.get(i[1]) in t and i[2] in y][0]

            return source_utils.strip_domain(r)
        except:
            return

    def __login(self):
        try:
            if (self.login == '' or self.password == ''):
                return

            url = urlparse.urljoin(self.base_link, '/login')
            post = urllib.urlencode({'email': self.login, 'password': self.password, 'autoLogin': 'on'})
            header = {'User-Agent': self.user_agent, 'Accept': 'text/html'}
            cookie = client.request(url, headers=header, referer=url, post=post, output='cookie')
            data = client.request(url, cookie=cookie, output='extended')

            if '/home/logout' in data[0]:
                self.cookie = cookie
                return

            return
        except:
            return

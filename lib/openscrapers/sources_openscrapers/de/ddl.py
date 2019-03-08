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

from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['de.ddl.me']
        self.base_link = 'http://de.ddl.me'
        self.search_link = '/search_99/?q=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__get_direct_url(imdb)
            if not url: return
            return urllib.urlencode({'url': url})
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return self.__get_direct_url(imdb)
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            j = self.__get_json(url)

            if not j: return

            j = [v['info'] for k, v in j.items()]
            j = [(i['nr'], i['staffel'], i['sid']) for i in j]
            j = [(i[2]) for i in j if int(i[0]) == int(episode) and int(i[1]) == int(season)][0]
            return urllib.urlencode({'url': url, 'sid': j})
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if url == None:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            j = self.__get_json(data['url'])

            if not j: return

            sid = data['sid'] if 'sid' in data else j.keys()[0]
            pcnt = int(j[sid]['1']) if '1' in j[sid] else 1

            for jHoster in j[sid]['links']:
                jLinks = [i[3] for i in j[sid]['links'][jHoster] if i[5] == 'stream']
                if len(jLinks) < pcnt: continue

                h_url = jLinks[0]
                valid, hoster = source_utils.is_host_valid(h_url, hostDict)
                if not valid: continue

                h_url = h_url if pcnt == 1 else 'stack://' + ' , '.join(jLinks)

                try: sources.append({'source': hoster, 'quality': 'SD', 'language': 'de', 'info' : '' if pcnt == 1 else 'multi-part', 'url': h_url, 'direct': False, 'debridonly': False})
                except: pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __get_direct_url(self, imdb):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % imdb)
            r = client.request(query, output='geturl')

            if self.search_link in r: return
            return r
        except:
            return

    def __get_json(self, url):
        try:
            result = client.request(url)
            result = re.compile('var\s+subcats\s+=\s*(.*?);').findall(result)[0]
            return json.loads(result)
        except:
            return

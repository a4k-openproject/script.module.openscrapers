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
        self.domains = ['video4k.to']
        self.base_link = 'http://video4k.to'
        self.request_link = '/request'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            return urllib.urlencode({'mID': re.sub('[^0-9]', '', imdb)})
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return urllib.urlencode({'mID': re.sub('[^0-9]', '', imdb)})
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None:
                return

            return urllib.urlencode({'mID': re.sub('[^0-9]', '', imdb), 'season': season, 'episode': episode})
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if url == None:
                return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            data.update({'raw': 'true', 'language': 'de'})
            data = urllib.urlencode(data)
            data = client.request(urlparse.urljoin(self.base_link, self.request_link), post=data)
            data = json.loads(data)
            data = [i[1] for i in data[1].items()]
            data = [(i['name'].lower(), i['links']) for i in data]

            for host, links in data:
                valid, host = source_utils.is_host_valid(host, hostDict)
                if not valid: continue

                for link in links:
                    try:sources.append({'source': host, 'quality': 'SD', 'language': 'de', 'url': link['URL'], 'direct': False, 'debridonly': False})
                    except: pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

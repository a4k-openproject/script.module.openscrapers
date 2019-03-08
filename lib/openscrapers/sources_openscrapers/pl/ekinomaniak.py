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
# Addon Provider: Mr.blamo
import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
import urllib


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['ekinomaniak.tv']

        self.base_link = 'http://ekinomaniak.tv'
        self.search_link = '/search_movies'

    def search(self, localtitle, year, search_type):
        try:

            url = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(url, redirect=False, post={'q': cleantitle.query(localtitle), 'sb': ''})
            r = client.parseDOM(r, 'div', attrs={'class': 'small-item'})

            local_simple = cleantitle.get(localtitle)
            for row in r:
                name_found = client.parseDOM(row, 'a')[1]
                year_found = name_found[name_found.find("(") + 1:name_found.find(")")]
                url = client.parseDOM(row, 'a', ret='href')[1]
                if not search_type in url:
                    continue

                if cleantitle.get(name_found) == local_simple and year_found == year:
                    return url
        except:
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(localtitle, year, 'watch-movies')

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.search(localtvshowtitle, year, 'watch-tv-shows')

    def demix(self, e):
        result = {"d": "A", "D": "a", "a": "D", "a": "d", "c": "B", "C": "b", "b": "C", "b": "c", "h": "E", "H": "e", "e": "H", "E": "h", "g": "F", "G": "f", "f": "G", "F": "g", "l": "I", "L": "i", "i": "L", "I": "l", "k": "J", "K": "j", "j": "K", "J": "k", "p": "M", "P": "m", "m": "P", "M": "p", "o": "N", "O": "n", "n": "O",
                  "N": "o", "u": "R", "U": "r", "r": "U", "R": "u", "t": "S", "T": "s", "s": "T", "S": "t", "z": "W", "Z": "w", "w": "Z", "W": "z", "y": "X", "Y": "x", "x": "Y", "X": "y", "3": "1", "1": "3", "4": "2", "2": "4", "8": "5", "5": "8", "7": "6", "6": "7", "0": "9", "9": "0"
                  }.get(e)
        if result == None:
            result = '%'
        return result

    def decodwrd(self, e):
        r = ""
        for i in range(len(e)):
            r += self.demix(e[i])
        return r

    def decodeURIComponent(self, r):
        return urllib.unquote(r.encode("utf-8"))

    def shwp(self, e):
        r = self.decodwrd(e)
        return self.decodeURIComponent(r)

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        url = urlparse.urljoin(self.base_link, url)
        r = client.request(url)        
        r = client.parseDOM(r, 'li', attrs={'class': 'active'})
        for row in r:
            span_season = client.parseDOM(row, 'span')[0]
            span_season = span_season.split(' ')[1]
            if span_season == season:
                eps = client.parseDOM(row, 'li')
                for ep in eps:
                    ep_no = client.parseDOM(ep, 'a')[0].split(' ')[1]
                    if ep_no == episode:
                        return client.parseDOM(ep, 'a', ret='href')[0]
                    
                
        return None

    def get_lang_by_type(self, lang_type):
        if 'Lektor' in lang_type:
            return 'Lektor'
        if 'Dubbing' in lang_type:
            return 'Dubbing'
        if 'Napisy' in lang_type:
            return 'Napisy'
        return None

    def sources(self, url, hostDict, hostprDict):

        sources = []
        try:
            if url == None: return sources
            r = client.request(urlparse.urljoin(self.base_link, url), redirect=False)
            info = self.get_lang_by_type(client.parseDOM(r, 'title')[0])
            r = client.parseDOM(r, 'div', attrs={'class': 'tab-pane active'})[0]
            r = client.parseDOM(r, 'script')[0]
            script = r.split('"')[1]
            decoded = self.shwp(script)
            
            link = client.parseDOM(decoded, 'iframe', ret='src')[0]
            valid, host = source_utils.is_host_valid(link, hostDict)
            if not valid: return sources
            q = source_utils.check_sd_url(link)
            sources.append({'source': host, 'quality': q, 'language': 'pl', 'url': link, 'info': info, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    Covenant Add-on

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

import urllib, urlparse, re, json

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser
from openscrapers.modules import tvmaze


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['es']
        self.domains = ['seriespapaya.com']
        self.base_link = 'http://www.seriespapaya.com'
        self.search_link = '/busqueda/'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'tvshowtitle': tvshowtitle}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            tvshowtitle = url.split('=')[1].lower().replace('+','-')
            if 'thrones' in tvshowtitle: tvshowtitle = tvshowtitle.replace('game','games')
            url = self.base_link
            url += '/ver/%s/temporada-%d/capitulo-%d.html' % (tvshowtitle, int(season), int(episode))
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            r = client.request(url)
            links = client.parseDOM(r, 'div', attrs={'class': 'mtos'})

            for i in range(1, len(links)):
                idioma = client.parseDOM(links[i], 'img', ret= 'src')[0]
                if 'in.' in idioma: continue
                quality = client.parseDOM(links[i], 'div', attrs={'class': 'dcalidad'})[0]
                servidor = re.findall("src='.+?'\s*/>(.+?)</div>", links[i])[0]

                lang, info = self.get_lang_by_type(idioma)
                quality = self.quality_fixer(quality)

                link = dom_parser.parse_dom(links[i], 'a', req='href')[0][0]['href']
                url = link
                if 'streamcloud' in url: quality = 'SD'
                valid, host = source_utils.is_host_valid(servidor, hostDict)

                sources.append({'source': host, 'quality': quality, 'language': lang, 'url': url, 'info': info,
                                'direct':False,'debridonly': False})

            return sources
        except:
            return sources

    def quality_fixer(self,quality):
        if '1080p' in quality: return 'HD'
        elif '720p' in quality: return 'SD'
        else: return 'SD'

    def get_lang_by_type(self, lang_type):
        if 'lat' in lang_type:
            return 'es', 'LAT'

        elif 'es' in lang_type:
            return 'es', 'CAST'

        elif 'sub' in lang_type:
            return 'en', 'SUB'

        elif 'in' in lang_type:
            return 'en', 'Ingles'
        return 'es', None

    def enlaces(self,url):
        try:
            data = client.request(url)
            url = re.findall("location\.href='(.+?)'\">", data, re.DOTALL)[0]
            return url
        except:
            pass


    def resolve(self, url):
        if 'papaya' in url:
            url = self.enlaces(url)
            return url
        else:
            return url
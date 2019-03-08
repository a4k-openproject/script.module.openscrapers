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

import urllib, urlparse, re

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils
from openscrapers.modules import dom_parser



class source:
    def __init__(self):
        self.priority = 1
        self.language = ['es']
        self.domains = ['megapelistv.com']
        self.base_link = 'http://megapelistv.com/'
        self.search_link = '/?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases),year)
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
            title = url.split('/')[2]
            url = '/episodes/%s-%dx%d/' % (title, int(season), int(episode))
            url = urlparse.urljoin(self.base_link, url)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            query = urlparse.urljoin(self.base_link, url)

            r = client.request(query)

            box_result = client.parseDOM(r, 'div', attrs={'id': 'views'})

            if (len(box_result) != 0):
                sources = self.get_links_from_box(box_result, hostDict)

            sources += self.get_from_main_player(r, sources,hostDict)


            return sources
        except:
            return sources


    def get_from_main_player(self, result, sources, hostDict):
        result_sources = []

        data = client.parseDOM(result, 'div', attrs={'id': 'playex'})

        links = client.parseDOM(data, 'iframe', ret='src')
        r = client.parseDOM(result, 'a', attrs={'class': 'options'})


        for i in range(len(r)):

            item = r[i].split()
            host = item[-4]
            q = item[-3]

            if 'Latino' in item[-1]: lang, info = 'es', 'LAT'
            else: lang, info = 'es', None

            url = links[i]
            if 'megapelistv' in url:
                url = client.request(url.replace('https://www.','http://'))
                url = client.parseDOM(url, 'a', ret='href')[0]
            else: url = url
            if (self.url_not_on_list(url, sources)):
                valid, host = source_utils.is_host_valid(url, hostDict)
                result_sources.append(
                    {'source': host, 'quality': q, 'language': lang, 'url': url, 'info': info, 'direct': False,
                    'debridonly': False})

        return result_sources

    def get_links_from_box(self, result, hostDict):
        sources = []

        src_url = client.parseDOM(result, 'tr', attrs={'id': 'mov\w+|tv\w+'})
        for item in src_url:

            url = client.parseDOM(item, 'a', ret='href')[0]

            url = client.request(url.replace('https://www.','http://'))

            url = client.parseDOM(url, 'a', ret='href')[0]


            data = re.findall('<td>(.+?)</td>', item, re.DOTALL)

            #lang_type = data[2].split()[1]

            if 'HD' in data[1]: q = 'HD'
            else: q = 'SD'

            #host = re.findall('">(.+?)\.',data[0], re.DOTALL )[0]
            valid, host = source_utils.is_host_valid(url, hostDict)

            lang, info = 'es', 'LAT'


            sources.append(
                {'source': host, 'quality': q, 'language': lang, 'url': url, 'info': info, 'direct': False,
                 'debridonly': False})

        return sources


    def url_not_on_list(self, url, sources):
        for el in sources:
            if el.get('url') == url:
                return False
        return True


    def __search(self, titles, year):
        try:

            query = self.search_link % (urllib.quote_plus(cleantitle.query(titles[0])))

            query = urlparse.urljoin(self.base_link, query)

            t = [cleantitle.get(i) for i in set(titles) if i][0]

            r = client.request(query)

            r = client.parseDOM(r, 'div', attrs={'class': 'details'})

            for i in r:
                title = client.parseDOM(i, 'div', attrs={'class': 'title'})[0]
                y = client.parseDOM(i, 'span', attrs={'class': 'year'})[0]
                title = re.findall('">(.+?)</a', title, re.DOTALL)[0]
                title = cleantitle.get_simple(title)

                if t in title and y == year:
                    x = dom_parser.parse_dom(i, 'a', req='href')
                    return source_utils.strip_domain(x[0][0]['href'])

            return
        except:
            return


    def resolve(self, url):
        return url
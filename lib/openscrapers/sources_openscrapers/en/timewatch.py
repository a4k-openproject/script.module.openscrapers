# -*- coding: utf-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
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

import re
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['www.timetowatch.video']
        self.base_link = 'https://www.timetowatch.video'
        self.search_link = '/?s=%s&3mh1='
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            search_id = title.lower()
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % (
                search_id.replace(':', '%3A').replace(',', '%2C').replace('&', '%26').replace("'", '%27').replace(' ',
                                                                                                                  '+').replace(
                    '...', ' '))
            search_results = self.scraper.get(url).content
            match = re.compile('<div data-movie-id=.+?href="(.+?)".+?oldtitle="(.+?)"', re.DOTALL).findall(
                search_results)
            for movie_url, movie_title in match:
                clean_title = cleantitle.get(title)
                movie_title = movie_title.replace('&#8230', ' ').replace('&#038', ' ').replace('&#8217', ' ').replace(
                    '...', ' ')
                clean_movie_title = cleantitle.get(movie_title)
                if clean_movie_title in clean_title:
                    return movie_url
            return
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources
            html = self.scraper.get(url).content
            links = re.compile('id="linkplayer.+?href="(.+?)"', re.DOTALL).findall(html)
            for link in links:
                quality, info = source_utils.get_release_quality(link, url)
                host = link.split('//')[1].replace('www.', '')
                host = host.split('/')[0].split('.')[0].title()
                sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': link, 'direct': False,
                                'debridonly': False})
            return sources
        except:
            return sources

    def resolve(self, url):
        return url

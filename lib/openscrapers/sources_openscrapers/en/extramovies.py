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

import base64
import re
import traceback
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import log_utils
from openscrapers.modules import source_utils


def clean_search(title):
    if title is None:
        return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|/|\(|\)|\[|\]|\{|\}|-|:|;|\*|\?|"|\'|<|>|\_|\.|\?', ' ', title).lower()
    title = ' '.join(title.split())
    return title


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['extramovies.trade', 'extramovies.guru', 'extramovies.wiki']  # http://extramovies.ind.in/
        self.base_link = 'http://extramovies.wiki'  # Dead  extramovies.host
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ExtraMovies - Exception: \n' + str(failure))
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ExtraMovies - Exception: \n' + str(failure))
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ExtraMovies - Exception: \n' + str(failure))
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            self.hostDict = hostDict + hostprDict
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            url = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(cleantitle.query(title)))
            if 'tvshowtitle' in data:
                html = self.scraper.get(url).content
                match = re.compile('class="post-item.+?href="(.+?)" title="(.+?)"', re.DOTALL).findall(html)
                for url, item_name in match:
                    if cleantitle.getsearch(title).lower() in cleantitle.getsearch(item_name).lower():
                        season_url = '%02d' % int(data['season'])
                        episode_url = '%02d' % int(data['episode'])
                        sea_epi = 'S%sE%s' % (season_url, episode_url)
                        result = self.scraper.get(url).content
                        regex = re.compile('href="(.+?)"', re.DOTALL).findall(result)
                        for ep_url in regex:
                            if sea_epi in ep_url:
                                quality, info = source_utils.get_release_quality(url, url)
                                sources.append(
                                    {'source': 'CDN', 'quality': quality, 'language': 'en', 'info': info, 'url': ep_url,
                                     'direct': False, 'debridonly': False})
            else:
                html = self.scraper.get(url).content
                match = re.compile('<div class="thumbnail".+?href="(.+?)" title="(.+?)"', re.DOTALL).findall(html)
                for url, item_name in match:
                    if cleantitle.getsearch(title).lower() in cleantitle.getsearch(item_name).lower():
                        quality, info = source_utils.get_release_quality(url, url)
                        result = self.scraper.get(url).content
                        regex = re.compile('href="/download.php.+?link=(.+?)"', re.DOTALL).findall(result)
                        for link in regex:
                            if 'server=' not in link:
                                try:
                                    link = base64.b64decode(link)
                                except Exception:
                                    pass
                                valid, host = source_utils.is_host_valid(link, self.hostDict)
                                if valid:
                                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'info': info,
                                                    'url': link, 'direct': False, 'debridonly': False})
            return sources
        except Exception:
            failure = traceback.format_exc()
            log_utils.log('ExtraMovies - Exception: \n' + str(failure))
            return sources

    def resolve(self, url):
        return url

# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    vidics scraper for Exodus forks.
    Nov 9 2018 - Checked
    Oct 23 2018 - Cleaned and Checked

    Updated and refactored by someone.
    Originally created by others.
'''
import re

from bs4 import BeautifulSoup

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from openscrapers.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vidics.ch, vidics.to']

        self.base_link = 'https://www.vidics.to'
        self.QUICK_SEARCH_URL = self.base_link + '/searchSuggest/{category}/{query}'
        self.SLOW_SEARCH_URL = self.base_link + '/Category-{category}/Genre-Any/{year}-{year}/Letter-Any/ByPopularity/1/Search-{query}.htm'
        self.EPISODE_PATH = '-Season-{season}-Episode-{episode}'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            return self._getSearchData(title, aliases, year, season=None, episode=None)
        except:
            return None

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return tvshowtitle, aliases, year
        except:
            return None

    def episode(self, data, imdb, tvdb, title, premiered, season, episode):
        try:
            tvshowtitle, aliases, year = data
            return self._getSearchData(tvshowtitle, aliases, year, int(season), int(episode))
        except:
            return None

    def sources(self, data, hostDict, hostprDict):
        try:
            r = self.scraper.get(data['pageURL'])
            soup = BeautifulSoup(r.content, 'html.parser')
            for langDIV in soup.findAll('div', class_='lang'):
                # Find the DIV with English-dubbed hosts.
                if next(langDIV.strings, None).strip().lower() == 'english':
                    page_url = data['pageURL']
                    sources = [
                        {
                            'source': a.text.strip().lower(),
                            'quality': 'SD',
                            'language': 'en',
                            'url': {
                                'pageURL': self.base_link + a['href'],
                                'referer': page_url
                            },
                            'direct': False,
                            'debridonly': False
                        }
                        for a in langDIV.findAll('a', href=True)
                    ]
                    return sources
            return None
        except:
            return None

    def resolve(self, data):
        r = self.scraper.get(data['pageURL'], headers={'referer':data['referer']})
        if not r.ok:
            return None

        match = re.search('movie_link1.*?<a.*?href=\"(.*?)\"', r.text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return None

    def _getSearchData(self, title, aliases, year, season, episode):
        try:
            query = quote(title.lower())

            search_url = self.QUICK_SEARCH_URL.format(
                category='TvShows' if episode else 'Movies', query=query
            )

            r = self.scraper.get(search_url)
            if not r.ok:
                return None

            possible_titles = set(
                (title.lower(),) + tuple((alias['title'].lower() for alias in aliases) if aliases else ())
            )

            # Using the pop-up search results uses way less bandwidth from them, like 1 KB (instead of 43 KB with
            # the traditional search page).
            # But when the search results have multiple entries with the same title (like the TV show "The Flash"
            # or the movie "The Dark Knight"), need to use an extra search with the year to differentiate them.

            best_url = None

            soup = BeautifulSoup(r.content, 'html.parser')
            for a in soup.findAll('a', href=True):
                if a.text.lower() in possible_titles:
                    if not best_url:
                        best_url = self.base_link + a['href']
                    else:
                        best_url = self._extraSearch(query, year, (episode is None),  best_url)
                        break

            if best_url:
                if episode:
                    best_url += self.EPISODE_PATH.format(season=season, episode=episode)
                return {'pageURL': best_url}
            else:
                return None  # No results found.
        except:
            return None

    def _extraSearch(self, query, year, is_movie, best_url):
        search_url = self.SLOW_SEARCH_URL.format(category='Movies' if is_movie else 'TvShows', year=year, query=query)
        r = self.scraper.get(search_url)
        if not r.ok:
            return best_url

        soup = BeautifulSoup(r.content, 'html.parser')
        results_td = soup.find('td', id='searchResults')
        if results_td:
            a = results_td.find('a', itemprop=True)
            if a:
                return self.base_link + a['href']
        return best_url


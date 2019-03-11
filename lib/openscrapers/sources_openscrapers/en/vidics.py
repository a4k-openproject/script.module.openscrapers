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
import requests

from bs4 import BeautifulSoup
from datetime import datetime
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

import time

from openscrapers.modules.client import randomagent


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vidics.ch, vidics.to']

        self.BASE_URL = 'https://www.vidics.to'
        self.QUICK_SEARCH_URL = self.BASE_URL + '/searchSuggest/{category}/{query}'
        self.SLOW_SEARCH_URL = self.BASE_URL + '/Category-{category}/Genre-Any/{year}-{year}/Letter-Any/ByPopularity/1/Search-{query}.htm'
        self.EPISODE_PATH = '-Season-{season}-Episode-{episode}'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            return self._getSearchData(title, aliases, year, self._createSession(), season=None, episode=None)
        except:
            self._logException()
            return None


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return tvshowtitle, aliases, year
        except:
            self._logException()
            return None


    def episode(self, data, imdb, tvdb, title, premiered, season, episode):
        try:
            tvshowtitle, aliases, year = data
            return self._getSearchData(tvshowtitle, aliases, year, self._createSession(), int(season), int(episode))
        except:
            self._logException()
            return None


    def sources(self, data, hostDict, hostprDict):
        try:
            session = self._createSession({'UA': data['UA']})
            r = self._sessionRequest(data['pageURL'], session, 1500)
            if not r.ok:
                self._logException('Sources page request failed: ' + pageURL)
                return None
            
            soup = BeautifulSoup(r.content, 'html.parser')
            for langDIV in soup.findAll('div', class_='lang'):
                # Find the DIV with English-dubbed hosts.
                if next(langDIV.strings, None).strip().lower() == 'english':
                    userAgent = data['UA']
                    pageURL = data['pageURL']
                    sources = [
                        {
                            'source': a.text.strip().lower(),
                            'quality': 'SD',
                            'language': 'en',
                            'url': {
                                'pageURL': self.BASE_URL + a['href'],
                                'UA': userAgent,
                                'referer': pageURL
                            },
                            'direct': False,
                            'debridonly': False
                        }
                        for a in langDIV.findAll('a', href=True)
                    ]
                    return sources
            return None
        except:
            self._logException()
            return None


    def resolve(self, data):
        session = self._createSession({'UA': data['UA'], 'referer': data['referer']})

        r = self._sessionRequest(data['pageURL'], session, 1500)
        if not r.ok:
            self._logException('Resolve request failed' + data['pageURL'])
            return None
        
        match = re.search('movie_link1.*?<a.*?href=\"(.*?)\"', r.text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return None


    def _sessionRequest(self, url, session, delayAmount, data=None):
        try:
            startTime = datetime.now() if delayAmount else None
            if data:
                r = session.post(url, data=data, timeout=8)
            else:
                r = session.get(url, timeout=8)

            if delayAmount:
                elapsed = int((datetime.now() - startTime).total_seconds())
                if elapsed < delayAmount and elapsed > 100:
                    time.sleep(delayAmount - elapsed)
            return r
        except:
            return type('FailedResponse', (object,), {'ok': False})


    def _createSession(self, customHeaders={}):
        # Create a 'requests.Session' and try to spoof a header from a web browser.
        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'User-Agent': customHeaders.get('UA', randomagent()),
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': customHeaders.get('referer', self.BASE_URL + '/'),
                'DNT': '1'
            }
        )
        return session


    def _getSearchData(self, title, aliases, year, session, season, episode):
        try:
            query = quote(title.lower())

            # Prepare the session and make the search request.
            oldAccept = session.headers['Accept']
            session.headers.update({'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest'})
            searchURL = self.QUICK_SEARCH_URL.format(
                category='TvShows' if episode else 'Movies', query=query
            )
            r = self._sessionRequest(searchURL, session, 1000, {'ajax': '1'})
            if not r.ok:
                return None
                
            # Restore the session headers.
            session.headers['Accept'] = oldAccept
            del session.headers['X-Requested-With']

            possibleTitles = set(
                (title.lower(),) + tuple((alias['title'].lower() for alias in aliases) if aliases else ())
            )
            
            # Using the pop-up search results uses way less bandwidth from them, like 1 KB (instead of 43 KB with
            # the traditional search page).
            # But when the search results have multiple entries with the same title (like the TV show "The Flash"
            # or the movie "The Dark Knight"), need to use an extra search with the year to differentiate them.
            
            bestURL = None
            
            soup = BeautifulSoup(r.content, 'html.parser')
            for a in soup.findAll('a', href=True):
                if a.text.lower() in possibleTitles:
                    if not bestURL:
                        bestURL = self.BASE_URL + a['href']
                    else:
                        bestURL = self._extraSearch(query, year, (episode == None), session, bestURL)
                        break

            if bestURL:
                if episode:
                    bestURL += self.EPISODE_PATH.format(season=season, episode=episode)
                return {'pageURL': bestURL, 'UA': session.headers['User-Agent']}
            else:
                return None # No results found.
        except:
            self._logException()
            return None
            
            
    def _extraSearch(self, query, year, isMovie, session, bestURL):
        searchURL = self.SLOW_SEARCH_URL.format(category='Movies' if isMovie else 'TvShows', year=year, query=query)
        r = self._sessionRequest(searchURL, session, 1500)
        if not r.ok:
            return bestURL
            
        soup = BeautifulSoup(r.content, 'html.parser')
        resultsTD = soup.find('td', id='searchResults')
        if resultsTD:
            a = resultsTD.find('a', itemprop=True)
            if a:
                return self.BASE_URL + a['href']            
        return bestURL        


    def _debug(self, name, val=None):
        pass


    def _logException(self, text=None):
        return # Comment this return statement to output errors to the Kodi log, useful for debugging this script.
        if text:
            xbmc.log('VIDICS Error >' + text, xbmc.LOGERROR)
        else:
            import traceback
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

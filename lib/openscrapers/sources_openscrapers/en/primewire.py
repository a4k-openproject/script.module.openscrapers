# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    Primewire-variant scraper for Exodus forks.
    Nov 9 2018 - Checked
    Sep 23 2018 - Cleaned and Checked.

    Updated and refactored by someone.
    Originally created by others.
'''
import re
import requests
import traceback
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from openscrapers.modules.client import randomagent
from openscrapers.modules import cleantitle
from openscrapers.modules import jsunpack


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['primewire.gr']
        self.base_link = 'http://m.primewire.gr'        

        # Use the **mobile** version of the website, a bit less traffic needed from them.
        self.BASE_URL = 'http://m.primewire.gr'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            lowerTitle = title.lower()
            possibleTitles = set(
                (lowerTitle, cleantitle.getsearch(lowerTitle))
                + tuple((alias['title'].lower() for alias in aliases) if aliases else ())
            )
            return self._getSearchData(lowerTitle, possibleTitles, year, self._createSession(), isMovie=True)
        except:
            self._logException()
            return None


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            lowerTitle = tvshowtitle.lower()
            possibleTitles = set(
                (lowerTitle, cleantitle.getsearch(lowerTitle))
                + tuple((alias['title'].lower() for alias in aliases) if aliases else ())
            )
            return self._getSearchData(lowerTitle, possibleTitles, year, self._createSession(), isMovie=False)
        except:
            self._logException()
            return None


    def episode(self, data, imdb, tvdb, title, premiered, season, episode):
        try:
            seasonsPageURL = data['pageURL']

            # An extra step needed before sources() can be called. Get the episode page.
            # This code will crash if they change the website structure in the future.

            session = self._createSession(data['UA'], data['cookies'], data['referer'])
            time.sleep(1)
            r = self._sessionGET(seasonsPageURL, session)
            if r.ok:
                soup = BeautifulSoup(r.content, 'html.parser')
                mainDIV = soup.find('div', {'class': 'tv_container'})
                firstEpisodeDIV = mainDIV.find('div', {'class': 'show_season', 'data-id': season})
                # Filter the episode HTML entries to find the one that represents the episode we're after.
                episodeDIV = next(
                    (
                        element for element in firstEpisodeDIV.next_siblings
                        if not isinstance(element, NavigableString) and next(element.a.strings, '').strip('E ') == episode
                    ),
                    None
                )
                if episodeDIV:
                    return {
                        'pageURL': self.BASE_URL + episodeDIV.a['href'],
                        'UA': session.headers['User-Agent'],
                        'referer': seasonsPageURL,
                        'cookies': session.cookies.get_dict()
                    }
            return None
        except:
            self._logException()
            return None


    def sources(self, data, hostDict, hostprDict):
        try:
            session = self._createSession(data['UA'], data['cookies'], data['referer'])
            pageURL = data['pageURL']

            time.sleep(1)
            r = self._sessionGET(pageURL, session)
            if not r.ok:
                self._logException('PRIMEWIRE > Sources page request failed: ' + data['pageURL'])
                return None

            sources = [ ]

            soup = BeautifulSoup(r.content, 'html.parser')
            mainDIV = soup.find('div', class_='actual_tab')
            for hostBlock in mainDIV.findAll('tbody'):

                # All valid host links always have an 'onclick' attribute.
                if 'onclick' in hostBlock.a.attrs:
                    onClick = hostBlock.a['onclick']
                    if 'Promo' in onClick:
                        continue # Ignore ad links.

                    hostName = re.search('''['"](.*?)['"]''', onClick).group(1)
                    qualityClass = hostBlock.span['class']
                    quality = 'SD' if ('cam' not in qualityClass and 'ts' not in qualityClass) else 'CAM'

                    # Send data for the resolve() function below to use later, when the user plays an item.
                    unresolvedData = {
                        'pageURL': self.BASE_URL + hostBlock.a['href'], # Not yet usable, see resolve().
                        'UA': data['UA'],
                        'cookies': session.cookies.get_dict(),
                        'referer': pageURL
                    }
                    sources.append(
                        {
                            'source': hostName,
                            'quality': quality,
                            'language': 'en',
                            'url': unresolvedData,
                            'direct': False,
                            'debridonly': False
                        }
                    )
            return sources
        except:
            self._logException()
            return None


    def resolve(self, data):
        try:
            hostURL = None
            DELAY_PER_REQUEST = 1000 # In milliseconds.

            startTime = datetime.now()
            session = self._createSession(data['UA'], data['cookies'], data['referer'])
            r = self._sessionGET(data['pageURL'], session, allowRedirects=False)
            if r.ok:
                if 'Location' in r.headers:
                    hostURL = r.headers['Location'] # For most hosts they redirect.
                else:
                    # On rare cases they JS-pack the host link in the page source.
                    try:
                        hostURL = re.search(r'''go\(\\['"](.*?)\\['"]\);''', jsunpack.unpack(r.text)).group(1)
                    except:
                        pass # Or sometimes their page is just broken.

            # Do a little delay, if necessary, between resolve() calls.
            elapsed = int((datetime.now() - startTime).total_seconds())
            if elapsed < DELAY_PER_REQUEST:
                time.sleep(max(DELAY_PER_REQUEST - elapsed, 100))

            return hostURL
        except:
            self._logException()
            return None


    def _getSearchData(self, query, possibleTitles, year, session, isMovie):
        try:
            searchURL = self.BASE_URL + ('/?' if isMovie else '/?tv=&') + urlencode({'search_keywords': query})
            r = self._sessionGET(searchURL, session)
            if not r.ok:
                return None

            bestGuessesURLs = [ ]

            soup = BeautifulSoup(r.content, 'html.parser')
            mainDIV = soup.find('div', role='main')
            for resultDIV in mainDIV.findAll('div', {'class': 'index_item'}, recursive=False):
                # Search result titles in Primewire.gr are usually "[Name of Movie/TVShow] (yyyy)".
                # Example: 'Star Wars Legends: Legacy of the Force (2015)'
                match = re.search(r'(.*?)(?:\s\((\d{4})\))?$', resultDIV.a['title'].lower().strip())
                resultTitle, resultYear = match.groups()
                if resultTitle in possibleTitles:
                    if resultYear == year: # 'resultYear' = '(yyyy)', with parenthesis.
                        bestGuessesURLs.insert(0, resultDIV.a['href']) # Use year to make better guesses.
                    else:
                        bestGuessesURLs.append(resultDIV.a['href'])

            if bestGuessesURLs:
                return {
                    'pageURL': self.BASE_URL + bestGuessesURLs[0],
                    'UA': session.headers['User-Agent'],
                    'referer': searchURL,
                    'cookies': session.cookies.get_dict(),
                }
            else:
                return None
        except:
            self._logException()
            return None


    def _sessionGET(self, url, session, allowRedirects=True):
        try:
            return session.get(url, allow_redirects=allowRedirects, timeout=8)
        except:
            return type('FailedResponse', (object,), {'ok': False})


    def _createSession(self, userAgent=None, cookies=None, referer=None):
        # Try to spoof a header from a web browser.
        session = requests.Session()
        session.headers.update(
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'User-Agent': userAgent if userAgent else randomagent(),
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': referer if referer else self.BASE_URL + '/',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1'
            }
        )
        if cookies:
            session.cookies.update(cookies)
        return session


    def _debug(self, name, val=None):
        pass


    def _logException(self, text=None):
        return # Comment this line to output errors to the Kodi log, useful for debugging this script.
        if text:
            xbmc.log(text, xbmc.LOGERROR)
        else:
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

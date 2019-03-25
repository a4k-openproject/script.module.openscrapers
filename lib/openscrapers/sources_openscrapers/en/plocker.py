# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

import re
import requests
import traceback
from bs4 import BeautifulSoup, SoupStrainer
try:
    from urllib import urlencode, quote_plus # Python 2
except ImportError:
    from urllib.parse import urlencode, quote_plus # Python 3

import xbmc

from openscrapers.modules.client import randomagent


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['putlocker.se', 'putlockertv.to']
        self.base_link = 'https://www6.putlockertv.to'

        self.ALL_JS_PATTERN = '<script src=\"(/assets/min/public/all.js?.*?)\"'
        self.DEFAULT_ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

        self.BASE_URL = 'https://www5.putlockertv.to'

        # Path to search for either a film or season from a tvshow.
        self.SEARCH_PATH = '/ajax/film/search?ts=%s&_=%i&keyword=%s&sort=year%%3Adesc'

        # Paths to retrieve a list of host names and internal URLs.
        self.UPDATE_PATH = 'ajax/film/update-views?ts=%s&_=%i&id=%s&random=1'
        self.SERVERS_PATH = '/ajax/film/servers/%s?ts=%s&_=%i'

        # Path to retrieve an unresolved host, to be sent to the ResolveURL plugin.
        self.INFO_PATH = '/ajax/episode/info?ts=%s&_=%i&id=%s&server=%s&update=0'

        # Used in sources() to map lowercase host names to debrid-friendly host names.
        self.DEBRID_HOSTS = {
            'openload': 'openload.co',
            'rapidvideo': 'rapidvideo.com',
            'streamango': 'streamango.com'
        }


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            session = self._createSession(randomagent())

            lowerTitle = title.lower()
            stringConstant, searchHTML = self._getSearch(lowerTitle, session)

            possibleTitles = set(
                (lowerTitle,) + tuple((alias['title'].lower() for alias in aliases) if aliases else ())
            )
            soup = BeautifulSoup(searchHTML, 'html.parser', parse_only=SoupStrainer('div', recursive=False))
            for div in soup:
                if div.span and (year in div.span.text) and (div.a.text.lower() in possibleTitles):
                    return {
                        'type': 'movie',
                        'pageURL': self.BASE_URL + div.a['href'],
                        'sConstant': stringConstant,
                        'UA': session.headers['User-Agent'],
                        'cookies': session.cookies.get_dict()
                    }
            return None # No results found.
        except:
            self._logException()
            return None


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return tvshowtitle.lower()
        except:
            self._logException()
            return None


    def episode(self, data, imdb, tvdb, title, premiered, season, episode):
        try:
            session = self._createSession(randomagent())

            # Search with the TV show name and season number string.
            lowerTitle = data
            stringConstant, searchHTML = self._getSearch(lowerTitle + ' ' + season, session)

            soup = BeautifulSoup(searchHTML, 'html.parser')
            for div in soup.findAll('div', recursive=False):
                resultName = div.a.text.lower()
                if lowerTitle in resultName and season in resultName:
                    return {
                        'type': 'episode',
                        'episode': episode,
                        'pageURL': self.BASE_URL + div.a['href'],
                        'sConstant': stringConstant,
                        'UA': session.headers['User-Agent'],
                        'cookies': session.cookies.get_dict()
                    }
            return None # No results found.
        except:
            self._logException()
            return None


    def sources(self, data, hostDict, hostprDict):
        try:
            isMovie = (data['type'] == 'movie')
            episode = data.get('episode', '')
            pageURL = data['pageURL']
            stringConstant = data['sConstant']

            session = self._createSession(data['UA'], data['cookies'])

            xbmc.sleep(1200)
            r = self._sessionGET(pageURL, session)
            if not r.ok:
                self._logException('%s Sources page request failed' % data['type'].capitalize())
                return None
            pageHTML = r.text
            timeStamp = self._getTimeStamp(pageHTML)

            # Get a HTML block with a list of host names and internal links to them.

            session.headers['Referer'] = pageURL # Refer to this page that "we're on" right now to avoid suspicion.
            pageID = pageURL.rsplit('.', 1)[1]
            token = self._makeToken({'ts': timeStamp}, stringConstant)
            xbmc.sleep(200)
            serversHTML = self._getServers(pageID, timeStamp, token, session)

            # Go through the list of hosts and create a source entry for each.

            sources = [ ]
            tempTokenData = {'ts': timeStamp, 'id': None, 'server': None, 'update': '0'}
            baseInfoURL = self.BASE_URL + self.INFO_PATH

            soup = BeautifulSoup(
                serversHTML,
                'html.parser',
                parse_only=SoupStrainer('div', {'class': 'server row', 'data-id': True}, recursive=False)
            )
            for serverDIV in soup:
                tempTokenData['server'] = serverDIV['data-id']
                hostName = serverDIV.label.text.strip().lower()
                hostName = self.DEBRID_HOSTS.get(hostName, hostName)

                for a in serverDIV.findAll('a', {'data-id': True}):
                    # The text in the <a> tag can be the movie quality ("HDRip", "CAM" etc.) or for TV shows
                    # it's the episode number with a one-zero-padding, like "09", for each episode in the season.
                    label = a.text.lower().strip()
                    hostID = a['data-id'] # A string identifying a host embed to be retrieved from putlocker's servers.

                    if isMovie or episode == str(int(label)):
                        if isMovie:
                            if 'hd' in label:
                                quality = 'HD'
                            else:
                                quality = 'SD' if ('ts' not in label and 'cam' not in label) else 'CAM'
                        else:
                            quality = 'SD'

                        tempTokenData['id'] = hostID
                        tempToken = self._makeToken(tempTokenData, stringConstant)

                        # Send data for the resolve() function below to use later, when the user plays an item.
                        # We send the CF cookies from the session (instead of reusing them from data['cfCookies'])
                        # because they might've changed.
                        unresolvedData = {
                            'url': baseInfoURL % (timeStamp, tempToken, hostID, tempTokenData['server']),
                            'UA': data['UA'],
                            'cookies': session.cookies.get_dict(),
                            'referer': pageURL + '/' + hostID
                        }
                        sources.append(
                            {
                                'source': hostName,
                                'quality': quality,
                                'language': 'en',
                                'url': unresolvedData, # Doesn't need to be a string, just repr()-able.
                                'direct': False,
                                'debridonly': False
                            }
                        )
            return sources
        except:
            self._logException()
            return None


    def resolve(self, data):
        # The 'data' parameter is the 'unresolvedData' dictionary sent from sources().
        try:
            session = self._createSession(data['UA'], data['cookies'], data['referer'])
            xbmc.sleep(500) # Give some room between requests (_getHost() -> _requestJSON() will also sleep some more).
            return self._getHost(data['url'], session) # Return a host URL for use with ResolveURL and play.
        except:
            self._logException()
            return None


    def _sessionGET(self, url, session):
        try:
            return session.get(url, timeout=10)
        except:
            return type('FailedResponse', (object,), {'ok': False})


    def _requestJSON(self, url, session):
        try:
            oldAccept = session.headers['Accept']
            session.headers.update(
                {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            xbmc.sleep(1500)
            r = self._sessionGET(url, session)
            session.headers['Accept'] = oldAccept
            del session.headers['X-Requested-With']
            return r.json() if r.ok and r.content else None
        except:
            self._logException()
            return None


    def _getHost(self, url, session):
        jsonData = self._requestJSON(url, session)
        if jsonData:
            return jsonData['target']
        else:
            self._logException('_getHost JSON request failed')
            return ''


    def _getServers(self, pageID, timeStamp, token, session):
        jsonData = self._requestJSON(
            self.BASE_URL + (self.SERVERS_PATH % (pageID, timeStamp, token)), session
        )
        if jsonData:
            return jsonData['html']
        else:
            self._logException('_getServers JSON request failed')
            return ''


    def _getSearch(self, lowerTitle, session):
        '''
        All the code in here assumes a certain website structure.
        If they change it in the future, it'll crash.
        '''
        # Get the homepage HTML.
        r = self._sessionGET(self.BASE_URL, session)
        if not r.ok:
            self._logException('Homepage request failed')
            return ''
        homepageHTML = r.text
        timeStamp = self._getTimeStamp(homepageHTML)

        # Get the minified main javascript file.
        jsPath = re.search(self.ALL_JS_PATTERN, homepageHTML, re.DOTALL).group(1)
        session.headers['Accept'] = '*/*' # Use the same 'Accept' for JS files as web browsers do.
        xbmc.sleep(200)
        allJS = self._sessionGET(self.BASE_URL + jsPath, session).text
        session.headers['Accept'] = self.DEFAULT_ACCEPT

        # Some unknown cookie flag that they use, set after 'all.js' is loaded.
        # Doesn't seem to make a difference, but it might help with staying unnoticed.
        session.cookies.set('', '__test')

        # Get the underscore token used to verify all requests. It's calculated from all parameters on JSON requests.
        # The value for 'keyword' is the search query, it should have normal spaces (like a movie title).
        data = {'ts': timeStamp, 'keyword': lowerTitle, 'sort': 'year:desc'}
        stringConstant = self._makeStringConstant(allJS)
        token = self._makeToken(data, stringConstant)

        # We use their JSON api as it's much less data needed from their servers. Easier on them, faster for us too.
        jsonData = self._requestJSON(
            self.BASE_URL + (self.SEARCH_PATH % (timeStamp, token, quote_plus(lowerTitle))), session
        )
        if jsonData:
            return stringConstant, jsonData['html']
        else:
            self._logException('_getSearch JSON request failed')
            return ''


    def _createSession(self, userAgent=None, cookies=None, referer=None):
        # Try to spoof a header from a web browser.
        session = requests.Session()
        session.headers.update(
            {
                'Accept': self.DEFAULT_ACCEPT,
                'User-Agent': userAgent if userAgent else randomagent(),
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': referer if referer else self.BASE_URL + '/',
                'DNT': '1'
            }
        )
        if cookies:
            session.cookies.update(cookies)
            session.cookies[''] = '__test' # See _getSearch() for more info on this.
        return session


    def _debug(self, name, val=None):
        xbmc.log('PLOCKER Debug > %s %s' % (name, repr(val) if val else ''), xbmc.LOGWARNING)


    def _logException(self, text=None):
        return # Comment this line to output errors to the Kodi log, useful for debugging this script.
        # ------------------
        if text:
            xbmc.log('PLOCKER ERROR > %s' % text, xbmc.LOGERROR)
        else:
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)


    # Token algorithm, present in "all.js".
    # ----------------------------------------------------------
    # You can get to it more quickly by searching for "Number(" in that JS file, one of
    # the occurrences will be in that section.
    # The references in the functions below were beautified with https://beautifier.io.
    #
    # To actually find it in the future in case they change it, you need to use the
    # Javascript debugger of your browser (like Firefox etc.), setting a breakpoint
    # at a specific query handler of an ajax request. It's called every time you type
    # something in the search field.
    # From then on you go step by step with the debugger, using Step-Overs mostly, and
    # then start to Step-In when you reach a part with "encode URI", as it's getting close.
    # Keep stepping until your reach some functions that use the Math and Number classes.

    def _getTimeStamp(self, html):
        return re.search(r'<html data-ts="(.*?)"', html, re.DOTALL).group(1)


    def _makeStringConstant(self, allJS):
        '''
        Reference:
        function r() {
            return Tv + k_ + Pm + k_ + pf + k_ + Zu
        }
        '''
        rSum = re.search('strict";function r\(\)\{return(.*?)\}', allJS, re.DOTALL).group(1)
        rSum = rSum.strip().replace(' ', '').split('+')
        rConstants = {
            key: re.search(',?' + key + '=\"(.*?)\"[,;]', allJS, re.DOTALL).group(1)
            for key in set(rSum)
        }
        return ''.join(rConstants.get(key, '') for key in rSum)


    def _e(self, t):
        '''
        Reference:
        function e(t) {
            var i, n = 0;
            for (i = 0; i < t[ik]; i++) n += t[Do + k_ + gm + k_ + au](i) + i;
            return n
        }
        '''
        return sum(ord(t[i]) + i for i in xrange(len(t)))


    def _makeToken(self, params, stringConstant):
        '''
        :returns: An integer token.

        Reference:
        i[u](function(t) {
            var n = function(t) {
                var n, o, s = e(r()),
                    u = {},
                    f = {};
                f[c] = k_ + a,
                    o = i[Sk](!0, {}, t, f);
                for (n in o) Object[ld][Ym + k_ + Ul + k_ + _h][eo](o, n) && (s += e(function(t, i) {
                    var n,
                        r = 0;
                    for (n = 0; n < Math[Mx](t[ik], i[ik]); n++) r += n < i[ik] ? i[Do + k_ + gm + k_ + au](n) : 0,
                        r += n < t[ik] ? t[Do + k_ + gm + k_ + au](n) : 0;
                    return Number(r)[St + k_ + Px](16)
                }(r() + n, o[n])));
                return u[c] = a, u[h] = s, u
        '''
        def __convolute(t, i):
            iLen = len(i)
            tLen = len(t)
            r = 0
            for n in xrange(max(tLen, iLen)):
                r += ord(i[n]) if n < iLen else 0
                r += ord(t[n]) if n < tLen else 0
            return self._e(hex(r)[2:]) # Skip two characters to ignore the '0x' from the Python hex string.

        s = self._e(stringConstant)
        for key in params.keys():
            s += __convolute(stringConstant + key, params[key])
        return s
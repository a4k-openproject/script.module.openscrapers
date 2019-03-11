#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    Torrentapi
'''

import re
import requests
import time

from openscrapers.modules import source_utils
from resolveurl.plugins.premiumize_me import PremiumizeMeResolver


class source:

    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'https://Torrentapi.top'
        self.api_key = PremiumizeMeResolver.get_setting('password')
        self.tvsearch = 'https://torrentapi.org//pubapi_v2.php?app_id=poached&mode=search&search_string=%s&category=tv&ranked=0&token=%s'
        self.msearch = 'https://torrentapi.org//pubapi_v2.php?app_id=poached&mode=search&search_string=%s&category=movies&ranked=0&token=%s'
        self.tokenta = 'https://torrentapi.org//pubapi_v2.php?app_id=poached&get_token=get_token'
        self.checkc = 'https://www.premiumize.me/api/torrent/checkhashes?apikey=%s&hashes[]=%s&apikey=%s'
        self.pr_link = 'https://www.premiumize.me/api/transfer/directdl?apikey=%s&src=magnet:?xt=urn:btih:%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'title': title, 'year': year}
            return url
        except:
            print("Unexpected error in Torrentapi Script: episode", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle
            return url
        except:
            print("Unexpected error in Torrentapi Script: TV", sys.exc_info()[0])
            return url
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            url = url
            url = {'tvshowtitle': url, 'season': season, 'episode': episode, 'premiered': premiered}
            return url
        except:
            print("Unexpected error in Torrentapi Script: episode", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            with requests.Session() as s:
                gettoken = s.get(self.tokenta).text
                time.sleep(2)
                tokenapi = re.compile('n\W+(.*?)[\'"]', re.I).findall(gettoken)[0]
                if 'episode' in url:
                    iep = url['episode'].zfill(2)
                    ise = url['season'].zfill(2)
                    se = 's' + ise + 'e' + iep
                    sel = url['tvshowtitle'].replace(' ','.') + '.' + se
                    search_link = self.tvsearch
                else:
                    sel = url['title'].replace(' ','.') + '.' + url['year']
                    search_link = self.msearch
                gs = s.get(search_link % (sel, tokenapi)).text
                gl = re.compile('ame\W+(.*?)[\'"].*?ih:(.*?)\W', re.I).findall(gs)
                for nam,hass in gl:
                    checkca = s.get(self.checkc % (self.api_key, hass, self.api_key)).text
                    quality = source_utils.check_sd_url(nam)
                    if 'finished' in checkca:
                        url = self.pr_link % (self.api_key, hass)
                        sources.append({
                            'source': 'cached',
                            'quality': quality,
                            'language': 'en',
                            'url': url,
                            'direct': False,
                            'debridonly': False,
                            'info': nam,
                        })  
            return sources
        except:
            print("Unexpected error in Torrentapi Script: Sources", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return sources

        
    def resolve(self, url):
        try:
            getpl = requests.get(url).text
            sl = re.compile('link.*?"(h.*?)["\'].\n.*?s.*?http', re.I).findall(getpl)[0]
            url = sl.replace('\\','')
            return url
        except:
            print("Unexpected error in Torrentapi Script: episode", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return url
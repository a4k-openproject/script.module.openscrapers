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

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['boxfilm.pl']
        
        self.base_link = 'https://www.boxfilm.pl'
        self.search_link = '/szukaj'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        try:

            url = urlparse.urljoin(self.base_link, self.search_link)
            r = client.request(url, redirect=False, post={'szukaj' :cleantitle.query(localtitle)})
            r = client.parseDOM(r, 'div', attrs={'class':'video_info'})
            
            local_simple = cleantitle.get(localtitle)            
            for row in r:                
                name_found = client.parseDOM(row, 'h1')[0]
                year_found = name_found[name_found.find("(") + 1:name_found.find(")")]                        
                if cleantitle.get(name_found) == local_simple and year_found == year:
                    url = client.parseDOM(row, 'a', ret='href')[0]               
                    return url
        except:
            return       
  
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return None


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return None

    def get_lang_by_type(self, lang_type):
        if 'LEKTOR' in lang_type:
            return 'pl', 'Lektor'
        if  'DUBBING' in lang_type: 
            return 'pl', 'Dubbing'
        if 'NAPIS' in lang_type :
            return 'pl', 'Napisy'
        return 'en', None
    
    def sources(self, url, hostDict, hostprDict):
        
        sources = []
        try:

            if url == None: return sources            
            result = client.request(urlparse.urljoin(self.base_link, url), redirect=False)
            
            section = client.parseDOM(result, 'section', attrs={'id':'video_player'})[0]
            link = client.parseDOM(section, 'iframe', ret='src')[0]
            valid, host = source_utils.is_host_valid(link, hostDict)
            if not valid: return sources
            spans = client.parseDOM(section, 'span')
            info = None
            for span in spans:
                if span == 'Z lektorem':
                    info = 'Lektor'

            q = source_utils.check_sd_url(link)
            sources.append({'source': host, 'quality':q, 'language': 'pl', 'url': link, 'info': info, 'direct': False, 'debridonly': False})
            
            return sources
        except:
            return sources
    
    def resolve(self, url):
        return url
        

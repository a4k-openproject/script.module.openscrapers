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


import re, urllib, urlparse, base64, json

from openscrapers.modules import cleantitle
from openscrapers.modules import client

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['trt.pl']
        
        self.base_link = 'http://www.trt.pl/'
        self.search_link = 'szukaj-filmy/%s'
           
    def movie(self, imdb, title, localtitle, aliases, year):
        return title + ' ' + year
    
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return tvshowtitle;

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        return url + ' s' + season.zfill(2) + 'e' + episode.zfill(2)
        
    def contains_word(self, str_to_check, word):
        return re.search(r'\b' + word + r'\b', str_to_check, re.IGNORECASE)
    
    def contains_all_wors(self, str_to_check, words):
        for word in words:
            if not self.contains_word(str_to_check, word):
                return False
        return True
    
    def sources(self, url, hostDict, hostprDict):
        try:
                                    
            words = cleantitle.getsearch(url).split(' ')
                            
            search_url = urlparse.urljoin(self.base_link, self.search_link) % urllib.quote_plus(url);
            result = client.request(search_url)

            sources = []
            
            result = client.parseDOM(result, 'div', attrs={'class':'tile-container'})
            for el in result :                      
                
                main = client.parseDOM(el, 'h3');
                
                link = client.parseDOM(main, 'a', ret='href')[0];
                found_title = client.parseDOM(main, 'a')[0];                      
                   
                if not self.contains_all_wors(found_title, words):
                    continue
                
                quality = client.parseDOM(el, 'a', attrs={'class':'qualityLink'});
                q = 'SD'
                if quality:
                    if(quality[0] == '720p'):
                        q='HD'
                    if(quality[0]=='1080p'):
                        q='1080p'                        
                                                              
                lang, info = self.get_lang_by_type(found_title)
                 
                sources.append({'source': 'trt', 'quality': q, 'language': lang, 'url': link, 'info': info, 'direct': False, 'debridonly': False})
            
            return sources
        except:
            return sources
        
    def get_lang_by_type(self, lang_type):
        if self.contains_word(lang_type, 'lektor') :
            return 'pl', 'Lektor'
        if self.contains_word(lang_type, 'Dubbing') :        
            return 'pl', 'Dubbing'
        if self.contains_word(lang_type, 'Napisy') :        
            return 'pl', 'Napisy'
        if self.contains_word(lang_type, 'Polski') :         
            return 'pl', None
        return 'en', None

    def resolve(self, url):
        try:
            return urlparse.urljoin(self.base_link, url);
        except:
            return

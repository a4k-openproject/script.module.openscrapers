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


import urllib, urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['openkatalog.com']
        
        self.base_link = 'https://openkatalog.com'
        self.search_link = '/?s=%s'
        self.video_tab = '?tab=video'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(localtitle, year)

    
    def search(self, localtitle, year):
        try:
            simply_name = cleantitle.get(localtitle)

            query = self.search_link % urllib.quote_plus(cleantitle.query(localtitle))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query)

            result = client.parseDOM(result, 'article')
          
            for row in result:
                a_href = client.parseDOM(row, 'h3')[0]  
                url = client.parseDOM(a_href, 'a', ret='href')[0] 
                name = client.parseDOM(a_href, 'a')[0]
                name = cleantitle.get(name)
                
                year_found = client.parseDOM(row, 'span', attrs={'class':'dtyear'})
                if year_found:
                    year_found = year_found[0]                
               
                if(name == simply_name and (not year_found or not year or year_found == year)):
                    return url
        except :
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return localtvshowtitle


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        query = url + ' s' + season.zfill(2) + 'e' + episode.zfill(2)
        return self.search(query, None)        

    def get_info_from_desc(self, desc):
        desc_list = desc.split(",")
        host = desc_list.pop(0)
        
        lang = None
        info = None
        q = 'SD'
        
        for el in desc_list:
            if 'napisy' in el:
                info = 'Napisy'
            elif 'lektor' in el:
                info = 'Lektor'
            elif 'dubbing' in el:
                info = 'Dubbing'

            if 'PL' in el:
                lang = 'pl'

            if '720p' in el:
                q = 'HD'
            elif '1080' in el:
                q = '1080p'             
       
        return host, lang, info, q
    
    def sources(self, url, hostDict, hostprDict):
        
        sources = []
        try:

            if url == None: return sources
            url = url + self.video_tab
            result = client.request(url)
                                    
            rows = client.parseDOM(result, 'ul', attrs={'class':'player_ul'})[0]
            rows = client.parseDOM(rows, 'li')        

            for row in rows:
                try:
                    desc = client.parseDOM(row, 'a')[0]
                    link = client.parseDOM(row, 'a', ret='href')[0]            
                    
                    host, lang, info, q = self.get_info_from_desc(desc)

                    sources.append({'source': host, 'quality': q, 'language': lang, 'url': link, 'info': info, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources
    
    def resolve(self, url):
        result = client.request(url)
        result = client.parseDOM(result, 'div', attrs={'class':'embed'})[0]
        result = client.parseDOM(result, 'iframe', ret='src')[0]
        
        return result      

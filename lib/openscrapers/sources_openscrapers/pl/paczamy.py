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


import urllib, urlparse, re

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['paczamy.pl']
        
        self.base_link = 'http://paczamy.pl'
        self.search_link = '/szukaj?q=%s'
        self.episode_link = '/seasons/%s/episodes/%s'
        
    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(localtitle, year, 'movies')
    

    def findMatchByYear(self, year, urls):
        
        for url in urls:
            result = client.request(url)
            result = client.parseDOM(result, 'h1')[0]
            result = client.parseDOM(result, 'a')[0]
            found_year = result[result.find("(") + 1:result.find(")")]
            if(found_year == year):
                return url
            
            
    
    def search(self, localtitle, year, search_type):
        try:
            simply_name = cleantitle.get(localtitle)

            query = self.search_link % urllib.quote_plus(cleantitle.query(localtitle))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query)

            result = client.parseDOM(result, 'div', attrs={'id':search_type})
            links = client.parseDOM(result, 'figcaption')
            names = client.parseDOM(result, 'figcaption', ret='title')                        
            urls = []
            for i in range(len(names)):
                name = cleantitle.get(names[i])
                url = client.parseDOM(links[i], 'a', ret='href')[0]                
                if(name == simply_name):
                    urls.append(url)
            if len(urls) == 1:
                return urls[0]
            else:
                return self.findMatchByYear(year, urls)

        except :
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.search(localtvshowtitle, year, 'series')


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            query = self.episode_link % (season, episode)
            return url + query                                
        except:
            return

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
            result = client.request(url)
            
            rows = client.parseDOM(result, 'tr', attrs={'data-id':'.*?'}) 
            

            for row in rows:
                try:
                    link = client.parseDOM(row, 'td', attrs={'class':'name hover'}, ret='data-bind')[0]
                    link = re.findall(r"'(.*?)'", link, re.DOTALL)[0] 
                                
                    valid, host = source_utils.is_host_valid(link, hostDict)
                    if not valid: continue                                   
                    
                    found_quality = client.parseDOM(row, 'td')[1] 
                    q = 'SD'
                    if 'Wysoka' in found_quality: q = 'HD'
                    
                    type_desc= client.parseDOM(row, 'font')[0]
                    lang, info = self.get_lang_by_type(type_desc)

                    sources.append({'source': host, 'quality': q, 'language': lang, 'url': link, 'info': info, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources
    
    def resolve(self, url):
        return url
        

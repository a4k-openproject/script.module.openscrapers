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

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['cda-hd.cc']

        self.base_link = 'http://cda-hd.cc/'
        self.search_link = '/?s=%s'

    def do_search(self, title, local_title, year, video_type):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % urllib.quote_plus(cleantitle.query(title))
            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs={'class': 'item'})
            for row in result:
                row_type = client.parseDOM(row, 'div', attrs={'class': 'typepost'})[0]
                if row_type != video_type:
                    continue
                names = client.parseDOM(row, 'span', attrs={'class': 'tt'})[0]
                names = names.split('/')
                year_found = client.parseDOM(row, 'span', attrs={'class': 'year'})
                
                titles = [cleantitle.get(i) for i in [title,local_title]]
                
                if self.name_matches(names, titles, year) and (len(year_found) == 0 or year_found[0] == year):
                    url = client.parseDOM(row, 'a', ret='href')[0]
                    return urlparse.urljoin(self.base_link, url)
        except :
            return

    def name_matches(self, names_found, titles, year):
        for name in names_found:
            name = name.strip().encode('utf-8')
            # if ends with year
            clean_found_title = cleantitle.get(name)            
            # sometimes they add year to title so we need to check thet
            if clean_found_title in titles:
                return True

        return False

    def get_first_not_none(self, collection):
        return next(item for item in collection if item is not None)


    def movie(self, imdb, title, localtitle, aliases, year):
        return self.do_search(title, localtitle, year, 'Film')

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.do_search(tvshowtitle, localtvshowtitle, year, 'Serial')

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            result = client.request(url)
            # cant user dom parser here because HTML is bugged div is not closed
            result = re.findall ('<ul class="episodios">(.*?)</ul>', result, re.MULTILINE | re.DOTALL)
            for item in result:
                season_episodes = re.findall ('<li>(.*?)</li>', item, re.MULTILINE | re.DOTALL)
                for row in season_episodes:
                    s = client.parseDOM(row, 'div', attrs={'class': 'numerando'})[0].split('x')
                    season_found = s[0].strip()
                    episode_found = s[1].strip()
                    if(season_found != season):
                        break
                    if episode_found == episode :
                        return client.parseDOM(row, 'a', ret='href')[0]

        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            result = client.request(url)
            box_result = client.parseDOM(result, 'li', attrs={'class': 'elemento'})
            
            if(len(box_result) != 0):
                sources = self.get_links_from_box(box_result)
            
            sources += self.get_from_main_player(result, sources) 

            return sources
        except:
            return sources
    
    def get_from_main_player(self, result, sources):
        
        q = 'SD'
        if len(sources) == 0 and (len(client.parseDOM(result, 'span', attrs={'class': 'calidad2'})) > 0):
            q = 'HD'
        player2 = client.parseDOM(result, 'div', attrs={'id': 'player2'})
        links = client.parseDOM(player2, 'iframe', ret='src')
        
        player_nav = client.parseDOM(result, 'div', attrs={'class': 'player_nav'})
        transl_type = client.parseDOM(player_nav, 'a')
        result_sources = []
        for i in range(0, len(links)):
            url = links[i]
            if(self.url_not_on_list(url, sources)):
                lang, info = self.get_lang_by_type(transl_type[i])
                host = url.split("//")[-1].split("/")[0]
                result_sources.append({'source': host, 'quality': q, 'language': lang, 'url': url, 'info': info, 'direct': False, 'debridonly': False})
            
        
        return result_sources
    
    def url_not_on_list(self, url, sources):
        for el in sources:
            if el.get('url') == url:
                return False
        return True
        
    def get_links_from_box(self, result):
        sources = []
        for row in result:
            src_url = client.parseDOM(row, 'a', ret='href')[0]
            lang_type = client.parseDOM(row, 'span', attrs={'class': 'c'})[0]
            quality_type = client.parseDOM(row, 'span', attrs={'class': 'd'})[0]
            host = client.parseDOM(row, 'img', ret='alt')[0]
            lang, info = self.get_lang_by_type(lang_type)
            q = 'SD'
            if quality_type == 'Wysoka':q = 'HD'
            sources.append({'source': host, 'quality': q, 'language': lang, 'url': src_url, 'info': info, 'direct': False, 'debridonly': False})
            
        return sources
    
    def get_lang_by_type(self, lang_type):
        if lang_type == 'Lektor PL':
            return 'pl', 'Lektor'
        if lang_type == 'Dubbing PL': 
            return 'pl', 'Dubbing'
        if lang_type == 'Napisy PL':
            return 'pl', 'Napisy'
        if lang_type == 'PL': 
            return 'pl', None
        return 'en', None
        
    def resolve(self, url):
        return url



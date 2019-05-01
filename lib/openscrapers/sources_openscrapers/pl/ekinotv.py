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

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['ekino-tv.pl']

        self.base_link = 'http://ekino-tv.pl'
        self.search_link = '/search/'
        self.resolve_link = '/watch/f/%s/%s'

    def search(self, title, localtitle, year, search_type):
        try:
            url = self.do_search(cleantitle.query(title), title, localtitle, year, search_type)
            if not url:
                url = self.do_search(cleantitle.query(localtitle), title, localtitle, year, search_type)
            return url
        except:
            return
        
    def do_search(self, search_string, title, localtitle , year, search_type):
        url = urlparse.urljoin(self.base_link, self.search_link)
        r = client.request(url, redirect=False, post={'search_field': search_string})
        r = client.parseDOM(r, 'div', attrs={'class': 'movies-list-item'})

        local_simple = cleantitle.get(localtitle)
        title_simple = cleantitle.get(title)
        for row in r:
            row = client.parseDOM(row, 'div', attrs={'class': 'opis-list'})[0]
            title_found = client.parseDOM(row, 'div', attrs={'class': 'title'})[0]
            link = client.parseDOM(title_found, 'a', ret='href')[0]                        
            if not search_type in link:
                continue
            
            local_found = client.parseDOM(title_found, 'a')[0]
            title_found = client.parseDOM(title_found, 'a', attrs={'class': 'blue'})
            if not title_found or not title_found[0]:
                title_found = local_found
            else: 
                title_found = title_found[0]
            
            local_found = local_found.replace('&nbsp;', '')
            title_found = title_found.replace('&nbsp;', '')
            year_found = client.parseDOM(row, 'p', attrs={'class': 'cates'})
            if year_found:
                year_found = year_found[0][:4]
            title_match = cleantitle.get(local_found) == local_simple or  cleantitle.get(title_found) == title_simple
            year_match = (not year_found) or year == year_found
            
            if title_match and year_match:
                return link

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.search(title, localtitle, year, '/movie/')

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.search(tvshowtitle, localtvshowtitle, year, '/serie/')

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        url = urlparse.urljoin(self.base_link, url)
        r = client.request(url)        
        r = client.parseDOM(r, 'div', attrs={'id': 'list-series'})[0]
        p = client.parseDOM(r, 'p')
        index = p.index('Sezon ' + season)
        r = client.parseDOM(r, 'ul')[index]
        r = client.parseDOM(r, 'li')
        for row in r:
            ep_no = client.parseDOM(row, 'div')[0]
            if ep_no == episode:
                return client.parseDOM(row, 'a', ret='href')[0]     
        return None

    def get_lang_by_type(self, lang_type):
        if lang_type:
            lang_type = lang_type[0]
            if 'Lektor' in lang_type:
                return 'pl', 'Lektor'
            if 'Dubbing' in lang_type:
                return 'pl', 'Dubbing'
            if 'Napisy' in lang_type:
                return 'pl', 'Napisy'
            if 'PL' in lang_type:
                return 'pl', None
        return 'en', None

    def sources(self, url, hostDict, hostprDict):

        sources = []
        try:
            if url == None: return sources
            r = client.request(urlparse.urljoin(self.base_link, url), redirect=False)
            rows = client.parseDOM(r, 'ul', attrs={'class': 'players'})[0]
            rows = client.parseDOM(rows, 'li')
            rows.pop()
            rows2 = client.parseDOM(r, 'div', attrs={'role': 'tabpanel'})
            
            for i in range(len(rows)):
                row = rows[i]
                row2 = rows2[i]                
                link = client.parseDOM(row2, 'a', ret='onClick')[0]
                data = client.parseDOM(row, 'a')[0]
                qual = client.parseDOM(row, 'img ', ret='title')
                lang_type = client.parseDOM(row, 'i ', ret='title')
                q = 'SD'
                if qual and 'Wysoka' in qual[0]:
                    q = 'HD'
                lang, info = self.get_lang_by_type(lang_type)
                host = data.splitlines()[0].strip()
                sources.append({'source': host, 'quality': q, 'language': lang, 'url': link, 'info': info, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            splitted = url.split("'")
            host = splitted[1]
            video_id = splitted[3]
            transl_url = urlparse.urljoin(self.base_link, self.resolve_link) % (host, video_id)
            result = client.request(transl_url, redirect=False, cookie="prch=true")
            scripts = client.parseDOM(result, 'script')
            for script in scripts:
                if 'var url' in script:
                    return script.split("'")[1]
        except: 
            return None 

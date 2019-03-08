# -*- coding: UTF-8 -*-
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
        self.domains = ['filionline.pl']

        self.base_link = 'http://filionline.pl/'
        self.url_transl = 'embed?salt=%s'
        self.search_link = 'szukaj?q=%s'
        self.episode_link = '-Season-%01d-Episode-%01d'


    def check_titles(self, cleaned_titles, found_titles):        
        return cleaned_titles[0] == cleantitle.get(found_titles[0]) or cleaned_titles[1] == cleantitle.get(found_titles[1])    
    
    def do_search(self, title, localtitle, year, is_movie_search):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            url = url % urllib.quote(title)
            result = client.request(url)
            result = result.decode('utf-8')

            result = client.parseDOM(result, 'ul', attrs={'id': 'resultList2'})
            li_list = []
            for el in result:
                li_list.extend(client.parseDOM(el, 'li'))
            

            result = [(client.parseDOM(i, 'a', ret='href')[0],
                       client.parseDOM(i, 'div', attrs={'class': 'title'})[0],
                       (client.parseDOM(i, 'div', attrs={'class': 'title_org'}) + [None])[0],
                       client.parseDOM(i, 'div', attrs={'class': 'info'})[0],
                       ) for i in li_list]

            search_type = 'Film' if is_movie_search else 'Serial'
            cleaned_titles = [cleantitle.get(title), cleantitle.get(localtitle)]                         
            # filter by name
            result = [x for x in result if self.check_titles(cleaned_titles, [x[2], x[1]])]
            # filter by type
            result = [x for x in result if x[3].startswith(search_type)]
            # filter by year
            result = [x for x in result if x[3].endswith(str(year))]

            if len(result) > 0:
                return result[0][0]
            else:
                return

        except :
            return

    def movie(self, imdb, title, localtitle, aliases, year):
        return self.do_search(title, localtitle, year, True)

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.do_search(tvshowtitle, localtvshowtitle, year, False)

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.urljoin(self.base_link, url)
            result = client.request(url)
            result = client.parseDOM(result, 'ul', attrs={'data-season-num': season})[0]
            result = client.parseDOM(result, 'li')
            for i in result:
                s = client.parseDOM(i, 'a', attrs={'class': 'episodeNum'})[0]
                e = int(s[7:-1])
                if e == int(episode):
                    return client.parseDOM(i, 'a', attrs={'class': 'episodeNum'}, ret='href')[0]

        except :
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs={'id': 'links'})
            attr = client.parseDOM(result, 'ul', ret='data-type')
            result = client.parseDOM(result, 'ul')
            for x in range(0, len(result)):
                transl_type = attr[x]
                links = result[x]
                sources += self.extract_sources(transl_type, links)

            return sources
        except:
            return sources

    def get_lang_by_type(self, lang_type):
        if lang_type == 'DUBBING':
            return 'pl', 'Dubbing'
        elif lang_type == 'NAPISY_PL':
            return 'pl', 'Napisy'
        if lang_type == 'LEKTOR_PL':
            return 'pl', 'Lektor'
        elif lang_type == 'POLSKI':
            return 'pl', None
        return 'en', None

    def extract_sources(self, transl_type, links):
        sources = []
        data_refs = client.parseDOM(links, 'li', ret='data-ref')
        result = client.parseDOM(links, 'li')

        lang, info = self.get_lang_by_type(transl_type)

        for i in range(0, len(result)):

            el = result[i];
            host = client.parseDOM(el, 'span', attrs={'class': 'host'})[0]
            quality = client.parseDOM(el, 'span', attrs={'class': 'quality'})[0]
            q = 'SD'
            if quality.endswith('720p'):
                q = 'HD'
            elif quality.endswith('1080p'):
                q = '1080p'

            sources.append({'source': host, 'quality': q, 'language': lang, 'url': data_refs[i], 'info': info, 'direct': False, 'debridonly': False})

        return sources

    def resolve(self, url):
        try:
            url_to_exec = urlparse.urljoin(self.base_link, self.url_transl) % url
            result = client.request(url_to_exec)

            search_string = "var url = '";
            begin = result.index(search_string) + len(search_string)
            end = result.index("'", begin)

            result_url = result[begin:end]                                    
            result_url = result_url.replace('#WIDTH', '100')
            result_url = result_url.replace('#HEIGHT', '100')
            return result_url
        except:
            return

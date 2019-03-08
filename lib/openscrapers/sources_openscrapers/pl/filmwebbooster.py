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
import urlparse
from openscrapers.modules import source_utils, dom_parser, client, cleantitle
import urllib
from httplib import FOUND

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['pl']
        self.domains = ['filmwebbooster.pl']
        
        self.base_link = 'http://178.19.110.218/filmweb/'
        self.base_link2 = 'http://178.19.110.218/filmweb/filmdb/dodatkowe_zrodla.php'
        self.search_more = 'wiecejzrodel.php'
        self.search_tvshow = 'search_serial.php'
        self.search_movie = 'search_film.php'      
        self.film_web='http://www.filmweb.pl' 
        self.filmdb = 'http://www.filmdb.pl'
        self.filmweb_search = '/search?q=%s&startYear=%s&endYear=%s&startRate=&endRate=&startCount=&endCount='   
        self.filmdb_search = '/ajax.php'
        
    def create_search_more(self, title, localtitle, year,sp,filmid,season,episode):
        if localtitle == 'Vikings':
            localtitle = 'Wikingowie'
        return {"title" : localtitle,'subtitle':title,'sezon':season,'odcinek':episode,"rok" : year,'sp' : sp,"filmid" : filmid}

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            result = {}
            result['url'] = urlparse.urljoin(self.base_link, self.search_movie)
            fw = self.get_filmweb_data('films', title, localtitle, year)
            try:
                result['post'] = { "szukany" : localtitle, "engTitle" : title,"rok" : year, "czastrwania" : '', "filmid" : fw['id'], "urlstrony" : fw['href'] }
            except:
                pass
            fdb = self.get_filmdb_data('film','film',title,localtitle,year)
            result['more'] = self.create_search_more(title, localtitle, year,str(fdb['sp']),fdb['filmid'],fdb['sezon'],fdb['odcinek'])
            debug =1;
            return result
        except Exception, e:
            print str(e)
    
    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            result = {}
            result['url'] = urlparse.urljoin(self.base_link, self.search_tvshow)
            fw = self.get_filmweb_data('serial', tvshowtitle, localtvshowtitle, year)
            try:
                result['post'] = { "szukany" : localtvshowtitle, "engTitle" : tvshowtitle,"rok" : year, "czastrwania" : '', "filmid" : fw['id'], "urlstrony" : fw['href'] }
            except:
                pass
            fdb = self.get_filmdb_data('serial','serial',tvshowtitle,localtvshowtitle,year)
            result['more'] = self.create_search_more(tvshowtitle, localtvshowtitle, year,str(fdb['sp']),str(fdb['filmid']),fdb['sezon'],fdb['odcinek'])
            return result
        except Exception, e:
            print str(e)
            return result

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        url['more']['sezon'] = season
        url['more']['odcinek'] = episode
        url['post']['odcinek'] = episode
        url['post']['sezon'] = season
        return url
    
    def get_filmdb_data(self, season, episode, title, localtitle, year):
        try:
            import requests

            titles = {localtitle,title}
            for item in titles:
                try:
                    if item == 'Vikings':
                        item = 'Wikingowie'
                    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Referer': 'http://filmdb.pl/' }
                    url = urlparse.urljoin(self.filmdb, self.filmdb_search)
                    data ={"search_film" : item}
                    r = requests.post(url, data=data, headers = headers)
                    result = r.text
                    hrefs = client.parseDOM(result, 'a', ret='href')
                    for href in hrefs:
                        result = client.request(self.filmdb + str(href))
                        fdbtitle = client.parseDOM(result, 'input', ret='value')[0]
                        fdbsubtitle = client.parseDOM(result, 'input', ret='value')[1]
                        fdbyear = client.parseDOM(result, 'input', ret='value')[2]
                        fdbfilmid = client.parseDOM(result, 'input', ret='value')[3]
                        fdbsp = client.parseDOM(result, 'input', ret='value')[4]
                        local_clean = cleantitle.get(localtitle)
                        title_clean = cleantitle.get(title)
                        found_clean = cleantitle.get(fdbsubtitle)
                        if found_clean == '':
                            found_clean = cleantitle.get(fdbtitle)
                        if title_clean == found_clean or local_clean == found_clean:
                            return {'sp':fdbsp, 'filmid':fdbfilmid, 'sezon':season, 'odcinek':episode}
                except:
                    pass
        except Exception, e:
            print str(e)
    def get_filmweb_data(self, type_url, title, localtitle, year):
        try:
            if localtitle == 'Vikings':
                localtitle = 'Wikingowie'
            titles = {localtitle,title}
            for item in titles:
                from urllib2 import Request, urlopen
                url = urlparse.urljoin(self.film_web, self.filmweb_search)
                url = url % (urllib.quote_plus(item), year, year)
                result = client.request(url)
                id = ''
                rows = client.parseDOM(result, 'div', attrs={'class':'ad__page-wrapper'})
                if not rows:
                    continue
                rows = client.parseDOM(rows, 'div', attrs={'id':'searchResult'})
                try:
                    id = client.parseDOM(rows, 'data', ret='data-id')[0]
                except:
                    pass
                rows = client.parseDOM(rows, 'div', attrs={'class':'filmPreview__card'})
                local_clean = cleantitle.get(localtitle)
                title_clean = cleantitle.get(title)
                if not rows:
                    url = urlparse.urljoin(self.film_web, self.filmweb_search)
                    url = url % (type_url, urllib.quote_plus(cleantitle.query(localtitle)), year, year)
                    q = Request(url)
                    a = urlopen(q)
                    result = a.read()
                    rows = client.parseDOM(rows, 'div', attrs={'id':'searchResult'})
                    try:
                        id = client.parseDOM(rows, 'data', ret='data-id')[0]
                    except:
                        pass
                    rows = client.parseDOM(rows, 'div', attrs={'class':'filmPreview__card'})
                    local_clean = cleantitle.get(localtitle)
                    title_clean = cleantitle.get(title)
                for row in rows:
                    row2 = row
                    row2 = client.parseDOM(row, 'div', attrs={'class':'filmPreview__originalTitle'})
                    if not row2:
                        row2 = client.parseDOM(row, 'h3', attrs={'class':'filmPreview__title'})
                    href = client.parseDOM(row, 'a', ret='href')[0]
                    found_clean = cleantitle.get(row2[0])
                    if title_clean == found_clean or local_clean == found_clean:
                        return {'href':href, 'id':id}
                    return {'href':href, 'id':id}                  
        except Exception, e:
            print str(e)
        

    def get_info_from_others(self, sources):
        infos = []
        for source in sources:
            info = source['info']
            if info :
                infos.append(info)
        infos.sort()
        if infos:            
            return infos[0]
        return ''
    
    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []         
            try:                             
                search_url = url['url'] 
                post = url['post']
                referer = urlparse.urljoin(self.film_web, post['urlstrony'])
                result = client.request(search_url, post=post,referer=referer)
                if not result.startswith('http'):
                    return sources
            
                valid, host = source_utils.is_host_valid(result, hostDict)
                q = source_utils.check_sd_url(result)
                info = ''
                if 'lektor' in result:
                    info = 'Lektor'
                if 'napisy' in result:
                    info = 'Napisy'
                first_found = {'source': host, 'quality': '720p', 'language': 'pl', 'url': result, 'info': info, 'direct': False, 'debridonly': False}      
                first_found['info'] = self.get_info_from_others(sources)
                sources.append(first_found)
            except:
                pass
            search_more_post = url['more']
            #search_url = urlparse.urljoin(self.base_link, self.search_more)
            result = client.request(self.base_link2, post=search_more_post)
            provider = client.parseDOM(result, 'option', ret='value')
            links = client.parseDOM(result, 'div', ret='data')
            wersja = client.parseDOM(result, 'div', attrs={'class':'wersja'})
            #result = dom_parser.parse_dom(result, 'a')            
            counter = 0
            for link in links :
                valid, host = source_utils.is_host_valid(link, hostDict)
                if not valid: continue
                q = source_utils.check_sd_url(link)
                sources.append({'source': host, 'quality': q, 'language': 'pl', 'url': link, 'info': wersja[counter], 'direct': False, 'debridonly': False})
                counter += 1
            return sources
        except:
            return sources
        
    def resolve(self, url):
        if 'speedvid' in url:
            test = len(url)
            url = url[0:test-23]
        return url        

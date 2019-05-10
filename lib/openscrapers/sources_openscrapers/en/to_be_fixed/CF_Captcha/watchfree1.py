# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

# -Cleaned and Checked on 04-15-2019 by JewBMX in Scrubs.

import base64
import re
import urllib
import urlparse

from openscrapers.modules import cfscrape
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['watchfree1.com']
        self.base_link = 'http://watchfree1.com'
        self.search_link = '/search-movies/%s.html'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title).replace('-', '+')
            url = urlparse.urljoin(self.base_link, (self.search_link % clean_title))
            r = self.scraper.get(url).content
            r = dom_parser.parse_dom(r, 'div', {'class': 'item'})
            r = [dom_parser.parse_dom(i, 'a', req=['href']) for i in r if i]
            r = [(i[0].attrs['href'], re.search('Release:\s*(\d+)', i[0].content)) for i in r if i]
            r = [(i[0], i[1].groups()[0]) for i in r if i[0] and i[1]]
            r = [(i[0], i[1]) for i in r if i[1] == year]
            if r[0]:
                url = r[0][0]
                return url
            else:
                return
        except Exception:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['premiered'], url['season'], url['episode'] = premiered, season, episode
            try:
                clean_title = cleantitle.geturl(url['tvshowtitle']) + '-season-%d' % int(season)
                search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
                r = client.request(search_url)
                r = client.parseDOM(r, 'div', {'class': 'item'})
                r = [(client.parseDOM(i, 'a', ret='href'),
                      re.findall('<b><i>(.+?)</i>', i)) for i in r]
                r = [(i[0][0], i[1][0]) for i in r if
                     cleantitle.get(i[1][0]) == cleantitle.get(clean_title)]
                url = r[0][0]
            except:
                pass
            data = self.scraper.get(url).content
            data = client.parseDOM(data, 'div', attrs={'id': 'details'})
            data = zip(client.parseDOM(data, 'a'), client.parseDOM(data, 'a', ret='href'))
            url = [(i[0], i[1]) for i in data if i[0] == str(int(episode))]
            return url[0][1]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            openload_limit = 1
            vshare_limit = 1
            flashx_limit = 1
            thevideobee_limit = 1
            entervideo_limit = 1
            megamp4_limit = 1
            vidtodo_limit = 1
            r = self.scraper.get(url).content
            try:
                v = re.findall('document.write\(Base64.decode\("(.+?)"\)', r)[0]
                b64 = base64.b64decode(v)
                url = client.parseDOM(b64, 'iframe', ret='src')[0]
                try:
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if valid:
                        sources.append({'source': host, 'quality': 'SD', 'language': 'en',
                                        'url': url.replace('\/', '/'), 'direct': False, 'debridonly': False})
                except:
                    pass
            except:
                pass
            r = client.parseDOM(r, 'div', {'class': 'server_line'})
            r = [(client.parseDOM(i, 'a', ret='href')[0],
                  client.parseDOM(i, 'p', attrs={'class': 'server_servername'})[0]) for i in r]
            if r:
                for i in r:
                    try:
                        host = re.sub('Server|Link\s*\d+', '', i[1]).lower()
                        url = i[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        if 'other' in host: continue
                        valid, host = source_utils.is_host_valid(host, hostDict)
                        if 'openload' in host:
                            if openload_limit < 1:
                                continue
                            else:
                                openload_limit -= 1
                        if 'vshare' in host:
                            if vshare_limit < 1:
                                continue
                            else:
                                vshare_limit -= 1
                        if 'flashx' in host:
                            if flashx_limit < 1:
                                continue
                            else:
                                flashx_limit -= 1
                        if 'thevideobee' in host:
                            if thevideobee_limit < 1:
                                continue
                            else:
                                thevideobee_limit -= 1
                        if 'entervideo' in host:
                            if entervideo_limit < 1:
                                continue
                            else:
                                entervideo_limit -= 1
                        if 'megamp4' in host:
                            if megamp4_limit < 1:
                                continue
                            else:
                                megamp4_limit -= 1
                        if 'vidtodo' in host:
                            if vidtodo_limit < 1:
                                continue
                            else:
                                vidtodo_limit -= 1
                        if valid:
                            sources.append(
                                {'source': host, 'quality': 'SD', 'language': 'en', 'url': url.replace('\/', '/'),
                                 'direct': False, 'debridonly': False})
                    except:
                        pass
            return sources
        except Exception:
            return

    def resolve(self, url):
        if self.base_link in url:
            url = self.scraper.get(url).content
            v = re.findall('document.write\(Base64.decode\("(.+?)"\)', url)[0]
            b64 = base64.b64decode(v)
            url = client.parseDOM(b64, 'iframe', ret='src')[0]
        return url

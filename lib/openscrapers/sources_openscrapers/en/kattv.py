# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
    OpenScrapers Project


    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>..
'''

import re,urlparse,urllib,base64
from openscrapers.modules import cleantitle,client,dom_parser2,cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['kat.tv']
        self.base_link = 'http://www1.kat.tv'
        self.search_link = '/search-movies/%s.html'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            clean_title = cleantitle.geturl(title)
            search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
            r = self.scraper.get(search_url).content
            r = dom_parser2.parse_dom(r, 'li', {'class': 'item'})
            r = [(dom_parser2.parse_dom(i, 'a', attrs={'class': 'title'}),
                  re.findall('status-year">(\d{4})</div', i.content, re.DOTALL)[0]) for i in r if i]
            r = [(i[0][0].attrs['href'], re.findall('(.+?)</b><br', i[0][0].content, re.DOTALL)[0], i[1]) for i in r if i]
            r = [(i[0], i[1], i[2]) for i in r if (cleantitle.get(i[1]) == cleantitle.get(title) and i[2] == year)]
            url = r[0][0]
            return url
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
                clean_title = cleantitle.geturl(url['tvshowtitle'])+'-season-%d' % int(season)
                search_url = urlparse.urljoin(self.base_link, self.search_link % clean_title.replace('-', '+'))
                r = self.scraper.get(search_url).content
                r = dom_parser2.parse_dom(r, 'li', {'class': 'item'})
                r = [(dom_parser2.parse_dom(i, 'a', attrs={'class': 'title'}),
                      dom_parser2.parse_dom(i, 'div', attrs={'class':'status'})[0]) for i in r if i]
                r = [(i[0][0].attrs['href'], re.findall('(.+?)</b><br', i[0][0].content, re.DOTALL)[0],
                      re.findall('(\d+)', i[1].content)[0]) for i in r if i]
                r = [(i[0], i[1].split(':')[0], i[2]) for i in r
                     if (cleantitle.get(i[1].split(':')[0]) == cleantitle.get(url['tvshowtitle']) and i[2] == str(int(season)))]
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
            r = self.scraper.get(url).content
            try:
                v = re.findall('document.write\(Base64.decode\("(.+?)"\)', r)[0]
                b64 = base64.b64decode(v)
                url = client.parseDOM(b64, 'iframe', ret='src')[0]
                try:
                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({
                        'source': host,
                        'quality': 'SD',
                        'language': 'en',
                        'url': url.replace('\/', '/'),
                        'direct': False,
                        'debridonly': False
                    })
                except:
                    pass
            except:
                pass
            r = client.parseDOM(r, 'div', {'class': 'server_line'})
            r = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'p', attrs={'class': 'server_servername'})[0]) for i in r]
            if r:
                for i in r:
                    try:
                        host = re.sub('Server|Link\s*\d+', '', i[1]).lower()
                        url = i[0]
                        host = client.replaceHTMLCodes(host)
                        host = host.encode('utf-8')
                        if 'other'in host: continue
                        sources.append({
                            'source': host,
                            'quality': 'SD',
                            'language': 'en',
                            'url': url.replace('\/', '/'),
                            'direct': False,
                            'debridonly': False
                        })
                    except:
                        pass
            return sources
        except Exception:
            return


    def resolve(self, url):
        if self.base_link in url:
            try:
                r = self.scraper.get(url).content
                v = re.findall('document.write\(Base64.decode\("(.+?)"\)', r)[0]
                b64 = base64.b64decode(v)
                url = client.parseDOM(b64, 'iframe', ret='src')[0]
            except:
                r = self.scraper.get(url).content
                r = client.parseDOM(r, 'div', attrs={'class':'player'})
                url = client.parseDOM(r, 'a', ret='href')[0]
        return url


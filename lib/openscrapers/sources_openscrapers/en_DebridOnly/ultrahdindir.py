# -*- coding: UTF-8 -*-
# -Cleaned and Checked on 08-24-2019 by JewBMX in Scrubs.
# Fixed by Tempest

import re,urllib,urlparse

from openscrapers.modules import client
from openscrapers.modules import debrid
from openscrapers.modules import dom_parser


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ultrahdindir.com']
        self.base_link = 'http://ultrahdindir.com'
        self.post_link = '/index.php?do=search'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None:
                return sources
            if debrid.status() is False:
                raise Exception()
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['title'].replace(':','').lower()
            year = data['year']
            query = '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)
            url = urlparse.urljoin(self.base_link, self.post_link)
            post = 'do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=%s' % urllib.quote_plus(query)
            r = client.request(url, post=post)
            r = client.parseDOM(r, 'div', attrs={'class': 'box-out margin'})
            r = [(dom_parser2.parse_dom(i, 'div', attrs={'class':'news-title'})) for i in r if data['imdb'] in i]
            r = [(dom_parser2.parse_dom(i[0], 'a', req='href')) for i in r if i]
            r = [(i[0].attrs['href'], i[0].content) for i in r if i]
            hostDict = hostprDict + hostDict
            for item in r:
                try:
                    name = item[0]
                    s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', name)
                    s = s[0] if s else '0'
                    data = client.request(item[0])
                    data = dom_parser2.parse_dom(data, 'div', attrs={'id': 'r-content'})
                    data = re.findall('\s*<b><a href="(.+?)".+?</a></b>', data[0].content, re.DOTALL)
                    for url in data:
                        try:
                            qual = client.request(url)
                            quals = re.findall('span class="file-title" id="file-title">(.+?)</span', qual)
                            for quals in quals:
                                if '4K' in quals:
                                    quality = '4K'
                                elif '2160p' in quals:
                                    quality = '4K'
                                elif '1080p' in quals:
                                    quality = '1080p'
                                elif '720p' in quals:
                                    quality = '720p'
                                elif any(i in ['dvdscr', 'r5', 'r6'] for i in quals):
                                    quality = 'SCR'
                                elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts'] for i in quals):
                                    quality = 'CAM'
                                else:
                                    quality = '720p'
                            info = []
                            if '3D' in name or '.3D.' in quals:
                                info.append('3D'); quality = '1080p'
                            if any(i in ['hevc', 'h265', 'x265'] for i in quals):
                                info.append('HEVC')
                            info = ' | '.join(info)
                            url = client.replaceHTMLCodes(url)
                            url = url.encode('utf-8')
                            if any(x in url for x in ['.rar', '.zip', '.iso']):
                                raise Exception()
                            if not 'turbobit' in url:
                                continue
                            if url in str(sources):
                                continue
                            sources.append({'source': 'turbobit', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': True, 'debridonly': True})
                        except:
                            pass
                except:
                    pass
            return sources
        except:
            return sources


    def resolve(self, url):
        return url


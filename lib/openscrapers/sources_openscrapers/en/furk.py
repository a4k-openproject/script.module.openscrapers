# -*- coding: UTF-8 -*-

#  ..#######.########.#######.##....#..######..######.########....###...########.#######.########..######.
#  .##.....#.##.....#.##......###...#.##....#.##....#.##.....#...##.##..##.....#.##......##.....#.##....##
#  .##.....#.##.....#.##......####..#.##......##......##.....#..##...##.##.....#.##......##.....#.##......
#  .##.....#.########.######..##.##.#..######.##......########.##.....#.########.######..########..######.
#  .##.....#.##.......##......##..###.......#.##......##...##..########.##.......##......##...##........##
#  .##.....#.##.......##......##...##.##....#.##....#.##....##.##.....#.##.......##......##....##.##....##
#  ..#######.##.......#######.##....#..######..######.##.....#.##.....#.##.......#######.##.....#..######.

'''
   Incursion Add-on
   Copyright (C) 2016 Incursion
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import requests, json, sys
from openscrapers.modules import source_utils
from resources.lib.modules import control


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domain = 'furk.net/'
        self.base_link = 'https://www.furk.net'
        self.meta_search_link = "/api/plugins/metasearch?api_key=%s&q=%s&cached=yes" \
                                "&match=%s&moderated=%s%s&sort=relevance&type=video&offset=0&limit=%s"
        self.tfile_link = "/api/file/get?api_key=%s&t_files=1&id=%s"
        self.login_link = "/api/login/login?login=%s&pwd=%s"
        self.user_name = control.setting('furk.user_name')
        self.user_pass = control.setting('furk.user_pass')
        self.api_key = control.setting('furk.api')
        self.search_limit = control.setting('furk.limit')
        self.files = []

    def get_api(self):

        try:

            api_key = self.api_key

            if api_key == '':
                if self.user_name == '' or self.user_pass == '':
                    return

                else:
                    s = requests.Session()
                    link = (self.base_link + self.login_link % (self.user_name, self.user_pass))
                    p = s.post(link)
                    p = json.loads(p.text)

                    if p['status'] == 'ok':
                        api_key = p['api_key']
                        control.setSetting('furk.api', api_key)
                    else:
                        pass

            return api_key

        except:
            print("Unexpected error in Furk Script: check_api", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = tvshowtitle
            return url
        except:
            pass

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            url = {'tvshowtitle': url, 'season': season, 'episode': episode}
            return url
        except:
            pass

    def sources(self, url, hostDict, hostprDict):

        api_key = self.get_api()

        if not api_key:
            return

        sources = []

        try:

            content_type = 'episode' if 'tvshowtitle' in url else 'movie'
            match = 'extended'
            moderated = 'no' if content_type == 'episode' else 'yes'
            search_in = ''

            if content_type == 'movie':
                title = url['title'].replace(':', ' ').replace(' ', '+').replace('&', 'and')
                title = title.replace("'", "")
                year = url['year']
                link = '@name+%s+%s+@files+%s+%s' % (title, year, title, year)

            elif content_type == 'episode':
                title = url['tvshowtitle'].replace(':', ' ').replace(' ', '+').replace('&', 'and')
                season = int(url['season'])
                episode = int(url['episode'])
                link = self.makeQuery(title, season, episode)

            s = requests.Session()
            link = self.base_link + self.meta_search_link % \
                   (api_key, link, match, moderated, search_in, self.search_limit)

            p = s.get(link)
            p = json.loads(p.text)

            if p['status'] != 'ok':
                return

            files = p['files']

            for i in files:
                if i['is_ready'] == '1' and i['type'] == 'video':
                    try:
                        source = 'SINGLE'
                        if int(i['files_num_video']) > 3:
                            source = 'PACK [B](x%02d)[/B]' % int(i['files_num_video'])
                        file_name = i['name']
                        file_id = i['id']
                        file_dl = i['url_dl']
                        if content_type == 'episode':
                            url = '%s<>%s<>%s' % (file_id, season, episode)
                            details = self.details(file_name, i['size'], i['video_info'])
                        else:
                            url = '%s<>%s<>%s+%s' % (file_id, 'movie', title, year)
                            details = self.details(file_name, i['size'], i['video_info']).split('|')
                            details = details[0] + ' | ' + file_name.replace('.', ' ')

                        quality = source_utils.get_release_quality(file_name, file_dl)
                        sources.append({'source': source,
                                        'quality': quality[0],
                                        'language': "en",
                                        'url': url,
                                        'info': details,
                                        'direct': True,
                                        'debridonly': False})
                    except:
                        pass

                else:
                    continue

            return sources

        except:
            print("Unexpected error in Furk Script: source", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass

    def resolve(self, url):

        try:

            info = url.split('<>')
            file_id = info[0]

            self.content_type = 'movie' if info[1] == 'movie' else 'episode'

            if self.content_type == 'episode': self.filtering_list = self.seasEpQueryList(info[1], info[2])

            link = (self.base_link + self.tfile_link % (self.api_key, file_id))
            s = requests.Session()
            p = s.get(link)
            p = json.loads(p.text)

            if p['status'] != 'ok' or p['found_files'] != '1':
                return

            files = p['files'][0]
            files = files['t_files']

            for i in files:
                if 'video' not in i['ct']:
                    pass
                else: self.files.append(i)

            url = self.managePack()

            return url

        except:
            print("Unexpected error in Furk Script: resolve", sys.exc_info()[0])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            pass

    def managePack(self):

        for i in self.files:
            name = i['name']
            if self.content_type == 'movie':
                if 'is_largest' in i:
                    url = i['url_dl']
            else:
                if 'furk320' not in name.lower() and 'sample' not in name.lower():
                    for x in self.filtering_list:
                        if x in name.lower():
                            url = i['url_dl']
                        else:
                            pass
        return url

    def details(self, name, size, video_info):

        import HTMLParser, re

        name = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", name)
        name = HTMLParser.HTMLParser().unescape(name)
        name = name.replace("&quot;", "\"")
        name = name.replace("&amp;", "&")
        size = float(size) / 1073741824
        fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*)(\.|\)|\]|\s)', '', name)
        fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
        fmt = [x.lower() for x in fmt]
        if '3d' in fmt:
            q = '  | 3D'
        else:
            q = ''
        try:
            info = video_info.replace('\n', '')
            v = re.compile('Video: (.+?),').findall(info)[0]
            a = re.compile('Audio: (.+?), .+?, (.+?),').findall(info)[0]
            info = '%.2f GB%s | %s | %s | %s' % (size, q, v, a[0], a[1])
            info = re.sub('\(.+?\)', '', info)
            info = info.replace('stereo', '2.0')
            info = info.replace('eac3', 'dd+')
            info = info.replace('ac3', 'dd')
            info = info.replace('channels', 'ch')
            info = ' '.join(info.split())
            return info
        except: pass
        try:
            if any(i in ['hevc', 'h265', 'x265'] for i in fmt): v = 'HEVC'
            else: v = 'h264'
            info = '%.2f GB%s | %s' % (size, q, v)
            return info
        except: pass
        try:
            info = '%.2f GB | [I]%s[/I]' % (size, name.replace('.', ' '))
            return info
        except: pass

    def makeQuery(self, title, season, episode):
        seasEpList = self.seasEpQueryList(season, episode)
        return '@name+%s+@files+%s+|+%s+|+%s' % (title, seasEpList[0], seasEpList[1], seasEpList[2])

    def seasEpQueryList(self, season, episode):
        return ['s%02de%02d' % (int(season), int(episode)), '%dx%02d' % (int(season), int(episode)),
                '%02dx%02d' % (int(season), int(episode))]
    

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
# Addon Provider: Mr.Blamo

import re
import json
import urlparse

from openscrapers.modules import cache
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['bs.to']
        self.base_link = 'https://www.bs.to/'
        self.api_link = 'api/%s'

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            return url + "%s/%s" % (season, episode)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if not url:
                return sources

            j = self.__get_json(url)
            j = [i for i in j['links'] if 'links' in j]
            j = [(i['hoster'].lower(), i['id']) for i in j]
            j = [(re.sub('hd$', '', i[0]), i[1], 'HD' if i[0].endswith('hd') else 'SD') for i in j]
            j = [(i[0], i[1], i[2]) for i in j]

            for hoster, url, quality in j:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue
                sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': ('watch/%s' % url), 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        try: return self.__get_json(url)['fullurl']
        except: return

    def __get_json(self, api_call):
        try:
            headers = bs_finalizer().get_header(api_call)
            result = client.request(urlparse.urljoin(self.base_link, self.api_link % api_call), headers=headers)
            return json.loads(result)
        except:
            return

    def __search(self, titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = cache.get(self.__get_json, 12, "series")
            r = [(i.get('id'), i.get('series')) for i in r]
            r = [(i[0], i[1], re.findall('(.+?) \((\d{4})\)?', i[1])) for i in r if cleantitle.get(i[1]) in t]
            r = [(i[0], i[2][0][0] if len(i[2]) > 0 else i[1], i[2][0][1] if len(i[2]) > 0 else '0') for i in r]
            r = sorted(r, key=lambda i: int(i[2]), reverse=True)  # with year > no year
            r = [i[0] for i in r if i[2] in y][0]

            return 'series/%s/' % r
        except:
            return


#############################################################

import sys
import time
import json as j
import base64 as l1
import hmac as l11ll1
import hashlib as l1ll


class bs_finalizer:
    def __init__(self):
        self.l1lll1 = sys.version_info[0] == 2
        self.l11 = 26
        self.l1l1l1 = 2048
        self.l11l = 7
        self.l1l1 = False

        try:
            self.l11l1l = self.l1111(u"ࡸࡪࡾ࡞ࡨ࡙ࡹࡲࡘࡻ࠶ࡒࡈࡣࡵࡧࡈࡍࡪࡸࡻࡆࡈࡷࡩࡲࡉ࡙ࡃ࠼ࡴࡩ࠳")
            self.l1l111 = self.l1111(u"ࡋ࡝࡬࡫ࡪࡩࡱࡰࡼࡹ࠸ࡱࡳ࠵ࡷ࠳ࡋࡽ࠶ࡌ࠸ࡥ࠷ࡹࡔ࠺࡯ࡨࡤࡵࡩࡿ࠳")
        except:
            pass

    def l1111(self, ll):
        l1ll11 = ord(ll[-1]) - self.l1l1l1
        ll = ll[:-1]

        if ll:
            l111l1 = l1ll11 % len(ll)
        else:
            l111l1 = 0

        if self.l1lll1:
            l111 = u''.join([unichr(ord(l1111l) - self.l1l1l1 - (l1l11l + l1ll11) % self.l11l) for l1l11l, l1111l in
                             enumerate(ll[:l111l1] + ll[l111l1:])])
        else:
            l111 = ''.join([unichr(ord(l1111l) - self.l1l1l1 - (l1l11l + l1ll11) % self.l11l) for l1l11l, l1111l in
                            enumerate(ll[:l111l1] + ll[l111l1:])])

        if self.l1l1:
            return str(l111)
        else:
            return l111

    def get_header(self, string):
        return {self.l1111(u"ࡄࡖ࠱࡙ࡵ࡫ࡦࡰࠥ"): self.l111ll(string), self.l1111(u"ࡘࡷࡪࡸ࠭ࡂࡩࡨࡲࡹࠦ"): self.l1111(u"ࡧࡹ࠮ࡢࡰࡧࡶࡴ࡯ࡤ࠽")}

    def l111ll(self, l1lll):
        l11l11 = int(time.time())
        l11lll = {self.l1111(u"ࡱࡷࡥࡰ࡮ࡩ࡟࡬ࡧࡼࠫ"): self.l11l1l, self.l1111(u"ࡸ࡮ࡳࡥࡴࡶࡤࡱࡵࡑ"): l11l11,
                  self.l1111(u"ࡩ࡯ࡤࡧࡇ"): self.l1l11(l11l11, l1lll)}
        return l1.b64encode(j.dumps(l11lll).encode(self.l1111(u"ࡻࡴࡧ࠯࠻ࠩ")))

    def l1l11(self, l11l11, l1l1l):
        l1ll1 = self.l1l111.encode(self.l1111(u'ࡺࡺࡦ࠮࠺ࡒ'))
        l1l1ll = str(l11l11) + self.l1111(u'࠵ࠛ') + str(l1l1l)
        l1l1ll = l1l1ll.encode(self.l1111(u'ࡦࡹࡣࡪ࡫࠯'))
        l1lllll = l11ll1.new(l1ll1, l1l1ll, digestmod=l1ll.sha256)
        return l1lllll.hexdigest()

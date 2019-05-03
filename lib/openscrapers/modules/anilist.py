# -*- coding: utf-8 -*-
"""
    OpenScrapers Module

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
"""

# Addon Name: OpenScrapers Module
# Addon id: script.module.openscrapers

import urllib
import urlparse

from openscrapers.modules import cache
from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import utils


def _getAniList(url):
    try:
        url = urlparse.urljoin('https://anilist.co', '/api%s' % url)
        return client.request(url, headers={'Authorization': '%s %s' % cache.get(_getToken, 1),
                                            'Content-Type': 'application/x-www-form-urlencoded'})
    except:
        pass


def _getToken():
    result = urllib.urlencode({'grant_type': 'client_credentials', 'client_id': 'kodiexodus-7erse',
                               'client_secret': 'XelwkDEccpHX2uO8NpqIjVf6zeg'})
    result = client.request('https://anilist.co/api/auth/access_token', post=result,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'}, error=True)
    result = utils.json_loads_as_str(result)
    return result['token_type'], result['access_token']


def getAlternativTitle(title):
    try:
        t = cleantitle.get(title)

        r = _getAniList('/anime/search/%s' % title)
        r = [(i.get('title_romaji'), i.get('synonyms', [])) for i in utils.json_loads_as_str(r) if
             cleantitle.get(i.get('title_english', '')) == t]
        r = [i[1][0] if i[0] == title and len(i[1]) > 0 else i[0] for i in r]
        r = [i for i in r if i if i != title][0]
        return r
    except:
        pass

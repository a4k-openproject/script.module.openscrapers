# -*- coding: utf-8 -*-
"""
	OpenScrapers Module
"""

import json
import re

try:
	from urlparse import urljoin
except ImportError:
	from urllib.parse import urljoin

from openscrapers.modules import client
from openscrapers.modules import log_utils
from openscrapers.modules import utils

BASE_URL = 'https://api.trakt.tv'
V2_API_KEY = '42740047aba33b1f04c1ba3893ce805a9ecfebd05de544a30fe0c99fabec972e'
CLIENT_SECRET = 'c7a3e7fdf5c3863872c8f45e1d3f33797b492ed574a00a01a3fadcb3d270f926'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'


def __getTrakt(url, post=None):
	try:
		url = urljoin(BASE_URL, url)
		post = json.dumps(post) if post else None
		headers = {'Content-Type': 'application/json', 'trakt-api-key': V2_API_KEY, 'trakt-api-version': 2}
		result = client.request(url, post=post, headers=headers, output='extended', error=True)
		resp_code = result[1]
		result = result[0]
		if resp_code in ['500', '502', '503', '504', '520', '521', '522', '524']:
			log_utils.log('Temporary Trakt Error: %s' % resp_code, log_utils.LOGWARNING)
			return
		elif resp_code in ['404']:
			log_utils.log('Object Not Found : %s' % resp_code, log_utils.LOGWARNING)
			return
		elif resp_code in ['429']:
			log_utils.log('Trakt Rate Limit Reached: %s' % resp_code, log_utils.LOGWARNING)
			return
		if resp_code not in ['401', '405']:
			return result
	except Exception as e:
		log_utils.log('Unknown Trakt Error: %s' % e, log_utils.LOGWARNING)
		pass


def getTraktAsJson(url, post=None):
	try:
		r = __getTrakt(url, post)
		r = utils.json_loads_as_str(r)
		return r
	except:
		log_utils.error()
		pass


def getMovieTranslation(id, lang, full=False):
	try:
		url = '/movies/%s/translations/%s' % (id, lang)
		item = getTraktAsJson(url)[0]
		return item if full else item.get('title')
	except:
		log_utils.error()
		pass


def getTVShowTranslation(id, lang, season=None, episode=None, full=False):
	try:
		if season and episode:
			url = '/shows/%s/seasons/%s/episodes/%s/translations/%s' % (id, season, episode, lang)
		else:
			url = '/shows/%s/translations/%s' % (id, lang)
		item = getTraktAsJson(url)[0]
		return item if full else item.get('title')
	except:
		log_utils.error()
		pass


def getMovieAliases(id):
	try:
		return getTraktAsJson('/movies/%s/aliases' % id)
	except:
		return []


def getTVShowAliases(id):
	try:
		return getTraktAsJson('/shows/%s/aliases' % id)
	except:
		return []


def getGenre(content, type, type_id):
	try:
		r = '/search/%s/%s?type=%s&extended=full' % (type, type_id, content)
		r = getTraktAsJson(r)
		r = r[0].get(content, {}).get('genres', [])
		return r
	except:
		log_utils.error()
		return []
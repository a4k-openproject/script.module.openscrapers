# -*- coding: utf-8 -*-

import json
import re

try: from urlparse import urljoin, parse_qsl, urlsplit, urlparse
except ImportError: from urllib.parse import urljoin, parse_qsl, urlsplit, urlparse
try: from urllib import urlencode
except ImportError: from urllib.parse import urlencode

from openscrapers.modules import client
from openscrapers.modules import dom_parser
from openscrapers.modules import source_utils


def moonwalk(link, ref, season, episode):
	try:
		if season and episode:
			q = dict(parse_qsl(urlsplit(link).query))
			q.update({'season': season, 'episode': episode})
			q = (urlencode(q)).replace('%2C', ',')
			link = link.replace('?' + urlparse(link).query, '') + '?' + q
		trans = __get_moonwalk_translators(link, ref)
		trans = trans if trans else [(link, '')]
		urls = []
		for i in trans:
			urls += __get_moonwalk(i[0], ref, info=i[1])
		return urls
	except:
		return []


def __get_moonwalk_translators(url, ref):
	try:
		r = client.request(url, referer=ref)
		r = dom_parser.parse_dom(r, 'select', attrs={'id': 'translator'})
		r = dom_parser.parse_dom(r, 'option', req='value')
		r = [(i.attrs['value'], i.content, i.attrs.get('selected')) for i in r]
		sel_trans = [i[0] for i in r if i[2]][0]
		return [(url.replace(sel_trans, i[0]), i[1]) for i in r]
	except:
		return []


def __get_moonwalk(url, ref, info=''):
	try:
		host = urlparse(url)
		host = '%s://%s' % (host.scheme, host.netloc)
		r = client.request(url, referer=ref, output='extended')
		headers = r[3]
		headers.update({'Cookie': r[2].get('Set-Cookie')})
		r = r[0]
		csrf = re.findall('name="csrf-token" content="(.*?)"', r)[0]
		story = re.findall('''["']X-CSRF-Token["']\s*:\s*[^,]+,\s*["']([\w\-]+)["']\s*:\s*["'](\w+)["']''', r)[0]
		headers.update({'X-CSRF-Token': csrf, story[0]: story[1]})
		for i in re.findall('window\[(.*?)\]', r):
			r = r.replace(i, re.sub('''["']\s*\+\s*["']''', '', i))
		varname, post_url = re.findall('''var\s*(\w+)\s*=\s*["'](.*?/all/?)["']\s*;''', r)[0]
		jsid = re.findall('''\.post\(\s*%s\s*,\s*([^(\);)]+)''' % varname, r)[0]
		jsdata = re.findall('(?:var\s*)?%s\s*=\s*({.*?})' % re.escape(jsid), r, re.DOTALL)[0]
		jsdata = re.sub(r'([\{\s,])(\w+)(:)', r'\1"\2"\3', jsdata)
		jsdata = re.sub(r'''(?<=:)\s*\'''', ' "', jsdata)
		jsdata = re.sub(r'''(?<=\w)\'''', '"', jsdata)
		jsdata = re.sub(''':\s*\w+\s*\?[^,}]+''', ': 0', jsdata)
		jsdata = re.sub(''':\s*[a-zA-Z]+[^,}]+''', ': 0', jsdata)
		jsdata = json.loads(jsdata)
		mw_key = re.findall('''var\s*mw_key\s*=\s*["'](\w+)["']''', r)[0]
		newatt = re.findall('''%s\[["']([^=]+)["']\]\s*=\s*["']([^;]+)["']''' % re.escape(jsid), r)[0]
		newatt = [re.sub('''["']\s*\+\s*["']''', '', i) for i in newatt]
		jsdata.update({'mw_key': mw_key, newatt[0]: newatt[1]})
		r = client.request(urljoin(host, post_url), post=jsdata, headers=headers, XHR=True)
		r = json.loads(r).get('mans', {}).get('manifest_m3u8')
		r = client.request(r, headers=headers)
		r = [(i[0], i[1]) for i in
		     re.findall('#EXT-X-STREAM-INF:.*?RESOLUTION=\d+x(\d+).*?(http.*?(?:\.abst|\.f4m|\.m3u8)).*?', r, re.DOTALL)
		     if i]
		r = [(source_utils.label_to_quality(i[0]), i[1] + '|%s' % urlencode(headers)) for i in r]
		r = [{'quality': i[0], 'url': i[1], 'info': info} for i in r]
		return r
	except:
		return []

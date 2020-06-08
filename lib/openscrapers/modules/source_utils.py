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


import base64
import hashlib
import re
try: from urlparse import urlparse
except ImportError: from urllib.parse import urlparse

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import directstream
from openscrapers.modules import log_utils
from openscrapers.modules import pyaes


RES_4K = ['.4k', 'hd4k', '4khd', 'uhd', 'ultrahd', 'ultra-hd', '2160', '2160p', '2160i', 'hd2160', '2160hd',
		  '1716p', '1716i', 'hd1716', '1716hd', '2664p', '2664i', 'hd2664', '2664hd', '3112p',
		  '3112i', 'hd3112', '3112hd', '2880p', '2880i', 'hd2880', '2880hd']
RES_1080 = ['1080', '1080p', '1080i', 'hd1080', '1080hd', '1200p', '1200i', 'hd1200', '1200hd']
RES_720 = ['720', '720p', '720i', 'hd720', '720hd', 'hdtv', '.hd.']
RES_SD = ['576', '576p', '576i', 'sd576', '576sd', '480', '480p', '480i', 'sd480', '480sd', '360', '360p',
		  '360i', 'sd360', '360sd', '240', '240p', '240i', 'sd240', '240sd']

SCR = ['dvdscr', 'screener', '.scr.', 'r5', 'r6']

CAM = ['camrip', 'cam.rip', 'tsrip', '.ts.rip.', 'dvdcam', 'dvd.cam', 'dvdts', 'dvd.ts.', 'cam', 'telesync', 'tele.sync']
HDCAM = ['hdcam', '.hd.cam.', 'hdts', '.hd.ts.', '.hdtc.', '.hd.tc.']

CODEC_H265 = ['hevc', 'h265', 'h.265', 'x265', 'x.265']
CODEC_H264 = ['avc', 'h264', 'h.264', 'x264', 'x.264']
CODEC_XVID = ['xvid', 'x.vid', 'x-vid']
CODEC_DIVX = ['divx', 'divx ', 'div2', 'div2 ', 'div3']
CODEC_MPEG = ['mp4', 'mpeg', 'm4v', 'mpg', 'mpg1', 'mpg2', 'mpg3', 'mpg4', 'mp4 ', 'msmpeg', 'msmpeg4',
			  'mpegurl']
CODEC_AVI = ['avi']
CODEC_MKV = ['mkv', '.mkv', 'matroska']

AUDIO_8CH = ['ch8', '8ch', '7.1', '7-1']
AUDIO_7CH = ['ch7', '7ch', '6.1', '6-1']
AUDIO_6CH = ['ch6', '6ch', '5.1', '5-1']
AUDIO_2CH = ['ch2', '2ch', '2.0', 'stereo']
AUDIO_1CH = ['ch1', '1ch', 'mono', 'monoaudio']

VIDEO_3D = ['3d', 'sbs', 'hsbs', 'sidebyside', 'side.by.side', 'stereoscopic', 'tab', 'htab', 'topandbottom',
			'top.and.bottom']

MULTI_LANG = ['hindi.eng', 'ara.eng', 'ces.eng', 'chi.eng', 'cze.eng', 'dan.eng', 'dut.eng', 'ell.eng', 'esl.eng',
			  'esp.eng', 'fin.eng', 'fra.eng', 'fre.eng', 'frn.eng', 'gai.eng', 'ger.eng', 'gle.eng', 'gre.eng',
			  'gtm.eng', 'heb.eng', 'hin.eng', 'hun.eng', 'ind.eng', 'iri.eng', 'ita.eng', 'jap.eng', 'jpn.eng', 'kor.eng',
			  'lat.eng', 'lebb.eng', 'lit.eng', 'nor.eng', 'pol.eng', 'por.eng', 'rus.eng', 'som.eng', 'spa.eng', 'sve.eng',
			  'swe.eng', 'tha.eng', 'tur.eng', 'uae.eng', 'ukr.eng', 'vie.eng', 'zho.eng', 'dual.audio', 'multi']

LANG = ['arabic', 'bgaudio', 'dutch', 'finnish', 'french', 'german', 'greek', 'italian', 'latino', 'polish', 'portuguese',
			  'russian', 'spanish', 'truefrech', 'truespanish', 'turkish', 'hebrew']

UNDESIREABLES = ['alexfilm', 'baibako', 'bonus.disc', 'coldfilm', 'eniahd', 'extras.only', 'gears media', 'jaskier', 'hamsterstudio',
			  'ideafilm', 'kerob', 'lakefilm', 'lostfilm', 'newstudio', 'profix media', 'sample', 'soundtrack', 'subtitle.only', 'teaser', 'vostfr']

DUBBED = ['dublado', 'dubbed']
SUBS = ['subs', 'subtitula', 'subfrench', 'subspanish', 'swesub']
ADDS = ['1xbet', 'betwin']


def get_qual(term):
	if any(i in term for i in RES_4K):
		return '4K'
	elif any(i in term for i in RES_1080):
		return '1080p'
	elif any(i in term for i in RES_720):
		return '720p'
	elif any(i in term for i in RES_SD):
		return 'SD'
	elif any(i in term for i in SCR):
		return 'SCR'
	elif any(i in term for i in CAM):
		return 'CAM'
	elif any(i in term for i in HDCAM):
		return 'CAM'


def is_anime(content, type, type_id):
	from openscrapers.modules import trakt
	try:
		r = trakt.getGenre(content, type, type_id)
		return 'anime' in r or 'animation' in r
	except:
		return False


def get_release_quality(release_name, release_link=None):
	if release_name is None:
		return
	try:
		release_name = release_name.encode('utf-8')
	except:
		pass
	try:
		quality = None
		release_name = release_name.upper()
		fmt = re.sub('(.+)(\d{4}|S\d+E\d+)(\.|\)\.|\)|\]\.|\]|\s)', '', release_name)
		# log_utils.log('fmt = %s' % fmt, log_utils.LOGDEBUG)
		fmt = fmt.lower()
		quality = get_qual(fmt)
		if not quality:
			if release_link:
				release_link = release_link.lower()
				try:
					release_link = release_link.encode('utf-8')
				except:
					pass
				quality = get_qual(release_link)
				if not quality:
					quality = 'SD'
			else:
				quality = 'SD'

		info = []
		if any(value in fmt for value in VIDEO_3D):
			info.append('3D')

		if any(value in fmt for value in CODEC_H265):
			info.append('HEVC')

		return quality, info
	except:
		log_utils.error()
		return 'SD', []


def getFileType(url):
	try:
		url = url.lower()
		url = url.replace(' ', '.')
	except:
		url = str(url)
	type = ''
	if any(value in url for value in ['bluray', 'blu-ray', 'blu.ray']):
		type += ' BLURAY /'
	if any(value in url for value in ['bd-r', 'bd.r', 'bdr', 'bd-rip', 'bd.rip', 'bdrip', 'brrip', 'br.rip']):
		type += ' BR-RIP /'
	if 'remux' in url:
		type += ' REMUX /'
	if any(i in url for i in ['dvd-rip', 'dvd.rip', 'dvdrip']):
		type += ' DVD /'
	if any(value in url for value in ['web-dl', 'web.dl', 'webdl', 'web-rip', 'web.rip', 'webrip']):
		type += ' WEB /'
	if 'hdtv' in url:
		type += ' HDTV /'
	if 'sdtv' in url:
		type += ' SDTV /'
	if any(value in url for value in ['hd-rip', 'hd.rip', 'hdrip']):
		type += ' HDRIP /'
	if 'hdr.' in url:
		type += ' HDR /'
	if any(value in url for value in ['dd5.1', 'dd-5.1', 'dolby-digital', 'dolby.digital']):
		type += ' DOLBYDIGITAL /'
	if any(value in url for value in ['.ddex', 'dd-ex', 'dolby-ex', 'dolby.digital.ex']):
		type += ' DD-EX /'
	if any(value in url for value in ['dolby-digital-plus', 'dolby.digital.plus', 'ddplus', 'dd-plus']):
		type += ' DD+ /'
	if any(value in url for value in ['true-hd', 'truehd', '.ddhd']):
		type += ' DOLBY-TRUEHD /'
	if 'atmos' in url:
		type += ' ATMOS /'
	if '.dts.' in url:
		type += ' DTS /'
	if any(value in url for value in ['dts-hd', 'dtshd', 'dts.hd']):
		type += ' DTS-HD /'
	if any(value in url for value in ['dts-es', 'dtses', 'dts.es']):
		type += ' DTS-ES /'
	if any(value in url for value in ['dts-neo', 'dtsneo', 'dts.neo']):
		type += ' DTS-NEO /'
	if '.thx.' in url:
		type += ' THX /'
	if any(value in url for value in ['.thx-ex', 'thxex']):
		type += ' THX-EX /'
	if any(value in url for value in AUDIO_8CH):
		type += ' 8CH /'
	if any(value in url for value in AUDIO_7CH):
		type += ' 7CH /'
	if any(value in url for value in AUDIO_6CH):
		type += ' 6CH /'
	if 'xvid' in url:
		type += ' XVID /'
	if 'divx' in url:
		type += ' DIVX /'
	if any(value in url for value in CODEC_MPEG):
		type += ' MPEG /'
	if '.avi' in url:
		type += ' AVI /'
	if 'ac3' in url:
		type += ' AC3 /'
	if any(value in url for value in CODEC_H264):
		type += ' X264 /'
	if any(value in url for value in CODEC_H265):
		type += ' X265 /'
	if any(value in url for value in CODEC_MKV):
		type += ' MKV /'
	if any(value in url for value in HDCAM):
		type += ' HDCAM /'
	if any(value in url for value in MULTI_LANG):
		type += ' MULTI-LANG /'
	if any(value in url for value in ADDS):
		type += ' ADDS /'
	if any(value in url for value in SUBS):
		if type != '':
			type += ' WITH SUBS'
		else:
			type = 'SUBS'
	type = type.rstrip('/')
	return type


def check_url(url):
	try:
		url = url.lower()
		try:
			url = url.encode('utf-8')
		except:
			pass
		quality = get_qual(url)
		if not quality:
			quality = 'SD'
		return quality
	except:
		log_utils.error()
		return 'SD'


def check_title(title, name, hdlr, year):
	try:
		match = True
		title = title.replace('!', '')
		n = name.lower()
		h = hdlr.lower()
		t = n.split(h)[0].replace(year, '').replace('(', '').replace(')', '').replace('&', 'and').replace('.us.', '.')
		# log_utils.log('cleantitle.get(t) = %s' % cleantitle.get(t), log_utils.LOGDEBUG)
		# log_utils.log('cleantitle.get(title) = %s' % cleantitle.get(title), log_utils.LOGDEBUG)
		if cleantitle.get(t) != cleantitle.get(title):
			match = False
		if h not in n:
			match = False
		return match
	except:
		log_utils.error()
		match = False


def label_to_quality(label):
	try:
		try:
			label = int(re.search('(\d+)', label).group(1))
		except:
			label = 0
		if label >= 2160:
			return '4K'
		elif 1920 <= label:
			return '1080p'
		elif 1280 <= label:
			return '720p'
		elif label <= 576:
			return 'SD'
	except:
		log_utils.error()
		return 'SD'


def strip_domain(url):
	try:
		if url.lower().startswith('http') or url.startswith('/'):
			url = re.findall('(?://.+?|)(/.+)', url)[0]
		url = client.replaceHTMLCodes(url)
		url = url.encode('utf-8')
		return url
	except:
		log_utils.error()
		return


def is_host_valid(url, domains):
	try:
		if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.']) or any(
				url.lower().endswith(x) for x in ['.rar', '.zip', '.iso']):
			return False, ''
		host = __top_domain(url)
		hosts = [domain.lower() for domain in domains if host and host in domain.lower()]
		if hosts and '.' not in host:
			host = hosts[0]
		if hosts and any([h for h in ['google', 'picasa', 'blogspot'] if h in host]):
			host = 'gvideo'
		if hosts and any([h for h in ['akamaized', 'ocloud'] if h in host]):
			host = 'CDN'
		return any(hosts), host
	except:
		log_utils.error()
		return False, ''


def __top_domain(url):
	elements = urlparse(url)
	domain = elements.netloc or elements.path
	domain = domain.split('@')[-1].split(':')[0]
	regex = "(?:www\.)?([\w\-]*\.[\w\-]{2,3}(?:\.[\w\-]{2,3})?)$"
	res = re.search(regex, domain)
	if res:
		domain = res.group(1)
	domain = domain.lower()
	return domain


def aliases_to_array(aliases, filter=None):
	try:
		if not filter:
			filter = []
		if isinstance(filter, str):
			filter = [filter]
		return [x.get('title') for x in aliases if not filter or x.get('country') in filter]
	except:
		log_utils.error()
		return []


def _size(siz):
	if siz in ['0', 0, '', None]: return 0, ''
	div = 1 if siz.lower().endswith(('gb', 'gib')) else 1024
	float_size = float(re.sub('[^0-9|/.|/,]', '', siz.replace(',', ''))) / div
	str_size = '%.2f GB' % float_size
	return float_size, str_size


def get_size(url): # not called
	try:
		size = client.request(url, output='file_size')
		# size = client.request(url, output='chunk')
		if size == '0':
			size = False
		float_size, str_size = convert_size(size)
		return float_size, str_size
	except:
		log_utils.error()
		return False


def convert_size(size_bytes, to='GB'):
	try:
		import math
		if size_bytes == 0:
			return 0, ''
		power = {'B' : 0, 'KB': 1, 'MB' : 2, 'GB': 3, 'TB' : 4, 'EB' : 5, 'ZB' : 6, 'YB': 7}
		i = power[to]
		p = math.pow(1024, i)
		float_size = round(size_bytes / p, 2)
		# if to == 'B' or to  == 'KB':
			# return 0, ''
		str_size = "%s %s" % (float_size, to)
		return float_size, str_size
	except:
		log_utils.error()
		return 0, ''


def check_directstreams(url, hoster='', quality='SD'):
	urls = []
	host = hoster
	if 'google' in url or any(x in url for x in ['youtube.', 'docid=']):
		urls = directstream.google(url)
		if not urls:
			tag = directstream.googletag(url)
			if tag:
				urls = [{'quality': tag[0]['quality'], 'url': url}]
		if urls:
			host = 'gvideo'
	elif 'ok.ru' in url:
		urls = directstream.odnoklassniki(url)
		if urls:
			host = 'vk'
	elif 'vk.com' in url:
		urls = directstream.vk(url)
		if urls:
			host = 'vk'
	elif any(x in url for x in ['akamaized', 'blogspot', 'ocloud.stream']):
		urls = [{'url': url}]
		if urls: host = 'CDN'
	direct = True if urls else False
	if not urls:
		urls = [{'quality': quality, 'url': url}]
	return urls, host, direct


def evp_decode(cipher_text, passphrase, salt=None):
	cipher_text = base64.b64decode(cipher_text)
	if not salt:
		salt = cipher_text[8:16]
		cipher_text = cipher_text[16:]
	data = evpKDF(passphrase, salt)
	decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(data['key'], data['iv']))
	plain_text = decrypter.feed(cipher_text)
	plain_text += decrypter.feed()
	return plain_text


def evpKDF(passwd, salt, key_size=8, iv_size=4, iterations=1, hash_algorithm="md5"):
	target_key_size = key_size + iv_size
	derived_bytes = ""
	number_of_derived_words = 0
	block = None
	hasher = hashlib.new(hash_algorithm)
	while number_of_derived_words < target_key_size:
		if block is not None:
			hasher.update(block)
		hasher.update(passwd)
		hasher.update(salt)
		block = hasher.digest()
		hasher = hashlib.new(hash_algorithm)
		for _i in range(1, iterations):
			hasher.update(block)
			block = hasher.digest()
			hasher = hashlib.new(hash_algorithm)
		derived_bytes += block[0: min(len(block), (target_key_size - number_of_derived_words) * 4)]
		number_of_derived_words += len(block) / 4
	return {"key": derived_bytes[0: key_size * 4], "iv": derived_bytes[key_size * 4:]}


def remove_lang(name):
	try:
		name = name.lower()
		name = name.replace(' ', '.')
	except:
		name = str(name)
	if any(value in name for value in LANG):
		return True
	elif any(value in name for value in UNDESIREABLES):
		return True
	elif name.endswith('.srt') and not any(value in name for value in ['with.srt', '.avi', '.mkv', '.mp4']):
		return True
	elif any(value in name for value in DUBBED):
		return True
	elif 'rus' in name and 'eng' not in name:
		return True
	else:
		return False


def scraper_error(provider):
	import traceback
	failure = traceback.format_exc()
	log_utils.log(provider.upper() + ' - Exception: \n' + str(failure), log_utils.LOGDEBUG)


def timeIt(func):
	import time
	fnc_name = func.__name__
	def wrap(*args, **kwargs):
		started_at = time.time()
		result = func(*args, **kwargs)
		log_utils.log('%s.%s = %s' % (__name__ , fnc_name, time.time() - started_at), log_utils.LOGDEBUG)
		return result
	return wrap
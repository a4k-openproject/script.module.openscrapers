# -*- coding: utf-8 -*-
"""
	OpenScrapers Module
"""

import base64
import hashlib
import json
import re
import string

try:
	from urllib import unquote_plus
	from urlparse import urlparse
except ImportError:
	from urllib.parse import urlparse, unquote_plus

from openscrapers.modules import cleantitle
from openscrapers.modules import client
from openscrapers.modules import control
from openscrapers.modules import directstream
from openscrapers.modules import log_utils
from openscrapers.modules import pyaes


RES_4K = ['.4k', 'hd4k', '4khd', 'uhd', 'ultrahd', 'ultra.hd', '2160', '2160p', '2160i', 'hd2160', '2160hd',
		  '1716p', '1716i', 'hd1716', '1716hd', '2664p', '2664i', 'hd2664', '2664hd', '3112p',
		  '3112i', 'hd3112', '3112hd', '2880p', '2880i', 'hd2880', '2880hd']
RES_1080 = ['1080', '1080p', '1080i', 'hd1080', '1080hd', '1200p', '1200i', 'hd1200', '1200hd']
RES_720 = ['720', '720p', '720i', 'hd720', '720hd', 'hdtv', '.hd.']
RES_SD = ['576', '576p', '576i', 'sd576', '576sd', '480', '480p', '480i', 'sd480', '480sd', '360', '360p',
		  '360i', 'sd360', '360sd', '240', '240p', '240i', 'sd240', '240sd']

SCR = ['dvdscr', 'screener', '.scr.', 'r5', 'r6']

CAM = ['camrip', 'cam.rip', 'tsrip', '.ts.rip.', 'dvdcam', 'dvd.cam', 'dvdts', 'dvd.ts.', 'cam', 'telesync', 'tele.sync']
HDCAM = ['hdcam', '.hd.cam.', 'hdts', '.hd.ts.', '.hdtc.', '.hd.tc.', '.hctc.', 'hc.tc.']

CODEC_H265 = ['hevc', 'h265', 'h.265', 'x265', 'x.265']
CODEC_H264 = ['avc', 'h264', 'h.264', 'x264', 'x.264']
CODEC_XVID = ['xvid', '.x.vid']
CODEC_DIVX = ['divx', 'divx ', 'div2', 'div2 ', 'div3']
CODEC_MPEG = ['mpeg', 'm4v', 'mpg', 'mpg1', 'mpg2', 'mpg3', 'mpg4', 'mp4 ', '.mp.4.', 'msmpeg', 'msmpeg4',
			  'msmpeg.4.', 'mpegurl']
CODEC_MKV = ['mkv', '.mkv', 'matroska']

AUDIO_8CH = ['ch8.', '8ch.', '.7.1.']
AUDIO_7CH = ['ch7.', '7ch.', '.6.1.']
AUDIO_6CH = ['ch6.', '6ch.', '.5.1.']
AUDIO_2CH = ['ch2', '2ch', '2.0', 'audio.2.0.', 'stereo']

VIDEO_3D = ['3d', 'sbs', 'hsbs', 'sidebyside', 'side.by.side', 'stereoscopic', 'tab', 'htab', 'topandbottom',
			'top.and.bottom']

MULTI_LANG = ['hindi.eng', 'ara.eng', 'ces.eng', 'chi.eng', 'cze.eng', 'dan.eng', 'dut.eng', 'ell.eng', 'esl.eng',
			  'esp.eng', 'fin.eng', 'fra.eng', 'fre.eng', 'frn.eng', 'gai.eng', 'ger.eng', 'gle.eng', 'gre.eng',
			  'gtm.eng', 'heb.eng', 'hin.eng', 'hun.eng', 'ind.eng', 'iri.eng', 'ita.eng', 'jap.eng', 'jpn.eng', 'kor.eng',
			  'lat.eng', 'lebb.eng', 'lit.eng', 'nor.eng', 'pol.eng', 'por.eng', 'rus.eng', 'som.eng', 'spa.eng', 'sve.eng',
			  'swe.eng', 'tha.eng', 'tur.eng', 'uae.eng', 'ukr.eng', 'vie.eng', 'zho.eng', 'dual.audio', 'multi']

LANG = ['arabic', 'bgaudio', 'castellano', 'chinese', 'dutch', 'finnish', 'french', 'german', 'greek', 'italian', 'latino', 'polish', 'portuguese',
			  'russian', 'spanish', 'tamil', 'telugu', 'truefrench', 'truespanish', 'turkish', 'hebrew']

ABV_LANG = ['.chi.', '.chs.', '.dut.', '.fin.', '.fre.', '.ger.', '.gre.', '.heb.', '.ita.', '.jpn.', '.pol.', '.por.', '.rus.', '.spa.', '.tur.', '.ukr.']

UNDESIREABLES = ['400p.octopus', '720p.octopus', '1080p.octopus', 'alexfilm', 'baibako', 'bonus.disc',
			  'courage.bambey', '.cbr', '.cbz', 'coldfilm', 'dilnix', 'dlrip', 'dutchreleaseteam', 'e.book.collection', 'empire.minutemen', 'eniahd',
			  '.exe', 'extras.only', 'gears.media', 'gearsmedia', 'hamsterstudio', 'hdrezka', 'hdtvrip', 'idea.film', 'ideafilm',
			  'jaskier', 'kb.1080p', 'kb.720p', 'kb.400p', 'kerob', 'kinokopilka', 'kravec', 'kuraj.bambey', 'lakefilm', 'lostfilm',
			  'megapeer', 'minutemen.empire', 'omskbird', 'newstudio', 'paravozik', 'profix.media', 'rifftrax', 'sample',
			  'soundtrack', 'subtitle.only', 'teaser', 'trailer', 'tumbler.studio', 'tvshows', 'vostfr', 'webdlrip', 'webhdrip', 'wish666']

DUBBED = ['dublado', 'dubbed']
SUBS = ['subita', 'subfrench', 'subs', 'subspanish', 'subtitula', 'swesub']
ADDS = ['1xbet', 'betwin']

season_list = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eigh', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
			'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'twenty-one', 'twenty-two', 'twenty-three',
			'twenty-four', 'twenty-five']

season_ordinal_list = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh', 'twelfth',
			'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth', 'twenty-first',
			'twenty-second', 'twenty-third', 'twenty-fourth', 'twenty-fifth']

season_ordinal2_list = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th', '16th',
			'17th', '18th', '19th', '20th', '21st', '22nd', '23rd', '24th', '25th']

season_dict = {'1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven', '8': 'eigh', '9': 'nine', '10': 'ten',
			'11': 'eleven', '12': 'twelve', '13': 'thirteen', '14': 'fourteen', '15': 'fifteen', '16': 'sixteen', '17': 'seventeen',
			'18': 'eighteen', '19': 'nineteen', '20': 'twenty', '21': 'twenty-one', '22': 'twenty-two', '23': 'twenty-three',
			'24': 'twenty-four', '25': 'twenty-five'}

season_ordinal_dict = {'1': 'first', '2': 'second', '3': 'third', '4': 'fourth', '5': 'fifth', '6': 'sixth', '7': 'seventh', '8': 'eighth', '9': 'ninth',
			'10': 'tenth', '11': 'eleventh', '12': 'twelfth', '13': 'thirteenth', '14': 'fourteenth', '15': 'fifteenth', '16': 'sixteenth',
			'17': 'seventeenth', '18': 'eighteenth', '19': 'nineteenth', '20': 'twentieth', '21': 'twenty-first', '22': 'twenty-second',
			'23': 'twenty-third', '24': 'twenty-fourth', '25': 'twenty-fifth'}

season_ordinal2_dict = {'1': '1st', '2': '2nd', '3': '3rd', '4': '4th', '5': '5th', '6': '6th', '7': '7th', '8': '8th', '9': '9th', '10': '10th',
			'11': '11th', '12': '12th', '13': '13th', '14': '14th', '15': '15th', '16': '16th', '17': '17th', '18': '18th', '19': '19th',
			'20': '20th', '21': '21st', '22': '22nd', '23': '23rd', '24': '24th', '25': '25th'}



def is_anime(content, type, type_id):
	from openscrapers.modules import trakt
	try:
		r = trakt.getGenre(content, type, type_id)
		return 'anime' in r or 'animation' in r
	except:
		log_utils.error()
		return False


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


def get_release_quality(release_title, release_link=None):
	try:
		quality = None
		fmt = release_title_strip(release_title)
		if fmt is not None:
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
		if fmt is not None:
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
		type = ''
		fmt = url_strip(url)
		if fmt is None:
			return type
		if any(value in fmt for value in ['blu.ray', 'bluray', '.bd.']):
			type += ' BLURAY /'
		if any(value in fmt for value in ['bd.r', 'bdr', 'bd.rip', 'bdrip', 'br.rip', 'brrip']):
			type += ' BR-RIP /'
		if 'remux' in fmt:
			type += ' REMUX /'
		if any(i in fmt for i in ['dvd.rip', 'dvdrip']):
			type += ' DVD /'
		if any(value in fmt for value in ['web.dl', 'webdl', 'web.rip', 'webrip']):
			type += ' WEB /'
		if 'hdtv' in fmt:
			type += ' HDTV /'
		if 'sdtv' in fmt:
			type += ' SDTV /'
		if any(value in fmt for value in ['hd.rip', 'hdrip']):
			type += ' HDRIP /'
		if 'hdr.' in fmt:
			type += ' HDR /'
		if any(value in fmt for value in ['dd.5.1.', 'dd.5.1ch.', 'dd5.1.', 'dolby.digital', 'dolbydigital']):
			type += ' DOLBYDIGITAL /'
		if any(value in fmt for value in ['.dd.ex.', 'ddex', 'dolby.ex.', 'dolby.digital.ex.', 'dolbydigital.ex.']):
			type += ' DD-EX /'
		if any(value in fmt for value in ['dolby.digital.plus', 'dolbydigital.plus', 'dolbydigitalplus', 'dd.plus.', 'ddplus']):
			type += ' DD+ /'
		if any(value in fmt for value in ['dd.7.1ch', 'dd.true.hd.', 'dd.truehd', 'ddtruehd']):
			type += ' DOLBY-TRUEHD /'
		if 'atmos' in fmt:
			type += ' ATMOS /'
		if '.dts.' in fmt:
			type += ' DTS /'
		if any(value in fmt for value in ['dts.hd.', 'dtshd']):
			type += ' DTS-HD /'
		if any(value in fmt for value in ['dts.hd.ma.', 'dtshd.ma.', 'dtshdma', '.hd.ma.', 'hdma']):
			type += ' DTS-HD MA/'
		if any(value in fmt for value in ['dts.x.', 'dtsx']):
			type += ' DTS-X /'
		if any(value in fmt for value in AUDIO_8CH):
			type += ' 8CH /'
		if any(value in fmt for value in AUDIO_7CH):
			type += ' 7CH /'
		if any(value in fmt for value in AUDIO_6CH):
			type += ' 6CH /'
		if any(value in fmt for value in AUDIO_2CH):
			type += ' 2CH /'
		if any(value in fmt for value in CODEC_XVID):
			type += ' XVID /'
		if any(value in fmt for value in CODEC_DIVX):
			type += ' DIVX /'
		if any(value in fmt for value in CODEC_MPEG):
			type += ' MPEG /'
		if '.avi' in fmt:
			type += ' AVI /'
		if any(value in fmt for value in ['.ac3', '.ac.3.']):
			type += ' AC3 /'
		if any(value in fmt for value in CODEC_H264):
			type += ' X264 /'
		if any(value in fmt for value in CODEC_H265):
			type += ' X265 /'
		if any(value in fmt for value in CODEC_MKV):
			type += ' MKV /'
		if any(value in fmt for value in HDCAM):
			type += ' HDCAM /'
		if any(value in fmt for value in MULTI_LANG):
			type += ' MULTI-LANG /'
		if any(value in fmt for value in ADDS):
			type += ' ADDS /'
		if any(value in fmt for value in SUBS):
			if type != '':
				type += ' WITH SUBS'
			else:
				type = 'SUBS'
		type = type.rstrip('/')
		return type
	except:
		log_utils.error()
		return ''


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


def aliases_to_array(aliases, filter=None):
	try:
		if all(isinstance(x, str) for x in aliases):
			return aliases
		if not filter:
			filter = []
		if isinstance(filter, str):
			filter = [filter]
		return [x.get('title') for x in aliases if not filter or x.get('country') in filter]
	except:
		log_utils.error()
		return []


def check_title(title, aliases, release_title, hdlr, year):
	try:
		aliases = json.loads(aliases)
		aliases = aliases_to_array(aliases)
	except:
		aliases = None

	# log_utils.log('aliases = %s' % str(aliases), __name__, log_utils.LOGDEBUG)
	# log_utils.log('aliases type = %s' % type(aliases), __name__, log_utils.LOGDEBUG)

	title_list = []
	if aliases:
		for item in aliases:
			alias = item.replace('!', '').replace('(', '').replace(')', '')
			# alias = re.sub(r'[^A-Za-z0-9\s\.-]+', '', item)
			for match in re.finditer(r'(.+?)(U\.S|U\.K)', alias):
				alias = match.group(1) + match.group(2).replace('.', '')
				title_list.append(alias)

	try:
		release_title = release_title_format(release_title)
		match = True
		title = title.replace('!', '').replace('(', '').replace(')', '')
		# title = re.sub(r'[^A-Za-z0-9\s\.-]+', '', title)
		title_list.append(title)
		n = release_title
		h = hdlr.lower()
		t = n.split(h)[0].replace(year, '').replace('(', '').replace(')', '').replace('&', 'and')
		if all(cleantitle.get(i) != cleantitle.get(t) for i in title_list):
			match = False
		if h not in n:
			match = False

		return match
	except:
		log_utils.error()
		match = False


def remove_lang(release_title, episode_title=None):
	try:
		fmt = release_title_strip(release_title)
		if fmt is None:
			return False
		# log_utils.log('fmt = %s for release_title = %s' % (str(fmt), str(release_title)), __name__, log_utils.LOGDEBUG)
		if episode_title:
			episode_title = episode_title.lower().replace("'", "")
			episode_title = re.sub('[^a-z0-9]+', '.', episode_title)
			fmt = '%s' % re.sub(episode_title, '', fmt)

		filter_undesirables = control.setting('filter.undesirables') == 'true'
		filter_foreign_single_audio = control.setting('filter.foreign.single.audio') == 'true'

		if filter_undesirables:
			if any(value in fmt for value in UNDESIREABLES):
				return True
		if any(value in fmt for value in DUBBED):
			return True
		if any(value in fmt for value in SUBS):
			return True
		# if any(value in fmt for value in ADDS):
			# return True
		if filter_foreign_single_audio:
			if any(value in fmt for value in LANG) and not any(value in fmt for value in ['.eng.', '.en.', 'english']):
				return True
			if any(value in fmt for value in ABV_LANG) and not any(value in fmt for value in ['.eng.', '.en.', 'english']):
				return True
		if fmt.endswith('.srt.') and not any(value in fmt for value in ['with.srt', '.avi', '.mkv', '.mp4']):
			return True
		return False
	except:
		log_utils.error()
		return False


# removes multi epsiode ranges returned from single epsiode query (ex. S01E01-E17 is also returned in S01E01 query)
def filter_single_episodes(hdlr, release_title):
	try:
		fmt = release_title_format(release_title)
		se = hdlr.lower()
		for item in [(se + r'(?:\.|-)e\d{1,2}(?:$|\.|-)'), (se + r'(?:\.|-)s[0-3]{1}[0-9]{1}e\d{1,2}(?:$|\.|-)'), (se + r'-\d{2}(?:$|\.|-)')]:
			if bool(re.search(item, fmt)):
				return False
		return True
	except:
		log_utils.error()
		return True


def filter_season_pack(show_title, aliases, year, season, release_title):
	try:
		try:
			aliases = json.loads(aliases)
			aliases = aliases_to_array(aliases, filter=None)
		except:
			aliases = None

		title_list = []
		if aliases:
			for item in aliases:
				alias = item.replace('!', '').replace('(', '').replace(')', '')
				# alias = re.sub(r'[^A-Za-z0-9\s\.-]+', '', item)
				for match in re.finditer(r'(.+?)(U\.S|U\.K)', alias):
					alias = match.group(1) + match.group(2).replace('.', '')
					title_list.append(alias)

		release_title = release_title_format(release_title)
		show_title = show_title.replace('!', '').replace('(', '').replace(')', '')
		title_list.append(show_title)

		season_fill = season.zfill(2)
		season_check = '.s%s.' % season
		season_fill_check = '.s%s.' % season_fill
		season_full_check = '.season.%s.' % season
		season_full_check_ns = '.season%s.' % season
		season_full_fill_check = '.season.%s.' % season_fill
		season_full_fill_check_ns = '.season%s.' % season_fill

		string_list = [season_check, season_fill_check, season_full_check, season_full_check_ns, season_full_fill_check, season_full_fill_check_ns]

		split_list = [season_check, season_fill_check, '.' + season + '.season', 'total.season', 'season', 'the.complete', 'complete', year]
		t = release_title.replace('-', '.')
		for i in split_list:
			t = t.split(i)[0]

		# log_utils.log('t = %s for release_title = %s' % (str(t), str(release_title)), __name__, log_utils.LOGDEBUG)
		if all(cleantitle.get(i) != cleantitle.get(t) for i in title_list):
			return False


# remove episode ranges
		episode_list = [
				r's\d{1,3}(?:\.|-)e\d{1,3}',
				r's\d{1,3}(?:\.|-)\d{1,3}e\d{1,3}',
				r's[0-3]{1}[0-9]{1}e\d{1,2}',
				r'season(?:\.|-)\d{1,2}(?:\.{0,1}|-{0,1})episode(?:\.|-)\d{1,2}',
				r'season(?:\.|-)\d{1,3}(?:\.|-)ep(?:\.|-)\d{1,3}']
		for item in episode_list:
			if bool(re.search(item, release_title)):
				return False

# remove season ranges - returned in showPack scrape, plus non conforming season and specific crap
		rt = release_title.replace('-', '.')
		if any(i in rt for i in string_list):
			for item in [
				season_check.rstrip('.') + r'(?:\.|-)s\d{1}(?:$|\.|-)', # ex. ".s1-s9"
				season_fill_check.rstrip('.') + r'(?:\.|-)s\d{2}(?:$|\.|-)', # ".s01-s09."
				season_fill_check.rstrip('.') + r'(?:\.|-)\d{2}(?:$|\.|-)', # ".s01.09."
				r'\Ws\d{2}\W%s' % season_fill_check.lstrip('.'), # may need more reverse ranges
				season_full_check.rstrip('.') + r'(?:\.|-)to(?:\.|-)\d{1}(?:$|\.|-)', # "season.1.to.9."
				season_full_check.rstrip('.') + r'(?:\.|-)season(?:\.|-)\d{1}(?:$|\.|-)', # "season.1.season.9."
				season_full_check.rstrip('.') + r'(?:\.|-)\d{1}(?:$|\.|-)', # "season.1.9."
				season_full_check.rstrip('.') + r'(?:\.|-)\d{1}(?:\.|-)\d{1,2}(?:$|\.|-)',
				season_full_check.rstrip('.') + r'(?:\.|-)\d{3}(?:\.|-)(?:19|20)[0-9]{2}(?:$|\.|-)',# single season followed by 3 digit followed by 4 digit year ex."season.1.004.1971"
				season_full_fill_check.rstrip('.') + r'(?:\.|-)\d{3}(?:\.|-)\d{3}(?:$|\.|-)',# 2 digit season followed by 3 digit dash range ex."season.10.001-025."
				season_full_fill_check.rstrip('.') + r'(?:\.|-)season(?:\.|-)\d{2}(?:$|\.|-)' # 2 digit season followed by 2 digit season range ex."season.01-season.09."
					]:
				if bool(re.search(item, release_title)):
					return False
			return True
		return False
	except:
		# return True
		log_utils.error()


def filter_show_pack(show_title, aliases, imdb, year, season, release_title, total_seasons):
	# log_utils.log('release_title = %s' % str(release_title), __name__, log_utils.LOGDEBUG)
	try:
		try:
			aliases = json.loads(aliases)
			aliases = aliases_to_array(aliases, filter=None)
		except:
			aliases = None

		title_list = []
		if aliases:
			for item in aliases:
				alias = item.replace('!', '').replace('(', '').replace(')', '')
				# alias = re.sub(r'[^A-Za-z0-9\s\.-]+', '', item)
				for match in re.finditer(r'(.+?)(U\.S|U\.K)', alias):
					alias = match.group(1) + match.group(2).replace('.', '')
					title_list.append(alias)

		release_title = release_title_format(release_title)
		show_title = show_title.replace('!', '').replace('(', '').replace(')', '')
		title_list.append(show_title)
		split_list = ['.all.seasons', 'seasons', 'season', 'the.complete', 'complete', 'all.torrent', 'total.series', 'tv.series', 'series', 'edited', 's1', 's01', year]
		t = release_title.replace('-', '.')
		for i in split_list:
			t = t.split(i)[0]
		# log_utils.log('t = %s for release_title = %s' % (str(t), str(release_title)), __name__, log_utils.LOGDEBUG)
		if all(cleantitle.get(i) != cleantitle.get(t) for i in title_list):
			return False, 0


# remove episode ranges
		episode_regex = [
				r's[0-3]{1}[0-9]{1}(?:\.|-)e\d{1,2}',
				r's[0-3]{1}[0-9]{1}(?:\.|-)\d{1,2}e\d{1,2}',
				r's[0-3]{1}[0-9]{1}e\d{1,2}',
				r'season(?:\.|-)\d{1,2}(?:\.{0,1}|-{0,1})episode(?:\.|-)\d{1,2}',
				r'season(?:\.|-)\d{1,2}(?:\.|-)ep(?:\.|-)\d{1,2}']
		for item in episode_regex:
			if bool(re.search(item, release_title)):
				return False, 0

# remove season ranges that do not begin at 1
		season_range_regex = [
				r'seasons(?:\.|-)[2-9]{1}(?:\.|-)[3-9]{1}(?:$)', # end of line ex. "seasons.5-6"
				r'seasons(?:\.|-)[2-9]{1}(?:\.|-)[3-9]{1}(?:\.|-)', # "seasons.5-6-
				r'season(?:\.|-)[2-9]{1}(?:\.|-)[3-9]{1}(?:$)', # end of line ex. "season.5-6"
				r'season(?:\.|-)[2-9]{1}(?:\.|-)[3-9]{1}(?:\.|-)', # "season.5-6-
				]
		for item in season_range_regex:
			if bool(re.search(item, release_title)):
				return False, 0

# remove single seasons - returned in seasonPack scrape
		season_regex = [
				r'season(?:\.{0,1}|-{0,1})([2-9]{1}).(?:0{1})\1.complete',	# "season.2.02.complete" when first number is >1 matches 2nd after a zero
				r'season(?:\.{0,1}|-{0,1})([2-9]{1}).(?:[0-9]+).complete', # "season.9.10.complete" when first number is >1 followed by 2 digit number
				r'season(?:\.{0,1}|-{0,1})\d{1,2}(?:\.|-)s\d{1,2}',		   # season.02.s02
				r'season(?:\.{0,1}|-{0,1})\d{1,2}(?:\.|-)complete',		 # season.02.complete
				r'season(?:\.{0,1}|-{0,1})\d{1,2}(?:\.|-)\d{3,4}p{0,1}',		  # "season.02.1080p" and no seperator "season02.1080p"
				r'season(?:\.|-)\d{1,2}(?:\.|-)(?!thru|to|\d+)', # not followed by "to", "thru", or another number(which would be a range)
				r'season(?:\.|-)\d{1,2}(?:\.)(?:$)',				 # end of line ex."season.1" or "season.01"
				r'season(?:\.|-)\d{1,2}(?:\.|-)(?:19|20)[0-9]{2}',			# single season followed by 4 digit year ex."season.1.1971" or "season.01.1971
				r'season(?:\.|-)\d{1,2}(?:\.|-)\d{3}(?:\.{1,2}|-{1,2})(?:19|20)[0-9]{2}',		   # single season followed by 4 digit year ex."season.1.004.1971" or "season.01.004.1971"
				r'(?<!thru)(?<!to)(?<!\d{2})(?:\.|-)s\d{2}(?:\.|-)complete',				# ".s02.complete" not proceeded by "thru", "to", or 2 digit number
				r'(?<!thru)(?<!to)(?<!s\d{2})(?:\.|-)s\d{2}(?:\.|-)(?!thru|to|s|\d+)'		# .s02. not followed or proceeded by "thru", "to" 
				]
		for item in season_regex:
			if bool(re.search(item, release_title)):
				return False, 0

# remove spelled out single seasons
		season_regex = []
		[season_regex.append(r'(complete(?:\.|-)%s(?:\.|-)season)' % x) for x in season_ordinal_list]
		[season_regex.append(r'(complete(?:\.|-)%s(?:\.|-)season)' % x) for x in season_ordinal2_list]
		[season_regex.append(r'(season(?:\.|-)%s)' % x) for x in season_list] 
		for item in season_regex:
			if bool(re.search(item, release_title)):
				return False, 0


# from here down we don't filter out, we set and pass "last_season" it covers for the range and addon can filter it so the db will have full valid showPacks.
# set last_season for range type ex "1.2.3.4" or "1.2.3.and.4" (dots or dashes)
		dot_release_title = release_title.replace('-', '.')
		dot_season_ranges = []
		all_seasons = '1'
		season_count = 2
		while season_count <= int(total_seasons):
			dot_season_ranges.append(all_seasons + '.and.%s' % str(season_count))
			all_seasons += '.%s' % str(season_count)
			dot_season_ranges.append(all_seasons)
			season_count += 1
		if any(i in dot_release_title for i in dot_season_ranges):
			keys = [i for i in dot_season_ranges if i in dot_release_title]
			last_season = int(keys[-1].split('.')[-1])
			return True, last_season



# "1.to.9" type range filter (dots or dashes)
		to_season_ranges = []
		start_season = '1'
		season_count = 2
		while season_count <= int(total_seasons):
			to_season_ranges.append(start_season + '.to.%s' % str(season_count))
			season_count += 1
		if any(i in dot_release_title for i in to_season_ranges):
			keys = [i for i in to_season_ranges if i in dot_release_title]
			last_season = int(keys[0].split('to.')[1])
			return True, last_season

# "1.thru.9" range filter (dots or dashes)
		thru_ranges = [i.replace('to', 'thru') for i in to_season_ranges]
		if any(i in dot_release_title for i in thru_ranges):
			keys = [i for i in thru_ranges if i in dot_release_title]
			last_season = int(keys[0].split('thru.')[1])
			return True, last_season

# "1-9" range filter
		dash_ranges = [i.replace('.to.', '-') for i in to_season_ranges]
		if any(i in release_title for i in dash_ranges):
			keys = [i for i in dash_ranges if i in release_title]
			last_season = int(keys[0].split('-')[1])
			return True, last_season



# 2 digit "01.to.09" range filter (dots or dashes)
		to_season_ranges = []
		start_season = '01'
		season_count = 2
		while season_count <= int(total_seasons):
			to_season_ranges.append(start_season + '.to.%s' % '0' + str(season_count) if int(season_count) < 10 else start_season + '.to.%s' % str(season_count))
			season_count += 1
		if any(i in dot_release_title for i in to_season_ranges):
			keys = [i for i in to_season_ranges if i in dot_release_title]
			last_season = int(keys[0].split('to.')[1])
			return True, last_season

# 2 digit "01.thru.09" range filter (dots or dashes)
		thru_ranges = [i.replace('to', 'thru') for i in to_season_ranges]
		if any(i in dot_release_title for i in thru_ranges):
			keys = [i for i in thru_ranges if i in dot_release_title]
			last_season = int(keys[0].split('thru.')[1])
			return True, last_season

# 2 digit  "01-09" range filtering
		dash_ranges = [i.replace('.to.', '-') for i in to_season_ranges]
		if any(i in release_title for i in dash_ranges):
			keys = [i for i in dash_ranges if i in release_title]
			last_season = int(keys[0].split('-')[1])
			return True, last_season




# "s1.to.s9" single digit range filte (dots or dashes)
		to_season_ranges = []
		start_season = 's1'
		season_count = 2
		while season_count <= int(total_seasons):
			to_season_ranges.append(start_season + '.to.s%s' % str(season_count))
			season_count += 1
		if any(i in dot_release_title for i in to_season_ranges):
			keys = [i for i in to_season_ranges if i in dot_release_title]
			last_season = int(keys[0].split('to.s')[1])
			return True, last_season

# "s1.thru.s9" single digit range filter (dots or dashes)
		thru_ranges = [i.replace('to', 'thru') for i in to_season_ranges]
		if any(i in dot_release_title for i in thru_ranges):
			keys = [i for i in thru_ranges if i in dot_release_title]
			last_season = int(keys[0].split('thru.s')[1])
			return True, last_season

# "s1-s9" single digit range filtering (dashes)
		dash_ranges = [i.replace('.to.', '-') for i in to_season_ranges]
		if any(i in release_title for i in dash_ranges):
			keys = [i for i in dash_ranges if i in release_title]
			last_season = int(keys[0].split('-s')[1])
			return True, last_season



# 2 digit "s01.to.s09" range filter (dots or dash)
		to_season_ranges = []
		start_season = 's01'
		season_count = 2
		while season_count <= int(total_seasons):
			to_season_ranges.append(start_season + '.to.s%s' % '0' + str(season_count) if int(season_count) < 10 else start_season + '.to.s%s' % str(season_count))
			season_count += 1
		if any(i in dot_release_title for i in to_season_ranges):
			keys = [i for i in to_season_ranges if i in dot_release_title]
			last_season = int(keys[0].split('to.s')[1])
			return True, last_season

# 2 digit "s01.thru.s09" range filter (dots or dashes)
		thru_ranges = [i.replace('to', 'thru') for i in to_season_ranges]
		if any(i in dot_release_title for i in thru_ranges):
			keys = [i for i in thru_ranges if i in dot_release_title]
			last_season = int(keys[0].split('thru.s')[1])
			return True, last_season

# 2 digit "s01-s09" range filtering (dashes)
		dash_ranges = [i.replace('.to.', '-') for i in to_season_ranges]
		if any(i in release_title for i in dash_ranges):
			keys = [i for i in dash_ranges if i in release_title]
			last_season = int(keys[0].split('-s')[1])
			return True, last_season

# 2 digit "s01.s09" range filtering (dots)
		dot_ranges = [i.replace('.to.', '.') for i in to_season_ranges]
		if any(i in release_title for i in dot_ranges):
			keys = [i for i in dot_ranges if i in release_title]
			last_season = int(keys[0].split('.s')[1])
			return True, last_season


		return True, total_seasons
	except:
		# return True, total_seasons
		log_utils.error()


def release_title_strip(release_title):
	try:
		try:
			release_title = release_title.encode('utf-8')
		except:
			pass
		release_title = release_title.lower().replace("'", "").lstrip('.').rstrip('.')
		fmt = re.sub('[^a-z0-9]+', '.', release_title)
		fmt = '.%s.' % fmt
		fmt = re.sub(r'(.+)((?:19|20)[0-9]{2}|season.\d+|s[0-3]{1}[0-9]{1}|e\d+|complete)(.complete\.|.episode\.\d+\.|.episodes\.\d+\.\d+\.|.series|.extras|.ep\.\d+\.|.\d{1,2}\.|-|\.|\s)', '', fmt) # new for pack files

# Fails for these cases
# release_title = Game.of.Thrones.S01.1080p.BluRay.10bit.HEVC-MkvCage.Season.1.One (ENCODED)
# fmt = .one.
# .yelowstone.season.03.hamsterstudio.2019.
# fmt = ''
# may be best to pass "tvshowtitle" and "ep_title" and strip that off, as well as strip seaon/s01 type info off

		if fmt == '':
			return None
		else:
			return '.%s' % fmt
	except:
		log_utils.error()
		return None


def release_title_format(release_title):
	try:
		release_title = release_title.lower().replace("'", "").lstrip('.').rstrip('.')
		fmt = re.sub('[^a-z0-9-]+', '.', release_title)
		fmt = fmt.replace('.-.', '-').replace('-.', '-').replace('.-', '-').replace('--', '-')
		fmt = '.%s.' % fmt
		return fmt
	except:
		log_utils.error()
		return release_title


def url_strip(url):
	try:
		url = unquote_plus(url)
		if 'magnet' in url:
			url = url.split('&dn=')[1]
		url = url.lower().replace("'", "").lstrip('.').rstrip('.')
		fmt = re.sub('[^a-z0-9]+', '.', url)
		fmt = '.%s.' % fmt
		fmt = re.sub(r'(.+)((?:19|20)[0-9]{2}|season.\d+|s[0-3]{1}[0-9]{1}|e\d+|complete)(.complete\.|.episode\.\d+\.|.episodes\.\d+\.\d+\.|.series|.extras|.ep\.\d+\.|.\d{1,2}\.|-|\.|\s)', '', fmt) # new for pack files
		if '.http' in fmt:
			fmt = None
		if fmt == '':
			return None
		else:
			return '.%s' % fmt
	except:
		log_utils.error()
		return None


def clean_name(title, release_title):
	try:
		unwanted = ['[zooqle.com]', '[horriblesubs]', '[.www.cpasbien.cm.]', '[.www.cpasbien.pw.]', '[auratorrent.pl].nastoletni.wilkoak', '[auratorrent.pl]', 'tamilrockers.com',
					'www.tamilrockers.com', '[.oxtorrent.com.]', '[.www.torrenting.com.]', '[.Www.nextorrent.site.]', '[.oxtorrent.com.]', '[gktorrent.com]', 'www.torrenting.com',
					'www.torrenting.org', 'www.torrent9.nz', '[.www.omgtorrent.com.]', '[.www.torrent9.uno.]', '[agusiq.torrents.pl]', '[katmoviehd.to]', '[3d.hentai]', '[dark.media]',
					'[filetracker.pl]', 'www-torrenting-com', 'www-torrenting-org', '[katmoviehd.eu]', 'www.scenetime.com', 'www.tamilrockerrs.pl', '[.torrent9.tv.]', '[nextorrent.net]',
					'+katmoviehd.pw+', 'www.movcr.tv', 'www.bludv.tv', '[www.torrent9.ph.]','[acesse.]', '[acesse-hd-elite-me]', '[torrentcouch.net]', 'ramin.djawadi', '[prof]', '[reup]',
					'[ah]', '[ul]', '+13.+', 'taht.oyunlar', '[agusiq-torrents.pl]', 'agusiq-torrents-pl', 'crazy4tv.com', '[tv]']

		unwanted2 = ['.', '..', '...', '{', '}', '[.]', '[.]', '[.', '+-+-', '-', '-.', '.-.']

		if release_title.lower().startswith('rifftrax'):
			return release_title

		release_title = strip_non_ascii_and_unprintable(release_title)
		release_title = release_title.lstrip('/ ')
		release_title = release_title.lower()
		release_title = release_title.replace(' ', '.')

		for i in unwanted:
			if release_title.startswith(i):
				release_title = release_title.replace(i, '')
				break

		for i in unwanted2:
			release_title = release_title.lstrip(i)
		# log_utils.log('final release_title: ' + str(release_title), log_utils.LOGDEBUG)
		return release_title

	except:
		log_utils.error()


def strip_non_ascii_and_unprintable(text):
	result = ''.join(char for char in text if char in string.printable)
	return result.encode('ascii', errors='ignore').decode('ascii', errors='ignore')


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


def scraper_error(provider):
	import traceback
	failure = traceback.format_exc()
	log_utils.log(provider.upper() + ' - Exception: \n' + str(failure), log_utils.LOGDEBUG)


def strip_domain(url):
	try:
		if url.lower().startswith('http') or url.startswith('/'):
			url = re.findall('(?://.+?|)(/.+)', url)[0]
		url = client.replaceHTMLCodes(url)
		try:
			url = url.encode('utf-8')
		except:
			pass
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


def timeIt(func):
	import time
	fnc_name = func.__name__
	def wrap(*args, **kwargs):
		started_at = time.time()
		result = func(*args, **kwargs)
		log_utils.log('%s.%s = %s' % (__name__ , fnc_name, time.time() - started_at), log_utils.LOGDEBUG)
		return result
	return wrap
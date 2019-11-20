# -*- coding: utf-8 -*-

import urlparse

from openscrapers import sources_openscrapers
from openscrapers.modules import control

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))
action = params.get('action')
mode = params.get('mode')
query = params.get('query')


def ScraperChoice():
	from openscrapers import providerSources
	sourceList = sorted(providerSources())
	control.idle()
	select = control.selectDialog([i for i in sourceList])
	if select == -1: return
	module_choice = sourceList[select]
	control.setSetting('module.provider', module_choice)
	control.openSettings('0.1')


if action == "OpenscrapersSettings":
	control.openSettings('0.0', 'script.module.openscrapers')

elif mode == "OpenscrapersSettings":
	control.openSettings('0.0', 'script.module.openscrapers')


elif action == "ScraperChoice":
	ScraperChoice()


elif action == "toggleAll":
	sourceList = []
	sourceList = sources_openscrapers.all_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllHosters":
	sourceList = []
	sourceList = sources_openscrapers.hoster_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Hoster providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllForeign":
	sourceList = []
	sourceList = sources_openscrapers.all_foreign_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Foregin providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllGerman":
	sourceList = []
	sourceList = sources_openscrapers.german_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All German providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllSpanish":
	sourceList = []
	sourceList = sources_openscrapers.spanish_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Spanish providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")



elif action == "toggleAllFrench":
	sourceList = []
	sourceList = sources_openscrapers.french_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Spanish providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllGreek":
	sourceList = []
	sourceList = sources_openscrapers.greek_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Greek providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllKorean":
	sourceList = []
	sourceList = sources_openscrapers.korean_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Spanish providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllPolish":
	sourceList = []
	sourceList = sources_openscrapers.polish_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Polish providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllRussian":
	sourceList = []
	sourceList = sources_openscrapers.russian_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Polish providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllPaid":
	sourceList = []
	sourceList = sources_openscrapers.all_paid_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Paid providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllDebrid":
	sourceList = []
	sourceList = sources_openscrapers.debrid_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Debrid providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllTorrent":
	sourceList = []
	sourceList = sources_openscrapers.torrent_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	#    xbmc.log('All Torrent providers = %s' % sourceList,2)
	control.openSettings(query, "script.module.openscrapers")

if action == "Defaults":
	sourceList = ['1putlocker', '5movies', '123movieshubz', 'alucxyz', 'animetoon', 'azmovie', 'bnwmovies',
	              'cartoonhd', 'cartoonhdto', 'cmovieshd', 'coolmoviezone', 'divxcrawler', 'extramovies', 'filmxy',
	              'fmovies',
	              'freefmovies', 'ganoolcam', 'gomo', 'gomoviesink', 'gowatchseries', 'hdmto', 'hdpopcorneu',
	              'hubmovie', 'iwaatch', 'iwannawatch',
	              'movie4kis', 'myhdpopcorn', 'primewire', 'projectfreetv', 'putlockerfree', 'putlockeronl',
	              'putlockeronline', 'seehd', 'series9',
	              'seriesonline', 'sharemovies', 'solarmoviefree', 'streamdreams', 'timewatch', 'toonget',
	              'tvbox', 'tvmovieflix', 'watchepisodes', 'watchserieshd', 'xwatchseries', 'yesmoviesgg',
	              '300mbdownload', '300mbfilms', 'ddlspot', 'ganool', 'ganool2',
	              'maxrls', 'mkvhub', 'mvrls', 'myvideolink', 'onlineseries', 'rapidmoviez', 'rlsbb',
	              'sceneddl', 'scenerls',
	              'ultrahdindir', '1337x', 'btdb', 'btscene', 'doublr', 'eztv', 'glodls', 'kickass2',
	              'limetorrents', 'magnetdl', 'mkvccage', 'piratebay', 'torrentapi', 'torrentdownloads',
	              'torrentgalaxy',
	              'torrentquest', 'yifyddl', 'yts', 'zoogle']
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	control.openSettings(query, "script.module.openscrapers")

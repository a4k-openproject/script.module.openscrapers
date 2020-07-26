# -*- coding: utf-8 -*-

import sys
try:
	from urlparse import parse_qsl
except:
	from urllib.parse import parse_qsl

from openscrapers import sources_openscrapers
from openscrapers.modules import control

params = dict(parse_qsl(sys.argv[2].replace('?', '')))
action = params.get('action')
mode = params.get('mode')
query = params.get('query')
name = params.get('name')


if action == "OpenscrapersSettings":
	control.openSettings('0.0', 'script.module.openscrapers')


elif mode == "OpenscrapersSettings":
	control.openSettings('0.0', 'script.module.openscrapers')


elif action == 'ShowChangelog':
	from openscrapers.modules import changelog
	changelog.get()
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == 'ShowHelp':
	from openscrapers.help import help
	help.get(name)
	control.openSettings(query, "script.module.openscrapers")


elif action == "Defaults":
	sourceList = []
	sourceList = sources_openscrapers.all_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		value = control.getSettingDefault(source_setting)
		control.setSetting(source_setting, value)
	# xbmc.log('provider-default = %s-%s' % (source_setting, value), 2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAll":
	sourceList = []
	sourceList = sources_openscrapers.all_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllPaid":
	sourceList = []
	sourceList = sources_openscrapers.all_paid_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Paid providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllHosters":
	sourceList = []
	sourceList = sources_openscrapers.hoster_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Hoster providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllDebrid":
	sourceList = []
	sourceList = sources_openscrapers.debrid_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Debrid providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllTorrent":
	sourceList = []
	sourceList = sources_openscrapers.torrent_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Torrent providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllPackTorrent":
	sourceList = []
	from openscrapers import pack_sources
	sourceList = pack_sources()
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Pack Torrent providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllForeign":
	sourceList = []
	sourceList = sources_openscrapers.all_foreign_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Foregin providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllGerman":
	sourceList = []
	sourceList = sources_openscrapers.german_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All German providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllSpanish":
	sourceList = []
	sourceList = sources_openscrapers.spanish_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Spanish providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllFrench":
	sourceList = []
	sourceList = sources_openscrapers.french_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All French providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllGreek":
	sourceList = []
	sourceList = sources_openscrapers.greek_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Greek providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllKorean":
	sourceList = []
	sourceList = sources_openscrapers.korean_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Korean providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllPolish":
	sourceList = []
	sourceList = sources_openscrapers.polish_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Polish providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllRussian":
	sourceList = []
	sourceList = sources_openscrapers.russian_providers
	for i in sourceList:
		source_setting = 'provider.' + i
		control.setSetting(source_setting, params['setting'])
	# xbmc.log('All Russian providers = %s' % sourceList,2)
	control.sleep(200)
	control.openSettings(query, "script.module.openscrapers")
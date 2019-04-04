# -*- coding: utf-8 -*-

import urlparse
from openscrapers import sources_openscrapers
from openscrapers.modules import control
from openscrapers import providerSources, providerNames


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
    sourcelist = []
    sourceList = sources_openscrapers.all_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllHosters":
    sourcelist = []
    sourceList = sources_openscrapers.hoster_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Hoster providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllForeign":
    sourcelist = []
    sourceList = sources_openscrapers.all_foreign_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Foregin providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllSpanish":
    sourcelist = []
    sourceList = sources_openscrapers.spanish_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Spanish providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllGerman":
    sourcelist = []
    sourceList = sources_openscrapers.german_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All German providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllGreek":
    sourcelist = []
    sourceList = sources_openscrapers.greek_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Greek providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllPolish":
    sourcelist = []
    sourceList = sources_openscrapers.polish_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Polish providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllPaid":
    sourcelist = []
    sourceList = sources_openscrapers.all_paid_providers
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
#    xbmc.log('All Paid providers = %s' % sourceList,2)
    control.openSettings(query, "script.module.openscrapers")


elif action == "toggleAllDebrid":
    sourcelist = []
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
    sourceList = ['123fox','123hbo','123movieshubz','animetoon','azmovies','bnwmovies','cartoonhd',
    'extramovies','fmovies','freefmovies','freeputlockers','gostream','Hdmto','hdpopcorns',
    'kattv','l23movies','iwaatch','openloadmovie','primewire','putlocker','reddit','rlsbb','scenerls',
    'seehd','series9','seriesfree','seriesonline','solarmoviez','tvbox','vidics','watchseries',
    'xwatchseries','vdonip','downflix','ymovies','ddlspot','filmxy','kickass2','sezonlukdizi']
    for i in sourceList:
        source_setting = 'provider.' + i
        control.setSetting(source_setting, params['setting'])
    control.openSettings(query, "script.module.openscrapers")


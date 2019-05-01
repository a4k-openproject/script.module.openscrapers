# -*- coding: UTF-8 -*-

import os.path

import de
import en
import en_DebridOnly
import en_Torrent
import es
import gr
import pl

scraper_source = os.path.dirname(__file__)
__all__ = [x[1] for x in os.walk(os.path.dirname(__file__))][0]

##--en--##
hoster_source = en.sourcePath
hoster_providers = en.__all__

##--en_DebridOnly--##
debrid_source = en_DebridOnly.sourcePath
debrid_providers = en_DebridOnly.__all__

##--en_Torrent--##
torrent_source = en_Torrent.sourcePath
torrent_providers = en_Torrent.__all__

##--Paid Debrid(Debrid and Torrents)--##
paid_providers = {'en_DebridOnly': debrid_providers, 'en_Torrent': torrent_providers}
all_paid_providers = []
for key, value in paid_providers.iteritems():
    all_paid_providers += value

##--Foreign Providers--##
spanish_providers = es.__all__
german_providers = de.__all__
greek_providers = gr.__all__
polish_providers = pl.__all__

##--All Foreign Providers--##
foreign_providers = {'es': spanish_providers, 'de': german_providers, 'gr': greek_providers, 'pl': polish_providers}
all_foreign_providers = []
for key, value in foreign_providers.iteritems():
    all_foreign_providers += value

##--All Providers--##
total_providers = {'en': hoster_providers, 'en_Debrid': debrid_providers, 'en_Torrent': torrent_providers,
                   'de': german_providers, 'es': spanish_providers, 'gr': greek_providers, 'pl': polish_providers}
all_providers = []
for key, value in total_providers.iteritems():
    all_providers += value

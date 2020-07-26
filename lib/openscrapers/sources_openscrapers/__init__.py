# -*- coding: UTF-8 -*-

import os.path

from . import de
from . import en
from . import en_DebridOnly
from . import en_Torrent
from . import es
from . import fr
from . import gr
from . import ko
from . import pl
from . import ru


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
try:
	for key, value in paid_providers.iteritems():
		all_paid_providers += value
except:
	for key, value in paid_providers.items():
		all_paid_providers += value

##--Foreign Providers--##
german_providers = de.__all__
spanish_providers = es.__all__
french_providers = fr.__all__
greek_providers = gr.__all__
korean_providers = ko.__all__
polish_providers = pl.__all__
russian_providers = ru.__all__

##--All Foreign Providers--##
foreign_providers = {'de': german_providers, 'es': spanish_providers, 'fr': french_providers, 'gr': greek_providers,
                     'ko': korean_providers, 'pl': polish_providers, 'ru': russian_providers}
all_foreign_providers = []
try:
	for key, value in foreign_providers.iteritems():
		all_foreign_providers += value
except:
	for key, value in foreign_providers.items():
		all_foreign_providers += value

##--All Providers--##
total_providers = {'en': hoster_providers, 'en_Debrid': debrid_providers, 'en_Torrent': torrent_providers,
                   'de': german_providers, 'es': spanish_providers, 'fr': french_providers, 'gr': greek_providers,
                   'ko': korean_providers, 'pl': polish_providers, 'ru': russian_providers}
all_providers = []
try:
	for key, value in total_providers.iteritems():
		all_providers += value
except:
	for key, value in total_providers.items():
		all_providers += value

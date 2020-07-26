# -*- coding: UTF-8 -*-

import os.path
import pkgutil

from openscrapers.modules import log_utils

try:
	import xbmcaddon
	__addon__ = xbmcaddon.Addon(id='script.module.openscrapers')
except:
	__addon__ = None
	pass

debug = __addon__.getSetting('debug.enabled') == 'true'

def sources(specified_folders=None):
	try:
		sourceDict = []
		if __addon__ is not None:
			provider = __addon__.getSetting('module.provider')
		else:
			provider = 'openscrapers'
		sourceFolder = getScraperFolder(provider)
		sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
		sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
		if specified_folders is not None:
			sourceSubFolders = specified_folders
		for i in sourceSubFolders:
			for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
				if is_pkg:
					continue
				if enabledCheck(module_name):
					try:
						module = loader.find_module(module_name).load_module(module_name)
						sourceDict.append((module_name, module.source()))
					except Exception as e:
						if debug:
							log_utils.log('Error: Loading module: "%s": %s' % (module_name, e), log_utils.LOGDEBUG)
						pass
		return sourceDict
	except:
		return []


def enabledCheck(module_name):
	if __addon__ is not None:
		if __addon__.getSetting('provider.' + module_name) == 'true':
			return True
		else:
			return False
	return True


def pack_sources():
	return ['7torrents', 'bitlord', 'btscene', 'idope', 'kickass2', 'limetorrents', 'magnetdl', 'piratebay',
				'skytorrents', 'solidtorrents', 'torrentapi', 'torrentdownload', 'torrentfunk', 'torrentgalaxy',
				'yourbittorrent', 'zoogle']


def providerSources():
	sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
	return getModuleName(sourceSubFolders)


def providerNames():
	providerList = []
	provider = __addon__.getSetting('module.provider')
	sourceFolder = getScraperFolder(provider)
	sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
	sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
	for i in sourceSubFolders:
		for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
			if is_pkg:
				continue
			correctName = module_name.split('_')[0]
			providerList.append(correctName)
	return providerList


def getAllHosters():
	def _sources(sourceFolder, appendList):
		sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
		sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
		for i in sourceSubFolders:
			for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
				if is_pkg:
					continue
				try:
					mn = str(module_name).split('_')[0]
				except:
					mn = str(module_name)
				appendList.append(mn)

	sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
	appendList = []
	for item in sourceSubFolders:
		if item != 'modules':
			_sources(item, appendList)
	return list(set(appendList))


def getScraperFolder(scraper_source):
	sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
	return [i for i in sourceSubFolders if scraper_source.lower() in i.lower()][0]


def getModuleName(scraper_folders):
	nameList = []
	for s in scraper_folders:
		try:
			nameList.append(s.split('_')[1].lower().title())
		except:
			pass
	return nameList
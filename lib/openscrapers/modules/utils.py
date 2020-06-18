# -*- coding: utf-8 -*-
"""
	OpenScrapers Module

"""

import json
import re


def json_load_as_str(file_handle):
	return byteify(json.load(file_handle, object_hook=byteify), ignore_dicts=True)


def json_loads_as_str(json_text):
	return byteify(json.loads(json_text, object_hook=byteify), ignore_dicts=True)


def byteify(data, ignore_dicts=False):
	if isinstance(data, unicode):
		return data.encode('utf-8')
	if isinstance(data, list):
		return [byteify(item, ignore_dicts=True) for item in data]
	if isinstance(data, dict) and not ignore_dicts:
		return dict(
			[(byteify(key, ignore_dicts=True), byteify(value, ignore_dicts=True)) for key, value in data.iteritems()])
	return data


def title_key(title):
	try:
		if title is None: title = ''
		articles_en = ['the', 'a', 'an']
		articles_de = ['der', 'die', 'das']
		articles = articles_en + articles_de
		match = re.match('^((\w+)\s+)', title.lower())
		if match and match.group(2) in articles:
			offset = len(match.group(1))
		else:
			offset = 0
		return title[offset:]
	except:
		return title
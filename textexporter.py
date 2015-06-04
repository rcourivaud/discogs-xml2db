__author__ = 'philip'

import csv, sys
from datetime import datetime

# TODO:
# - store artist
# - options for nulls
# - options for separator

csv.register_dialect('pgcopy', delimiter='\t')
def format_array(arr):
	if not len(arr):
		return '{}'
	else:
		return arr

class TextExporter(object):
	def __init__(self, options, data_quality):
		self.min_data_quality = data_quality
		now = datetime.now()
		self.files = {
			'artist': {
				'name': 'artist_dump-%s' % now,
				'writer': None
			},
		}

	def _good_quality(self, what):
		if len(self.min_data_quality):
			return what.data_quality.lower() in self.min_data_quality
		return True

	def _writer(self, name):
		config = self.files[name]
		if not config['writer']:
			config['file'] = sys.stdout
			config['writer'] = csv.writer(config['file'], dialect='pgcopy')

		return config['writer']

	def finish(self, completely_done=False):
		pass

	def storeArtist(self, artist):
		order = [
				'id',
				'name',
				'realname',
				'urls',
				'namevariations',
				'aliases',
				'releases',
				'profile',
				'members',
				'groups',
				'data_quality'
		        ]
		row = []
		for c in order:
			if hasattr(artist, c):
				val = getattr(artist, c)
				if type(val) is list:
					row.append(format_array(val))
				else:
					if hasattr(val, 'encode'):
						row.append(val.encode('utf-8'))
					else:
						row.append(val)

			else:
				print "Artist doesn't have %s" % c

		if row:
			self._writer('artist').writerow(row)





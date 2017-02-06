import csv, sys
from datetime import datetime
from cStringIO import StringIO

# TODO:
# - store artist
# - options for nulls
# - options for separator

csv.register_dialect('pgcopy', delimiter='\t', doublequote=False, escapechar='@', quotechar='\0', quoting=csv.QUOTE_NONE)
csv.register_dialect('pgarray', delimiter=',', doublequote=False, escapechar='\\', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
csv.register_dialect('pgquotes', delimiter=',', doublequote=True, escapechar='\\', quotechar='"', quoting=csv.QUOTE_ALL)


class TabQuoter(object):
	def format_array(self, arr):
		if not len(arr):
			return '\\N'
		else:
			actuals = [prepare_value(x) for x in arr]
			tmp_file = StringIO()
			tmp_writer = csv.writer(tmp_file, dialect='pgarray')
			tmp_writer.writerow(actuals)
			tmp = tmp_file.getvalue().rstrip()
			tmp_file.close()
			return "{%s}" % tmp.replace("\\\"", "\\\\\"")


	def prepare_value(self, value):
		if value is None or (type(value) is str and value == ''):
			return '\\N'
		if type(value) is list:
			return format_array(value)
		else:
			if hasattr(value, 'encode'):
				val = value.encode('utf-8')\
					.replace('\n', '\\n')\
					.replace('\r', '\\r')\
					.replace('\t', '\\t')
				return val
			else:
				return str(value)

class CsvQuoter(object):
	def format_array(self):
		pass
	def prepare_value(self)
		pass


class PgTextExporter(object):
	def __init__(self, options, data_quality):
		self.quoter = TabQuoter()
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
			config['file'] = StringIO()
			# config['file'] = open(config['name'], 'wb')
			config['writer'] = csv.writer(config['file'], dialect='pgcopy')

		return config['writer']

	def finish(self, completely_done=False):
		for name in self.files:
			config = self.files[name]
			if config['writer'] and config['file']:
				file = config['file']
				if hasattr(file, 'getvalue'):
					out = file.getvalue()
					print out
				#if completely_done:
					file.close()
				config['file'] = None

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
				row.append(self.quoter.prepare_value(val))
			else:
				row.append(self.quoter.prepare_value(None))

		if row:
			self._writer('artist').writerow(row)

#!/usr/bin/env python
"""
A simple webservice for matching sequences to a pre-existing library of seqs.

It presents a two-step form. In the first, the user (may* enter a sequence, how
sequences are to be compared and what genomic region is to be examined. In the
second step, genes from the genomic region are selected. These are then
compared as requested (fasta or neighbour joining) and the results compared.

Input should be checked and cleaned. Users should be able to step back and
forward in the steps of the program as desired, with values being populated
appropriately (e.g. returning to the start of the form to change the sequence
or the region searched).
"""

###
# CONFIGURATION DETAILS FOR LOCAL INSTALLATION CAN BE FOUND BELOW IN CONSTANTS
###


__version__ = '0.2'
__author__ = 'Paul-Michael Agapow (pma@agapow,net)'


### IMPORTS

from cgi import parse_qs, escape

import config
import templates
import formbuilder
import dbconn


### CONSTANTS & DEFINES

# all comparison methods available
ALL_METHODS = [
	('fasta', 'FASTA'),
	('nj', 'Neighbour-joining')
]


### IMPLEMENTATION ###

def make_db_connection():
	return dbconn.DbConn (
		type = 'mysql',
		host = config.DB_HOST,
		user = config.DB_USER, 
		passwd = config.DB_PASSWD,
		name = config.DB_NAME,
	)


### APPLICATION & PROCESSING

def get_args (environ):
	"""
	Unpack arguments in appropriate way.
	
	Note that the awkward code below is actually legit if you are using POST
	(which we are due to the size of what we're passing). If you use GET, it's
	a lot simpler.
	"""
	# In this idiom you must issue a list containing a default value.
	#age = d.get('age', [''])[0] # Returns the first age value.
	#hobbies = d.get('hobbies', []) # Returns a list of hobbies.
	
	# Always escape user input to avoid script injection
	#age = escape(age)
	#hobbies = [escape(hobby) for hobby in hobbies]
	
	# grab args as a dict containing lists as values
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except (ValueError):
		request_body_size = 0
	request_body = environ['wsgi.input'].read(request_body_size)
	args = {}
	for k, v in parse_qs(request_body).iteritems():
		print "arg:", k, v
		if (k != 'regions'):
			if v in [[''], []]:
				v = None
			else:
				v = v[0]
		args[k] = v
		
	print "KEYS: %s " % args.keys()
	return args


def render_choose_regions (args):
	print "stage 1"
	all_regions = make_db_connection().select_regions()
	return formbuilder.select_region_form (args, ALL_METHODS, all_regions)


def render_enter_and_select_genes (form):
	print "stage 2"
	available_genes = make_db_connection().select_genes (args['regions'])
	return formbuilder.enter_and_select_genes_form (args, ALL_METHODS, available_genes)


def application(environ, start_response):

	# get the passed values, if any
	args = get_args (environ)
	print "ARGS: %s" % args
	
	# process request
	messages = []
	results = []
	
	# the form can be in 3 different states or stages as we progress thru form:
	# 1. opening page, enter seq, select region
	# 2. second page, select method & enter sequence
	# 3. third & final page, show results
	if (args.get ("submit", False) in [False, config.RESELECT_REGIONS]):
		# 1. if we are new to the form or have returned to the initial page
		return render_choose_regions (args)
	elif args.get ("submit", config.SUBMIT_SELECT_REGIONS):
		# 2. have just selected regions, if valid allow entry & selection of genes
		# otherwise return to region selection
		try:
			assert (0 < len (args.get("regions", []))), "need to select at least 1 region"
			return render_choose_regions (args)
		except:
			# go back to the page
			# TODO: append error message
			conn = make_db_connection().select_regions()
			form_body = formbuilder.render_form_select_region (args, ALL_METHODS, all_regions)
	elif args.get ("submit", False):
		# 3. have selected genes, now want to do the match & show results
		# TODO: check args
		print "stage 3"
		if (True):
			# TODO: render results
			form_body = formbuilder.render_form_select_genes (args)
		else:
			# go back to the page
			# TODO: append error message
			form_body = formbuilder.render_form_select_genes (args)
	else:
		print "SHOUDL NOT GET HERE", args
	
	# build page to return
	response_body = templates.PAGE % {
		'MESSAGES': '\n'.join (['<p class="%s">%s</p>' % (r[0], r[1]) for r in messages]),
		'RESULTS': '\n'.join (results),
		'SCRIPT_NAME': __file__,
		'FORM': form_body,
	}
	response_headers = [
		('Content-Type', 'text/html'),
		('Content-Length', str (len (response_body))),
	]
	start_response ('200 OK', response_headers)
	
	## Postconditions & return:
	# NOTE: have to do this as wsgi doesn't handle unicode but bytes
	# NOTE: must return an iterable
	return [response_body.encode('utf-8')]


### TEST & DEBUG

# Run this file to make a server & run the application to test it
# for Windows kill in Task Manager, in Linux use Ctrl-C 
# Note that this doesn't serve static content.
if __name__ == '__main__':
	if config.DEV_MODE:
		# These settings are to be used solely for the purposes of testing and
		# development and should not be taken as advisory for production.
		
		TEST_ADDR = "158.119.147.40"
		TEST_PORT = 9123
		
		from wsgiref.simple_server import make_server
		import static
		httpd = make_server (TEST_ADDR, TEST_PORT, application)
		httpd.serve_forever()
	else:
		import wsgiref.handlers
		wsgiref.handlers.CGIHandler().run (application)


### END ###

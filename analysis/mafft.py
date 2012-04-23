#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rapid alignment with Mafft.


"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

import os

from Bio import SeqRecord, SeqIO, AlignIO

import clineapp, scratchfile
#from relais.dev.common import *


## CONSTANTS & DEFINES ###

INSEQ_FILENAME = 'inseq.fasta'
OUTALIGN_FILENAME = 'outalign.fasta'


### IMPLEMENTATION ###

class MafftCline (clineapp.ClineApp):
	
	def __init__ (self, exepath='/usr/bin/mafft'):
		
		clineapp.ClineApp.__init__ (self, exepath, use_workdir=True,
			remove_workdir=False, check_requirements=False)
	
	def run (self, bioseqs, *clargs):
		"""
		Run Mafft on the supplied biosequences.
		
		This function accepts Biopython SeqRecords.
		
		:Params:
			bioseqs
				An iterable of SeqRecords.
			*args
				The commandline arguments to be passed to mafft.
			
		:Returns:
			to be decided
		
		"""		
		## Preconditions:
		assert (2 <= len (bioseqs))
		## Main:
		self._inseqs = bioseqs
		self.call_cmdline (*clargs)
		
	def run_fftns (self, bioseqs):
		self.run (bioseqs, '--retree 2', '--maxiterate 0')
		
	run_quick_and_dirty = run_fftns
				
	def extract_results (self):
		"""
		Obtain the output produced by Mafft.
		
		:Returns:
			A Biopython Alignment object.
		
		We call this as a seperate function, so the caller has a chance to 
		check the status and error output first. 
		
		"""
		## Preconditions:
		# make sure that cline has actually run & output exists
		assert (self._curr_cline)
		output_path = os.path.join (self._curr_workdir, OUTALIGN_FILENAME)
		assert (os.path.exists (output_path)), \
			"can't find outfile %s" % output_path
		## Main:
		# extract the data
		output_hndl = open (output_path, 'rU')
		align = AlignIO.read (output_hndl, 'fasta')
		## Postconditions:
		return align
				
	def setup_workdir (self):
		"""
		Perpare the necessary input files for mafft.
		
		This creates a temporary working area, and writes the input sequence
		file.
		
		"""		
		# create workdir and input sequence file
		clineapp.ClineApp.setup_workdir (self)
		self._inseq_path = scratchfile.make_scratch_file ('inseq.fasta',
			self._curr_workdir)
		# convert sequences and fill inseq file
		inseqs = []
		for s in self._inseqs:
			assert (isinstance (s, SeqRecord.SeqRecord))
			inseqs.append (s)
		inseq_hndl = open (self._inseq_path, 'w')
		SeqIO.write (inseqs, inseq_hndl, 'fasta')
		inseq_hndl.close()	
		
	def extract_diagnostics (self):
		"""
		Return contents of files generated by cline, for development purposes.
		"""
		# TODO: something like this could move into the base class
		diag = {}
		filenames = [
			INSEQ_FILENAME,
			OUTALIGN_FILENAME,
		]
		for item in filenames:
			fpath = os.path.join (self._curr_workdir, item)
			diag[item] = utils.file_to_string (fpath)
		return diag
		
	def _build_cmdline (self, *clargs):
		"""
		Construct commandline.
		
		Modified to direct output to file.
		"""
		#MSG (clargs)
		clargs = list (clargs) + [INSEQ_FILENAME]
		#MSG (clargs)
		cmdline = clineapp.ClineApp._build_cmdline (self, *clargs)
		cmdline += ' > %s' % OUTALIGN_FILENAME
		#MSG (cmdline)
		return cmdline
		
	def extract_results (self):
		"""
		Obtain the output produced by Mafft.

		We call this as a seperate function, so the caller has a chance to 
		check the status and error output first.
		"""
		## Preconditions:
		# make sure that cline has actually run & output exists
		assert (self._curr_cline)
		output_path = os.path.join (self._curr_workdir, OUTALIGN_FILENAME)
		assert (os.path.exists (output_path)), \
			"can't find outfile %s" % output_path
		## Main:
		# extract the data
		aln_hndl = open (output_path, 'rU')
		aln = AlignIO.read (aln_hndl, 'fasta')
		## Postconditions:
		return aln


### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ####################################################################
#!/usr/bin/python
#emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# -*- coding: utf-8 -*-
#ex: set sts=4 ts=4 sw=4 noet:
#------------------------- =+- Python script -+= -------------------------
"""
 @file      philips_order.py
 @date      Thu Apr 24 16:37:48 2014
 @brief


  Yaroslav Halchenko                                            Dartmouth
  web:     http://www.onerussian.com                              College
  e-mail:  yoh@onerussian.com                              ICQ#: 60653192

 DESCRIPTION (NOTES):

 COPYRIGHT: Yaroslav Halchenko 2014

 LICENSE: MIT

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
"""
#-----------------\____________________________________/------------------

__author__ = 'Yaroslav Halchenko'
__revision__ = '$Revision: $'
__date__ = '$Date:  $'
__copyright__ = 'Copyright (c) 2014 Yaroslav Halchenko'
__license__ = 'MIT'

import sys
import dicom
import numpy as np

np.set_printoptions(linewidth=1000)
# if decide to be fancy and provide name for that sequence containing SOPInstanceUID
#from dicom.datadict import DicomDictionary
#DicomDictionary.update({ 0x2005140f: 

def report_order(f):
    d = dicom.read_file(f, defer_size='1KB', stop_before_pixels=True)

    print "\n", f
    print " Series:    %s" % (d.SeriesDescription,)
    print " Sequence:  %s" % (d.PulseSequenceName,)

    all_slices = d.PerFrameFunctionalGroupsSequence
    slices = [s for s in all_slices
              if s.FrameContentSequence[0].TemporalPositionIndex == 1]
    assert(len(slices) == d[0x2001,0x1018].value)
    slice_position = [s.PlanePositionSequence[0].ImagePositionPatient
                      for s in slices]


    # The magical timing field
    slice_timing_str = [v[0x2005, 0x140f][0].SOPInstanceUID.split('.')[-1]
                        for v in slices]
    # convert all those to integers
    slice_timing = np.array([int(x) for x in slice_timing_str])
    # and actual slice order is simply
    slice_order = np.argsort(slice_timing)
    # and compute time-offset relative to the first one
    # TODO: figure out either those SOP instance UIDs are actually timed,
    # so far scale/timing looks not exactly right ;)
    slice_timing = slice_timing - slice_timing[slice_order == 0]

    print " # slices:  %d" % (len(slice_timing_str))
    print " order:     %s" % slice_order
    print " TR (sec):  %.2f" % (float(d.SharedFunctionalGroupsSequence[0].MRTimingAndRelatedParametersSequence[0].RepetitionTime)/1000.)
    print " timing???: %s" % str(slice_timing/100000.)
    print " max(???):  %.2f" % max(slice_timing/100000.)

if __name__ == '__main__':
    import sys
    for f in sys.argv[1:]:
        try:
            report_order(f)
        except Exception, e:
            print " Failed to figure out for %s (skipped): %s" % (f, e)
        sys.stdout.flush()

#!/usr/bin/env python

"""
Converts the log output from mmal_opencv_modect to a microdvd sub file, suitable with merging with the video output to produce a video file with timestamps.

--

run mmal_opencv_modect like this:

./mmal_opencv_modect > video.h264 2> video.log

then run this script like this:

./modect2sub.py video.log > video.sub

then some ffmpeg magic to a) convert our shoddy h264 to something more solid and b) hardsub our timestamps onto the video

./ffmpeg -r 30 -i video.h264  -vf "subtitles=video.sub" -r 30 video.avi

*ffmpeg will need to be built with libass
"""

fps = "30.00"

import re
import time 
import sys

log = sys.argv[1]

data = []

#open the mmal_opencv_modect log file and parse the KEYFRAME lines in to the 'data' list of dicts
with open(log) as f:
  for line in f:
    #print line.strip()
    m = re.search('KEYFRAME \((.*):(.*)\)', line)
    #print m
    if m:
      frame = m.group(2)
      ts = m.group(1)
      #print "frame: %s, ts: %s" % (frame, ts)
      i = {
        'ts': ts,
        'start': frame,
        'end': None
      }
      
      if len(data) > 0:
        if i != data[-1]:
          data.append(i)
      else:
        data.append(i)

#fix up the 'end' values (this should be collapsed into the next loop)  
for i in range(0, len(data)):
  d = data[i]
  try:  
    d['end'] = data[i+1]['start']
  except IndexError:
    pass
   
# this magic is the microdvd sub format's way of setting the frame rate
# we set it here otherwise ffmpeg assumes the subs are @ 25fps
print "{1}{1}%s" % fps

#convert the timestamp to something for a human
#then write a microdvd.sub 'event'
for d in data:
  ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(d['ts'])))

  if d['end'] is not None:
    print "{%s}{%s}%s" % (d['start'], d['end'], ts)
  else:
    pass


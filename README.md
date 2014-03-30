cue2tracks
==========

split flac, wav, ape formats with cue to traks and package it with images in folders


example:
find /media/data/music/_unsorted -type f -iname "*.cue" -exec ./cue2tracks.py {} /media/data/music \;

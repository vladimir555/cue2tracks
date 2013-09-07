#!/usr/bin/python3


'''
Created on 23.08.2013

@author: volodja
'''


import sys
import os


def printList(name, list_):
    print(name + ":")
    for row in list_:
        print(str(row).replace("\n", ""))


def executeShellCommand(command):
    print("exec: " + command)
    result_pipe = os.popen(command)
    result_     = result_pipe.readlines()
    result      = []
    for line in result_:
        result.append(line.replace('\n', ''))
    return result


def capitalizeWords(s):
    s = s.split(" ")
    r = ""
    for l in s:
        r = r + l.capitalize() + " "
    r = str(r).strip()
    return r

#begin
print("args = '" + str(sys.argv) + "'")
if len(sys.argv) < 3  or  len(sys.argv) > 4:
    print(sys.argv[0] + " cue_file destination_dir [cue_encoding]")
    exit(1)


file_name_cue = sys.argv[1]
if file_name_cue[-4:].lower() != '.cue':
    print("'" + file_name_cue + "' not CUE file")
    exit(1) 

if not os.path.isfile(file_name_cue):
    print("wrong cue file '" + file_name_cue + "'")
    exit(1)

file_name_destination_dir = sys.argv[2]
#executeShellCommand("mkdir -p '" + file_name_destination_dir + "'")
if not os.path.isdir(file_name_destination_dir):
    print("wrong destination dir '" + file_name_destination_dir + "'")
    exit(1)

file_name_source    = ""
source_name         = file_name_cue[:-3]  
if os.path.isfile(source_name + "ape"):
    file_name_source = source_name + "ape"
else:
    if os.path.isfile(source_name + "flac"):
        file_name_source = source_name + "flac"
    else:
        print("APE or FLAC not found")
        exit(1)

print("file_name_source = '" + file_name_source + "'")

if len(sys.argv) == 4:
    cue_encoding = sys.argv[3]
else:
    cue_encoding = ""


file_cue    = open(file_name_cue)
cue         = file_cue.readlines()


album       = ""
artist      = ""
year        = ""
tracks      = []
is_track    = False


for cue_item in cue:
    cue_item = cue_item.replace("\n", "").replace("\"", "").lstrip()
    if is_track:
        if cue_item[:5] == "TITLE":
            tracks.append(capitalizeWords(cue_item[6:]))
    else:
        if cue_item[:4] == "FILE":
            is_track    = True

        if cue_item[:8] == "REM DATE":
            year        = cue_item[9:] 

        if cue_item[:5] == "TITLE":
            album       = capitalizeWords(cue_item[6:])

        if cue_item[:9] == "PERFORMER":
            artist      = capitalizeWords(cue_item[10:])


print("album     = '" + album       + "'")
print("artist    = '" + artist      + "'")
print("year      = '" + year        + "'")
print("tracks    = '" + str(tracks) + "'")


if len(album) == 0  or  len(artist) == 0  or  len(year) == 0  or  len(tracks) == 0:
    print("error parse cue")
    exit(1)


artist_dir  = file_name_destination_dir + "/" + artist
if not os.path.exists(artist_dir):
    os.mkdir(artist_dir)
    
album_dir   = artist_dir + "/" + year + " " + album
if not os.path.exists(album_dir):
    os.mkdir(album_dir)
else:
    print("'" + album_dir + "' already exists, skip")
    exit(0)
    
tmp_dir     = album_dir + "/tmp"    
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

if file_name_source[-3:] == "ape":
    ape     = file_name_source
    flac    = os.path.splitext(os.path.split(file_name_source)[1])[0] + ".flac"
    executeShellCommand("avconv -i '" + ape + "' '" + tmp_dir + "/" + flac + "' > /dev/tty")
    file_name_source = tmp_dir + "/" + flac

# os.rename(file_name_cue     , tmp_dir + "/source.cue")
# os.rename(file_name_source  , tmp_dir + "/source.flac")
 
file_name_cue       = os.path.abspath(file_name_cue)
file_name_source    = os.path.abspath(file_name_source)
 
split_command =                 "cd '" + tmp_dir + "' && "
# split_command = split_command + "cuebreakpoints 'source.cue' | shnsplit -o flac source.flac > /dev/tty && "
# split_command = split_command + "cuetag 'source.cue' `ls split-track*.flac` > /dev/tty"
split_command = split_command + "cuebreakpoints '" + file_name_cue + "' | shnsplit -o flac '" + file_name_source + "' > /dev/tty && "
split_command = split_command + "cuetag '"+ file_name_cue + "' `ls split-track*.flac` > /dev/tty"
executeShellCommand(split_command)


i = 0
for track_name in tracks:
    i = i + 1
    track_number = str(i).rjust(2, "0")
    os.rename(tmp_dir + "/split-track" + track_number + ".flac", album_dir + "/" + track_number + " " + track_name + ".flac")

executeShellCommand("rm -rf '" + tmp_dir + "'")

# #!/bin/bash
#  FILE_NAME_CUE="$1"
#  cuebreakpoints "$FILE_NAME_CUE" | shnsplit -o flac *.flac &&
#  cuetag "$FILE_NAME_CUE" `ls split-track*.flac` &&
#  for i in split-track*.flac;
#     do TRACK_NAME=`grep "TRACK ${i:11:2} AUDIO" -A 1 "$FILE_NAME_CUE" | grep TITLE | sed "s/.*\"\(.*\)\"\r/\1/g"` && mv -v "$i" "$TRACK_NAME".flac;
#  done
#  echo DONE && exit 0 ||
#  echo FAIL
#  %                                                                                                                                                             

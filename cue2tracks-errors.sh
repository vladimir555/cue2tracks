echo $1
echo $2
./cue2tracks.py "$1" "$2" || echo "$1" >> ./cue2tracks.errors

#!/usr/bin/env bash

[ $# -ne 2 ] && echo -e "Using: bash $0 <jpg_dir> <video_out_dir>\n\n\tPut something like this in crontab:\n\n\t0 * * * * /bin/bash wingsitv/camencode.sh /tmp/camdaemon /media/data/camrecords\n" && exit

cd "$1"
ls *.jpg >list.txt


d=`date +%H`
s=`date -d "$d" +%s`
h=`python -c "from datetime import datetime; print(datetime.fromtimestamp($s).timetuple()[3])"`

vout_dir="$2/"`python -c "from datetime import date; print('/'.join(map(str, date.fromtimestamp($s).timetuple()[:3])))"`
vout_file="${vout_dir}/$h.avi"

[ -e "$vout_dir" ] || mkdir -p "$vout_dir"

[ -e divx2pass.log ] && rm divx2pass.log
mencoder mf://@list.txt -mf fps=3 -o "${vout_file}.temp" -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=128:turbo:vpass=1 -really-quiet
mencoder mf://@list.txt -mf fps=3 -o "${vout_file}.temp" -ovc lavc -lavcopts vcodec=mpeg4:mbd=1:v4mv:trell:vbitrate=128:vpass=2 -idx -really-quiet

if [ -e "$vout_file" ]
then
    mv "$vout_file" "${vout_file}.prev"
    mencoder -ovc copy -o "$vout_file" "${vout_file}.prev" "${vout_file}.temp" -idx -really-quiet
    rm "${vout_file}.prev" "${vout_file}.temp"
else
    mv "${vout_file}.temp" "$vout_file"
fi

for i in `cat list.txt`
do
    rm "$i"
done

rm list.txt


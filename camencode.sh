#!/usr/bin/env bash
#
#   Copyright (c) 2010-2011, Andrew Grigorev <andrew@ei-grad.ru>
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#       Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.  Redistributions
#       in binary form must reproduce the above copyright notice, this list of
#       conditions and the following disclaimer in the documentation and/or
#       other materials provided with the distribution.  Neither the name of
#       the <ORGANIZATION> nor the names of its contributors may be used to
#       endorse or promote products derived from this software without
#       specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#   IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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


#!/bin/bash
decode_hextream() {
        while IFS= read -r -n2 pair; do
                 echo -ne '\x'$pair
        done
}

INPUT=~/bt_recording.pcap
INPUT=/tmp/wireshark_11XIWWK1.pcapng
test -n "$1" && INPUT="$1"

tshark -r "$INPUT" -Y zbee_aps.fragments -Tpdml |
xsltproc pdml.xslt - | while read packet; do
    timestamp=$(echo $packet | awk '{print $1}' | awk -F: '{print $2}' | awk -F. '{print $1}')
    data=$(echo $packet | awk '{print $2}' | awk -F: '{print $2}')
    if [[ "$data" == 01036800* ]]; then
        power=${data:62:4}
        printf "%s %d\n" $timestamp $((16#$power))
    fi
done


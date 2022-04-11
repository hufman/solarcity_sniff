#!/bin/bash

start_capture() {
	capture_timeout=$((3600 - (`date +%-M` * 60 + `date +%-S`)))
	if [ $capture_timeout -gt 0 ]; then
		timeout $capture_timeout ./record.sh > data/solarcity_$(date +%Y%m%d_%H%M).pcap &
		echo $!
	fi
}

capture_pid=""

while sleep 1; do
	[ "$capture_pid" == "0" ] && capture_pid=""
	if [ -n "$capture_pid" ]; then
		kill -0 "$capture_pid" 2>/dev/null || capture_pid=""
	fi
	if [ -z "$capture_pid" ]; then
		capture_pid=`start_capture`
		trap "[ -z '$capture_pid' ] || kill $capture_pid" EXIT
	fi
	ls data/*pcap | tail -n 2 | while read file; do
		./parse_solarcity.sh "$file" | ./influx.sh
	done
	sleep 180
done

#!/bin/sh
gnuplot -p -e "set xdata time; set timefmt '%s'; set format x '%H:%M'; set xlabel 'time'; offset=$(date +%s -d '1 Jan 1970'); plot '<cat' using (\$1 - offset):2 title 'Power?'"

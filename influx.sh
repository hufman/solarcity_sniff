#!/bin/sh

host="myopia.alucodev.net"
db="energy"
measurement="solarcity"

while read line; do
        timestamp=$(echo "$line" | awk '{print $1 * 1000 * 1000 * 1000}')
        value=$(echo "$line" | awk '{print $2}')
        curl -X POST "http://$host:8086/write?db=$db" --data-binary "$measurement value=$value $timestamp"
done


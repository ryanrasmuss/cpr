#!/bin/bash

./cpr.sh login 192.168.1.20 443 admin
./cpr.sh show-hosts details-level full
python3 parse-hosts.py
./cpr.sh delete-host -csv deletehosts.csv
./cpr.sh publish
sleep 5
./cpr.sh logout

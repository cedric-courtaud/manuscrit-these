#!/usr/bin/env bash

FEATURES=('b' 'b Q' 'b Q tau' 'B' 'B Q' 'B Q tau' 'L1' 'L1 Q' 'L1 Q tau')

for f in "${FEATURES[@]}";do
  IFS=' '; read -a array <<< $f
  fname=$(IFS='_' ; echo "${array[*]}")
  echo $f
  python regression-results.py --features "$f" -o $1/${fname}.pdf
done

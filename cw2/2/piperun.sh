#! /bin/bash
test=(1)
# shellcheck disable=SC2068
for test in ${test[@]}
do
  python3 Receiver2.py '7777' 'test1.jpg' & python3 Sender2.py '127.0.0.1' '7777' 'test.jpg' "$1"
  wait
done
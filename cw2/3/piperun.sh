#! /bin/bash
test=(1 2 3 4 5)
# shellcheck disable=SC2068
for test in ${test[@]}
do
#  python3 Receiver3.py '7777' 'test1.jpg' & python3 Sender3.py '127.0.0.1' '7777' 'test.jpg' "$1" '32'
  python3 Receiver3.py '7777' 'test1.jpg' & python3 Sender3.py '127.0.0.1' '7777' 'test.jpg' '210' "$1"
  wait
done

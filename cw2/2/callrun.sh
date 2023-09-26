#! /bin/bash
# shellcheck disable=SC2091
para_list=(200 205 210 215 220 225)
# shellcheck disable=SC2068
for para in ${para_list[@]}
do
  echo "exec ${para}"
  source  ./piperun.sh "${para}"
  wait
done
#! /bin/bash
# shellcheck disable=SC2091
para_list=(1 2 4 8 16 32)
#para_list=(250 300 350)
# shellcheck disable=SC2068
for para in ${para_list[@]}
do
  echo "exec ${para}"
  source  ./piperun.sh "${para}"
  wait
done
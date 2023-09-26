#! /bin/bash
sudo tc qdisc del dev lo root;
echo "clear tc";
sudo tc qdisc add dev lo root netem loss "$1"% delay "$2"ms rate "$3"mbit;
echo "set tc loss $1% delay $2ms rate $3mbit";
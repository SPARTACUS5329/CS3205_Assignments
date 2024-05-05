#!/bin/bash

bandwidth=100
declare -a latencies=(50 100 150 200 250 500)
declare -a losses=(0.1 0.5 1 1.5 2 5)
declare -a methods=("GBN" "SW" "SR")

rm gbn.txt
rm sw.txt

# Limit the bandwidth to 100kBps
tc qdisc add dev eth0 root handle 1:0 netem rate 800kbit

rows=${#latencies[@]}
columns=${#losses[@]}

for ((i = 0; i < rows; i++)); do
	latency=${latencies[$i]}
	# Set the latency
	tc qdisc change dev eth0 root netem delay ${latency}ms 10ms distribution normal
	for ((j = 0; j < columns; j++)); do
		loss=${losses[$j]}
		# Set the packet loss
		tc qdisc change dev eth0 root netem loss ${loss}%
		for method in "${methods[@]}"; do
			echo "Starting $method for $latency $loss%"
			case $method in
				SW)
					python3 receiver.py out.jpeg $1 >> sw.txt &
					pid1=$!
					python3 sender.py loco.jpeg SW $1 &
					pid2=$!
					wait $pid1
					wait $pid2
					;;
				GBN)
					python3 receiver.py out.jpeg $1 >> gbn.txt &
					pid1=$!
					python3 sender.py loco.jpeg GBN 10 $1 &
					pid2=$!
					wait $pid1
					wait $pid2
					;;
				SR)
					echo "Not implemented yet"
					;;
			esac
			echo "Finished $method done for $latency $loss%"
		done
	done
done

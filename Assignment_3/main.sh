#!/bin/bash


bandwidth=100
declare -a latencies=(50 100 150 200 250 500)
declare -a losses=(0.1 0.5 1 1.5 2 5)
declare -a methods=("SW" "GBN" "SR")

# Limit the bandwidth to 100kBps
tc qdisc add dev eth0 root handle 1:0 netem rate 800kbit

rows=${#latencies[@]}
columns=${#losses[@]}

declare -A sw 
declare -A gbn 
declare -A sr 

declare -a results=($sw $gbn $sr)

for ((i = 0; i < rows; i++)); do
	latency=${latencies[$i]}
	# Set the latency
	tc qdisc change dev eth0 root netem delay ${latency}ms 10ms distribution normal
    for ((j = 0; j < columns; j++)); do
		loss=${losses[$j]}
		# Set the packet loss
		tc qdisc change dev eth0 root netem loss ${loss}%
		for method in "${methods[@]}"; do
			case $method in
				SW)
					sw[$i,$j]=$(python3 receiver.py out.jpeg &)
					pid1=$!
					python3 sender.py loco.jpeg SW &
					pid2=$!
					;;
				GBN)
					gbn[$i,$j]=$(python3 receiver.py out.jpeg &)
					pid1=$!
					python3 sender.py loco.jpeg GBN 10 &
					pid2=$!
					;;
				SR)
					echo "Not implemented yet"
					;;
			esac
			wait $pid1
			wait $pid2
			echo "$method done for $latency $loss%"
		done
	done
done

for res in "${results[@]}"; do 
	for row in "${res[@]}"; do
		for element in "${row[@]}"; do
			echo "${element} "
    	done
    	echo
	done
	echo "\n\n"
done

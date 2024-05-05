# Assignment 3

### Command to run:

`chmod +x ./main.sh && ./main.sh 0`

### Results

<div style="display: flex;">
    <img src="image/README/1714928083541.png" alt="Go Back N" height="50%" width="50%">
    <img src="image/README/1714928107851.png" alt="Stop and Wait" height="50%" width="50%">
</div>

### Commands under the hood

1. `python3 receiver.py [-fileName] [-debugCode] >> {method}.txt`

   1. `fileName`: The file to which the sender's packets are copied
   2. `debugCode`
      1. `0`: No debug outputs
      2. `1`: Debug outputs are logged to stdout
2. `python3 sender.py [-fileName] [-method] [-windowSize] [-debugCode]`

   1. `fileName`: File to read from to create the packets
   2. `method`
      1. `SW`: Stop and Wait
      2. `GBN`: Go Back N
   3. `windowSize`
      1. Need to mention only if `method` == `GBN`
   4. `debugCode`
      1. `0`: No debug outputs
      2. `1`: Debug outputs are logged to stdout
3. `python3 plot.py`
4. `tc qdisc add dev eth0 root handle 1:0 netem rate 800kbit`
5. `tc qdisc change dev eth0 root netem delay ${latency}ms 10ms distribution normal`
6. `tc qdisc change dev eth0 root netem loss ${loss}%`

**Disclaimer:** There was a resource issue while running the batch script, so it was run in batches to get the values of the download time.

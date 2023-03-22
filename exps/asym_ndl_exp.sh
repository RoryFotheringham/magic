#!/usr/bin/env bash

source ./../venv/bin/activate
echo "" > asym_ndl_res.txt

for DEPTH in 3 4 5 6;
do 
	echo "=========| k = 15 , depth = $DEPTH |=============" >> asym_ndl_res.txt;
	for SEED in 0 1 2 3 0 1;
	do
		python ./../synthesis_loop.py 15 $DEPTH $SEED 1 1 1 >> asym_ndl_res.txt;
		echo " " >> asym_ndl_res.txt;
	done;
done 
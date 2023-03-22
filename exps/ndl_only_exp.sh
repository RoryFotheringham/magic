#!/usr/bin/env bash

source ./../venv/bin/activate
echo "" > ndl_only_res.txt

for DEPTH in 3 4 5 6;
do 
	echo "=========| k = 15 , depth = $DEPTH |=============" >> ndl_only_res.txt;
	for SEED in 0 1 2 3 0 1;
	do
		python ./../synthesis_loop.py 15 $DEPTH $SEED 1 1 0 >> ndl_only_res.txt;
		echo " " >> ndl_only_res.txt;
	done;
done 
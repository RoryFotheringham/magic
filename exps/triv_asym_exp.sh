#!/usr/bin/env bash

source ./../venv/bin/activate


for DEPTH in 5 6;
do 
	echo "=========| k = 15 , depth = $DEPTH |=============" >> triv_asym_res.txt;
	for SEED in 0 1 2 3 0 1;
	do
		python ./../synthesis_loop.py 15 $DEPTH $SEED 1 0 1 >> triv_asym_res.txt;
		echo " " >> triv_asym_res.txt;
	done;
done 
#!/usr/bin/env bash

source venv/bin/activate
echo "" > cut_test.txt

for CUTS in 1 2 3;
do 
	echo "=========| k = 15 , depth = $DEPTH |=============" >> cut_test.txt;
	for SEED in 0 1 2 3;
	do
		python synthesis_loop.py 15 4 $SEED $CUTS>> cut_test.txt;
		echo " " >> cut_test.txt;
	done;
done 
	


#!/usr/bin/env bash

source venv/bin/activate
echo "" > ndl_test.txt

for NDL in 1 0;
do 
	echo "=========| k = 15 , depth = 4, ndl = $NDL, cuts = 1 |=============" >> ndl_test.txt;
	for SEED in 0 1 2 3 0 1 2 3 0 1 2 3 0;
	do
		python synthesis_loop.py 15 4 $SEED 1 $NDL  >> ndl_test.txt;
		echo " " >> ndl_test.txt;
	done;
done 
	
#!/bin/bash

## Give the Job a descriptive name
#PBS -N makejob

## Output and error files
#PBS -o makejob.out
#PBS -e makejob.err

## How many machines should we get?
#PBS -l nodes=1

## Start
## Load appropriate module
module load openmpi/1.8.3

## Run make in the src folder (modify properly)
cd /home/parallel/parlab05/a1/
make

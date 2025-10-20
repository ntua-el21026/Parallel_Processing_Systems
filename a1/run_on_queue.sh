#!/bin/bash

## Give the Job a descriptive name
#PBS -N life_par

## Output and error files
#PBS -o life_par.out
#PBS -e life_par.err

## How many machines should we get?
#PBS -l nodes=1:ppn=8

## How long should the job run for?
#PBS -l walltime=01:00:00

## Module Load
module load openmp

## Defaults if not passed via -v
: "${THREADS:=8}"
: "${N:=1024}"
: "${STEPS:=1000}"

## Start
cd /home/parallel/parlab05/a1/ || exit 1

# --- OpenMP runtime settings ---
export OMP_NUM_THREADS="${THREADS}"   # 1,2,4,6,8 per the assignment

# Run and capture outputs by config
RESULT_DIR="benchmarks/N${N}_T${THREADS}"
mkdir -p "${RESULT_DIR}"

./life_par "${N}" "${STEPS}" \
  > "${RESULT_DIR}/life_${THREADS}_${N}.out" \
  2> "${RESULT_DIR}/life_${THREADS}_${N}.err"


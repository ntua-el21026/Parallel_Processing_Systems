#!/bin/bash
#PBS -q parlab
#PBS -N life_par
#PBS -o life_par.out
#PBS -e life_par.err
#PBS -l nodes=1:ppn=8
#PBS -l walltime=00:10:00

# OpenMP job — no MPI needed
module load openmpi/1.8.3

# Defaults if not passed via -v
: "${THREADS:=8}"
: "${N:=1024}"
: "${STEPS:=1000}"

cd /home/parallel/parlab05/a1/ || exit 1

# --- OpenMP runtime settings ---
export OMP_NUM_THREADS="${THREADS}"   # 1,2,4,6,8 per the assignment
export OMP_PROC_BIND=TRUE             # pin threads to CPUs (stable timing)
export OMP_PLACES=cores               # one “place” per core

# Optional: make scheduling explicit (matches default, but reproducible)
export OMP_SCHEDULE=static

# Run and capture outputs by config
RESULT_DIR="benchmarks/N${N}_T${THREADS}"
mkdir -p "${RESULT_DIR}"

./life_par "${N}" "${STEPS}" \
  > "${RESULT_DIR}/life_${THREADS}_${N}.out" \
  2> "${RESULT_DIR}/life_${THREADS}_${N}.err"


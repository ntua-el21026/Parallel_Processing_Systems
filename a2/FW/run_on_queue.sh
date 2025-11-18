#!/bin/bash

#PBS -N run_fw_sr_p

## Output error 
#PBS -o run_fw_sr_p.pbs_out
#PBS -e run_fw_sr_p.pbs_err

## Sandman, serial queue, 64 threads
#PBS -q serial
#PBS -l nodes=sandman:ppn=64

#PBS -l walltime=01:00:00

cd /home/parallel/parlab05/a2/FW

module load openmp 

N_VALUES="1024 2048 4096"

# Block size 
B=64

OUTDIR="benchmarks"
mkdir -p "$OUTDIR"

for N in $N_VALUES; do
    for T in 1 2 4 8 16 32 64; do
        
        export OMP_NUM_THREADS=$T
        echo "Running N=$N, B=$B, threads=$T"
        
        #outputs
        OUT="${OUTDIR}/fw_sr_p_N${N}_T${T}.out"
        ERR="${OUTDIR}/fw_sr_p_N${N}_T${T}.err"
        
        #  - stdout → OUT
        #  - stderr → ERR
        ./fw_sr_p "$N" "$B" >"$OUT" 2>"$ERR"
    done
done


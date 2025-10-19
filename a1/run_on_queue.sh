# run_on_queue.sh
#!/bin/bash
#PBS -q parlab
#PBS -N life_par
#PBS -o life_par.out
#PBS -e life_par.err
#PBS -l nodes=1:ppn=8
#PBS -l walltime=00:10:00

# OpenMP job — no MPI needed
module load openmpi/1.8.3

cd /home/parallel/parlab05/a1/ || exit 1

# THREADS and N come from qsub -v
export OMP_NUM_THREADS="${THREADS}"

RESULT_DIR="benchmarks/N${N}_T${THREADS}"
mkdir -p "${RESULT_DIR}"

./life_par "${N}" 1000 \
  > "${RESULT_DIR}/life_${THREADS}_${N}.out" \
  2> "${RESULT_DIR}/life_${THREADS}_${N}.err"


#!/bin/bash

#PBS -N run_kmeans
#PBS -o run_kmeans.out
#PBS -e run_kmeans.err
#PBS -l nodes=1:ppn=64
#PBS -l walltime=01:00:00

# Submission details
# usage—no affinity (default): qsub -q serial -l nodes=sandman:ppn=64 -v THREADS=32,BIN=omp_naive_kmeans run_on_queue.sh
# with default affinity (bind 0..T-1): qsub -q serial -l nodes=sandman:ppn=64 -v THREADS=32,AFFINITY=default,BIN=omp_naive_kmeans run_on_queue.sh
# BIN=seq_kmeans|omp_naive_kmeans|omp_reduction_kmeans
# optional VARS: SIZE=256,COORDS=16,CLUSTERS=32,LOOPS=10

set -euo pipefail
cd /home/parallel/parlab05/a2/kmeans || exit 1

: "${BIN:=seq_kmeans}"
: "${SIZE:=256}"
: "${COORDS:=16}"
: "${CLUSTERS:=32}"
: "${LOOPS:=10}"
: "${THREADS:?Set THREADS via qsub -v THREADS=...}"
: "${AFFINITY:=none}"

export OMP_NUM_THREADS="${THREADS}"
AFF_LABEL="noaff"
if [[ "${AFFINITY,,}" == "default" ]]; then
  CPUSET="$(seq 0 $((THREADS-1)) | paste -sd' ' -)"
  export GOMP_CPU_AFFINITY="${CPUSET}"
  AFF_LABEL="aff"
else
  unset GOMP_CPU_AFFINITY || true
fi

BENCH_ROOT="/home/parallel/parlab05/a2/kmeans/benchmarks"
case "${BIN}" in
  *seq*)                BENCH_SUBDIR_BASE="serial" ;;
  *naive*)              BENCH_SUBDIR_BASE="naive" ;;
  *reduction*|*copied*) BENCH_SUBDIR_BASE="reduction" ;;
  *)                    BENCH_SUBDIR_BASE="other" ;;
esac
BENCH_SUBDIR="${BENCH_SUBDIR_BASE}/${AFF_LABEL}"

RUN_TAG="S${SIZE}_N${COORDS}_C${CLUSTERS}_L${LOOPS}_T${THREADS}"
RESULT_DIR="${BENCH_ROOT}/${BENCH_SUBDIR}/${RUN_TAG}"
mkdir -p "${RESULT_DIR}"

{
  echo "[run_on_queue] BIN=${BIN}"
  echo "[run_on_queue] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
  echo "[run_on_queue] GOMP_CPU_AFFINITY=${GOMP_CPU_AFFINITY:-<unset>}"
  echo "[run_on_queue] AFF_LABEL=${AFF_LABEL}"
  echo "[run_on_queue] Params: -s ${SIZE} -n ${COORDS} -c ${CLUSTERS} -l ${LOOPS}"
  echo "[run_on_queue] Result dir: ${RESULT_DIR}"
} | tee "${RESULT_DIR}/meta.txt"

"./${BIN}" -s "${SIZE}" -n "${COORDS}" -c "${CLUSTERS}" -l "${LOOPS}" \
  | tee "${RESULT_DIR}/output.txt"



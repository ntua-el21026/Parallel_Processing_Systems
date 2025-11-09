.KEEP_STATE:

CC = gcc

CFLAGS   = -Wall -Wextra -Wno-unused -O3 -std=gnu11
# Compile OpenMP sources with -fopenmp (+CFLAGS)
OMPFLAGS = $(CFLAGS) -fopenmp

# Link step includes -fopenmp so binaries link libgomp if any object used OpenMP
LDFLAGS  = -fopenmp

H_FILES  = kmeans.h
COMM_SRC = file_io.c util.c

# Build all variants
all: seq_kmeans omp_naive_kmeans omp_reduction_kmeans
seq_kmeans: main.o file_io.o util.o seq_kmeans.o
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

omp_naive_kmeans: main.o file_io.o util.o omp_naive_kmeans.o
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

omp_reduction_kmeans: main.o file_io.o util.o omp_reduction_kmeans.o
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

main.o: main.c $(H_FILES)
	$(CC) $(CFLAGS) -c $< -o $@

seq_kmeans.o: seq_kmeans.c $(COMM_SRC) $(H_FILES)
	$(CC) $(CFLAGS) -c $< -o $@

# OpenMP objects use OMPFLAGS so pragmas are honored
omp_naive_kmeans.o: omp_naive_kmeans.c $(COMM_SRC) $(H_FILES)
	$(CC) $(OMPFLAGS) -c $< -o $@

omp_reduction_kmeans.o: omp_reduction_kmeans.c $(COMM_SRC) $(H_FILES)
	$(CC) $(OMPFLAGS) -c $< -o $@

file_io.o: file_io.c
	$(CC) $(CFLAGS) -c $< -o $@

util.o: util.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf *.o seq_kmeans omp_naive_kmeans omp_reduction_kmeans


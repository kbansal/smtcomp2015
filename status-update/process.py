#!/bin/python

from __future__ import print_function

import zipfile
import csv
import os.path
import math
import sys
import pickle


DIR="raw/"
if len(sys.argv) == 2:
    job_ids = [int(sys.argv[1])]
else:
    job_ids= [2509, 2510, 2511, 2512, 2514,
              2515, 2517, 2608, 2609, 2610,
              2669, 2670, 2671, 2672, 2700,
              2701, 2733, 2734, 2735, 2736,
              2737]

solved_threshold = 2
assert solved_threshold >= 1

LOG_ERROR = "process_errors.txt"
LOG_CORRECT = "process_fornextstep.txt"
LOG_FULL = "process_full.txt"

log_error = open(LOG_ERROR, 'w')
log_correct = open(LOG_CORRECT, 'w')
log_full = open(LOG_FULL, 'w')

# does not have to be pretty
starexeccsvheader=["pair id",
                   "benchmark",
                   "benchmark id",
                   "solver",
                   "solver id",
                   "configuration",
                   "configuration id",
                   "status",
                   "cpu time",
                   "wallclock time",
                   "memory usage",
                   "result",
                   "expected"]

header_pos = dict()
for i in xrange(len(starexeccsvheader)):
    header_pos[starexeccsvheader[i]] = i

def starExecZipToCsv(job_zip_filename, job_filename):
    assert zipfile.is_zipfile(job_zip_filename)
    zf = zipfile.ZipFile(job_zip_filename, 'r')
    rows = []
    try:
        data = zf.open(job_filename)
        csvreader = csv.reader(data, delimiter=',', quotechar='|')
        header = csvreader.next()
        assert header == starexeccsvheader

        for row in csvreader:
            rows.append(row)
    finally:
        zf.close()
    return rows

def starExecOutputApply(job_output_filename, val_fn_pairs, func, aux):
    assert zipfile.is_zipfile(job_output_filename)
    zf = zipfile.ZipFile(job_output_filename, 'r')
    try:
        for (val,fn) in val_fn_pairs:
            fnzf = zf.open(fn, 'r')
            try:
                func(val, fnzf, aux)
            finally:
                fnzf.close()
    finally:
        zf.close()


def isConfiguration(config, row):
    return row[header_pos["configuration"]] == config

def isSatOrUnsat(row):
    res  = row[header_pos["result"]]
    return res == "sat" or res == "unsat"

def getResult(row):
    return row[header_pos["result"]]

def getSolverAndConfiguration(row):
    return row[header_pos["solver"]]+":"+row[header_pos["configuration"]]

def setEquality(s,t):
    return s.issubset(t) and s.issuperset(t)

def toPairIds(rows):
    pairIdMap = dict ()
    for row in rows:
        pairIdMap[ row[header_pos["pair id"]] ] = row
    return pairIdMap

def keyMatchesMap(rows, key):
    pos = header_pos[key]
    matchesMap = dict()
    for row in rows:
        keyval = row[pos]
        if keyval not in matchesMap:
            matchesMap[keyval] = []
        assert keyval in matchesMap
        matchesMap[keyval].append(row)
    return matchesMap
    

def configurationsMap(rows):
    return keyMatchesMap(rows, "configuration")

def benchmarkMap(rows):
    return keyMatchesMap(rows, "benchmark")

CACHEFILE="process_cache.pycache"
readCache = False
writeCache = False

original_rows = None

if readCache:
    if os.path.isfile(CACHEFILE):
        with open(CACHEFILE, 'rb') as input:
            original_rows = pickle.load(input)

if not original_rows:
    original_rows = []
    for job_id in job_ids:
        job_zip_filename = DIR + "Job"+str(job_id)+"_info.zip"
        job_filename = "Job"+str(job_id)+"_info.csv"
        print("Reading " + job_zip_filename)
        original_rows += starExecZipToCsv(job_zip_filename, job_filename)

    if writeCache:
        with open(CACHEFILE, 'wb') as output:
            pickle.dump(original_rows, output, pickle.HIGHEST_PROTOCOL)


configurationidSolverMap = {}
for cid, cidrows in keyMatchesMap(original_rows, "configuration id").iteritems():
    configurationidSolverMap[cid] = getSolverAndConfiguration(cidrows[0])

benchmarks = benchmarkMap(original_rows)

def print_details(benchmark, solved, outputfile, addnlmsg=None):
    print("Benchmark: " + benchmark, file=outputfile)
    if addnlmsg:
        print(addnlmsg, file=outputfile)
    for s,r in solved:
        print("  \""+r+"\" is what "+configurationidSolverMap[s] + " believes.", file=outputfile)
    print("", file=outputfile)

total_num = len(benchmarks)
current_num = 0

for benchmark, benchmarkrows in benchmarks.iteritems():

    current_num = current_num + 1
    if(current_num % 10000 == 0):
        print(str(current_num) + " / " + str(total_num))
    
    solvers = keyMatchesMap(benchmarkrows, "configuration id")

    solved = []
    
    for solver, solverrows in solvers.iteritems():
        assert len(solverrows) == 1, print(solverrows)
        if isSatOrUnsat(solverrows[0]):
            solved += [(solver, getResult(solverrows[0]))]

    if len(solved) >= solved_threshold:
        if not all(r == solved[0][1] for s,r in solved):
            addnlmsg="ERROR: solvers don't agree on correct answer"
            print_details(benchmark, solved, log_error, addnlmsg)
            print_details(benchmark, solved, log_full, addnlmsg)
        else:
            addnlmsg=(str(len(solved))+" of "+str(len(solvers))+
                      " succeeded, and all agreed.")
            print_details(benchmark, solved, log_full, addnlmsg)
            print(benchmark + ", " + solved[0][1], file=log_correct)

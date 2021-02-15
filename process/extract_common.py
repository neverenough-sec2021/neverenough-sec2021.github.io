#!/usr/bin/env python

import os
import sys
import json
import logging
import subprocess

from multiprocessing import Pool, cpu_count
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def run(json_stats_name, worker_func):
    args = get_args()
    setup_logging(args.logfile)

    jobs = get_jobs(args, json_stats_name)
    worker_pool = Pool(args.cpus)

    logging.info("Loading and processing tgen json data...")
    results = parallelize(worker_pool, worker_func, jobs)
    logging.info("Done processing! Got {} results".format(len(results)))

    logging.info("All done!")

def parallelize(worker_pool, func, work, batch_size=10000):
    all_results = []
    work_batches = [work[i:i+batch_size] for i in range(0, len(work), batch_size)]

    logging.info("Parallelizing {} work tasks in {} batch(es)".format(len(work), len(work_batches)))

    for i, work_batch in enumerate(work_batches):
        try:
            logging.info("Running batch {}/{}".format(i+1, len(work_batches)))
            results = worker_pool.map(func, work_batch)
            all_results.extend(results)
        except KeyboardInterrupt:
            print >> sys.stderr, "interrupted, terminating process pool"
            worker_pool.terminate()
            worker_pool.join()
            sys.exit(1)

    return all_results

def make_directories(path):
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)

def get_experiment_name(filepath):
    parts = filepath.split('/')
    for p in parts:
        if "shadowtor-" in p:
            return p
    return "unknown"

def get_jobs(args, json_stats_name):
    logging.info("Searching for tgen stats files in {}".format(args.inpath))
    jobs = []
    for root, dirs, files in os.walk(args.inpath):
        for name in files:
            if json_stats_name in name:
                s = os.path.join(root, name)
                logging.info("Found {}".format(s))
                exp = get_experiment_name(s)
                jobs.append([root, name, exp, args.outpath])
    logging.info("Found {} total tgen stats files".format(len(jobs)))
    return jobs

def load_json(data_path):
    filename = os.path.abspath(os.path.expanduser(data_path))
    if filename.endswith(".xz"):
        xzcatp = subprocess.Popen(["xzcat", filename], stdout=subprocess.PIPE)
        data = json.load(xzcatp.stdout)
    else:
        with open(filename, 'r') as fin:
            data = json.load(fin)
    return data

def load_txt(data_path):
    filename = os.path.abspath(os.path.expanduser(data_path))
    data = []
    if filename.endswith(".xz"):
        xzcatp = subprocess.Popen(["xzcat", filename], stdout=subprocess.PIPE)
        for line in xzcatp.stdout:
            data.append(str(line.decode('UTF-8').strip()))
    else:
        with open(filename, 'r') as fin:
            for line in fin:
                data.append(str(line.decode('UTF-8').strip()))
    return data

def setup_logging(logfilename=None):
    my_handlers = []

    stdout_handler = logging.StreamHandler(sys.stdout)
    my_handlers.append(stdout_handler)

    if logfilename != None:
        file_handler = logging.FileHandler(filename=logfilename)
        my_handlers.append(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(created)f [extractor] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=my_handlers,
    )

    msg = "Logging system initialized! Logging events to stdout"
    if logfilename != None:
        msg += " and to '{}'".format(logfilename)
    logging.info(msg)

class CustomHelpFormatter(ArgumentDefaultsHelpFormatter):
    # adds the 'RawDescriptionHelpFormatter' to the ArgsDefault one
    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

def get_args():
    parser = ArgumentParser(
            description='Extract plot data from tgen analysis json files',
            formatter_class=CustomHelpFormatter)

    parser.add_argument('-i', '--inpath', help="Path to a root directory containing multiple tgen experiments", metavar="PATH", default=".")
    parser.add_argument('-o', '--outpath', help="Path to store the output data", metavar="PATH", default="plot_data")
    parser.add_argument('-c', '--cpus', help="Number of CPU workers to use", metavar="N", type=int, default=cpu_count())
    parser.add_argument('-l', '--logfile', help="Name of the file to store log output in addition to stdout", metavar="PATH", default="extractor.log")

    args = parser.parse_args()
    return args

#!/usr/bin/env python

import os
import sys
import json
import lzma
import logging

from multiprocessing import Pool, cpu_count
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from stem import Flag
from stem.descriptor import parse_file
from stem.descriptor import DocumentHandler
from stem.version import Version

## process consensus files from:
## https://collector.torproject.org/archive/relay-descriptors/consensuses/consensuses-2019-01.tar.xz
## To extract relay churn over time

def main():
    args = get_args()
    setup_logging(args.logfile)

    cons_paths = get_file_list(args.consensuses)

    worker_pool = Pool(cpu_count())

    logging.info("Processing {} consensus files...".format(len(cons_paths)))
    results = parallelize(worker_pool, process_cons_file, cons_paths)

    logging.info("Merging results from {} consensus files...".format(len(results)))
    churn = merge_results(results)

    logging.info("Saving churn data to disk as json")

    with lzma.open('data/tor/relay-churn.json.xz', 'wt') as outf:
        json.dump(churn, outf, indent=2)

    logging.info("All done!")

# this func is run by helper processes in process pool
def process_cons_file(path):
    net_status = next(parse_file(path, document_handler='DOCUMENT', validate=False))

    assert net_status.valid_after != None

    cons_bw_sum = 0
    relays = set()

    for (fp, router_entry) in net_status.routers.items():
        if router_entry.bandwidth != None:
            if int(router_entry.bandwidth) > 0:
                relays.add(fp)

    result = {
        'pub_ts': float(net_status.valid_after.strftime("%s")),
        'relays': list(relays), # Objects of type set are not JSON serializable
    }

    return result

def merge_results(results):
    churn = {}

    for result in results:
        if result is None: continue
        churn[float(result['pub_ts'])] = result['relays']

    return churn

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

def setup_logging(logfilename):
    file_handler = logging.FileHandler(filename=logfilename)
    stdout_handler = logging.StreamHandler(sys.stdout)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(created)f [collector-parser] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[file_handler, stdout_handler],
    )

    logging.info("Logging system initialized! Logging events to stdout and to '{}'".format(logfilename))

def get_file_list(dir_path):
    file_paths = []
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            file_paths.append(os.path.join(root, filename))
    return file_paths

def get_args():
    parser = ArgumentParser(
            description='Parse a set of archived collector consensus and server descriptors',
            formatter_class=CustomHelpFormatter)

    parser.add_argument('consensuses', help="Path to a directory containing multiple consensus files", metavar="PATH")
    parser.add_argument('-l', '--logfile', help="Name of the file to store log output in addition to stdout", metavar="PATH", default="parser.log")

    args = parser.parse_args()
    return args

class CustomHelpFormatter(ArgumentDefaultsHelpFormatter):
    # adds the 'RawDescriptionHelpFormatter' to the ArgsDefault one
    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

if __name__ == "__main__":
    sys.exit(main())

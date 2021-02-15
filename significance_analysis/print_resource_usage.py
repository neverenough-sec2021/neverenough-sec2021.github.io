#!/usr/bin/python

import sys
import logging

from datetime import timedelta
from numpy import median

from plot_common import *

def main():
    args = get_args()
    setup_logging(args.logfile)
    run(args)
    logging.info("All done!")

def run(args):
    logging.info("Running")
    logging.info("Searching for stats files in {}".format(args.inpath))
    stats_paths = get_filepaths(args.inpath, "resource_usage")
    logging.info("Found {} total stats files".format(len(stats_paths)))

    db = {}

    for path in stats_paths:
        logging.info("Loading data from {}".format(path))

        perc = get_load_percentage(path)
        db.setdefault(perc, {"max_gib_used":[], "seconds":[]})

        data = load_json(path)

        db[perc]["max_gib_used"].append(float(data["ram"]["max_gib_used"]))
        db[perc]["seconds"].append(float(data["run_time"]["seconds"]))

    stats_filename = "resource_usage.txt"
    if os.path.exists(stats_filename):
        os.remove(stats_filename)

    keys_sorted = sorted(db.keys())
    labels = [str(perc)+"\%" for perc in keys_sorted]
    dataset = [db[perc] for perc in keys_sorted]

    for i, _ in enumerate(dataset):
        log_stats(stats_filename, "ram usage gib:", dataset[i]["max_gib_used"])

    for i, _ in enumerate(dataset):
        log_stats(stats_filename, "runtime in seconds:", dataset[i]["seconds"])

    with open(stats_filename, 'a') as outf:
        for i, _ in enumerate(dataset):
            s_med = median(dataset[i]["seconds"])
            td = timedelta(seconds=s_med)
            print("median runtime in human: runtime={}".format(str(td)), file=outf)

if __name__ == "__main__":
    sys.exit(main())

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
    stats_paths = get_filepaths(args.inpath, "resource_usage.json")
    logging.info("Found {} total stats files".format(len(stats_paths)))

    db = {}

    for path in stats_paths:
        logging.info("Loading data from {}".format(path))

        scale = get_net_scale(path)
        load = get_load_percentage(path)
        db.setdefault(scale, {}).setdefault(load, {"max_gib_used":[], "seconds":[]})

        data = load_json(path)

        db[scale][load]["max_gib_used"].append(float(data["ram"]["max_gib_used"]))
        db[scale][load]["seconds"].append(float(data["run_time"]["seconds"]))

    stats_filename = "resource_usage.txt"
    if os.path.exists(stats_filename):
        os.remove(stats_filename)

    for scale in sorted(db.keys()):
        for load in sorted(db[scale].keys()):
            dataset = db[scale][load]

            s_med = median(dataset["seconds"])
            td = timedelta(seconds=s_med)

            with open(stats_filename, 'a') as outf:
                print(f"########## Stats for scale={scale} load={load} ##########", file=outf)

            log_stats(stats_filename, f"ram usage gib: ", dataset["max_gib_used"])
            log_stats(stats_filename, f"runtime in seconds: ", dataset["seconds"])

            with open(stats_filename, 'a') as outf:
                print(f"median runtime in human: {str(td)}", file=outf)
                print(f"----------\n", file=outf)

if __name__ == "__main__":
    sys.exit(main())

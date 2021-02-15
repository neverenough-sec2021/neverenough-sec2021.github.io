#!/usr/bin/python

import sys
import logging

from datetime import timedelta, datetime
from numpy import median

def main():
    for size in ['0.31', '1.0']:
        is_100 = size == '1.0'
        upper = 3 if is_100 else 10
        max_ram, bootstrap_time, total_time = [], [], []
        for i in range(1, upper+1):
            r, b, t = handlesim(f"data/shadowtor-{size}-{i}-1.0-seed1", is_100)
            max_ram.append(r)
            bootstrap_time.append(b)
            total_time.append(t)

        print(f"Network size {size}")
        print(f"Max RAM usage is: {max(max_ram)}")
        print(f"Max bootstrap time is: {max(bootstrap_time)}")
        print(f"Max total time is: {max(total_time)}")

def handlesim(dirpath, is_100):
    bootstrap_time, total_time = 0, 0
    with open(f"{dirpath}/runtime.dat", 'r') as inf:
        for line in inf:
            parts = line.strip().split()
            if parts[1] == "00:20:00.000000000":
                tparts = parts[0].split(':')
                bootstrap_time = 3600.0*int(tparts[0]) + 60.0*int(tparts[1]) + float(tparts[2])
            elif parts[1] == "00:45:00.000000000":
                tparts = parts[0].split(':')
                total_time = 3600.0*int(tparts[0]) + 60.0*int(tparts[1]) + float(tparts[2])

    ram = []
    with open(f"{dirpath}/memused.dat", 'r') as inf:
        for line in inf:
            s = line.strip()
            if len(s) > 0:
                ram.append(int(s))

    # 31% experiments continued to run after the period of interest
    if is_100:
        total_ram = (max(ram) - min(ram))/2**30
    else:
        total_ram = (max(ram[:int(total_time)]) - min(ram))/2**30
    return total_ram, bootstrap_time, total_time

if __name__ == "__main__":
    sys.exit(main())

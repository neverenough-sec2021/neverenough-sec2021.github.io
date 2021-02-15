### Overview

This page provides some general details about our experimental process, including the exact versions of software we used, how we stage and generate Tor models, and how we process the output.

Generally, our research follows this process:

  1. stage and generate some Tor network models using our methods from §3;
  1. simulate the models in Shadow;
  1. collect and process Shadow's output; and
  1. visualized the processed data.

Unfortunately, the size of the raw data files produced by Shadow are too large to distribute here. Instead, we provide the Tor model configuration bundles that are used as input to Shadow, and Shadow's output data after performing an intermediate processing step. The data that we provide can be used to reproduce the figures presented in the paper.

Please note that all of these steps have been simplified in and are handled directly by the latest version of [TorNetTools](https://github.com/shadow/tornettools). We provide details of the more manual process that we followed for posterity.

### Software Versions

The contributions we made as part of our work were merged as described on [the main page](/). However, we used slightly different versions of these tools when running experiments and collecting results for this paper. We list here the exact commits that we used during our research for this paper:

  - [TorNetTools](https://github.com/shadow/tornettools) at commit [`c126160d5f2e16bff30e623b3a9f830e43801b5c`](https://github.com/shadow/tornettools/commit/c126160d5f2e16bff30e623b3a9f830e43801b5c)
  - [Shadow](https://github.com/shadow/shadow) at commit [`a7b7d49168d398b074c6ce38e203c1ef980fce51`](https://github.com/shadow/shadow/commit/a7b7d49168d398b074c6ce38e203c1ef980fce51)
  - [TGen](https://github.com/shadow/tgen) at commit [`8825a1500cda63e81499be95a60d2783267c39cd`](https://github.com/shadow/tgen/commit/8825a1500cda63e81499be95a60d2783267c39cd)
  - [OnionTrace](https://github.com/shadow/oniontrace) at commit [`6c467177306226bcaa82f73be4da388916f81198`](https://github.com/shadow/oniontrace/commit/6c467177306226bcaa82f73be4da388916f81198)
  - [Shadow-plugin-tor]() at commit [`3bb048d754833912a00576ddb072dd1ef644e9c8`](https://github.com/shadow/shadow-plugin-tor/commit/3bb048d754833912a00576ddb072dd1ef644e9c8)
  - [Tor]() at commit [`5030edfb534245ed3f7e6b476f38a706247f3cb8`](https://gitweb.torproject.org/tor.git/commit/?id=5030edfb534245ed3f7e6b476f38a706247f3cb8) (v0.3.5.8) with [this patch](/process/tor_neverenough.patch) applied

### Setting up Python

We used a variety of python modules to simplify our processing and visualization steps, which we installed into a virtual environment as follows:

```
python3 -m venv ~/venvs/nevenufenv
source ~/venvs/nevenufenv/bin/activate
pip3 install numpy scipy matplotlib

git clone https://github.com/shadow/tornettools
cd tornettools
git checkout -b nevenuf c126160d5f2e16bff30e623b3a9f830e43801b5c
pip3 install -r requirements.txt
pip3 install -I .
cd ..

git clone https://github.com/shadow/tgen
cd tgen
git checkout -b nevenuf 8825a1500cda63e81499be95a60d2783267c39cd
cd tools
pip3 install -r requirements.txt
pip3 install -I .
cd ../..

git clone https://github.com/shadow/oniontrace
cd oniontrace
git checkout -b nevenuf 6c467177306226bcaa82f73be4da388916f81198
cd tools
pip3 install -r requirements.txt
pip3 install -I .
cd ../..
```

### Tor Model Configs

Generating Tor models involves staging and generation.

#### Staging

We first run the staging phase by downloading Tor consensus, server descriptor, and Tor performance results and processing them as described in the [TorNetTools staging instructions](https://github.com/shadow/tornettools/blob/c126160d5f2e16bff30e623b3a9f830e43801b5c/README.md). Here we provide the staging files that we produced, covering Tor network state during the period from `2019-01-01` through `2019-01-31`:

  - [relayinfo_staging_2019-01-01--2019-02-01.json](/relayinfo_staging_2019-01-01--2019-02-01.json)
  - [userinfo_staging_2019-01-01--2019-02-01.json](/userinfo_staging_2019-01-01--2019-02-01.json)

#### Generation

Given the above staging files, we can generate any number of Tor models. We use a script similar to the one below for all Tor model configuration bundles that we use in §4, §5, and §6 in the paper, where we modified the `n`, `l`, and `v` parameters (in the for loops) according to the specific requirements for each section of the paper.

```
source ~/venvs/nevenufenv/bin/activate
base=/home/rjansen/tors/tor-0.4.3.6
export PATH=${PATH}:${base}/src/core/or:${base}/src/app:${base}/src/tools

OUT=configs

for n in 0.01 0.1 0.3 1.0
do
  for l in 1.0 1.2
  do
    for v in {1..100}
    do
      tornetgen generate \
        relayinfo_staging_2019-01-01--2019-02-01.json \
        userinfo_staging_2019-01-01--2019-02-01.json \
        tmodel-ccs2018.github.io \
        --network_scale ${n} \
        --load_scale ${l} \
        --prefix ${OUT}/shadowtor-${n}-${v}-${l}-config \
        --atlas /storage/rjansen/share/atlas.201801.shadow113.noloss.graphml.xml \
        --events BW,ORCONN,CIRC,STREAM
    done
  done
done
```

Notes:
- The `tornetgen` tool shown above was later renamed to `tornettools`.
- `tmodel-ccs2018.github.io` refers to a clone of [this github repo](https://github.com/tmodel-ccs2018/tmodel-ccs2018.github.io.git) from previous work.
- In the generated `shadow.config.xml` files, you will need to update the atlas path to point to your own local copy of [this atlas topology file](https://tmodel-ccs2018.github.io/data/shadow/network/atlas-lossless.201801.shadow113.graphml.xml.xz).

Unfortunately, we did not record the seeds that were used when generating the configs, so we cannot deterministically recreate them using [TorNetTools](https://github.com/shadow/tornettools). (The latest version of [TorNetTools](https://github.com/shadow/tornettools) has corrected this oversight.)

The [model validation](/model_validation), [significance analysis](/significance_analysis), and [performance analysis](/performance_analysis) pages describe the generated Tor model configuration bundles included in this repository.

### Simulating the Models in Shadow

We used the following to run the Shadow experiments. This assumes that Shadow, TGen, OnionTrace, and shadow-plugin-tor have been installed according to the installation instructions of each tool (see the software version links above).

After the Shadow, TGen, OnionTrace, and shadow-plugin-tor tools are installed, the following commands should be run *inside* of a Tor model configuration bundle directory, such as `shadowtor-0.1-1-1.0-config`.

```
dstat -cmstTy --fs --output dstat.log > /dev/null &
dstat_pid=$!

date > free.log
free -w -b -l -s 1 >> free.log &
free_pid=$!

shadow -w 32 shadow.config.xml | xz -T 2 > shadow.log.xz

kill ${free_pid}
kill ${dstat_pid}
date >> free.log
```

### Processing Shadow's Output

Shadow's output is processed into multiple steps: parsing the log files, extracting visualization data from the processed output, and plotting the results.

#### Parsing

We use the TGenTools and OnionTraceTools python modules (installed as described above) to parse the respective log files.

The following commands should be run *inside* of a model configuration directory, such as `shadowtor-0.1-1-1.0-config`.

```
source ~/venvs/nevenufenv/bin/activate

xz -T 0 -e -9 free.log
xz -T 0 -e -9 dstat.log

tgentools parse -m 0 shadow.data/hosts
oniontracetools parse -m 0 shadow.data/hosts -e ".*oniontrace\.1001\.log"
xzcat shadow.log.xz | pypy /home/rjansen/shadow/src/tools/parse-shadow.py -m 0 -
```

#### Extraction

In this phase, we extract visualization data from the parsing step to simplify our plotting scripts. The extraction scripts are provided in [the process directory in the repository](https://github.com/neverenough-sec2021/neverenough-sec2021.github.io/tree/main/process).

```
source ~/venvs/nevenufenv/bin/activate
dir=shadowtor-0.1-1-1.0-config

python3 extract_oniontrace_cbt.py -i ${dir} -o data
python3 extract_oniontrace_tput.py -i ${dir} -o data
python3 extract_resource_usage.py -i ${dir} -o data
python3 extract_tgen_errrate.py -i ${dir} -o data
python3 extract_tgen_rtt.py -i ${dir} -o data
python3 extract_tgen_ttb.py -i ${dir} -o data
```

The [model validation](/model_validation), [significance analysis](/significance_analysis), and [performance analysis](/performance_analysis) pages describe the extracted data included in this repository.

#### Plotting

The [model validation](/model_validation), [significance analysis](/significance_analysis), and [performance analysis](/performance_analysis) pages describe the scripts we used to produce the figures for the paper.

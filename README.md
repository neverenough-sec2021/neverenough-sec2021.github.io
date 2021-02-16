### Overview

This is the landing page for the following research publication:

**Once is Never Enough: Foundations for Sound Statistical Inference in Tor Network Experimentation**  
_Proceedings of [the 30th USENIX Security Symposium](https://www.usenix.org/conference/usenixsecurity21) (Sec 2021)_  
by [Rob Jansen](https://www.robgjansen.com), Justin Tracey, and [Ian Goldberg](https://cs.uwaterloo.ca/~iang)  
\[[Conference version](https://www.robgjansen.com/publications/neverenough-sec2021.pdf)\] \[[Extended version](https://arxiv.org/abs/2102.05196)\]

If you reference this paper or use any of the data or code provided on this site, please cite the paper. Here is a bibtex entry for latex users:

```
@inproceedings{neverenough-sec2021,
  author = {Rob Jansen and Justin Tracey and Ian Goldberg},
  title = {Once is Never Enough: Foundations for Sound Statistical Inference in {Tor} Network Experimentation},
  booktitle = {30th USENIX Security Symposium (Sec)},
  year = {2021},
  note = {See also \url{https://neverenough-sec2021.github.io}},
}
```

### Methods and Tools

In §3 of our paper, we describe our approach for producing models that accurately represent the composition and traffic characteristics of the public Tor network. In §4 of our paper, we describe enhancements we made to the Shadow simulator to improve its performance, scalability, and accuracy. In §5 of our paper, we describe analysis methods that allow us to make statistical statements about the results of Tor experiments.

We have distilled our contributions into the following tools. These have been merged upstream to the Shadow project so that the community may benefit from our work:

  - [TorNetTools](https://github.com/shadow/tornettools) as of [v1.1.0](https://github.com/shadow/tornettools/releases/tag/v1.1.0)
  - [Shadow](https://github.com/shadow/shadow) as of [v1.13.2](https://github.com/shadow/shadow/releases/tag/v1.13.2)
  - [TGen](https://github.com/shadow/tgen) as of [v1.0.0](https://github.com/shadow/tgen/releases/tag/v1.0.0)
  - [OnionTrace](https://github.com/shadow/oniontrace) as of [v1.0.0](https://github.com/shadow/oniontrace/releases/tag/v1.0.0)

Whether you are trying to reproduce our results or performing Tor research of your own, the best place to start is with our [TorNetTools](https://github.com/shadow/tornettools) artifact. This tool implements our modeling and analysis methods and will help you run Tor simulations in Shadow using best practices. TorNetTools will guide you through the following experimentation phases:

  - **stage**:     Process Tor metrics data for staging network generation
  - **generate**:  Generate TorNet network configurations
  - **simulate**:  Run a TorNet simulation in Shadow
  - **parse**:     Parse useful data from simulation log files
  - **plot**:      Plot previously parsed data to visualize results
  - **archive**:   Cleanup and compress Shadow simulation data

The tool includes an extensive help menu and [the GitHub page](https://github.com/shadow/tornettools) provides more details to help you get started.

### Experiments

The general experimental process that we used during our research is described on [the process page](/process). The specific Tor model configuration bundles and visualization data for each section of the paper are described separately as follows.

#### Model Validation

In §4 of our paper, we run some experiments to evaluate our modeling tools and Shadow improvements. More information about reproducing the analysis and graphs (in Figures 1, 2, and 3, and Table 2 in the paper) is available on [the model validation page](/model_validation).

#### Significance Analysis

In §5 of our paper, we describe an analysis methodology that allows us to compute confidence intervals over a set of simulations results, in order to make more informed inferences about Tor network performance. More information about reproducing the analysis and graphs (in Figures 4, 5, and 6 in the paper) is available on [the significance analysis page](/significance_analysis).

#### Performance Analysis Case Study

In §6 of our paper, we present the results of a case study of the effects of an increase in Tor usage on Tor client performance. More information about reproducing the analysis and graphs (in Figures 7 and 8 in the paper, and in Figures 9, 10, 11, and 12 in the full version) is available on [the performance analysis page](/performance_analysis).

# Automatic productivity report

As a mexican researcher I spend a lot of time writing productivity reports for many queries. For example, Conacyt, SNI, Politécnico, etc. Therefore, I decided to build an unified platform that can construct such reports using the lowest effort. The result is this project where the reports are built in latex using python as an intermediary language. In some sense I tried to imitate what Flask do for web pages.

One of the examples is the construction of my CV.

## Installation instructions

- Build a conda environment: report
```sh
conda create -n "report" python=3
```
- Activate environment
```sh
source activate report
```
- Install aditional packages
```sh
conda install jupyter numpy matplotblib
```
- Install other packages from pip
```sh
pip install bibtexparser
```


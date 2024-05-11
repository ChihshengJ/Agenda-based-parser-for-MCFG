# Agenda Based Parser for Multiple Context-Free Grammars

## Introduction

This Python package implements an agenda-based parser as described in [Shieber et al. 1995](https://doi.org/10.1016/0743-1066(95)00035-I) for Multiple Context Free Grammars (MCFG). The parser supports parsing complex hierarchical structures that are common in natural language and other structured data. The module consists of three parts, the grammar-related classes, the parser-related classes, and a tree structure for representing parse trees. There's also a comprehensive test suite that can be easily tested using `Pytest`



## Installation

You can install `mcfg-parser` directly from GitHub using pip:

```bash
pip install git+https://github.com/ChihshengJ/MCFG-parser.git
```

Alternatively, if you plan to contribute or modify the parser, clone the repository:

```bash
git clone https://github.com/your-github-username/mcfg-parser.git 
cd mcfg-parser
pip install -e .
```



## Usage

Below is an example on how to utilize this package in your parsing task. 

### Initialize a multiple context free grammar

```python
import grammar, tree, abparser
from copy import deepcopy

literal_rules=[
    "S(uv) -> NP(u) VP(v)",
    "S(uv) -> NPwh(u) VP(v)",
    "S(vuw) -> Aux(u) Swhmain(v, w)",
    "S(uvw) -> NPdisloc(u, v) VP(w)",
    "S(uwv) -> NPwhdisloc(u, v) VP(w)",
    "Sbar(uv) -> C(u) S(v)",
    "Sbarwh(v, uw) -> C(u) Swhemb(v, w)",
    "Sbarwh(u, v) -> NPwh(u) VP(v)",
    "Swhmain(v, uw) -> NP(u) VPwhmain(v, w)",
    "Swhmain(w, uxv) -> NPdisloc(u, v) VPwhmain(w, x)",
    "Swhemb(v, uw) -> NP(u) VPwhemb(v, w)",
    "Swhemb(w, uxv) -> NPdisloc(u, v) VPwhemb(w, x)",
    "Src(v, uw) -> NP(u) VPrc(v, w)",
    "Src(w, uxv) -> NPdisloc(u, v) VPrc(w, x)",
    "Src(u, v) -> N(u) VP(v)",
    "Swhrc(u, v) -> Nwh(u) VP(v)",
    "Swhrc(v, uw) -> NP(u) VPwhrc(v, w)",
    "Sbarwhrc(v, uw) -> C(u) Swhrc(v, w)",
    "VP(uv) -> Vpres(u) NP(v)",
    "VP(uv) -> Vpres(u) Sbar(v)",
    "VPwhmain(u, v) -> NPwh(u) Vroot(v)",
    "VPwhmain(u, wv) -> NPwhdisloc(u, v) Vroot(w)",
    "VPwhmain(v, uw) -> Vroot(u) Sbarwh(v, w)",
    "VPwhemb(u, v) -> NPwh(u) Vpres(v)",
    "VPwhemb(u, wv) -> NPwhdisloc(u, v) Vpres(w)",
    "VPwhemb(v, uw) -> Vpres(u) Sbarwh(v, w)",
    "VPrc(u, v) -> N(u) Vpres(v)",
    "VPrc(v, uw) -> Vpres(u) Nrc(v, w)",
    "VPwhrc(u, v) -> Nwh(u) Vpres(v)",
    "VPwhrc(v, uw) -> Vpres(u) Sbarwhrc(v, w)",
    "NP(uv) -> D(u) N(v)",
    "NP(uvw) -> D(u) Nrc(v, w)",
    "NPdisloc(uv, w) -> D(u) Nrc(v, w)",
    "NPwh(uv) -> Dwh(u) N(v)",
    "NPwh(uvw) -> Dwh(u) Nrc(v, w)",
    "NPwhdisloc(uv, w) -> Dwh(u) Nrc(v, w)",
    "Nrc(v, uw) -> C(u) Src(v, w)",
    "Nrc(u, vw) -> N(u) Swhrc(v, w)",
    "Nrc(u, vwx) -> Nrc(u, v) Swhrc(w, x)",
    "N(uv) -> N(u) N(v)",
    "PP(uv) -> P(u) NP(v)",
    "NP(uv) -> NP(u) PP(v)",
    "VP(uv) -> VP(u) PP(v)",
    "Dwh(which)",
    "Nwh(who)",
    "D(the)",
    "D(a)",
    "N(greyhound)",
    "N(human)",
    "N(saw)",
    "N(salmon)",
    "Vpres(saw)",
    "Vroot(see)",
    "Vpres(believes)",
    "Vroot(believe)",
    "Aux(does)",
    "Aux(did)",
    "C(that)",
    "P(with)"]

# customize these code for your task, but please make sure the types of the parameters are all correct
initiated_rules = {grammar.MCFGRule.from_string(r) for r in literal_rules}
variables = {i for r in initiated_rules for i in deepcopy(r.right_side) + ((deepcopy(r.left_side)),)}
start_variables = {i for i in 
                   {i for r in initiated_rules for i in deepcopy(r.right_side) + ((deepcopy(r.left_side)),)} 
                   if i.variable == 'S'}

grammar.MultipleContextFreeGrammar.parser_class = abparser.AgendaBasedParser
g = grammar.MultipleContextFreeGrammar(
                    alphabet={'the', 'a', 'greyhound', 'salmon', 'human', 'believe', 'believes', 'see', 'saw', 'who', 'which', 'does', 'did', 'that', 'with'},
                    variables=variables,
                    rules=initiated_rules,
                    start_variables=start_variables)
```

### Parse a sentence

```python
# call the grammar with recognize mode to get the boolean value indicating whether this sentence is grammatical or not with regard to your rules
mcfg(['the', 'human', 'that', 'believes', 'the', 'salmon', 'saw', 'the', 'greyhound'], mode="recognize")

# call the grammar with parse mode to get a set of parse trees that represents the parsing result
tree = mcfg(['the', 'human', 'saw', 'the', 'greyhound', 'with', 'the', 'salmon'], mode = 'parse')
if tree:
    for t in tree:
      print(t)
```

## Setting Up the Environment

This project uses `pyparsing` for parsing trees and `pytest` for running tests. To ensure compatibility and the success of installation, setting up an environment can be helpful. Follow the steps below to create and activate an environment for the project:

### Install Conda

If you do not have Conda installed, download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution).

### Create the Environment

Open your terminal and create a new Conda environment called `mcfg_parser_env` by running:

```bash
conda create --name mcfg_parser_env python=3.8 pyparsing pytest
```

### Activate the environment

```bash
conda activate mcfg_parser_env
```


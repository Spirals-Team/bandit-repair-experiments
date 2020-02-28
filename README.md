# Open-science Experimental Results

This repository contains the raw results of our experiments in the field of runtime repair and failure-oblivious computing.

Reference: [Exhaustive Exploration of the Failure-oblivious Computing Search Space](https://arxiv.org/pdf/1710.09722) ([doi:10.1109/ICST.2018.00023](https://doi.org/10.1109/ICST.2018.00023))

```bibtex
@inproceedings{durieux:hal-01624988,
 title = {Exhaustive Exploration of the Failure-oblivious Computing Search Space},
 author = {Durieux, Thomas and Hamadi, Youssef and Yu, Zhongxing and Baudry, Benoit and Monperrus, Martin},
 url = {https://arxiv.org/pdf/1710.09722},
 booktitle = {{ICST 2018 - 11th IEEE Conference on Software Testing, Validation and Verification}},
 year = {2018},
 doi = {10.1109/ICST.2018.00023},
}
```

## Repository architecture
```
results                     // the raw results
|- 2016-February            // the periode of execution
|-- bandit_exploration      // the bandit exploration experimentation
|--- collections360         // Bug ID
|---- 1454946524433.json    // the raw result of the execution
|---- ...
|--- ...
|-- exhaustive_exploration  // the exhaustive exploration experimentation
|--- collections360         
|---- ...
|--- ...
src                         // the scripts used the generate all figures
```


## Result format
```javascript
{
  "executions": [
    /* all laps */
    {
      "result": {
        "error": "<the exception>",
        "type": "<the oracle type>",
        "success": true
      },
      /* all decisions points */
      "locations": [{
        "sourceEnd": 12234,
        "executionCount": 0,
        "line": 352,
        "class": "org.apache.commons.collections.iterators.CollatingIterator",
        "sourceStart": 12193
      }],
      /* the runned test */
      "test": {
        "name": "testNullComparator",
        "class": "org.apache.commons.collections.iterators.TestCollatingIterator"
      },
      /* all decision made during the laps */
      "decisions": [{
        /* the location of the laps */
        "location": {
          "sourceEnd": 12234,
          "line": 352,
          "class": "org.apache.commons.collections.iterators.CollatingIterator",
          "sourceStart": 12193
        },
        /* the value used by the decision */
        "value": {
          "variableName": "leastObject",
          "value": "leastObject",
          "type": "int"
        },
        /* the value of the epsilon */
        "epsilon": 0.4,
        // the name of the strategy
        "strategy": "Strat4 VAR",
        "used": true,
        /* the decision type (new, best, random) */
        "decisionType": "new"
      }],
      "startDate": 1453918743999,
      "endDate": 1453918744165,
      "metadata": {"seed": 10}
    },
    ...
  ],
  "searchSpace": [
    /* all detected decisions */
    {
      "location": {
        "sourceEnd": 12234,
        "line": 352,
        "class": "org.apache.commons.collections.iterators.CollatingIterator",
        "sourceStart": 12193
      },
      "value": {
        "value": "1",
        "type": "int"
      },
      "epsilon": 0,
      "strategy": "Strat4 NEW",
      "used": false,
      "decisionType": "random"
    },
    ...
  ],
  "date": "Wed Jan 27 19:19:37 CET 2016"
}
```

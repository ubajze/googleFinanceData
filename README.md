# Get Google Finance data for specific stock ticker

## Overview

This script allow you to specify stock ticker and get basic data from Google Finance for that ticker. When you run a script, the script connects to the Google Finance and parse information. The information about specific ticker is then displayed in command line.

## Basic usage

To run a script, just go to command line and run program with the list of tickers that you want to inspect. You can run script without argument to get the help and some additional options.

```
python googleFinance.py GOOGL AAPL
Progress: [====================] 100%
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Ticker   | Range             | 52 week           | Open     | Vol / Avg.      | Mkt cap   | P/E     | Dividend   | Div. yield   | EPS     | Shares    | Beta   | Inst. own   |
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
AAPL     | 106.68 - 107.88   | 89.47 - 123.82    | 107.39   | 25.09M/32.37M   | 575.27B   | 12.56   | 0.57       | 2.12         | 8.56    | 5.39B     | 1.12   | 58%         |
GOOGL    | 787.23 - 794.72   | 617.84 - 813.88   | 792.00   | 1.20M/1.51M     | 533.62B   | 30.09   | -          | -            | 26.30   | 294.84M   | 1.03   | 82%         |
```

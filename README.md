# CSE 163 Final Project
#### Peter Gunarso and Brian Zhu

## Instructions for Gathering Data
Within the `scripts` directory, there are three usable scripts:
    
- `theworld2.py`
- `top.py`
- `bot.py`

To run the scripts, ensure that your terminal is in the `scripts` directory and that the directory `Final Project/data/{Rank}` exists.

`theworld2.py` ask for the account you are using, the associated api key, the league and rank you want to search, and the server you want to collect the data from.

`top.py` and `bot.py` gather the first and second halves of the data `theworld2.py` does. This way, data for one rank can be collected twice as fast using two api keys. The outputs of these scripts should be put together using `assemble.py`.
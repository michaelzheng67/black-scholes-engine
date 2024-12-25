# Multi-threaded Options Pricing Engine


### Overview
Wanted to play around with the new free-threaded mode in python 3.13. This repo works by spawning
multiple client processes to collect data, while a main server process running the 3.13t
interpreter spawns up threads to do the work of computing black-scholes options values and
displaying contracts where the values differ greatly.


### Setup

Create venv and install requirements:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then to run the repo:
```
cd scripts
chmod +x setup.sh
./setup.sh
```
*Note*:
This project is a work-in-progress. Things might subject to change without notice and documentations might not be up-to-date. 

## Required Hardware
[BOM Link](https://docs.google.com/spreadsheets/d/1xkdiwz52t9tl3BoCPHdAoMXMj6laNYFDfEBpR4JUP3w/edit?usp=sharing)

## Suggested Environment Setup
1. [Anaconda](https://www.anaconda.com/products/individual)
2. [PyCharm Community/Professional](https://www.jetbrains.com/pycharm/download/)
3. [Arduino IDE](https://www.arduino.cc/en/software)

## Quick Start
[video demo]() of the steps below
1. Download code from Github
    - `git clone https://github.com/augcog/ROAR-Junior-Racing.git && cd ROAR-Junior-Racing`
2. Install dependencies
    - make sure that you are in the right virtual environment
    - `pip install -r requirements.txt`
3. Write configuration(s)
    - find your BLE device by runnig `python findBLE.py`
4. Run `python junior_runner_ble.py`

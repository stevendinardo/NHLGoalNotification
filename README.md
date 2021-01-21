# NHLGoalNotification

A python program that performs actions in real-time after an event in an NHL hockey game by querying the NHL API.
e.g. Play a goal horn sound after a goal.

There is probably a delay between the NHL API and the stream you're watching so DELAY can be changed to make the program 
wait until the stream catches up.

## Usage
For a demo when there's no game on, use the --demo flag. For help, use -h or --help.

NHLGoalNotification.py [-h] [--demo] [-t TEAM] [-d DELAY]


## Events
- Start of game
- Goal (for or against your selected team)
- Start and end of intermission
- Win or Loss

## Sweet Examples
- Play a goal horn when Auston Matthews snipes it top cheese
- Make a HomeAssistant API call to change your RGB LED lights to blue when John Tavares rips it bardownski
- Turn off your computer when the Habs score
- Turn up your game volume when William Nylander does a dirty dangle to score

## Requirements
- Python 3.6+
- requests
- winsound (if you want to play sounds on Windows)

## TODO
- Seperate actions from implementation for flexibility
- Pass parameters like selected team as parameters
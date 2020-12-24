import datetime
import os
import sys
import time
import winsound

import requests
from ArduinoGoalLight import ArduinoGoalLight

DEBUG = True
TEAM = 'TBL'
#NHL_API_URL = 'http://statsapi.web.nhl.com/api/v1/'
NHL_API_URL = 'http://sdpc.home.lan/api/v1/'
DELAY = 15
MUTE_INTERMISSION = True
MUTE_PREGAME = False
LIGHT = False

headers = {
	'Host': 'statsapi.web.nhl.com',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
	'Accept': '*/*',
	'Accept-Language': 'en-US,en;q=0.5',
	'Accept-Encoding': 'gzip, deflate, br',
	'Referer': 'https://www.nhl.com/',
	'Origin': 'https://www.nhl.com',
	'DNT': '1',
	'Connection': 'keep-alive',
	'Pragma': 'no-cache',
	'Cache-Control': 'no-cache'
}

teams = dict(
	ANA=24, ARI=53, BOS=6, BUF=7, CAR=12, CBJ=29, CGY=20, CHI=16, COL=21, DAL=25, DET=17, EDM=22, FLA=13,
	LAK=26, MIN=30, MTL=8, NJD=1, NSH=18, NYI=2, NYR=3, OTT=9, PHI=4, PIT=5, SJS=28, STL=19, TBL=14, TOR=10,
	VAN=23, VGK=54, WPG=52, WSH=15
)


class Game:
	def __init__(
			self, team_id, gamepk, abstract_game_state, detailed_state, goals, opponent_goals, in_intermission,
			game_date
	):
		self.team_id = team_id
		self.gamepk = gamepk
		self.abstract_game_state = abstract_game_state
		self.detailed_state = detailed_state
		self.goals = goals
		self.opponent_goals = opponent_goals
		self.in_intermission = in_intermission
		self.game_date = game_date


def get_game_state(team):
	if not team:
		team_id = ''
	else:
		team_id = teams[team]
	date = f"{datetime.datetime.now():%Y-%m-%d}"
	nhl_url = f'{NHL_API_URL}schedule?date={date}&teamId={team_id}&hydrate=team,linescore'
	nhl_url_response = requests.get(nhl_url, headers=headers)
	nhl_game_json = nhl_url_response.json()

	if not nhl_game_json['dates']:  # No game today for that team
		return None

	nhl_game_json = nhl_game_json['dates'][0]['games'][0]

	if nhl_game_json['teams']['away']['team']['id'] == team_id:
		home_string = 'away'
		opponent_home_string = 'home'
	else:
		home_string = 'home'
		opponent_home_string = 'away'

	gamepk = nhl_game_json['gamePk']
	abstract_game_state = nhl_game_json['status']['abstractGameState']
	detailed_state = nhl_game_json['status']['detailedState']
	goals = nhl_game_json['teams'][home_string]['score']
	opponent_goals = nhl_game_json['teams'][opponent_home_string]['score']
	game_date = nhl_game_json['gameDate']
	in_intermission = nhl_game_json['linescore']['intermissionInfo']['inIntermission']
	return Game(
		team_id, gamepk, abstract_game_state, detailed_state, goals, opponent_goals, in_intermission,
		game_date
	)


def goal() -> None:
	if DEBUG:
		print(f"{get_utc():%Y-%m-%d %H:%M:%S} GOAL. Waiting {DELAY} seconds.")
	time.sleep(DELAY)
	winsound.PlaySound('positivechime.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if LIGHT:
		goal_light.goal(TEAM)

def goal_against() -> None:
	if DEBUG:
		print(f"{get_utc():%Y-%m-%d %H:%M:%S} GOAL AGAINST. Waiting {DELAY} seconds.")
	time.sleep(DELAY)
	winsound.PlaySound('negativechime.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if LIGHT:
		goal_light.goal_against()


def win() -> None:
	if DEBUG:
		print("Win!")
	time.sleep(DELAY)
	winsound.PlaySound('leafswin.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if LIGHT:
		goal_light.win()


def loss() -> None:
	if DEBUG:
		print("Loss.")
	time.sleep(DELAY)
	if LIGHT:
		goal_light.loss()


def game_start() -> None:
	if DEBUG:
		print("Start of Game.")
	winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if MUTE_PREGAME:
		os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 100")
	if LIGHT:
		goal_light.game_started()


def start_of_intermission() -> None:
	if DEBUG:
		print("Start of Intermission.")
	time.sleep(DELAY)
	winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if MUTE_INTERMISSION:
		os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 0")
	if LIGHT:
		goal_light.start_of_intermission()


def end_of_intermission() -> None:
	if DEBUG:
		print("End of Intermission.")
	time.sleep(DELAY)
	winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if MUTE_INTERMISSION:
		os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 100")
	if LIGHT:
		goal_light.end_of_intermission()


def get_utc() -> datetime.datetime:
	return datetime.datetime.utcnow()


def custom_sleep(seconds) -> None:
	for i in range(seconds):
		print(f"Sleep: {seconds - i}")
		time.sleep(1)


def intermission_loop() -> None:
	start_of_intermission()
	intermission = True
	while intermission:
		if DEBUG:
			print(f"{get_utc():%Y-%m-%d %H:%M:%S} Intermission. Sleeping for 60 seconds.")
		time.sleep(61)
		intermission = get_game_state(TEAM).in_intermission
	end_of_intermission()


def pre_game_loop() -> None:
	game_started = False
	if MUTE_PREGAME:
		os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 0")
	while not game_started:
		if DEBUG:
			print("Game not started. Sleeping for 60 seconds.")
		time.sleep(61)
		game_started = get_game_state(TEAM).abstract_game_state != 'Preview'


def game_loop(initial_goals, initial_opponent_goals) -> None:
	goals = initial_goals
	opponent_goals = initial_opponent_goals
	final = False
	game_update = None
	while not final:
		time.sleep(21)

		game_update = get_game_state(TEAM)
		final = game_update.abstract_game_state == 'Final'

		if game_update.goals > goals:
			goal()
		if game_update.opponent_goals > opponent_goals:
			goal_against()
		if game_update.in_intermission:
			intermission_loop()
		if DEBUG:
			print(
				f"{get_utc():%Y-%m-%d %H:%M:%S} "
				f"Score: "
				f"{game_update.goals} - {game_update.opponent_goals}"
			)
		goals = game_update.goals
		opponent_goals = game_update.opponent_goals

	if game_update.goals > game_update.opponent_goals:
		win()
	else:
		loss()


if __name__ == "__main__":

	try:
		game_details = get_game_state(TEAM)
	except Exception as e:
		print(f"Error fetching game: {e}")
		exit(1)

	if not game_details:
		print("No game today for that team.")
		exit(1)
	if game_details.detailed_state == 'Postponed':
		print("Game has been postponed.")
		exit(1)

	if DEBUG:
		print(f"Team is {TEAM}.")
		print(f"Game date is {game_details.game_date}.")
		print(f"Gamepk is {game_details.gamepk}.")

	if LIGHT:
		goal_light = ArduinoGoalLight()

	if game_details.abstract_game_state == 'Preview':
		pre_game_loop()
		game_details = get_game_state(TEAM)

	if game_details.abstract_game_state == 'Live':
		game_start()
		game_loop(game_details.goals, game_details.opponent_goals)

	if LIGHT:
		goal_light.exit()

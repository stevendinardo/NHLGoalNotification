import datetime
import json
import os
import string
import sys
import time
import winsound

import requests

# import ArduinoGoalLight

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
			intermission_time_remaining, game_date
	):
		self.team_id = team_id
		self.gamepk = gamepk
		self.abstract_game_state = abstract_game_state
		self.detailed_state = detailed_state
		self.goals = goals
		self.opponent_goals = opponent_goals
		self.in_intermission = in_intermission
		self.intermission_time_remaining = intermission_time_remaining
		self.game_date = game_date


def get_game_state(team):
	if not team:
		team_id = ''
	else:
		team_id = teams[team]
	date = datetime.datetime.now().strftime('%Y-%m-%d')
	nhl_url = '{0}schedule?date={1}&teamId={2}&hydrate=team,linescore'.format(NHL_API_URL, date, team_id)
	nhl_url_response = requests.get(nhl_url, headers=headers)
	nhl_game_json = json.loads(nhl_url_response.text)

	if not nhl_game_json['dates']:  # No game today for that team
		return None

	if nhl_game_json['dates'][0]['games'][0]['teams']['away']['team']['id'] == team_id:
		home_string = 'away'
		opponent_home_string = 'home'
	else:
		home_string = 'home'
		opponent_home_string = 'away'

	gamepk = nhl_game_json['dates'][0]['games'][0]['gamePk']
	abstract_game_state = nhl_game_json['dates'][0]['games'][0]['status']['abstractGameState']
	detailed_state = nhl_game_json['dates'][0]['games'][0]['status']['detailedState']
	goals = nhl_game_json['dates'][0]['games'][0]['teams'][home_string]['score']
	opponent_goals = nhl_game_json['dates'][0]['games'][0]['teams'][opponent_home_string]['score']

	game_date = nhl_game_json['dates'][0]['games'][0]['gameDate']

	# linescore_url = '{0}game/{1}/linescore'.format(NHL_API_URL, gamepk)
	# linescore_response = requests.get(linescore_url, headers=headers)
	# linescore_json = json.loads(linescore_response.text)
	# in_intermission = linescore_json['intermissionInfo']['inIntermission']
	in_intermission = nhl_game_json['dates'][0]['games'][0]['linescore']['intermissionInfo']['inIntermission']
	# intermission_time_remaining = linescore_json['intermissionInfo']['intermissionTimeRemaining']
	intermission_time_remaining = \
		nhl_game_json['dates'][0]['games'][0]['linescore']['intermissionInfo']['intermissionTimeRemaining']
	return Game(
		team_id, gamepk, abstract_game_state, detailed_state, goals, opponent_goals, in_intermission,
		intermission_time_remaining, game_date
	)


def goal() -> None:
	if DEBUG:
		print(str(get_utc().strftime('%Y-%m-%d %H:%M:%S')) + ": GOAL. Waiting " + str(DELAY) + " seconds.")
	time.sleep(DELAY)
	winsound.PlaySound('positivechime.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)


# winsound.PlaySound('leafsgoal.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)


def goal_against() -> None:
	if DEBUG:
		print(str(get_utc().strftime('%Y-%m-%d %H:%M:%S')) + ": GOAL AGAINST. Waiting " + str(DELAY) + " seconds.")
	time.sleep(DELAY)
	winsound.PlaySound('negativechime.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)


def win() -> None:
	if DEBUG:
		print("Win!.")
	time.sleep(DELAY)
	winsound.PlaySound('leafswin.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)


def loss() -> None:
	if DEBUG:
		print("Loss.")
	time.sleep(DELAY)
	return None


def game_started() -> None:
	if DEBUG:
		print("Start of Game.")
	winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if MUTE_PREGAME:
		os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 100")


def start_of_intermission() -> None:
	if DEBUG:
		print("Start of Intermission.")
	time.sleep(DELAY)
	winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if MUTE_INTERMISSION:
		os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 0")


def end_of_intermission() -> None:
	if DEBUG:
		print("End of Intermission.")
	time.sleep(DELAY)
	winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
	if MUTE_INTERMISSION:
		os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 100")


def get_utc() -> datetime.datetime:
	return datetime.datetime.utcnow()


def custom_sleep(seconds) -> None:
	for i in range(seconds):
		print("Sleep:", seconds - i)
		time.sleep(1)


if __name__ == "__main__":
	if 8 < get_utc().time().hour < 15:
		print("Game not on API yet. Wait until time.")
	#	exit(1)

	first_game_update = get_game_state(TEAM)
	pregame = True
	intermission = False
	if not first_game_update:
		print("No game today for that team.")
		exit(1)
	if first_game_update.detailed_state == 'Postponed':
		print("Game postponed")
		exit(1)
	else:
		if DEBUG:
			print("Gamepk is", first_game_update.gamepk)
		if first_game_update.abstract_game_state == 'Preview':
			pregame = True

	while first_game_update.abstract_game_state != 'Final':
		first_game_update = get_game_state(TEAM)
		if first_game_update.detailed_state == "Scheduled":

			date = datetime.datetime.strptime(first_game_update.game_date, "%Y-%m-%dT%H:%M:%SZ")
			diff = date - get_utc()
			print("Sleeping until " + str(date))
			custom_sleep(int(diff.total_seconds()))
		# if DEBUG: print("Game has not started yet. Sleeping for 20 minutes.")
		# time.sleep(1200)
		# custom_sleep(60)
		elif first_game_update.detailed_state == "Pre-Game":
			date = datetime.datetime.strptime(first_game_update.game_date, "%Y-%m-%dT%H:%M:%SZ")
			diff = date - get_utc()
			print("Sleeping until " + str(date))
			custom_sleep(int(diff.total_seconds()))
			if DEBUG:
				print("Pre-game. Sleeping for 60 seconds.")
			custom_sleep(61)

		while first_game_update.abstract_game_state == 'Live':
			if pregame:
				game_started()
				pregame = False
			print("Sleeping 20 seconds.")
			time.sleep(21)
			second_game_update = get_game_state(TEAM)
			print(
				str(get_utc().strftime('%Y-%m-%d %H:%M:%S'))
				+ ' Score: '
				+ str(first_game_update.goals)
				+ ' - ' + str(first_game_update.opponent_goals)
			)

			if second_game_update.goals > first_game_update.goals:
				goal()
			elif second_game_update.opponent_goals > first_game_update.opponent_goals:
				goal_against()

			if second_game_update.in_intermission:
				if not intermission:
					start_of_intermission()

				sleep_time = second_game_update.intermission_time_remaining + 15
				if DEBUG:
					print("Intermission. Waiting " + str(DELAY) + " seconds.")
					print("Sleeping for " + str(sleep_time))
				time.sleep(DELAY)

				custom_sleep(sleep_time)
				end_of_intermission()

			if second_game_update.abstract_game_state == 'Final':
				time.sleep(DELAY)
				if second_game_update.goals > second_game_update.opponent_goals:
					win()
				else:
					loss()
			first_game_update = second_game_update


# light = ArduinoGoalLight.ArduinoGoalLight()

# start_of_intermission()
# light.start_of_intermission()
# time.sleep(5)
# end_of_intermission()
# light.end_of_intermission()

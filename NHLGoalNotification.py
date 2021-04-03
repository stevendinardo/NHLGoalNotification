import argparse
import datetime
import os
import sys
import time
import winsound

import requests
from ArduinoGoalLight import ArduinoGoalLight

DEBUG = True
NHL_API_URL = 'http://statsapi.web.nhl.com/api/v1/'
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


def get_shifted_time() -> datetime.datetime:
	return datetime.datetime.now() - datetime.timedelta(hours=6)


def get_nhl_json(team_id, session):
	date = f"{get_shifted_time():%Y-%m-%d}"
	nhl_url = f'{NHL_API_URL}schedule?date={date}&teamId={team_id}&hydrate=team,linescore'
	nhl_url_response = session.get(nhl_url, headers=headers)
	return nhl_url_response.json()


class Game:
	def __init__(self, team_id, delay, goal_light=None):
		self.team_id = team_id
		self.opponent_team_id = None
		self.gamepk = None
		self.game_date = None
		self.abstract_game_state = None
		self.detailed_state = None
		self.goals = None
		self.opponent_goals = None
		self.in_intermission = None
		self.delay = delay
		self.goal_light = goal_light
		self.session = requests.Session()
		self.update()

	def update(self):
		game_json = get_nhl_json(self.team_id, self.session)
		if not game_json['dates']:  # No game today for that team
			return

		game_json = game_json['dates'][0]['games'][0]

		if game_json['teams']['away']['team']['id'] == self.team_id:
			home_string = 'away'
			opponent_home_string = 'home'
		else:
			home_string = 'home'
			opponent_home_string = 'away'

		self.gamepk = game_json['gamePk']
		self.abstract_game_state = game_json['status']['abstractGameState']
		self.detailed_state = game_json['status']['detailedState']
		self.goals = game_json['teams'][home_string]['score']
		self.opponent_goals = game_json['teams'][opponent_home_string]['score']
		self.game_date = game_json['gameDate']
		self.in_intermission = game_json['linescore']['intermissionInfo']['inIntermission']

	def win(self):
		if DEBUG:
			print("Win!")
		time.sleep(self.delay)
		winsound.PlaySound('leafswin.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
		if self.goal_light:
			self.goal_light.win(self.team_id)

	def loss(self):
		if DEBUG:
			print("Loss.")
		time.sleep(self.delay)
		if LIGHT:
			self.goal_light.loss()

	def goal(self):
		if DEBUG:
			print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} GOAL. Waiting {self.delay} seconds.")
		time.sleep(self.delay)
		winsound.PlaySound('positivechime.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
		if LIGHT:
			self.goal_light.goal(self.team_id)

	def goal_against(self):
		if DEBUG:
			print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} GOAL AGAINST. Waiting {self.delay} seconds.")
		time.sleep(self.delay)
		winsound.PlaySound('negativechime.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
		if LIGHT:
			self.goal_light.goal_against()

	def game_start(self):
		if DEBUG:
			print("Start of Game.")
		winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
		if MUTE_PREGAME:
			os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 100")
		if LIGHT:
			self.goal_light.game_started()

	def start_of_intermission(self):
		if DEBUG:
			print("Start of Intermission.")
		time.sleep(30)
		winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
		if MUTE_INTERMISSION:
			os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 0")
		if LIGHT:
			self.goal_light.start_of_intermission()

	def end_of_intermission(self):
		if DEBUG:
			print("End of Intermission.")
		time.sleep(5)
		winsound.PlaySound('notification.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
		if MUTE_INTERMISSION:
			os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 100")
		if LIGHT:
			self.goal_light.end_of_intermission()

	def intermission_loop(self):
		self.start_of_intermission()
		while self.in_intermission:
			if DEBUG:
				print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} Intermission. Sleeping for 60 seconds.")
			time.sleep(61)
			self.update()
		self.end_of_intermission()

	def pre_game_loop(self):
		if MUTE_PREGAME:
			os.system("D:\\Steven\\Documents\\NHLGames\\mpv\\mpv-remote.bat set volume 0")
		while self.abstract_game_state == 'Preview':
			if DEBUG:
				print("Game not started. Sleeping for 60 seconds.")
			time.sleep(61)
			self.update()

	def game_loop(self):
		initial_goals = self.goals
		initial_opponent_goals = self.opponent_goals
		while self.abstract_game_state != 'Final':
			time.sleep(21)
			self.update()

			if self.goals > initial_goals:
				self.goal()
			if self.opponent_goals > initial_opponent_goals:
				self.goal_against()
			if self.in_intermission:
				self.intermission_loop()
			if DEBUG:
				print(
					f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} "
					f"Score: "
					f"{self.goals} - {self.opponent_goals}"
				)
			initial_goals = self.goals
			initial_opponent_goals = self.opponent_goals

		if self.goals > self.opponent_goals:
			self.win()
		else:
			self.loss()


def demo():
	print("Running a demo. Sleep times have been reduced by 75%. ")
	print("Game not started. Sleeping for 60 seconds.")
	time.sleep(20)
	print("Start of Game.")
	print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}  Score: 0 - 0")
	time.sleep(5)
	print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} GOAL AGAINST. Waiting {DELAY} seconds.")
	time.sleep(3)
	print("Start of Intermission.")
	time.sleep(10)
	print("End of Intermission.")
	time.sleep(5)
	print(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} GOAL. Waiting {DELAY} seconds.")
	time.sleep(5)
	print("Win!")
	exit(0)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--demo', action="store_true", default=False, help="Run a small demo when theres no game")
	parser.add_argument('-t', '--team', default='TOR', help='Enter the three letter team code. Defualt is "TOR".')
	parser.add_argument('-d', '--delay', type=int, help='Enter stream delay in seconds. Default is 15.')
	args = parser.parse_args()

	if args.demo:
		demo()

	team_id = teams[args.team]
	game = None
	goal_light = None

	try:
		game = Game(team_id=team_id, delay=args.delay, goal_light=None)
	except Exception as e:
		print(f"Error fetching game: {e}")
		exit(1)

	if not game.gamepk:
		print("No game today for that team.")
		exit(1)
	if game.detailed_state == 'Postponed':
		print("Game has been postponed.")
		exit(1)

	if DEBUG:
		print(f"Team is {args.team}.")
		print(f"Game date is {game.game_date}.")
		print(f"Gamepk is {game.gamepk}.")

	if LIGHT:
		goal_light = ArduinoGoalLight()

	if game.abstract_game_state == 'Preview':
		game.pre_game_loop()
		game.update()

	if game.abstract_game_state == 'Live':
		game.game_start()
		game.game_loop()

	if LIGHT:
		goal_light.exit()


if __name__ == "__main__":
	main()

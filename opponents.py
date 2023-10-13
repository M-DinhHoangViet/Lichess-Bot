import json
import os
from datetime import datetime, timedelta

from botli_dataclasses import Bot, Matchmaking_Type
from enums import Challenge_Color, Perf_Type


class Matchmaking_Data:
    def __init__(self, release_time: datetime = datetime.now(), multiplier: int = 1, color: Challenge_Color = Challenge_Color.WHITE) -> None:
        self.release_time = release_time
        self.multiplier = multiplier
        self.color = color

    def to_dict(self) -> dict:
        return {"release_time": self.release_time.isoformat(timespec="seconds"),
                "multiplier": self.multiplier}


class Opponent:
    def __init__(self, username: str, data: dict[Perf_Type, Matchmaking_Data]) -> None:
        self.username = username
        self.data = data

    @classmethod
    def from_dict(cls, dict_: dict) -> "Opponent":
        username = dict_.pop("username")

        data: dict[Perf_Type, Matchmaking_Data] = {}
        for key, value in dict_.items():
            release_time = datetime.fromisoformat(value["release_time"])
            data[Perf_Type(key)] = Matchmaking_Data(release_time, value["multiplier"])

        return cls(username, data)

    def to_dict(self) -> dict:
        dict_: dict[str, str | dict] = {"username": self.username}
        dict_.update({perf_type.value: data.to_dict() for perf_type, data in self.data.items()})

        return dict_

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Opponent):
            return __o.username == self.username

        return NotImplemented


class Opponents:
    def __init__(self, delay: int, username: str) -> None:
        self.delay = timedelta(seconds=delay)
        self.matchmaking_file = f"{username}_matchmaking.json"
        self.opponent_list = self._load(self.matchmaking_file)
        self.busy_bots: list[Bot] = []
        self.last_opponent: tuple[Bot, Challenge_Color] | None = None

    def get_next_opponent(self, online_bots: dict[Perf_Type, list[Bot]], matchmaking_type: Matchmaking_Type) -> tuple[Bot, Challenge_Color]:
        while True:
            for bot in sorted(online_bots[matchmaking_type.perf_type], key=lambda bot: abs(bot.rating_diff)):
                if matchmaking_type.rated and bot.tos_violation:
                    continue

                if not matchmaking_type.min_rating_diff <= abs(bot.rating_diff) <= matchmaking_type.max_rating_diff:
                    continue

                if bot in self.busy_bots:
                    continue

                opponent = self._find(matchmaking_type.perf_type, bot.username)
                opponent_data = opponent.data[matchmaking_type.perf_type]
                if opponent_data.color == Challenge_Color.BLACK or opponent_data.release_time <= datetime.now():
                    self.last_opponent = (bot, opponent_data.color)
                    return bot, opponent_data.color

            print("Resetting matchmaking ...")
            self.reset_release_time(matchmaking_type.perf_type)

    def add_timeout(self, success: bool, game_duration: timedelta, matchmaking_type: Matchmaking_Type) -> None:
        assert self.last_opponent

        bot, color = self.last_opponent
        opponent = self._find(matchmaking_type.perf_type, bot.username)
        opponent_data = opponent.data[matchmaking_type.perf_type]

        if success and opponent_data.multiplier > 1:
            opponent_data.multiplier //= 2
        elif not success:
            opponent_data.multiplier += 1

        opponent_multiplier = opponent_data.multiplier if opponent_data.multiplier >= 5 else 1
        duration_ratio = game_duration / matchmaking_type.estimated_game_duration
        timeout = duration_ratio * matchmaking_type.estimated_game_duration + self.delay
        timeout *= matchmaking_type.multiplier * opponent_multiplier

        if opponent_data.release_time > datetime.now():
            timeout += opponent_data.release_time - datetime.now()

        opponent_data.release_time = datetime.now() + timeout
        release_str = opponent_data.release_time.isoformat(sep=" ", timespec="seconds")
        print(f"{bot.username} will not be challenged to a new game pair before {release_str}.")

        if success:
            opponent_data.color = Challenge_Color.BLACK if color == Challenge_Color.WHITE else Challenge_Color.WHITE

        if opponent not in self.opponent_list:
            self.opponent_list.append(opponent)

        self.busy_bots.clear()
        self._save(self.matchmaking_file)

    def skip_bot(self) -> None:
        assert self.last_opponent

        self.busy_bots.append(self.last_opponent[0])

    def reset_release_time(self, perf_type: Perf_Type) -> None:
        for opponent in self.opponent_list:
            if perf_type in opponent.data:
                opponent.data[perf_type].release_time = datetime.now()

        self.busy_bots.clear()

    def _find(self, perf_type: Perf_Type, username: str) -> Opponent:
        try:
            opponent = self.opponent_list[self.opponent_list.index(Opponent(username, {}))]
        except ValueError:
            return Opponent(username, {perf_type: Matchmaking_Data()})

        if perf_type not in opponent.data:
            opponent.data[perf_type] = Matchmaking_Data()

        return opponent

    def _load(self, matchmaking_file: str) -> list[Opponent]:
        if os.path.isfile(matchmaking_file):
            with open(matchmaking_file, encoding="utf-8") as json_input:
                return [Opponent.from_dict(opponent) for opponent in json.load(json_input)]
        else:
            return []

    def _save(self, matchmaking_file: str) -> None:
        try:
            with open(matchmaking_file, "w", encoding="utf-8") as json_output:
                json.dump([opponent.to_dict() for opponent in self.opponent_list], json_output, indent=4)
        except PermissionError:
            print("Saving the matchmaking file failed due to missing write permissions.")

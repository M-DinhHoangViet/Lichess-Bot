from dataclasses import dataclass, field
from datetime import timedelta

import chess
from chess.polyglot import MemoryMappedReader
from aliases import Challenge_ID, Has_Reached_Rate_Limit, Is_Misconfigured, No_Opponent, Success
from enums import Challenge_Color, Variant, Perf_Type


@dataclass
class API_Challenge_Reponse:
    challenge_id: Challenge_ID | None = None
    was_accepted: bool = False
    error: str | None = None
    was_declined: bool = False
    invalid_initial: bool = False
    invalid_increment: bool = False
    has_reached_rate_limit: bool = False


@dataclass
class Bot:
    username: str
    tos_violation: bool
    rating_diffs: dict[Perf_Type, int]

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Bot):
            return __o.username == self.username

        return NotImplemented


@dataclass
class Challenge_Request:
    opponent_username: str
    initial_time: int
    increment: int
    rated: bool
    color: Challenge_Color
    variant: Variant
    timeout: int

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Challenge_Request):
            return __o.opponent_username == self.opponent_username

        return NotImplemented


@dataclass
class Chat_Message:
    username: str
    text: str
    room: str

    @classmethod
    def from_chatLine_event(cls, chatLine_event: dict) -> "Chat_Message":
        username = chatLine_event["username"]
        text = chatLine_event["text"]
        room = chatLine_event["room"]

        return cls(username, text, room)


@dataclass
class Challenge_Response:
    challenge_id: Challenge_ID | None = None
    success: bool = False
    has_reached_rate_limit: bool = False
    is_misconfigured: bool = False


@dataclass(frozen=True)
class Game_Information:
    id_: str
    white_title: str | None
    white_name: str
    white_rating: int | None
    white_ai_level: int | None
    white_provisional: bool
    black_title: str | None
    black_name: str
    black_rating: int | None
    black_ai_level: int | None
    black_provisional: bool
    initial_time_ms: int
    increment_ms: int
    speed: str
    rated: bool
    variant: Variant
    variant_name: str
    initial_fen: str
    is_white: bool
    state: dict

    @classmethod
    def from_gameFull_event(cls, gameFull_event: dict, username: str) -> "Game_Information":
        assert gameFull_event["type"] == "gameFull"

        id_ = gameFull_event["id"]
        white_title = gameFull_event["white"].get("title")
        white_name = gameFull_event["white"].get("name", "AI")
        white_rating = gameFull_event["white"].get("rating")
        white_ai_level = gameFull_event["white"].get("aiLevel")
        white_provisional = gameFull_event["white"].get("provisional", False)
        black_title = gameFull_event["black"].get("title")
        black_name = gameFull_event["black"].get("name", "AI")
        black_rating = gameFull_event["black"].get("rating")
        black_ai_level = gameFull_event["black"].get("aiLevel")
        black_provisional = gameFull_event["black"].get("provisional", False)
        initial_time_ms = gameFull_event["clock"]["initial"]
        increment_ms = gameFull_event["clock"]["increment"]
        speed = gameFull_event["speed"]
        rated = gameFull_event["rated"]
        variant = Variant(gameFull_event["variant"]["key"])
        variant_name = gameFull_event["variant"]["name"]
        initial_fen = gameFull_event["initialFen"]
        is_white = white_name == username
        state = gameFull_event["state"]

        return cls(id_, white_title, white_name, white_rating, white_ai_level, white_provisional, black_title,
                   black_name, black_rating, black_ai_level, black_provisional, initial_time_ms,
                   increment_ms, speed, rated, variant, variant_name, initial_fen, is_white, state)

    @property
    def id_str(self) -> str:
        return f"ID: {self.id_}"

    @property
    def white_name_str(self) -> str:
        title_str = f"{self.white_title} " if self.white_title else ""
        return f"{title_str}{self.white_name}"

    @property
    def white_str(self) -> str:
        provisional_str = "?" if self.white_provisional else ""
        rating_str = f"{self.white_rating}{provisional_str}" if self.white_rating else f"Level {self.white_ai_level}"
        return f"{self.white_name_str} ({rating_str})"

    @property
    def black_name_str(self) -> str:
        title_str = f"{self.black_title} " if self.black_title else ""
        return f"{title_str}{self.black_name}"

    @property
    def black_str(self) -> str:
        provisional_str = "?" if self.black_provisional else ""
        rating_str = f"{self.black_rating}{provisional_str}" if self.black_rating else f"Level {self.black_ai_level}"
        return f"{self.black_name_str} ({rating_str})"

    @property
    def tc_str(self) -> str:
        initial_time_min = self.initial_time_ms / 60_000
        if initial_time_min.is_integer():
            initial_time_str = str(int(initial_time_min))
        elif initial_time_min == 0.25:
            initial_time_str = "¼"
        elif initial_time_min == 0.5:
            initial_time_str = "½"
        elif initial_time_min == 0.75:
            initial_time_str = "¾"
        else:
            initial_time_str = str(initial_time_min)
        increment_sec = self.increment_ms // 1000
        return f"TC: {initial_time_str}+{increment_sec}"

    @property
    def rated_str(self) -> str:
        return "rated" if self.rated else "Casual"

    @property
    def variant_str(self) -> str:
        return f"Variant: {self.variant_name}"

    @property
    def opponent_is_bot(self) -> bool:
        return self.black_title == "BOT" if self.is_white else self.white_title == "BOT"

    @property
    def opponent_username(self) -> str:
        return self.black_name if self.is_white else self.white_name

    @property
    def opponent_title(self) -> str | None:
        return self.black_title if self.is_white else self.white_title

    @property
    def opponent_rating(self) -> int | None:
        return self.black_rating if self.is_white else self.white_rating


@dataclass
class Book_Settings:
    selection: str = ""
    max_depth: int = 600
    readers: dict[str, MemoryMappedReader] = field(default_factory=dict)


@dataclass
class Matchmaking_Type:
    name: str
    initial_time: int
    increment: int
    estimated_game_duration: timedelta = field(init=False)
    rated: bool
    variant: Variant
    perf_type: Perf_Type
    multiplier: int
    weight: int
    min_rating_diff: int
    max_rating_diff: int

    def __post_init__(self) -> None:
        self.estimated_game_duration = timedelta(seconds=(self.initial_time * 0.8 + self.increment * 80) * 2)

    @property
    def to_str(self) -> str:
        initial_time_min = self.initial_time / 60
        if initial_time_min.is_integer():
            initial_time_str = str(int(initial_time_min))
        elif initial_time_min == 0.25:
            initial_time_str = "¼"
        elif initial_time_min == 0.5:
            initial_time_str = "½"
        elif initial_time_min == 0.75:
            initial_time_str = "¾"
        else:
            initial_time_str = str(initial_time_min)
        tc_str = f"TC: {initial_time_str}+{self.increment}"
        rated_str = "rated" if self.rated else "Casual"
        variant_str = f"Variant: {self.variant.value}"
        delimiter = 5 * " "

        return delimiter.join([self.name, tc_str, rated_str, variant_str])


@dataclass
class Move_Response:
    move: chess.Move
    public_message: str
    private_message: str = field(default="", kw_only=True)
    pv: list[chess.Move] = field(default_factory=list, kw_only=True)
    is_drawish: bool = field(default=False, kw_only=True)
    is_resignable: bool = field(default=False, kw_only=True)
    is_engine_move: bool = field(default=False, kw_only=True)

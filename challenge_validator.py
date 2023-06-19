from enums import Decline_Reason


class Challenge_Validator:
    def __init__(self, config: dict) -> None:
        self.variants = config['challenge']['variants']
        self.time_controls = config['challenge']['time_controls']
        self.bullet_with_increment_only = config['challenge'].get('bullet_with_increment_only', False)
        self.min_increment = config['challenge'].get('min_increment', 0)
        self.max_increment = config['challenge'].get('max_increment', 180)
        self.min_initial = config['challenge'].get('min_initial', 0)
        self.max_initial = config['challenge'].get('max_initial', 315360000)
        self.bot_modes = config['challenge']['bot_modes']
        self.human_modes = config['challenge']['human_modes']
        self.blacklist = config.get('blacklist', [])

    def get_decline_reason(self, challenge_event: dict) -> Decline_Reason | None:
        if challenge_event['challenge']['challenger']['id'] in self.blacklist:
            print('Challenger is blacklisted.')
            return Decline_Reason.GENERIC

        is_bot = challenge_event['challenge']['challenger']['title'] == 'BOT'
        modes = self.bot_modes if is_bot else self.human_modes
        if modes is None:
            if is_bot:
                print('Bots are not allowed according to config.')
                return Decline_Reason.NO_BOT
            else:
                print('Only bots are allowed according to config.')
                return Decline_Reason.ONLY_BOT

        variant = challenge_event['challenge']['variant']['key']
        if variant not in self.variants:
            print(f'Variant "{variant}" is not allowed according to config.')
            return Decline_Reason.VARIANT

        speed = challenge_event['challenge']['speed']
        increment = challenge_event['challenge']['timeControl'].get('increment')
        initial = challenge_event['challenge']['timeControl'].get('limit')
        if speed == 'correspondence':
            print('LichessBOT-Việt does not support time control "Correspondence".')
            return Decline_Reason.TIME_CONTROL
        elif speed not in self.time_controls:
            print(f'Time control "{speed}" is not allowed according to config.')
            return Decline_Reason.TIME_CONTROL
        elif increment < self.min_increment:
            print(f'Increment {increment} is too short according to config.')
            return Decline_Reason.TOO_FAST
        elif increment > self.max_increment:
            print(f'Increment {increment} is too long according to config.')
            return Decline_Reason.TOO_SLOW
        elif initial < self.min_initial:
            print(f'Initial time {initial} is too short according to config.')
            return Decline_Reason.TOO_FAST
        elif initial > self.max_initial:
            print(f'Initial time {initial} is too long according to config.')
            return Decline_Reason.TOO_SLOW
        elif is_bot and speed == 'bullet' and increment == 0 and self.bullet_with_increment_only:
            print('Bullet against bots is only allowed with increment according to config.')
            return Decline_Reason.TOO_FAST

        is_rated = challenge_event['challenge']['rated']
        is_casual = not is_rated
        if is_rated and 'rated' not in modes:
            print('Rated is not allowed according to config.')
            return Decline_Reason.CASUAL
        elif is_casual and 'casual' not in modes:
            print('Casual is not allowed according to config.')
            return Decline_Reason.RATED

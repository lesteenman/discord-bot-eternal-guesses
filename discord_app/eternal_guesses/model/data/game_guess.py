from datetime import datetime


class GameGuess:
    def __init__(self, user_id: int = None, guess: str = None, nickname: str = None, timestamp: datetime = None):
        self.user_id = user_id
        self.guess = guess
        self.nickname = nickname
        self.timestamp = timestamp

    def __repr__(self):
        return f"<GameGuess user_id={self.user_id}, guess={self.guess}, nickname={self.nickname}, " \
               f"timestamp={self.timestamp}"

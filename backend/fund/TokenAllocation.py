import json
import traceback
from typing import Dict, Optional


class TokenAllocation:
    """
    Wrapper for a sell_target holding target, comprised of buy and sell targets.
    """

    # The token to hold in a sell_target.
    token: str

    # The desired percent allocation of the token within a sell_target.
    portfolio_pct: float

    # The highest price at which to buy the token.
    buy_target: float

    # The lowest price at which to sell the token.
    sell_target: float

    def __init__(self,
                 token: str,
                 portfolio_pct: float,
                 buy_target: float,
                 sell_target: float):
        self.token = token
        self.portfolio_pct = portfolio_pct
        self.buy_target = buy_target
        self.sell_target = sell_target

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self) -> Dict:
        return {
            'token':         self.token,
            'portfolio_pct': self.portfolio_pct,
            'buy_target':    self.buy_target,
            'sell_target':   self.sell_target
        }

    @classmethod
    def from_str(cls,
                 str_data: str) -> Optional['TokenAllocation']:
        """
        Converts the string into a TokenAllocation wrapper,
            or None if the data is invalid.
        """
        return cls.from_json(json.loads(str_data))

    @classmethod
    def from_json(cls,
                  json_data: Dict) -> Optional['TokenAllocation']:
        """
        Converts the json object into a TokenAllocation wrapper,
            or None if the data is invalid.
        """
        try:
            token = json_data.get('token', json_data.get('id', None))
            buy_target = json_data.get('buy_target', None)
            sell_target = json_data.get('sell_target', None)
            assert token is not None and buy_target is not None and sell_target is not None
            return TokenAllocation(token=token,
                                   portfolio_pct=json_data.get('portfolio_pct', 1),
                                   buy_target=buy_target,
                                   sell_target=sell_target)
        except Exception as e:
            print(f'ERROR! Something went wrong trying to load portfolio token '
                  f'from json: {traceback.format_exc()}')
            return None

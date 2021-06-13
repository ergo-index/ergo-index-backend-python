import json
import traceback
from typing import Dict, List, Optional

from backend.redis.RedisManager import RedisManager
from backend.util import clean_email


class FundUser:
    """
    Wrapper for a JSON object that can be decoded and displayed by the frontend.
    """

    # User's email address.
    email: str

    # User's name (could be full name, screen name, or same as email).
    name: str

    # Ids of funds in which the user participates or manages.
    funds: List[str]

    def __init__(self,
                 email: str,
                 name: str,
                 funds: List[str]):
        self.email = email
        self.name = name
        self.funds = funds

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self) -> Dict:
        return {
            'email': self.email,
            'name':  self.name,
            'funds': self.funds
        }

    @classmethod
    def from_json(cls,
                  json_data: Dict) -> Optional['FundUser']:
        """
        Converts the json object into a FundUser wrapper,
            or None if the data is invalid.
        """
        try:
            user_email = json_data.get('email', None)
            assert user_email is not None
            return FundUser(email=user_email,
                            name=json_data.get('name', user_email),
                            funds=json_data.get('funds', list()))
        except Exception as e:
            print(f'ERROR! Something went wrong trying to load a user profile '
                  f'from json: {traceback.format_exc()}')
            return None

    @classmethod
    def from_db(cls,
                user_email: str,
                redis: RedisManager) -> Optional['FundUser']:
        """
        Loads and returns the FundUser data associated with the email,
            or None if the user doesn't have any data stored in Redis.
        """
        try:
            user_email = clean_email(user_email)
            name = redis.get_user_name(user_email)
            if name is None:
                return None
            fund_ids = redis.get_user_fund_ids(user_email)
            return FundUser(email=user_email,
                            name=name,
                            funds=fund_ids)
        except Exception as e:
            print(f'ERROR! Something went wrong trying to load a user profile '
                  f'from redis: {traceback.format_exc()}')
            return None

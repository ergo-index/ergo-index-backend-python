import json
import traceback
from typing import Dict, List, Optional

from backend.fund.FundPortfolio import FundPortfolio
from backend.redis.RedisManager import RedisManager
from backend.util import clean_email


class IndexFundSnapshot:
    """
    Wrapper for a JSON object that can be decoded and displayed by the frontend.
    """

    # Fund's name/id.
    fund_id: str

    # Emails of fund manager_email.
    manager_email: str

    # Emails of non-managerial fund investor_emails.
    investor_emails: List[str]

    # Fund's portfolio.
    portfolio: FundPortfolio

    def __init__(self,
                 fund_id: str,
                 manager_email: str,
                 investor_emails: List[str],
                 portfolio: FundPortfolio):
        self.fund_id = fund_id
        self.manager_email = manager_email
        self.investor_emails = investor_emails
        self.portfolio = portfolio

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self) -> Dict:
        return {
            'fund_id':         self.fund_id,
            'manager_email':   self.manager_email,
            'investor_emails': self.investor_emails,
            'portfolio':       self.portfolio.to_json()
        }

    @classmethod
    def from_str(cls,
                 str_data: str) -> Optional['IndexFundSnapshot']:
        """
        Converts the string into an IndexFundSnapshot wrapper,
            or None if the data is invalid.
        """
        return cls.from_json(json.loads(str_data))

    @classmethod
    def from_json(cls,
                  json_data: Dict) -> Optional['IndexFundSnapshot']:
        """
        Converts the json object into an IndexFundSnapshot wrapper,
            or None if the data is invalid.
        """
        try:
            fund_id = json_data.get('fund_id', json_data.get('id', None))
            manager_email = json_data.get('manager_email', None)
            assert fund_id is not None and manager_email is not None
            manager_email = clean_email(manager_email)
            portfolio = FundPortfolio.from_json(json_data.get('portfolio'), {})
            return IndexFundSnapshot(fund_id=fund_id,
                                     manager_email=manager_email,
                                     investor_emails=json_data.get('investor_emails', list()),
                                     portfolio=portfolio)
        except Exception as e:
            print(f'ERROR! Something went wrong trying to load fund data '
                  f'from json: {traceback.format_exc()}')
            return None

    @classmethod
    def from_db(cls,
                fund_id: str,
                redis: RedisManager) -> Optional['IndexFundSnapshot']:
        """
        Loads and returns the IndexFundSnapshot data associated with the id,
            or None if the user doesn't have any data stored in Redis.
        """
        try:
            manager_email = redis.get_fund_manager_email(fund_id)
            investor_emails = redis.get_fund_investor_emails(fund_id)
            portfolio = redis.get_fund_portfolio(fund_id)
            return IndexFundSnapshot(fund_id=fund_id,
                                     manager_email=manager_email,
                                     investor_emails=investor_emails,
                                     portfolio=portfolio)
        except Exception as e:
            print(f'ERROR! Something went wrong trying to load a fund snapshot '
                  f'from redis: {traceback.format_exc()}')
            return None

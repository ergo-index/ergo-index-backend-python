import time as pytime
import traceback
from typing import List, Optional

from decouple import config
from redis import BusyLoadingError, Redis

from backend.fund.FundPortfolio import FundPortfolio


class RedisManager:
    """
    Handles connection and operations on the redis database.
    """
    client: Redis

    def connect(self) -> bool:
        """
        Returns false if there was a problem initializing the connection.
        """
        try:
            self.client = Redis(host=config('REDIS_IP', cast=str),
                                port=config('REDIS_PORT', cast=int))
            db_loaded = False
            load_start_time = pytime.monotonic()
            while not db_loaded and pytime.monotonic() - load_start_time < 60:
                try:
                    self.client.ping()
                    db_loaded = True
                except BusyLoadingError as ex:
                    pytime.sleep(0.5)
            if not db_loaded:
                print('WARNING: Could not confirm redis connection. Busy loading '
                      'data from disk for over a minute')
                return False
        except Exception as e:
            traceback.print_exc()
            print('ERROR: Could not initialize connection to Redis database. Fatal connection error')
            return False
        return True

    def save_new_user(self,
                      user_email: str,
                      user_name: str) -> None:
        """
        Saves the new user's email with his name in the Redis database.
        """
        try:
            self.client.hset('user_name', user_email, user_name if len(user_name) != 0 else user_email)
        except Exception as e:
            print(f'Error saving new user in Redis: {traceback.format_exc()}')

    def get_user_name(self,
                      user_email: str) -> Optional[str]:
        """
        Returns the user's name, or None if no such user exists.
        """
        try:
            user_name = self.client.hget('user_name', user_email)
            return None if user_name is None or len(user_name) == 0 else user_name.decode('utf-8')
        except Exception as e:
            print(f'Error getting user name for "{user_email}" from Redis: {traceback.format_exc()}')
            return None

    def get_user_fund_ids(self,
                          user_email: str) -> List[str]:
        """
        Returns the funds in which the user participates or manages,
            or None if no such user exists.
        """
        try:
            user_fund_ids_str = self.client.hget('user_fund_ids', user_email)
            return user_fund_ids_str.decode('utf-8').split(',')
        except Exception as e:
            print(f'Error getting user fund ids for "{user_email}" from Redis: {traceback.format_exc()}')
            return []

    def set_user_fund_ids(self,
                          user_email: str,
                          fund_ids: List[str]) -> bool:
        """
        Returns True if the funds list was updated successfully.
        """
        try:
            self.client.hset('user_fund_ids', user_email, ','.join(fund_ids))
            return True
        except Exception as e:
            print(f'Error setting user fund ids for "{user_email}" from Redis: {traceback.format_exc()}')
            return False

    def get_fund_manager_email(self,
                               fund_id: str) -> Optional[str]:
        """
        Returns the email of the fund's manager, or None.
        """
        try:
            fund_manager_email = self.client.hget('fund_manager_email', fund_id)
            return None if fund_manager_email is None or len(fund_manager_email) == 0 else str(fund_manager_email.decode('utf-8'))
        except Exception as e:
            print(f'Error getting fund manager for "{fund_id}" from Redis: {traceback.format_exc()}')
            return None

    def set_fund_manager_email(self,
                          fund_id: str,
                          manager_email: str) -> bool:
        """
        Returns True if the fund's manager was updated successfully.
        """
        try:
            self.client.hset('fund_manager_email', fund_id, manager_email)
            return True
        except Exception as e:
            print(f'Error setting fund manager for "{fund_id}" from Redis: {traceback.format_exc()}')
            return False

    def get_fund_investor_emails(self,
                                 fund_id: str) -> List[str]:
        """
        Returns the emails of the fund's investors, or an empty list.
        """
        try:
            fund_investors_str = self.client.hget('fund_investor_emails', fund_id)
            return str(fund_investors_str.decode('utf-8')).split(',')
        except Exception as e:
            print(f'Error getting fund investors for "{fund_id}" from Redis: {traceback.format_exc()}')
            return []

    def set_fund_investor_emails(self,
                          fund_id: str,
                          investor_emails: List[str]) -> bool:
        """
        Returns True if the fund's investors list was updated successfully.
        """
        try:
            self.client.hset('fund_investor_emails', fund_id, ','.join([email.replace(',', '') for email in
                                                                        investor_emails]))
            return True
        except Exception as e:
            print(f'Error setting fund investors list for "{fund_id}" from Redis: {traceback.format_exc()}')
            return False

    def get_fund_portfolio(self,
                                 fund_id: str) -> Optional[FundPortfolio]:
        """
        Returns a FundPortfolio wrapper for the fund's holdings, or None.
        """
        try:
            fund_portfolio_str = self.client.hget('fund_portfolio', fund_id)
            if fund_portfolio_str is None or len(fund_portfolio_str) == 0:
                return None
            return FundPortfolio.from_str(fund_portfolio_str.decode('utf-8'))
        except Exception as e:
            print(f'Error getting fund portfolio for "{fund_id}" from Redis: {traceback.format_exc()}')
            return None

    def set_fund_portfolio(self,
                          fund_id: str,
                          portfolio: FundPortfolio) -> bool:
        """
        Returns True if the fund's portfolio was updated successfully.
        """
        try:
            self.client.hset('fund_portfolio', fund_id, str(portfolio))
            return True
        except Exception as e:
            print(f'Error setting fund portfolio for "{fund_id}" from Redis: {traceback.format_exc()}')
            return False
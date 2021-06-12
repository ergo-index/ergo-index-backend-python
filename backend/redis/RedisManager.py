import time as pytime
import traceback

from decouple import config
from redis import BusyLoadingError, Redis


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

import json
import traceback
from typing import Dict, List, Optional

from backend.fund.TokenAllocation import TokenAllocation


class FundPortfolio:
    """
    Wrapper for a list of asset positions.
    """
    
    # List of asset positions which the fund desires.
    tokens: List[TokenAllocation]

    def __init__(self,
                 tokens: List[TokenAllocation]):
        self.tokens = tokens

    def __str__(self):
        return json.dumps(self.to_json())

    def to_json(self) -> Dict:
        return {
            'tokens': [token.to_json() for token in self.tokens],
        }

    @classmethod
    def from_str(cls,
                 str_data: str) -> Optional['FundPortfolio']:
        """
        Converts the string into a FundPortfolio wrapper,
            or None if the data is invalid.
        """
        return cls.from_json(json.loads(str_data))

    @classmethod
    def from_json(cls,
                  json_data: Dict) -> Optional['FundPortfolio']:
        """
        Converts the json object into a FundPortfolio wrapper,
            or None if the data is invalid.
        """
        try:
            token_allocation_strs = json_data.get('tokens', [])
            token_allocations = [TokenAllocation.from_json(token_str) for token_str in token_allocation_strs]
            return FundPortfolio(tokens=token_allocations)
        except Exception as e:
            print(f'ERROR! Something went wrong trying to load portfolio data '
                  f'from json: {traceback.format_exc()}')
            return None
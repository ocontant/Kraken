# my_project/api/schemas/balance.py
from pydantic import BaseModel, RootModel
from typing import Dict, List, Optional

class SchemasAccountBalance(RootModel[Dict[str, str]]):
    pass

    model_config = {
        'from_attributes': True
    }

class SchemasBalanceResponse(BaseModel):
    error: List[str]
    result: SchemasAccountBalance
    

""" Explanation

    BalanceResponse: Represents the entire response from the get_account_balance API, including the result and potential errors.
        result: An instance of AccountBalance containing the balances.
        error: A list of errors returned by the API, if any. """
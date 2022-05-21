"""
Here we can put functions which are imported and used by controllers.py
This way we don't have to clutter the controllers.py file with function
declarations that are unrelated to hooking pages to URLs
"""
from .common import db

def get_portfolio(user_id:int) -> dict:
    transactions = db(db.transaction.user_id == user_id).select(orderby=db.transaction.transaction_date)
    holdings = {}
    spent, gained = 0.0, 0.0
    for row in transactions:
        if row.transaction_type == 'buy':
            if row.company_id not in holdings:
                holdings[row.company_id] = 0.0
            holdings[row.company_id] += row.count
            spent += row.count * row.value_per_share
        else:
            if row.company_id not in holdings:
                raise KeyError('Attempted to sell a stock the user does not own')
            if row.count > holdings[row.company_id]:
                raise ValueError(f'Cannot sell {row.count} shares, user owns {holdings[row.company_id]}')
            holdings[row.company_id] -= row.count
            gained += row.count * row.value_per_share
    value = gained - spent
    for k, v in holdings.items():
        share_val = db(db.company.id == k).select().first().current_stock_value
        value += v * share_val
    return {'holdings' : holdings, 'spent' : spent, 'gained' : gained, 'value' : value}

# Function to get user balance, might be useful when computing the total
# value of the user's holdings using functions similar to ones below.
def get_user_balance(user_id = None):
    """
    Get the balance of the user from the database
    """
    assert user_id is not None
    user = db(db.user.id == user_id).select().first()
    if user is None:
        return None
    return user.user_balance

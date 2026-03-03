import pandas as pd


def american_to_decimal(american_odds):
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1


def calculate_probability(odds):
    return 1 / odds


def vig_removal(odds, market_type='2-way'):
    if market_type == '2-way':
        decimal_odds = [american_to_decimal(odds[0]), american_to_decimal(odds[1])]
        implied_prob = [calculate_probability(odd) for odd in decimal_odds]
        total_prob = sum(implied_prob)
        return [prob / total_prob for prob in implied_prob]
    elif market_type == '3-way':
        decimal_odds = [american_to_decimal(odd) for odd in odds]
        implied_prob = [calculate_probability(odd) for odd in decimal_odds]
        total_prob = sum(implied_prob)
        return [prob / total_prob for prob in implied_prob]


def parse_odds_event(event_data):
    event_info = {
        'event': event_data.get('event_name'),
        'date': event_data.get('event_date'),
        'odds': event_data.get('odds')
    }
    return event_info


def identify_arbitrage(opportunities):
    arbitrage_opps = []
    for opportunity in opportunities:
        if opportunity['probability'] < 1:
            arbitrage_opps.append(opportunity)
    return arbitrage_opps


def convert_to_dataframe(data):
    return pd.DataFrame(data)
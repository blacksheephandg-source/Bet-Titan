def convert_odds_to_probability(odds):
    """
    Convert odds to probability.
    odds : float: The odds in decimal format
    return : float: Probability as a percentage
    """
    probability = 1 / odds * 100
    return probability


def remove_vig(odds, vig_percent):
    """
    Remove vigorish (vig) from the given odds.
    odds : float: The original odds
    vig_percent : float: The vig percentage to remove
    return : float: Adjusted odds
    """
    return odds / (1 + (vig_percent / 100))


def odds_conversion(odds):
    """
    Comprehensive conversion of odds from decimal to fractional and American format.
    odds : float: The odds in decimal format
    return : dict: Conversion results containing fractional and American odds
    """
    if odds >= 2.0:
        fractional = f'{int(odds - 1)}:1'
        american = int((odds - 1) * 100) if odds >= 2.0 else -100 / (odds - 1)
    else:
        fractional = f'1:{int(1 / (odds - 1))}'
        american = -100 / (odds - 1)

    return {
        'fractional': fractional,
        'american': american
    }

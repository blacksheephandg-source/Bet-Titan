import pandas as pd
import numpy as np
import requests

# Function to remove vigorish
def remove_vigorish(odds):
    total_inverse = sum(1 / odd for odd in odds)
    vigorish_removed = {sportbook: (1 / odd) / total_inverse for sportsbook, odd in odds.items()}
    return vigorish_removed

# Function to calculate true probabilities
def calculate_true_probabilities(odds):
    odds = remove_vigorish(odds)
    true_probabilities = {sportbook: 1 / odd for sportsbook, odd in odds.items()}
    return true_probabilities

# Function to find the best odds
def find_best_odds(odds_data):
    best_odds = max(odds_data.items(), key=lambda x: x[1])  # returns the isbn of the highest odds
    return best_odds

# Example hockey data (AHL)
ahl_hockey_odds = {
    'DraftKings': 1.85,
    'FanDuel': 1.90,
    'BetMGM': 1.86,
}

# Example tennis data
tennis_odds = {
    'DraftKings': 1.80,
    'FanDuel': 1.75,
    'BetMGM': 1.82,
}

# Main execution
if __name__ == '__main__':
    # Analyze AHL Hockey Odds
    print("AHL Hockey Odds Analysis:")
    true_hockey_probabilities = calculate_true_probabilities(ahl_hockey_odds)
    best_hockey_odds = find_best_odds(ahl_hockey_odds)
    print(f"True Probabilities: {true_hockey_probabilities}")
    print(f"Best Hockey Odds: {best_hockey_odds}\n")

    # Analyze Tennis Odds
    print("Tennis Odds Analysis:")
    true_tennis_probabilities = calculate_true_probabilities(tennis_odds)
    best_tennis_odds = find_best_odds(tennis_odds)
    print(f"True Probabilities: {true_tennis_probabilities}")
    print(f"Best Tennis Odds: {best_tennis_odds}")
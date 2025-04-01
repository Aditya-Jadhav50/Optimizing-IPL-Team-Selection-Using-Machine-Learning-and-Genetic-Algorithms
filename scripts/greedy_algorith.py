import pandas as pd

# Load player data (merged data for all players)
players_data = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/merged_player_data_with_roles_and_wickets_new.csv')

# Parameters
SQUAD_SIZE = 17
OVERSEAS_LIMIT = 6
COMPOSITION = {'Batsman': 6, 'Bowler': 6, 'All-Rounder': 3, 'Wicketkeeper': 2}

# Fitness function
def calculate_fitness(team):
    """
    Calculate fitness of a team based on batting, bowling, and all-rounder contributions.
    """
    valid_economy_rate = team['economy_rate'].replace([float('inf'), float('-inf'), 0], 1e-5)
    batting_score = team['total_runs'].sum()
    bowling_score = (100 / valid_economy_rate).sum()
    all_rounder_score = team['all_rounder_index'].sum()
    return batting_score * 0.4 + bowling_score * 0.4 + all_rounder_score * 0.2

# Greedy selection function
def greedy_algorithm(players):
    """
    Select the optimal team using a greedy approach based on player performance metrics.
    """
    team = pd.DataFrame()
    remaining_players = players.copy()

    # Select players for each role
    for role, count in COMPOSITION.items():
        role_players = remaining_players[remaining_players['Role'] == role].sort_values(
            by=['total_runs', 'strike_rate', 'boundary_percentage'], ascending=False
        ).head(count)
        team = pd.concat([team, role_players])
        remaining_players = remaining_players[~remaining_players['Player_Id'].isin(role_players['Player_Id'])]

    # Enforce foreign player limit
    foreign_players = team[team['Country'] != 'India']
    if len(foreign_players) > OVERSEAS_LIMIT:
        excess_count = len(foreign_players) - OVERSEAS_LIMIT
        foreign_players_to_remove = foreign_players.tail(excess_count)
        team = team[~team['Player_Id'].isin(foreign_players_to_remove['Player_Id'])]

        # Replace removed players with domestic players
        for _, player in foreign_players_to_remove.iterrows():
            replacement = remaining_players[(remaining_players['Role'] == player['Role']) & (remaining_players['Country'] == 'India')].head(1)
            if not replacement.empty:
                team = pd.concat([team, replacement])
                remaining_players = remaining_players[~remaining_players['Player_Id'].isin(replacement['Player_Id'])]

    # Ensure no duplicate players
    team = team.drop_duplicates(subset='Player_Id')

    return team

# Select the optimal team
optimal_team = greedy_algorithm(players_data)

# Calculate team fitness
optimal_team_fitness = calculate_fitness(optimal_team)

# Display the optimal team and fitness
print("Optimal Team Selected Using Greedy Algorithm:")
print(optimal_team)
print("\nOverall Fitness Score:", optimal_team_fitness)

# Save the optimal team to a CSV file
optimal_team.to_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project/final_output/optimal_team_greedy.csv', index=False)

import pandas as pd
import random
import numpy as np
from multiprocessing import Pool

# Load player data (batsmen, bowlers, all-rounders)
players_data = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/merged_player_data_with_roles_and_wickets_new.csv')  # Merged data for all players

# Parameters
SQUAD_SIZE = 17
POPULATION_SIZE = 100
GENERATIONS = 50
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.8
OVERSEAS_LIMIT = 6

COMPOSITION = {'Batsman': 6, 'Bowler': 6, 'All-Rounder': 3, 'Wicketkeeper': 2}

# Fitness function
def calculate_fitness(team):
    """
    Calculate fitness of a team based on batting, bowling, and all-rounder contributions.
    """
    valid_economy_rate = team['economy_rate'].replace([np.inf, -np.inf, 0], 1e-5)
    batting_score = team['total_runs'].sum()
    bowling_score = (100 / valid_economy_rate).sum()
    all_rounder_score = team['all_rounder_index'].sum()
    return batting_score * 0.4 + bowling_score * 0.4 + all_rounder_score * 0.2

# Validate constraints
def validate_constraints(team):
    """
    Validate team constraints: role distribution, squad size, and composition.
    """
    role_counts = team['Role'].value_counts()
    return (
        len(team) == SQUAD_SIZE and
        role_counts.get('Batsman', 0) >= COMPOSITION['Batsman'] and
        role_counts.get('Bowler', 0) >= COMPOSITION['Bowler'] and
        role_counts.get('All-Rounder', 0) >= COMPOSITION['All-Rounder'] and
        role_counts.get('Wicketkeeper', 0) >= COMPOSITION['Wicketkeeper']
    )

# Generate initial population
def initialize_population(players):
    """
    Generate an initial population of valid teams with a foreign player limit.
    """
    population = []
    for _ in range(POPULATION_SIZE):
        while True:
            # Select roles ensuring constraints
            batsmen = players[players['Role'] == 'Batsman'].drop_duplicates(subset='Player_Id').sample(n=COMPOSITION['Batsman'], replace=False)
            bowlers = players[players['Role'] == 'Bowler'].drop_duplicates(subset='Player_Id').sample(n=COMPOSITION['Bowler'], replace=False)
            all_rounders = players[players['Role'] == 'All-Rounder'].drop_duplicates(subset='Player_Id').sample(n=COMPOSITION['All-Rounder'], replace=False)
            wicketkeepers = players[players['Role'] == 'Wicketkeeper'].drop_duplicates(subset='Player_Id').sample(n=COMPOSITION['Wicketkeeper'], replace=False)

            # Combine and enforce foreign player limit
            sampled_team = pd.concat([batsmen, bowlers, all_rounders, wicketkeepers]).drop_duplicates(subset='Player_Id')
            foreign_players = sampled_team[sampled_team['Country'] != 'India']
            if len(foreign_players) > OVERSEAS_LIMIT:
                continue  # Retry if the foreign player limit is exceeded

            # Validate constraints
            if validate_constraints(sampled_team):
                population.append(sampled_team)
                break
    return population

# Selection
def tournament_selection(population, fitness_scores, k=3):
    """
    Select parents for crossover using tournament selection.
    """
    selected = random.sample(list(zip(population, fitness_scores)), k)
    return max(selected, key=lambda x: x[1])[0]

# Crossover
def crossover(parent1, parent2):
    """
    Perform crossover to create offspring from two parents.
    """
    split_point = random.randint(1, SQUAD_SIZE - 1)
    child1 = pd.concat([parent1.iloc[:split_point], parent2.iloc[split_point:]]).drop_duplicates(subset='Player_Id')
    child2 = pd.concat([parent2.iloc[:split_point], parent1.iloc[split_point:]]).drop_duplicates(subset='Player_Id')

    # Fill missing slots if required and enforce constraints
    for child in [child1, child2]:
        while len(child) < SQUAD_SIZE:
            role = random.choice(list(COMPOSITION.keys()))
            replacement = players_data[players_data['Role'] == role].drop_duplicates(subset='Player_Id').sample(n=1)
            child = pd.concat([child, replacement]).drop_duplicates(subset='Player_Id')
    return child1, child2

# Mutation
def mutate(team):
    """
    Mutate a team by replacing a random player with another valid player.
    """
    if random.random() < MUTATION_RATE:
        role = random.choice(list(COMPOSITION.keys()))
        available_players = players_data[players_data['Role'] == role].drop_duplicates(subset='Player_Id')
        replacement = available_players[~available_players['Player_Id'].isin(team['Player_Id'])].sample(n=1)
        replace_index = random.randint(0, len(team) - 1)
        team.iloc[replace_index] = replacement.iloc[0]
    return team

# Calculate metrics
def calculate_metrics(team):
    """
    Calculate detailed metrics for the selected team to evaluate performance.
    """
    batsmen = team[team['Role'] == 'Batsman']
    bowlers = team[team['Role'] == 'Bowler']
    all_rounders = team[team['Role'] == 'All-Rounder']
    total_runs = batsmen['total_runs'].sum()
    average_strike_rate = batsmen['strike_rate'].replace([np.inf, -np.inf], np.nan).mean()
    boundary_percentage = batsmen['boundary_percentage'].replace([np.inf, -np.inf], np.nan).mean()
    total_wickets = bowlers['wickets'].sum()
    average_all_rounder_index = all_rounders['all_rounder_index'].replace([np.inf, -np.inf], np.nan).mean()
    fitness_score = calculate_fitness(team)
    balance_score = len(batsmen) / 6 + len(bowlers) / 6 + len(all_rounders) / 3
    metrics = {
        "Total Runs (Batsmen)": total_runs,
        "Average Strike Rate (Batsmen)": f"{average_strike_rate:.3f}" if not np.isnan(average_strike_rate) else "N/A",
        "Boundary Percentage (Batsmen)": f"{boundary_percentage:.3f}%" if not np.isnan(boundary_percentage) else "N/A",
        "Total Wickets (Bowlers)": total_wickets,
        "Average All-Rounder Index (Team)": f"{average_all_rounder_index:.3f}" if not np.isnan(average_all_rounder_index) else "N/A",
        "Overall Fitness Score (Team)": f"{fitness_score:.3f}",
        "Balance Score": f"{balance_score:.3f}"
    }
    return metrics

# Genetic Algorithm
def genetic_algorithm():
    """
    Optimize the team selection using a genetic algorithm.
    """
    population = initialize_population(players_data)
    print("Initial population generated.")
    for generation in range(GENERATIONS):
        print(f"Generation {generation + 1}/{GENERATIONS}")
        fitness_scores = [calculate_fitness(team) for team in population]
        next_generation = []
        while len(next_generation) < POPULATION_SIZE:
            parent1 = tournament_selection(population, fitness_scores)
            parent2 = tournament_selection(population, fitness_scores)
            if random.random() < CROSSOVER_RATE:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            child1 = mutate(child1)
            child2 = mutate(child2)
            next_generation.extend([child1, child2])
        population = next_generation[:POPULATION_SIZE]
    fitness_scores = [calculate_fitness(team) for team in population]
    best_team = population[np.argmax(fitness_scores)]
    best_score = max(fitness_scores)
    return best_team, best_score

# Execute Genetic Algorithm
optimal_team, optimal_score = genetic_algorithm()
optimal_team_metrics = calculate_metrics(optimal_team)
print("\nOptimal Team Metrics:")
for metric, value in optimal_team_metrics.items():
    print(f"{metric}: {value}")

metrics_df = pd.DataFrame([optimal_team_metrics])
metrics_df.to_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project/metrics/optimal_team_metrics.csv', index=False)
optimal_team.to_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project/final_output/optimal_team_new.csv', index=False)
print(f"Optimal Team Score: {optimal_score}")
print("Optimal Team:")
print(optimal_team)

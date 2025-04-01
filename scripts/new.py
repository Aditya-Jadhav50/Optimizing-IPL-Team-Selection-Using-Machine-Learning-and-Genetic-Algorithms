import pandas as pd
import random
import numpy as np
from multiprocessing import Pool

# Load player data (batsmen, bowlers, all-rounders)
players_data = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/merged_player_data_with_roles_and_wickets.csv')  # Merged data for all players

# Parameters
SQUAD_SIZE = 17
POPULATION_SIZE = 100
GENERATIONS = 50
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.8
OVERSEAS_LIMIT = 6

COMPOSITION = {'Batsman': 4, 'Bowler': 4, 'All-Rounder': 7, 'Wicketkeeper': 2}

# Fitness function
def calculate_fitness(team):
    """
    Calculate fitness of a team based on batting, bowling, and all-rounder contributions.
    """
    batting_score = team['total_runs'].sum()
    bowling_score = (100 / (team['economy_rate'] + 1e-5)).sum()
    all_rounder_score = team['all_rounder_index'].sum()
    return batting_score * 0.4 + bowling_score * 0.4 + all_rounder_score * 0.2

# Validate constraints
def validate_constraints(team):
    """
    Validate team constraints: role distribution, overseas player limit, and squad size.
    """
    role_counts = team['Role'].value_counts()
    overseas_count = len(team[team['Country'] != 'India'])
    return (
        len(team) == SQUAD_SIZE and
        role_counts.get('Batsman', 0) >= COMPOSITION['Batsman'] and
        role_counts.get('Bowler', 0) >= COMPOSITION['Bowler'] and
        role_counts.get('All-Rounder', 0) >= COMPOSITION['All-Rounder'] and
        role_counts.get('Wicketkeeper', 0) >= COMPOSITION['Wicketkeeper'] and
        overseas_count == OVERSEAS_LIMIT
        
    )

# Generate initial population
def initialize_population(players):
    """
    Generate an initial population of valid teams.
    """
    population = []
    for _ in range(POPULATION_SIZE):
        while True:
            # Select roles
            batsmen = players[(players['Role'] == 'Batsman')].sample(n=COMPOSITION['Batsman'], replace=False)
            bowlers = players[(players['Role'] == 'Bowler')].sample(n=COMPOSITION['Bowler'], replace=False)
            all_rounders = players[(players['Role'] == 'All-Rounder')].sample(n=COMPOSITION['All-Rounder'], replace=False)
            wicketkeepers = players[(players['Role'] == 'Wicketkeeper')].sample(n=COMPOSITION['Wicketkeeper'], replace=False)

            # Combine and validate overseas limit
            sampled_team = pd.concat([batsmen, bowlers, all_rounders, wicketkeepers])
            overseas_count = len(sampled_team[sampled_team['Country'] != 'India'])

            if overseas_count <= OVERSEAS_LIMIT and validate_constraints(sampled_team):
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
    child1 = pd.concat([parent1.iloc[:split_point], parent2.iloc[split_point:]]).drop_duplicates()
    child2 = pd.concat([parent2.iloc[:split_point], parent1.iloc[split_point:]]).drop_duplicates()
    
    # Fill missing slots if required
    for child in [child1, child2]:
        while len(child) < SQUAD_SIZE:
            role = random.choice(list(COMPOSITION.keys()))
            replacement = players_data[players_data['Role'] == role].sample(n=1)
            child = pd.concat([child, replacement]).drop_duplicates()
    return child1, child2

# Mutation
def mutate(team):
    """
    Mutate a team by replacing a random player with another valid player.
    """
    if random.random() < MUTATION_RATE:
        role = random.choice(list(COMPOSITION.keys()))
        replacement = players_data[players_data['Role'] == role].sample(n=1)
        replace_index = random.randint(0, len(team) - 1)
        team.iloc[replace_index] = replacement.iloc[0]
    return team

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
    
    # Select the best team
    fitness_scores = [calculate_fitness(team) for team in population]
    best_team = population[np.argmax(fitness_scores)]
    best_score = max(fitness_scores)
    return best_team, best_score

# Run the genetic algorithm
optimal_team, optimal_score = genetic_algorithm()

# Save the result
optimal_team.to_csv('optimal_team_test.csv', index=False)
print(f"Optimal Team Score: {optimal_score}")
print("Optimal Team:")
print(optimal_team)
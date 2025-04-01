import pandas as pd
import random
import numpy as np

# Load player data
players_data = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/merged_player_data_with_roles_and_wickets_new.csv')  # Merged data for all players

# Parameters
SQUAD_SIZE = 17
OVERSEAS_LIMIT = 6
COMPOSITION = {'Batsman': 6, 'Bowler': 6, 'All-Rounder': 3, 'Wicketkeeper': 2}
INITIAL_TEMPERATURE = 100
COOLING_RATE = 0.95
MAX_ITERATIONS = 500  # Reduced for performance
EARLY_STOPPING_ROUNDS = 50  # Stop if no improvement in this many rounds

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

# Constraint validation
def validate_constraints(team):
    """
    Validate team constraints: role distribution, squad size, and foreign player limit.
    """
    role_counts = team['Role'].value_counts()
    overseas_count = len(team[team['Country'] != 'India'])
    return (
        len(team) == SQUAD_SIZE and
        role_counts.get('Batsman', 0) >= COMPOSITION['Batsman'] and
        role_counts.get('Bowler', 0) >= COMPOSITION['Bowler'] and
        role_counts.get('All-Rounder', 0) >= COMPOSITION['All-Rounder'] and
        role_counts.get('Wicketkeeper', 0) >= COMPOSITION['Wicketkeeper'] and
        overseas_count <= OVERSEAS_LIMIT
    )

# Generate initial solution
def generate_initial_solution(players):
    """
    Generate an initial valid team satisfying all constraints.
    """
    while True:
        batsmen = players[players['Role'] == 'Batsman'].sample(n=COMPOSITION['Batsman'], replace=False)
        bowlers = players[players['Role'] == 'Bowler'].sample(n=COMPOSITION['Bowler'], replace=False)
        all_rounders = players[players['Role'] == 'All-Rounder'].sample(n=COMPOSITION['All-Rounder'], replace=False)
        wicketkeepers = players[players['Role'] == 'Wicketkeeper'].sample(n=COMPOSITION['Wicketkeeper'], replace=False)
        team = pd.concat([batsmen, bowlers, all_rounders, wicketkeepers]).drop_duplicates(subset='Player_Id')
        if validate_constraints(team):
            return team

# Mutate a team
def mutate_team(team, players):
    """
    Mutate a team by replacing a random player with another valid player.
    """
    for _ in range(10):  # Limit mutation attempts to avoid infinite loops
        role = random.choice(list(COMPOSITION.keys()))
        available_players = players[players['Role'] == role]
        replacement = available_players[~available_players['Player_Id'].isin(team['Player_Id'])].sample(n=1)
        replace_index = random.randint(0, len(team) - 1)
        team.iloc[replace_index] = replacement.iloc[0]
        if validate_constraints(team):
            return team
    return team  # Return the original team if no valid mutation is found

# Simulated Annealing
def simulated_annealing(players):
    """
    Optimize team selection using Simulated Annealing.
    """
    current_team = generate_initial_solution(players)
    current_fitness = calculate_fitness(current_team)
    best_team = current_team.copy()
    best_fitness = current_fitness
    temperature = INITIAL_TEMPERATURE
    no_improvement_rounds = 0

    for iteration in range(MAX_ITERATIONS):
        new_team = mutate_team(current_team.copy(), players)
        if validate_constraints(new_team):
            new_fitness = calculate_fitness(new_team)

            # Accept new team based on fitness improvement or probabilistic acceptance
            if new_fitness > current_fitness or np.random.rand() < np.exp((new_fitness - current_fitness) / temperature):
                current_team = new_team
                current_fitness = new_fitness

                # Update best team if current team is better
                if current_fitness > best_fitness:
                    best_team = current_team.copy()
                    best_fitness = current_fitness
                    no_improvement_rounds = 0  # Reset early stopping counter
                else:
                    no_improvement_rounds += 1

        # Cool down temperature
        temperature *= COOLING_RATE

        # Check for early stopping
        if no_improvement_rounds >= EARLY_STOPPING_ROUNDS:
            print("Early stopping triggered due to no improvement.")
            break

        # Debug: Print progress every 10% of iterations
        if (iteration + 1) % (MAX_ITERATIONS // 10) == 0:
            print(f"Iteration {iteration + 1}/{MAX_ITERATIONS}, Best Fitness: {best_fitness:.2f}")

    return best_team, best_fitness

# Run Simulated Annealing
optimal_team, optimal_score = simulated_annealing(players_data)

# Save results
optimal_team.to_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project/final_output/optimal_team_simulated_annealing.csv', index=False)
print(f"Optimal Team Score: {optimal_score:.2f}")
print("Optimal Team:")
print(optimal_team)


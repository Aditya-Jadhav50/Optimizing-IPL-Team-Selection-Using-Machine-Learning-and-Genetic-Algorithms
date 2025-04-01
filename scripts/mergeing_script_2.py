import pandas as pd

# Load datasets
print("Loading datasets...")
ball_by_ball=pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/ball_by_ball_cleaned.csv')  # Ball-by-ball cleaned dataset
players_data =  pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/player_cleaned.csv')
merged_data =pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/final_merged_dataset.csv')    # Merged dataset
player_match_data = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/player_match_cleaned.csv')
team_data = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/team_cleaned.csv')

# Step 1: Calculate valid dismissals credited to bowlers
print("Calculating valid dismissals credited to bowlers...")
valid_dismissals = ball_by_ball[ball_by_ball['Dissimal_Type'].isin(['caught', 'bowled', 'lbw', 'stumped', 'hit wicket', 'caught and bowled'])]
wickets_data = valid_dismissals.groupby('Bowler_Id').size().reset_index(name='wickets')

# Step 2: Map Bowler_Id to Player_Id using player_cleaned dataset
print("Mapping bowler IDs to player IDs...")
wickets_data = wickets_data.merge(players_data[['Player_Id', 'Player_Name']], left_on='Bowler_Id', right_on='Player_Id', how='left')

# Step 3: Merge wickets data into the merged dataset
print("Merging wickets data into merged dataset...")
merged_data = merged_data.merge(wickets_data[['Player_Id', 'wickets']], on='Player_Id', how='left')
merged_data['wickets'] = merged_data['wickets'].fillna(0).astype(int)  # Fill missing wickets with 0 and convert to int

# Step 4: Map Team Name to players
print("Mapping team names to players...")
player_match_team = player_match_data.merge(team_data[['Team_Id', 'Team_Name']], on='Team_Id', how='left')
team_mapping = player_match_team[['Player_Id', 'Team_Name']].drop_duplicates()
merged_data = merged_data.merge(team_mapping, on='Player_Id', how='left')

# Step 4: Dynamically assign roles based on performance dominance
print("Assigning roles dynamically...")
merged_data['Role'] = 'Batsman'  # Default to Batsman

# Assign players with over 1,000 runs as Batsmen
batsman_condition = merged_data['total_runs'] > 1000
merged_data.loc[batsman_condition, 'Role'] = 'Batsman'

# Assign All-Rounders: Significant contributions in both batting and bowling
all_rounder_condition = (merged_data['total_runs'] > 100) & (merged_data['wickets'] >= 5) & ~batsman_condition
merged_data.loc[all_rounder_condition, 'Role'] = 'All-Rounder'

# Assign Bowlers: High wickets and low batting contribution
bowler_condition = (merged_data['wickets'] > 10) & (merged_data['total_runs'] <= 1000)
merged_data.loc[bowler_condition, 'Role'] = 'Bowler'

# Assign Wicketkeepers: Players marked as Is_Keeper
keeper_condition = merged_data['Is_Keeper'] == 1
merged_data.loc[keeper_condition, 'Role'] = 'Wicketkeeper'

# Save the updated dataset
print("Saving updated merged dataset with roles and accurate wickets...")
merged_data.to_csv('merged_player_data_with_roles_and_wickets_new.csv', index=False)

print("Updated dataset saved as 'merged_player_data_with_roles_and_wickets.csv'")

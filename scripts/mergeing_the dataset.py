import pandas as pd

batsman_data = pd.read_csv("C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/batsmen_stats.csv")
bowler_data = pd.read_csv("C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/bowling_stats.csv")
all_rounder_data = pd.read_csv("C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/all_rounder_stats.csv")
player_match_cleaned = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/player_match_cleaned.csv')  # Player match dataset
player_cleaned = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/player_cleaned.csv')  # Player dataset (with Country column)


# Rename columns for clarity to avoid conflicts during merging
batsman_data = batsman_data.rename(columns={
    'Batsman_Id': 'Player_Id',
    'Player_Name': 'Player_Name'
})

bowler_data = bowler_data.rename(columns={
    'Bowler_Id': 'Player_Id',
    'Player_Name': 'Player_Name'
})

all_rounder_data = all_rounder_data.rename(columns={
    'Batsman_Id': 'Player_Id',
    'Player_Name_batting': 'Player_Name',
    'Player_Name_bowling': 'Player_Name'
})

# Extract `Is_Keeper` and `Country` columns
keeper_info = player_match_cleaned[['Player_Id', 'Is_Keeper']].drop_duplicates()
country_info = player_cleaned[['Player_Id', 'Country']]

# Merge batsman data
merged_data = batsman_data[['Player_Id', 'total_runs', 'balls_faced', 'boundaries', 'strike_rate', 
                            'boundary_percentage', 'Player_Name']]

# Merge bowler data
merged_data = pd.merge(merged_data, bowler_data[['Player_Id', 'total_runs_conceded', 'balls_bowled', 
                                                 'economy_rate']], on='Player_Id', how='outer')

# Merge all-rounder data
merged_data = pd.merge(merged_data, all_rounder_data[['Player_Id', 'all_rounder_index']], on='Player_Id', how='outer')

# Merge with `Is_Keeper` information
merged_data = pd.merge(merged_data, keeper_info, on='Player_Id', how='left')

# Merge with `Country` information
merged_data = pd.merge(merged_data, country_info, on='Player_Id', how='left')

# Clean player names (remove leading/trailing spaces)
merged_data['Player_Name'] = merged_data['Player_Name'].str.strip()

# Remove rows with missing or blank player names
merged_data = merged_data[merged_data['Player_Name'].notnull() & (merged_data['Player_Name'] != '')]

# Ensure all relevant columns are included
final_columns = [
    'Player_Id', 'Player_Name', 'total_runs', 'balls_faced', 'boundaries', 'strike_rate', 
    'boundary_percentage', 'total_runs_conceded', 'balls_bowled', 'economy_rate', 
    'all_rounder_index', 'Is_Keeper', 'Country'
]

# Reorder the columns
merged_data = merged_data[final_columns]

# Save the final merged dataset
merged_data.to_csv('final_merged_dataset.csv', index=False)

print("Final merged dataset saved as 'final_merged_dataset.csv'.")
print(merged_data.head())

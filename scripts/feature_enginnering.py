# Feature Engineering for IPL Dataset

import pandas as pd

# Load Datasets
ball = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/ball_by_ball_cleaned.csv')
player = pd.read_csv('C:/Users/Aditya/OneDrive - University of Hertfordshire/Project_2/outputs/player_cleaned.csv')
# Feature Engineering for IPL Dataset

# Inspect Columns
print("Columns in ball dataset:", ball.columns)
print("Columns in player dataset:", player.columns)

# Calculate Batting Metrics
ball["Batsman_Scored"] = pd.to_numeric(ball["Batsman_Scored"], errors="coerce")
batting_stats = ball.groupby("Batsman_Id").agg(
    total_runs=("Batsman_Scored", "sum"),
    balls_faced=("Ball_Id", "count"),
    boundaries=("Batsman_Scored", lambda x: sum((x == 4) | (x == 6)))
).reset_index()

# Add Additional Batting Metrics
batting_stats["strike_rate"] = (batting_stats["total_runs"] / batting_stats["balls_faced"]) * 100
batting_stats["boundary_percentage"] = (batting_stats["boundaries"] / batting_stats["balls_faced"]) * 100

# Map Player Names
player_names = dict(zip(player["Player_Id"], player["Player_Name"]))
batting_stats["Player_Name"] = batting_stats["Batsman_Id"].map(player_names)

# Filter Batsmen Based on Performance
batsmen = batting_stats[batting_stats["balls_faced"] > 20]  # Minimum threshold for balls faced

# Calculate Bowling Metrics
valid_deliveries = ball[ball["Extra_Type"].isna() | (ball["Extra_Type"] != "wides")]
valid_deliveries["Runs_Conceded"] = pd.to_numeric(valid_deliveries["Batsman_Scored"], errors="coerce") + pd.to_numeric(valid_deliveries["Extra_Runs"], errors="coerce")

bowling_stats = valid_deliveries.groupby("Bowler_Id").agg(
    total_runs_conceded=("Runs_Conceded", "sum"),
    balls_bowled=("Ball_Id", "count")
).reset_index()

# Calculate Economy Rate
bowling_stats["economy_rate"] = bowling_stats["total_runs_conceded"] / (bowling_stats["balls_bowled"] / 6)

# Filter Bowlers Based on Performance
bowlers = bowling_stats[bowling_stats["balls_bowled"] > 12]  # Minimum threshold for balls bowled
bowlers["Player_Name"] = bowlers["Bowler_Id"].map(player_names)

# Combine Batting and Bowling Metrics for All-Rounders
all_rounder_stats = pd.merge(
    batsmen,
    bowlers,
    left_on="Batsman_Id",
    right_on="Bowler_Id",
    how="inner",
    suffixes=("_batting", "_bowling")
)

# Calculate All-Rounder Index
all_rounder_stats["all_rounder_index"] = (
    0.5 * all_rounder_stats["strike_rate"] +
    0.5 * (100 / all_rounder_stats["economy_rate"]) # inverting the metric to align with the logic of batting strike rate (higher values are better)
)

# Save Results
batsmen.to_csv("batsmen_stats.csv", index=False)
bowlers.to_csv("bowlers_stats.csv", index=False)
all_rounder_stats.to_csv("all_rounder_stats.csv", index=False)

# Display Final Metrics
print("Batsmen Stats Sample:")
print(batsmen.head())

print("\nBowlers Stats Sample:")
print(bowlers[["Player_Name", "balls_bowled", "total_runs_conceded", "economy_rate"]].head())

print("\nAll-Rounder Stats Sample:")
print(all_rounder_stats[["Player_Name_batting", "all_rounder_index"]].head())

import pandas as pd
import os

def load_datasets(data_path):
    """Load all IPL datasets."""
    datasets = {
        "ball_by_ball": pd.read_csv(os.path.join(data_path, "Ball_by_Ball.csv")), #os.path Handles file paths in a platform-independent way.
        "match": pd.read_csv(os.path.join(data_path, "Match.csv")),
        "player": pd.read_csv(os.path.join(data_path, "Player.csv")),
        "player_match": pd.read_csv(os.path.join(data_path, "Player_Match.csv")),
        "season": pd.read_csv(os.path.join(data_path, "Season.csv")),
        "team": pd.read_csv(os.path.join(data_path, "Team.csv")),
    }
    return datasets

def clean_ball_by_ball(ball_by_ball_df):
    
    """Clean the Ball by Ball dataset."""
    # Rename columns for clarity
    ball_by_ball_df.rename(columns={
        "Striker_Id": "Batsman_Id",
        "Non_Striker_Id": "Runner_Id"
    }, inplace=True)
    
    # Drop unnecessary columns if any
    ball_by_ball_df.drop(columns=["Player_dissimal_Id"], inplace=True, errors="ignore")

    return ball_by_ball_df

def clean_match_data(match_df):
    """Clean the Match dataset."""
    # Handle missing values
    match_df["Venue_Name"].fillna("Unknown", inplace=True)
    match_df["City_Name"].fillna("Unknown", inplace=True)
    
    # Add Match_Year for easier grouping
    match_df["Match_Year"] = pd.to_datetime(match_df["Match_Date"]).dt.year

    return match_df

def clean_player_data(player_df):
    """Clean the Player dataset."""
    # Fill missing values for names
    player_df["Player_Name"].fillna("Unknown Player", inplace=True)

    # Standardize batting and bowling hands
    player_df["Batting_Hand"] = player_df["Batting_Hand"].fillna("Unknown").str.strip()
    player_df["Bowling_Skill"] = player_df["Bowling_Skill"].fillna("Unknown").str.strip()

    return player_df

def clean_player_match_data(player_match_df):
    """Clean the Player Match dataset."""
    # Ensure all numeric columns are filled
    player_match_df.fillna(0, inplace=True)
    return player_match_df

def clean_season_data(season_df):
    """Clean the Season dataset."""
    # No specific cleaning needed, but ensure no duplicates
    season_df = season_df.drop_duplicates()
    return season_df

def clean_team_data(team_df):
    """Clean the Team dataset."""
    # Standardize team names and remove duplicates
    team_df["Team_Name"] = team_df["Team_Name"].str.strip().str.title()
    team_df = team_df.drop_duplicates()
    return team_df

def save_cleaned_data(datasets, output_path):
    """Save cleaned datasets to the output directory."""
    for name, df in datasets.items():
        df.to_csv(os.path.join(output_path, f"{name}_cleaned.csv"), index=False)

if __name__ == "__main__":
    # Define paths
    data_path = "data/"  # Adjust path as needed
    output_path = "outputs/"
    os.makedirs(output_path, exist_ok=True)
    
    # Load datasets
    datasets = load_datasets(data_path)
    
    # Clean each dataset
    datasets["ball_by_ball"] = clean_ball_by_ball(datasets["ball_by_ball"])
    datasets["match"] = clean_match_data(datasets["match"])
    datasets["player"] = clean_player_data(datasets["player"])
    datasets["player_match"] = clean_player_match_data(datasets["player_match"])
    datasets["season"] = clean_season_data(datasets["season"])
    datasets["team"] = clean_team_data(datasets["team"])
    
    # Save cleaned datasets
    save_cleaned_data(datasets, output_path)

    print("Data cleaning completed. Cleaned datasets are saved in the 'outputs/' directory.")

import pandas as pd
import numpy as np
import operator
import math
from sklearn.metrics import mean_squared_error
from statistics import mean
from user_CF import userBased_CF

# Get data from csv file
def get_data():
    df_movies = pd.read_csv('/Users/pouriatoopchi/Documents/Github_Sample_Upload/Local_path/Recommendation_System/data/movies.csv')
    df_ratings = pd.read_csv('/Users/pouriatoopchi/Documents/Github_Sample_Upload/Local_path/Recommendation_System/data/ratings.csv')
    # Currently not required
    del df_movies['genres']
    del df_ratings['timestamp']
    # Remove year from movie title and create as separate column
    df_movies['movie_year'] = df_movies['title'].str.extract("\((.*)\)")
    df_movies['title'] = df_movies['title'].str.replace("\((.*)\)", "", regex=True)
    return df_movies, df_ratings

# Run the User-Based CF
def run():
    # Get data
    df_movies, df_ratings = get_data()
    # Run user-based CF class
    userCF = userBased_CF(df_movies, df_ratings)
    metrics = userCF.main_run_evaluate(K=50, positive_only=False, threshold=0.0)
    print(metrics)

if __name__ == '__main__':
    run()

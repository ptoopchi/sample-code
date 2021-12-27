import pandas as pd
import numpy as np
import operator
import math
from sklearn.metrics import mean_squared_error

class model_evaluate:
    def __init__(self, df_ratings):
        self.df_ratings = df_ratings

    # Calculate final ranking for target user and each of the movies
    def base_score_calculate(self, target, sim_users):
        # List of movies watched by target
        movie_list = target['movieId'].tolist()
        # Ratings of other people watched target movies
        sim_other_ratings = sim_users.merge(self.df_ratings, left_on='userId', right_on='userId')
        # Only get movies that are watched by target
        sim_other_ratings = sim_other_ratings[sim_other_ratings['movieId'].isin(movie_list)]
        # Calculate the weighted rating
        sim_other_ratings['weighted_rating'] = sim_other_ratings['similarity'] * sim_other_ratings['rating']
        # Group by movieId and calculate sum
        sum_ratings = sim_other_ratings.groupby('movieId', as_index=False).sum()[
            ['movieId', 'similarity', 'weighted_rating']]
        # From the sum, calculate the final weighted rating score for each movie for target
        sum_ratings['final_rating'] = sum_ratings['weighted_rating'] / sum_ratings['similarity']
        # Get the original ratings for each movie
        sum_ratings = sum_ratings.merge(target[['movieId', 'rating']], left_on='movieId', right_on='movieId')[
            ['movieId', 'final_rating', 'rating']]
        return sum_ratings

    # Calculate RMSE
    def RMSE(self, target, sim_users):
        sum_ratings = self.base_score_calculate(target, sim_users)
        # RMSE score of actual vs predicted
        return mean_squared_error(sum_ratings['rating'].tolist(), sum_ratings['final_rating'].tolist(), squared=False)

    # Calculate MSE
    def MSE(self, target, sim_users):
        sum_ratings = self.base_score_calculate(target, sim_users)
        # MSE score of actual vs predicted
        return mean_squared_error(sum_ratings['rating'].tolist(), sum_ratings['final_rating'].tolist(), squared=True)

    # Calculate Pres & Recall
    def Precision_Recall(self, target, sim_users, K):
        sum_ratings = self.base_score_calculate(target, sim_users)
        # Original relevant items [>= 3.5] = relevant
        original_relevant_items = sum_ratings[sum_ratings['rating'] >= 3.5]['movieId'].tolist()
        # Predicted relevant items [>= 3.5] = relevant for up to value 'K'
        temp_sum_ratings = sum_ratings.head(K)
        predicted_relevant_items = temp_sum_ratings[temp_sum_ratings['final_rating'] >= 3.5]['movieId'].tolist()
        # Calculate the intersection of lists
        relevant_items = len(set(original_relevant_items) & set(predicted_relevant_items))
        # Precision = (relevant @k) / (all items @k)
        precision = (relevant_items / temp_sum_ratings.shape[0])
        # recall = (relevant @k) / (total relevant items)
        recall = (relevant_items / len(original_relevant_items))
        return precision, recall
import pandas as pd
import numpy as np
import sys
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from statistics import mean


class userBased_CF:
    def __init__(self, df_movies, df_ratings):
        self.df_movies = df_movies
        self.df_ratings = df_ratings
        # Create ratings matrix
        self.ratings_matrix = df_ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        # Create the user similarity matrix [Cosine Similarity]
        self.user_sim_matrix = pd.DataFrame(cosine_similarity(self.ratings_matrix), index=self.ratings_matrix.index,
                                            columns=self.ratings_matrix.index)

    # Create predictions for all movies for a given user
    def create_all_recommendations(self, target_user, N=100):
        # Get the top N most similar users [index, similarity] (index is userId)
        # Below excludes the first user and gets N sim users
        most_similar_users = self.user_sim_matrix.loc[target_user].sort_values(ascending=False)[1:(N + 1)]
        # Get the sub matrix of all the top N similar users
        sub_user_matrix = self.ratings_matrix.loc[most_similar_users.index]
        # Converts Matrix to standard table
        sub_df = sub_user_matrix.stack().reset_index().rename(
            columns={'level_0': 'userId', 'level_1': 'movieId', 0: 'rating'})
        # Removes ratings that are NaN
        sub_df = sub_df[sub_df['rating'] != 0]
        # Merges ratings with the similarity score
        sub_df = sub_df.merge(most_similar_users, left_on='userId', right_on='userId').rename(
            columns={target_user: 'similarity'})
        # Calculate weighted rating
        sub_df['weighted_rating'] = sub_df['similarity'] * sub_df['rating']
        # Calculate sum of weights for each movie
        sub_df = sub_df.groupby('movieId', as_index=False).sum()[['movieId', 'similarity', 'weighted_rating']]
        # From the sum, calculate the final weighted rating score for each movie for target
        sub_df['prediction_userCF'] = sub_df['weighted_rating'] / sub_df['similarity']
        # Sort based on the predicted rating
        return sub_df[['movieId', 'prediction_userCF']]

    # Nicely presents the recommendations as a table
    def get_recommendations(self, target_user, K=30, random=False):
        # To get the recommend movies of each user
        recommend_items = self.create_all_recommendations(target_user).sort_values(by=['prediction_userCF'],
                                                                                   ascending=False)
        recommend_items = recommend_items.merge(self.df_movies[['movieId', 'title']], left_on='movieId',
                                                right_on='movieId')
        if random:
            # Selects N samples from the top 3 * N movies
            return recommend_items.head(3 * K).sample(K)
        else:
            # Selects the top N movies
            return recommend_items.head(K)

    # Base Method for Evaluations
    def base_score_CF(self, target_user, N=100):
        # Get dataframe of Movies already watched by user
        movie_list = self.df_ratings[self.df_ratings['userId'] == target_user][['movieId', 'rating']]
        # Get Predictions
        predictions = self.create_all_recommendations(target_user, N)
        # Create complete dataframe
        complete_df = movie_list.merge(predictions, left_on='movieId', right_on='movieId')
        return complete_df.sort_values(by=['prediction_userCF'], ascending=False)

    # Calculates the MSE score for a single user
    def MSE(self, target_user):
        complete_df = self.base_score_CF(target_user)
        return mean_squared_error(complete_df['rating'].tolist(), complete_df['prediction_userCF'].tolist(),
                                  squared=True)

    # Calculates the average MSE for all users
    def average_mse(self):
        scores = []
        counter = 0
        max_users = len(self.df_ratings['userId'].unique())
        for x in self.df_ratings['userId'].unique():
            counter += 1
            scores.append(self.MSE(x))
            # Updating Progress
            sys.stdout.write('\rEvaluated user: ' + str(counter) + ' out of ' + str(max_users))
            sys.stdout.flush()
        print("")  # Corrects the the last print of the sys
        return mean(scores)

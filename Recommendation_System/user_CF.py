import pandas as pd
import numpy as np
import operator
import math
from statistics import mean
from model_evaluate import model_evaluate
import sys

class userBased_CF:
    def __init__(self, df_movies, df_ratings):
        self.df_movies = df_movies
        self.df_ratings = df_ratings

    # Get other users that have watched the same movies as the target user
    def get_viewers_of_target(self, target_user, positive_only=False):
        # Gets list of movies rated by target (False)
        target_movies = target_user['movieId'].tolist()
        # If True then gets list of movies that are rated positively only by target
        if (positive_only):
            target_movies = target_user[target_user['rating'] >= 3.5]['movieId'].tolist()
        # Gets a subset of other people that have watched those movies
        viewers = self.df_ratings[(self.df_ratings['userId'] != target_user['userId'].values[0]) & (self.df_ratings['movieId'].isin(target_movies))]
        # Create sub-dataframes for each user [makes it easier to sort based on number of similar movies seen to target]
        viewers_sub_dataframes = viewers.groupby(['userId'])
        viewers_sub_dataframes = sorted(viewers_sub_dataframes, key=lambda x: len(x[1]), reverse=True)
        # Convert the sub dataframes back into a single dataframe
        return pd.concat(map(lambda x: x[1], viewers_sub_dataframes))

    # Get correlation of two users
    def user_correlation(self, target, other):
        # Get list of movies IDs of the other user
        sub_df_movies = other['movieId'].tolist()
        # Get movies by target that have also been watched by other user and then sort
        sorted_temp_target = target[(target['movieId'].isin(sub_df_movies))].sort_values(by=['movieId'])[
            'rating'].tolist()
        # Get the ratings of the movies (this list is already sorted)
        sorted_other_user = other['rating'].tolist()
        # Calculate Pearsons Correlation
        with np.errstate(all='ignore'):
            score = (np.corrcoef(sorted_temp_target, sorted_other_user)[0, 1])
            if (np.isnan(score)):
                return 0
            return score

    # Get similar users for the target user
    def get_similar_users(self, target, potential_users, process_num=100):
        # Get unique list of users IDs
        users_list = potential_users['userId'].unique()
        # Get similarity of each user to the target user
        sim_users = dict([(x, self.user_correlation(target, potential_users[potential_users['userId'] == x])) for x in
                          users_list[:process_num]])
        # Sort the dict based on value and return dataframe
        sim_users = dict(sorted(sim_users.items(), key=operator.itemgetter(1), reverse=True))
        return pd.DataFrame(sim_users.items(), columns=['userId', 'similarity'])

    # Filter users based on a pre-defined threshold
    def select_best_users(self, user_sim_df, threshold=0.6):
        return user_sim_df[user_sim_df['similarity'] >= threshold]

    # Create recommendations based on target user
    def create_recommendations(self, sim_users):
        # Ratings for all movies by similar users to the target user
        sim_other_ratings = sim_users.merge(self.df_ratings, left_on='userId', right_on='userId')
        # Calculate the weighted rating
        sim_other_ratings['weighted_rating'] = sim_other_ratings['similarity'] * sim_other_ratings['rating']
        # Group by movieId and calculate sum
        sum_ratings = sim_other_ratings.groupby('movieId', as_index=False).sum()[
            ['movieId', 'similarity', 'weighted_rating']]
        # From the sum, calculate the final weighted rating score for each movie for target
        sum_ratings['final_rating'] = sum_ratings['weighted_rating'] / sum_ratings['similarity']
        # Return the table along with the movies
        return sum_ratings.sort_values(by=['final_rating'], ascending=False)[['movieId', 'final_rating']]

    # Select recommendations based on the list created
    def select_K_recommendations(self, recommend_items, N):
        movie_ids = recommend_items['movieId'].tolist()
        titles = [self.df_movies.loc[self.df_movies['movieId'] == x, 'title'].values[0] for x in movie_ids]
        recommend_items['title'] = titles
        return recommend_items.head(N)

    # Provide either random of standard recommendations to user
    def get_recommendations(self, sim_users, N=10, random=False):
        # To get the recommend movies of each user
        recommend_items = self.create_recommendations(sim_users)
        # If random = True it will create 2N recommendations and random sample N items
        if (random):
            return self.select_K_recommendations(recommend_items, (2*N)).sample(N)
        else:
            return self.select_K_recommendations(recommend_items, N)

    # Creates the list of movies recommended for target user
    def user_recommend(self, userId, positive_only=False, threshold=0.0, N=10, random=False):
        # Dataset Split
        target = self.df_ratings[self.df_ratings['userId'] == userId]
        # Get other users that have watched the same movies seen in the training set
        viewers = self.get_viewers_of_target(target, positive_only)
        # Check how similar these users are to the target user
        sim_users = self.get_similar_users(target, viewers, process_num=50)
        # Selecting a subset of these similar users
        sim_users = self.select_best_users(sim_users, threshold=threshold)
        return self.get_recommendations(sim_users, N=N, random=random)

    def user_train_test_split(self, target, testing_split=0.2):
        train_set_size = math.floor(len(target) * (1 - testing_split))
        df_shuffle = target.sample(frac=1)
        return df_shuffle[:train_set_size], df_shuffle[train_set_size:]

    def main_run_evaluate(self, K, positive_only=False, threshold=0.6):
        count = 0
        fails = 0
        # Mean MSE, Precision and Recall Score
        avg_mse_test = []
        avg_precision_test = []
        avg_recall_test = []
        # List of all unique users
        all_users = self.df_ratings['userId'].unique()
        # initialise the model_evaluate class
        modelEval = model_evaluate(self.df_ratings)
        # Performing the calculation for all users in dataset
        for user in (all_users):
            try:
                target = self.df_ratings[self.df_ratings['userId'] == user]
                other = self.df_ratings[self.df_ratings['userId'] != user]
                # Create user training and test set
                train, test = self.user_train_test_split(target, testing_split=0.2)
                # Get other users that have watched the same movies seen in the training set
                viewers = self.get_viewers_of_target(train, positive_only)
                # Check how similar these users are to the target user
                sim_users = self.get_similar_users(train, viewers, process_num=50)
                # Selecting a subset of these similar users
                sim_users = self.select_best_users(sim_users, threshold=threshold)
                # Evaluate the performance for target user
                mse_test = modelEval.MSE(test, sim_users)
                precision_test, recall_test = modelEval.Precision_Recall(test, sim_users, K=K)
                # Append to avg lists
                avg_mse_test.append(mse_test)
                avg_precision_test.append(precision_test)
                avg_recall_test.append(recall_test)
            except:
                # Due to small dataset size if it cant find other users with any related movies
                # it will throw an exception and it is caught error
                fails += 1
            # Dynamically print the percentage without adding new line each time
            sys.stdout.write('\rPercentage Complete:  ' + str(round(count / len(all_users) * 100)) + "%")
            sys.stdout.flush()
            count += 1
        # Ensures new line is made so other print statements fall on the next line
        print("")
        metrics = {'avg_mse_test': mean(avg_mse_test), 'avg_precision_test': mean(avg_precision_test),
                   'avg_recall_test': mean(avg_recall_test)}

        return metrics






import numpy as np
from sklearn.metrics import mean_squared_error
from content_based import content_based
from user_CF import userBased_CF
from sklearn.svm import SVR
import sys
from statistics import mean


class hybrid:
    def __init__(self, df_movies, df_ratings, df_movies_features):
        self.df_movies = df_movies
        self.df_ratings = df_ratings
        self.df_movies_features = df_movies_features
        # Initialise the models
        self.userCF = userBased_CF(df_movies, df_ratings)
        self.content_model = content_based(df_movies_features, df_ratings)
        self.model = SVR(C=1.5)

    # Creates a weighted prediction of several models
    # For weights i[0] = user-based model and i[1] = content based model
    def create_user_recommendation(self, target_user, weights=(0.5, 0.5)):
        # Get Predictions from Content-Based Model
        df_content = self.content_model.create_user_predictions(target_user)
        # Get Predictions from User-Based Model
        df_user_based = self.userCF.create_all_recommendations(target_user, N=100)
        # Combine the results into one Dataframe
        df_combine = df_user_based.merge(df_content[['movieId', 'prediction_content']], left_on='movieId',
                                         right_on='movieId')
        df_combine['weighted_prediction'] = (df_combine['prediction_userCF'] * weights[0]) + (
                df_combine['prediction_content'] * weights[1])
        return df_combine[['movieId', 'weighted_prediction']]

    # Calculates the MSE score for a single user
    def MSE(self, target_user, weights=(0.4, 0.6)):
        # Get dataframe of Movies already watched by user
        movie_list = self.df_ratings[self.df_ratings['userId'] == target_user][['movieId', 'rating']]
        # Get Predictions
        predictions = self.create_user_recommendation(target_user, weights)
        # Create complete dataframe
        complete_df = movie_list.merge(predictions, left_on='movieId', right_on='movieId')
        complete_df = complete_df.sort_values(by=['weighted_prediction'], ascending=False)
        return mean_squared_error(complete_df['rating'].tolist(), complete_df['weighted_prediction'].tolist(),
                                  squared=True)

    # Base Method for Evaluations
    def hybrid_evaluate(self, weights=(0.4, 0.6)):
        scores = []
        counter = 0
        max_users = len(self.df_ratings['userId'].unique())
        for x in self.df_ratings['userId'].unique():
            counter += 1
            scores.append(self.MSE(x, weights))
            # Updating Progress
            sys.stdout.write('\rEvaluated user: ' + str(counter) + ' out of ' + str(max_users))
            sys.stdout.flush()
        print("")  # Corrects the the last print of the sys
        return mean(scores)

    # Used to Find the best weights for hybrid model
    # The Best was (0.4, 0.6) = [0.4 = user based & 0.6 = content based]
    def hybrid_gridsearch(self):
        scores = []
        x = np.arange(0.3, 0.8, 0.1)  # Creates list from 0.3 to 0.7 in 0.1 increments
        y = x[::-1]  # reverses the above array
        weights = zip(x, y)
        for weight in weights:
            print("Testing Weights: ", str(weight))
            score = self.hybrid_evaluate(weights=weight)
            print("Average Score: ", score)
            scores.append((weight, score))
            print("-----")

        print("\nFinal Scores:")
        for result in scores:
            print(result)

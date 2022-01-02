import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.svm import SVR
from statistics import mean
import sys


class content_based:
    def __init__(self, df_movies_features, df_ratings):
        self.df_movies_features = df_movies_features
        self.df_ratings = df_ratings
        # Gets group by DF of ratings for each user
        self.df_user_content = pd.merge(df_ratings, df_movies_features, on='movieId')
        self.df_user_content = self.df_user_content.groupby(['userId'])
        # Gets dataframe of the unique movies in DF
        self.movies = df_movies_features[df_movies_features.columns.difference(['movieId', 'title'])]

    # Evaluates the models MSE Score
    # Used for model testing
    def model_evaluate(self, model):
        mse_score = []
        counter = 0
        max_users = len(self.df_user_content)
        # Loop through each user
        for group_name, df_group in self.df_user_content:
            y = df_group['rating']
            df_group = df_group[df_group.columns.difference(['title', 'movieId', 'userId', 'rating'])]
            # Create train and test split
            X_train, X_test, y_train, y_test = train_test_split(df_group, y, test_size=0.2)
            model.fit(X_train, y_train)
            # Create predictions
            preds = model.predict(X_test)
            mse_score.append(mean_squared_error(y_test, preds))
            # Updating Progress
            counter += 1
            sys.stdout.write('\rEvaluated Model for user: ' + str(counter) + ' out of ' + str(max_users))
            sys.stdout.flush()
        print("")  # Corrects the the last print of the sys
        return mean(mse_score)

    # Creates movie predictions for selected user
    def create_user_predictions(self, user_id):
        df_group = self.df_user_content.get_group(user_id)
        y = df_group['rating']
        df_group = df_group[df_group.columns.difference(['title', 'movieId', 'userId', 'rating'])]
        # Create train and test split
        X_train, X_test, y_train, y_test = train_test_split(df_group, y, test_size=0.2)
        model = SVR(C=1.5).fit(X_train, y_train)
        # Create predictions
        preds = model.predict(self.movies)
        # Return predictions
        data = {'userId': ([user_id] * len(self.df_movies_features['movieId'].tolist())),
                'movieId': self.df_movies_features['movieId'].tolist(), 'prediction': preds}
        return pd.DataFrame(data)

    # Create Predictions for every user
    def all_users_prediction(self):
        all_predictions = []
        counter = 0
        max_users = len(self.df_ratings['userId'].unique())
        for x in self.df_ratings['userId'].unique():
            counter += 1
            all_predictions.append(self.create_user_predictions(x))
            # Updating Progress
            sys.stdout.write('\rCreating Predictions for user: ' + str(counter) + ' out of ' + str(max_users))
            sys.stdout.flush()
        print("")  # Corrects the the last print of the sys
        return pd.concat(all_predictions)

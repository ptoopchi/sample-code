import pandas as pd

from movies_web_scrapper import movie_scrape
from user_CF import userBased_CF
from movies_feature_engineering import feature_engineering

# Get data from csv file
def get_data():
    df_movies = pd.read_csv('data/movies.csv')
    df_ratings = pd.read_csv('data/ratings.csv')
    # Currently not required
    del df_movies['genres']
    del df_ratings['timestamp']
    # Remove year from movie title and create as separate column
    df_movies['movie_year'] = df_movies['title'].str.extract("\((.*)\)")
    df_movies['title'] = df_movies['title'].str.replace("\((.*)\)", "", regex=True)
    return df_movies, df_ratings

def extra_movies_data():
    df_tags = pd.read_csv('data/tags.csv')
    df_movies = pd.read_csv('data/movies.csv')
    df_links = pd.read_csv('data/links.csv')
    scrap = movie_scrap(df_movies, df_links, df_tags)
    df_movies_detailed = scrap.run()
    return df_movies_detailed

# THIS METHOD WILL ONLY WORK ONCE THE extra_movies_data() has been ran.
def get_movies_details():
    df_movies = pd.read_csv('data/detailed_movies_features.csv')
    return df_movies

def run():
    print("Running...")
    print("Get Data...")
    # Get data
    df_movies, df_ratings = get_data()
    # Gets DF with movie features
    df_movies_features = get_movies_details_features()
    # Gets group by DF of ratings for each user
    df_user_content = pd.merge(df_ratings, df_movies_features, on='movieId')
    df_user_content = df_user_content.groupby(['userId'])
    # Gets dataframe of the unique movies in DF
    movies = df_movies_features[df_movies_features.columns.difference(['movieId', 'title'])]

    # Run user-based CF class
    # print("Starting CF RS...")
    # userCF = userBased_CF(df_movies, df_ratings)
    # metrics = userCF.main_run_evaluate(K=50, positive_only=False, threshold=0.0)
    # print(metrics)

    print("Starting Content Based RS...")
    # Content Based
    content = content_based(df_movies_features, df_ratings, df_user_content, movies)
    model = SVR(C=1.5)
    print(content.model_evaluate(model))


if __name__ == '__main__':
    run()

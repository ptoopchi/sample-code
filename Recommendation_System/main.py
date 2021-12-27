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
    df_movies = pd.read_csv('data/detailed_movies.csv')
    return df_movies

# Run the User-Based CF
def run():
    # Get data
    # df_movies, df_ratings = get_data()
    # Run user-based CF class
    # userCF = userBased_CF(df_movies, df_ratings)
    # metrics = userCF.main_run_evaluate(K=50, positive_only=False, threshold=0.0)
    # print(metrics)
    df_detailed_movies = get_movies_details()
    features = feature_engineering(df_detailed_movies)
    df_features = features.run()


if __name__ == '__main__':
    run()

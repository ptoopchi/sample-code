import pandas as pd

from content_based import content_based
from data_process.movies_web_scrapper import movie_scrape
from user_CF import userBased_CF
from sklearn.svm import SVR


# Get data from CSV file
def get_data():
    df_movies = pd.read_csv(
        'data/movies.csv')
    df_ratings = pd.read_csv(
        'data/ratings.csv')
    # Currently not required
    del df_movies['genres']
    del df_ratings['timestamp']
    # Remove year from movie title and create as separate column
    df_movies['movie_year'] = df_movies['title'].str.extract("\((.*)\)")
    df_movies['title'] = df_movies['title'].str.replace("\((.*)\)", "", regex=True)
    return df_movies, df_ratings


def extra_movies_data():
    df_tags = pd.read_csv(
        'data/tags.csv')
    df_movies = pd.read_csv(
        'data/movies.csv')
    df_links = pd.read_csv(
        'data/links.csv')
    scrape = movie_scrape(df_movies, df_links, df_tags)
    df_movies_detailed = scrape.run()
    return df_movies_detailed


# THIS METHOD WILL ONLY WORK ONCE THE extra_movies_data() has been ran.
def get_movies_details_features():
    df_movies = pd.read_csv(
        'detailed_movies_features.csv')
    return df_movies


# Run the User-Based CF
def run():
    print("Getting Data...")
    # Get data
    df_movies, df_ratings = get_data()
    # Gets DF with movie features
    df_movies_features = get_movies_details_features()

    print("Starting CF RS...")
    # Run user-based CF class
    userCF = userBased_CF(df_movies, df_ratings)
    print("Average MSE:", userCF.average_mse())

    print("Starting Content Based RS...")
    # Run Content Based RS
    content = content_based(df_movies_features, df_ratings)
    model = SVR(C=1.5)
    print("Average MSE", content.model_evaluate(model))


if __name__ == '__main__':
    run()

import pandas as pd
from data_process.movies_web_scrapper import movie_scrape
from hybrid_model import hybrid


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


# Run the model
def run():
    print("Getting Data...")
    # Get data
    df_movies, df_ratings = get_data()
    # Gets DF with movie features
    df_movies_features = get_movies_details_features()

    print("Starting Hybrid Model...")
    model = hybrid(df_movies, df_ratings, df_movies_features)
    print(model.hybrid_evaluate())


if __name__ == '__main__':
    run()

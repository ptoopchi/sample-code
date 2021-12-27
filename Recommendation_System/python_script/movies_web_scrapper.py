import pandas as pd
import requests
from lxml import html
import numpy as np
from difflib import SequenceMatcher
import sys
import json

# This class Scrapes the TMDB website for more information about each movie within the dataset
# out of the 1500 movies only 18 of them are not on the site so they are added to the dataset manually

class movie_scrape:
    def __init__(self, df_movies, df_links, df_tags):
        self.df_movies = df_movies
        self.df_links = df_links
        self.df_tags = df_tags
        self.counter = 0

    # Converts titles from American President, The to The American President
    def fix_title(self, text, sub):
        text = text.strip()
        if text.endswith(sub):
            text = text[:(len(text) - len(sub))]
            text = " ".join(("The", text))
        return text

    # Gets the html script from website
    def html_tree(self, link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
        page = requests.get(link, headers=headers)
        return html.fromstring(page.content)

    # Checks how similar two strings are
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    # Finds the details of the movie from the website
    def get_movie_details(self, movieId, tmdbId):
        try:
            tree = self.html_tree('https://www.themoviedb.org/movie/' + str(tmdbId))
            title = ""
            # title checking is required as site splits movies and tv shows
            # into different categories with the same ID
            try:
                title = tree.xpath('//*[@id="original_header"]/div[2]/section/div[1]/h2/a')[0].text
                df_title = list(self.df_movies[self.df_movies['movieId'] == movieId]['title'].values)[0]
                # This checks how similar the titles are as in some cases the movie 'Seven' is known as 'Se7en'
                # or the movie 'Guardians of the Galaxy 2' is known as 'Guardians of the Galaxy Vol. 2'
                if (self.similar(title, df_title) < 0.75):
                    raise Exception('Failed to get correct page!')
            except:
                tree = self.html_tree('https://www.themoviedb.org/tv/' + str(tmdbId))
            # Get the director name
            director = tree.xpath('//*[@id="original_header"]/div[2]/section/div[2]/ol/li[1]/p[1]/a')[0].text
            # description of video
            description = tree.xpath('//*[@id="original_header"]/div[2]/section/div[2]/div/p')[0].text
            # returns the top 3 actors in the video
            people = tree.xpath('//*[@id="cast_scroller"]/ol/li')
            actors = []
            for x in people[0:4]:
                actors.append(x.xpath('p[1]/a')[0].text)

            output = {'director': director, 'description': description, 'actors': actors}
            return output
        except:
            output = {'director': np.nan, 'description': np.nan, 'actors': np.nan}
            return output

    # Getter method for the comp list
    def get_data(self, x, y, size):
        self.counter += 1
        sys.stdout.write('\rFetched ' + str(self.counter) + ' out of ' + str(size))
        sys.stdout.flush()
        return self.get_movie_details(x, y)
    # Main runner method
    def run(self):
        print("Preparing Data...")
        # Remove year from movie title and create as separate column
        self.df_movies['movie_year'] = self.df_movies['title'].str.extract("\((.*)\)")
        self.df_movies['title'] = self.df_movies['title'].str.replace("\((.*)\)", "", regex=True)

        # Fix movie titles
        self.df_movies['title'] = self.df_movies['title'].apply(lambda x: self.fix_title(x, sub=', The'))
        self.df_movies['title'] = self.df_movies['title'].apply(lambda x: self.fix_title(x, sub=', A'))
        self.df_movies['title'] = self.df_movies['title'].apply(lambda x: self.fix_title(x, sub=', La'))

        # Remove the movie which does not appear in the website
        row_index = self.df_movies[self.df_movies['movieId'] == 26587].index
        df_movies = self.df_movies.drop(row_index)

        row_index = self.df_links[self.df_links['movieId'] == 26587].index
        df_links = self.df_links.drop(row_index)

        # Manually Add the TMDB IDs for the missing values
        df_links.at[624, 'tmdbId'] = 706007
        df_links.at[843, 'tmdbId'] = 10642
        df_links.at[2141, 'tmdbId'] = 2141
        df_links.at[3027, 'tmdbId'] = 31392
        df_links.at[5854, 'tmdbId'] = 39850
        df_links.at[6059, 'tmdbId'] = 3137
        df_links.at[7382, 'tmdbId'] = 7154

        print("Merging Dataframes...")
        # Gets the tags for each movie and converts it into dict in the form of {movieID : list of keyworkds}
        movie_tags = dict(self.df_tags[['movieId', 'tag']].groupby('movieId')['tag'].apply(list))
        # Convert to pandas dataframe
        movie_tags = pd.DataFrame(movie_tags.items(), columns=['movieId', 'tags'])
        # Merge with df_movies dataframe
        df_movies = df_movies.merge(movie_tags, left_on='movieId', right_on='movieId')
        # Merge df_movies with tmdb id for web scrapping data
        df_movies = df_movies.merge(df_links[['movieId', 'tmdbId']], left_on='movieId', right_on='movieId')
        df_movies['tmdbId'] = df_movies['tmdbId'].astype(int)

        print("Starting Data Fetching...")
        # Fetch the Details
        movie_details_list = [self.get_data(x[0], x[1], df_movies.shape[0]) for x in df_movies[['movieId', 'tmdbId']].values]
        # Set the column values
        df_movies['director'] = [x['director'] for x in movie_details_list]
        df_movies['description'] = [x['description'] for x in movie_details_list]
        df_movies['actors'] = [x['actors'] for x in movie_details_list]

        print("Processing Manual Data...")
        # Open manual data file and add to main dataframe
        with open('data/manual_data.json') as f:
            manual_data = json.load(f)

        for x in manual_data:
            index = df_movies[df_movies['tmdbId'] == x['tmdbId']].index[0]
            df_movies.at[index, 'director'] = x['director']
            df_movies.at[index, 'description'] = x['description']
            df_movies.at[index, 'actors'] = x['actors']

        # Export
        print("Exporting Dataframe...")
        df_movies.to_csv('detailed_movies.csv', index=False)
        return df_movies





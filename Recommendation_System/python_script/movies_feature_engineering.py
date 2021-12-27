import pandas as pd
import ast
import string
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.decomposition import PCA


class feature_engineering:
    def __init__(self, df_detailed_movies):
        self.df_detailed_movies = df_detailed_movies

    # Removes numbers and punctuation from a text entry
    def remove_punctation_numbers(self, text):
        text = text.translate(str.maketrans('', '', (string.punctuation + '––‘’“”—')))
        text = text.translate(str.maketrans('', '', '0123456789'))
        return text.strip()

    # Performs lemmatization for a word
    def lem_POS(self, word, lemmatizer):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                    "N": wordnet.NOUN,
                    "V": wordnet.VERB,
                    "R": wordnet.ADV}
        tag = tag_dict.get(tag, wordnet.NOUN)
        return lemmatizer.lemmatize(word, tag)

    # Removes stopwords from a text entry
    def remove_stopwords(self, text, stopwords):
        return [w for w in text if not w.lower() in stopwords]

    # Executes the stopword removal and lemmatization for a text entry
    def clean_text(self, text, lemmatizer, stopwords):
        text = [self.lem_POS(word, lemmatizer) for word in word_tokenize(text)]
        text = self.remove_stopwords(text, stopwords)
        return text

    # Convert to lowercase, remove duplicates & perform lemming for movie tags
    def tag_clean(self, tag, lemmatizer, stopwords):
        lower = [x.lower() for x in tag]
        unique = list(set(lower))
        text = " ".join(unique).strip()
        text = self.remove_punctation_numbers(text)
        return self.clean_text(text, lemmatizer, stopwords)

    # This is done as text is already tokenized
    # It allows the vectorizer understand the main text is the tokenized values,
    # for this to work lowercase=False must be set, this is fine as text is already lowercase
    def tokenizer(self, text):
        return text

    # Creates one hot encoding for a single column [In cases of list of lists]
    def create_one_hot_encoding(self, col):
        mlb = MultiLabelBinarizer()
        res = pd.DataFrame(mlb.fit_transform(col),
                           columns=mlb.classes_,
                           index=col.index)
        return res

    # Creates one-hot encoding for both actors and movie genres
    def create_actors_and_genres(self):
        # Append the director to actors for one hot encoding
        self.df_detailed_movies['actors'] = self.df_detailed_movies['actors'].apply(ast.literal_eval)
        col = pd.Series(
            [a + [b] for a, b in zip(self.df_detailed_movies['actors'], self.df_detailed_movies['director'])])
        # One-hot encoding
        actors_encoding = self.create_one_hot_encoding(col)
        # Create one-hot encoding for genres
        # Convert genres to list
        self.df_detailed_movies['genres'] = self.df_detailed_movies['genres'].apply(lambda x: x.split('|'))
        # One-hot encoding
        genres_encoding = self.create_one_hot_encoding(self.df_detailed_movies['genres'])
        return actors_encoding, genres_encoding

    # Reduces the dimensions of a df by performing PCA
    def dimension_reduction(self, dataframe, variance=0.95):
        # Perform PCA to reduce the dimensions
        pca = PCA(n_components=variance)
        matrix = pca.fit_transform(dataframe)
        # Conver to pandas df
        columns = ['pca_%i' % i for i in range(pca.n_components_)]
        df_pca = pd.DataFrame(matrix, columns=columns, index=dataframe.index)
        return df_pca

    def run(self):
        global stopwords
        nltk.download('wordnet')
        print('Cleaning Description...')
        # convert to lowercase and remove numbers and punctuation
        self.df_detailed_movies['description_clean'] = self.df_detailed_movies['description'].str.lower()
        self.df_detailed_movies['description_clean'] = self.df_detailed_movies['description_clean'].apply(
            self.remove_punctation_numbers)
        # Cleaning for the description
        print('Performing word lemmatization...')
        lemmatizer = WordNetLemmatizer()
        stopwords = set(stopwords.words('english'))
        self.df_detailed_movies['description_clean'] = [self.clean_text(x, lemmatizer, stopwords) for x in
                                                        self.df_detailed_movies['description_clean'].tolist()]
        # Cleaning for the tags
        print('Cleaning Tags...')
        # During import the tags list is converted to string, to fix this the ast.literal_eval(??) is used.
        self.df_detailed_movies['tags_clean'] = [self.tag_clean(ast.literal_eval(x), lemmatizer, stopwords) for x in
                                                 self.df_detailed_movies['tags'].tolist()]
        # Create TF-IDF Dataframe from movie descriptions
        # tf-idf for description and tags
        print('Creating TF-IDF Dataframe...')
        merged = self.df_detailed_movies['description_clean'] + self.df_detailed_movies['tags_clean']
        vectorizer = TfidfVectorizer(tokenizer=self.tokenizer, lowercase=False, analyzer='word', min_df=3, max_df=0.95)
        vectors = vectorizer.fit_transform(merged.tolist())
        tfidf_desc_tags = pd.DataFrame(vectors.toarray(), columns=vectorizer.get_feature_names())
        # Create one-hot encoding for actors and genres
        print('Performing One-hot encoding...')
        actors_encoding, genres_encoding = self.create_actors_and_genres()
        # Perform PCA on TF-IDF
        print('Performing Dimension reduction...')
        df_pca = self.dimension_reduction(tfidf_desc_tags)
        # Create dataframe with all features together
        df_movies_features = pd.concat(
            [self.df_detailed_movies[['movieId', 'title']], df_pca, actors_encoding, genres_encoding], axis=1,
            join="inner")
        # Export
        print("Exporting Dataframe...")
        df_movies_features.to_csv('detailed_movies_features.csv', index=False)
        return df_movies_features

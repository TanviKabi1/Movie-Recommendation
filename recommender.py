import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

DATA_PATH = os.path.join("data", "ml-latest-small")

def load_data():
    """Loads movies.csv and ratings.csv"""
    movies = pd.read_csv(os.path.join(DATA_PATH, "movies.csv"))
    ratings = pd.read_csv(os.path.join(DATA_PATH, "ratings.csv"))
    return movies, ratings

def build_similarity_matrix(movies, ratings, min_ratings=20):
    """
    Builds an item-based similarity matrix using cosine similarity.
    Filters out movies with less than min_ratings to improve quality and performance.
    """
    # Filter movies with less than min_ratings
    movie_stats = ratings.groupby('movieId').agg({'rating': ['count', 'mean']})
    movie_stats.columns = movie_stats.columns.droplevel()
    popular_movies_ids = movie_stats[movie_stats['count'] >= min_ratings].index
    
    filtered_ratings = ratings[ratings['movieId'].isin(popular_movies_ids)]
    
    # Merge datasets maps titles to movieIds
    movie_ratings = pd.merge(filtered_ratings, movies, on='movieId')
    
    # Create user-item matrix (index=title, columns=userId, values=rating)
    user_movie_matrix = movie_ratings.pivot_table(index='title', columns='userId', values='rating')
    
    # Fill NaN with 0 because cosine similarity needs numerical values
    user_movie_matrix = user_movie_matrix.fillna(0)
    
    # Compute cosine similarity
    item_similarity = cosine_similarity(user_movie_matrix)
    
    # Create a DataFrame for easy lookup
    item_similarity_df = pd.DataFrame(item_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)
    
    return item_similarity_df

def get_recommendations(movie_title, item_similarity_df, top_n=5):
    """
    Given a movie title and similarity matrix, returns top_n similar movies.
    """
    if movie_title not in item_similarity_df.index:
        return []
    
    # Get similarity scores for the chosen movie
    similar_scores = item_similarity_df[movie_title].sort_values(ascending=False)
    
    # Exclude the movie itself
    similar_scores = similar_scores.drop(movie_title)
    
    # Return top N
    return similar_scores.head(top_n).index.tolist()

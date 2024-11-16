# Import specific functions from a custom module and libraries for computations and formatting
from functions import (cleaner_pipeline,
                       restaurants_matcher,
                       top_k_printer,
                       normalize_vectors,
                       upgrade_TF_IDF_score,
                       drop_down_menu) # Custom utility functions
import numpy as np  # Numerical operations
from sklearn.metrics.pairwise import cosine_similarity  # Pairwise cosine similarity computation
from tabulate import tabulate  # For displaying data in table format
import pandas as pd  # DataFrame handling
import asyncio

# Define a function to search and display restaurant matches without ranking them
def non_ranked_engine(querry, restaurants_df, vocabulary, reverse_index, top_k_to_print):
    """
    Matches restaurants based on query words but without ranking.
    
    Parameters:
    - querry: User's search query as a string.
    - restaurants_df: DataFrame containing restaurant information.
    - vocabulary: Dictionary mapping words to IDs.
    - reverse_index: Dictionary mapping word IDs to restaurant IDs.

    Returns:
    - Processed results using the top_k_printer function.
    """
    # Clean and preprocess the query
    processed_querry = cleaner_pipeline(querry)
    
    # Map each processed word to its corresponding ID in the vocabulary if it exists
    processed_querry = [vocabulary[key] for key in processed_querry if key in vocabulary.keys()]
    
    # Exit if no valid words are found in the query
    if len(processed_querry) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False  
    
    # Retrieve restaurant IDs for each word in the query using the reverse index
    matching_resturants = [reverse_index[key] for key in processed_querry]
    
    # Find common restaurants across all query words
    matching_resturants = restaurants_matcher(matching_resturants)

    # Format and print the results
    return top_k_printer(matching_resturants, restaurants_df,top_k_to_print)

# Define a function to rank restaurants based on cosine similarity
def ranked_engine(sample_input, restaurants_df, vocabulary, reverse_index_tf_idf, IDF_by_words, top_k_to_print):
    """
    Ranks restaurants based on cosine similarity between query and restaurant TF-IDF vectors.
    
    Parameters:
    - sample_input: User's search query as a string.
    - restaurants_df: DataFrame containing restaurant details.
    - vocabulary: Dictionary mapping words to IDs.
    - reverse_index_tf_idf: Reverse index mapping word IDs to TF-IDF values for each document.
    - IDF_by_words: Dictionary of inverse document frequency (IDF) values for each word.
    - ID_descritpion: Description IDs mapped to their content.

    Returns:
    - True if matches are found and processed; False otherwise.
    """
    # Clean and preprocess the query
    stemmed_querry = cleaner_pipeline(sample_input)
    processed_query = []
    # Map query words to vocabulary IDs if they exist
    for word in stemmed_querry:
        if word in vocabulary:
            processed_query.append(vocabulary[word])
        else:
            vocabulary[word] = len(vocabulary) + 1
            processed_query.append(vocabulary[word])
    
    # Exit if no valid words are found
    if len(processed_query) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False

    # Calculate TF and IDF for each word in the query
    query_IDF = {word: IDF_by_words.get(word, 0) for word in processed_query}
    query_TF = {word: processed_query.count(word) / len(processed_query) for word in processed_query}

    # Compute the TF-IDF vector for the query
    query_tf_idf = np.zeros(len(vocabulary))  # Initialize vector with zeros
    for querry_word in processed_query:
        query_tf_idf[querry_word-1] = query_TF[querry_word] * query_IDF[querry_word]  # TF-IDF weight
    
    # Normalize the query vector
    # query_tf_idf = normalize_vectors(query_tf_idf)
    # query_tf_idf[query_tf_idf == 0] += 1  # Avoid division by zero errors

    # Get restaurant IDs and their TF-IDF values for matching query words
    matching_restaurants = {word: reverse_index_tf_idf[word] for word in processed_query if word in reverse_index_tf_idf}
    
    # Construct TF-IDF vectors for each document (restaurant)
        # Construct TF-IDF vectors for each document (restaurant)
    TF_IDF_matrix = {}
    vocabulary_index = list(vocabulary.values())
    for word_id, doc_id_and_tfidf in matching_restaurants.items():
        for doc_id, tf_idf in doc_id_and_tfidf:
            if doc_id not in TF_IDF_matrix:
                TF_IDF_matrix[doc_id] = np.zeros(len(vocabulary))
            word_index = vocabulary_index.index(word_id)  # Index of the word
            TF_IDF_matrix[doc_id][word_index] = tf_idf  # Set the TF-IDF value


    # Calculate cosine similarity for each restaurant
    result_cosine = []
    for restaurant, tf_idf_vector in TF_IDF_matrix.items():
        if np.linalg.norm(tf_idf_vector) == 0:  # Handle zero vectors
            similarity = 0
        else:
            tf_idf_vector = normalize_vectors(tf_idf_vector)  # Normalize document vector
            similarity = cosine_similarity(query_tf_idf.reshape(1, -1), tf_idf_vector.reshape(1, -1))[0][0]  # Cosine similarity
        result_cosine.append((restaurant, similarity))


    # Sort restaurants by similarity score in descending order
    result_cosine = sorted(result_cosine, key=lambda x: x[1], reverse=True)

    # Extract restaurant IDs and scores
    result_restaurant = [tup[0] for tup in result_cosine]
    result_cosine = [tup[1] for tup in result_cosine]

    # Format results and display the top matches
    restaurants_df = restaurants_df.loc[result_restaurant, ["restaurantName", "address", "description", "website"]]
    restaurants_df["cosine_score"] = result_cosine
    restaurants_df["description"] = [desc[:47] + "..." if len(desc) > 47 else desc for desc in restaurants_df["description"]]
    if len(restaurants_df) < top_k_to_print : top_k_to_print = len(restaurants_df)
    print(tabulate(
        restaurants_df[:top_k_to_print],  # Display top 5 results
        headers=["Restaurant Name", "Address", "Description", "Website", "Cosine"],
        tablefmt="rounded_grid",
        showindex=False,
        maxcolwidths=25
    ))
    
    return restaurants_df[:top_k_to_print]

def upgraded_ranked_engine(facilities, cusine_types, vocabulary, IDF_by_words, reverse_index_tf_idf, restaurants_df):

    querry, facility_choosen, cusine, min_money, max_money, k= drop_down_menu(facilities, cusine_types)


    # Clean and preprocess the query
    stemmed_querry = cleaner_pipeline(querry)
    processed_query = []
    # Map query words to vocabulary IDs if they exist
    for word in stemmed_querry:
        if word in vocabulary:
            processed_query.append(vocabulary[word])
        else:
            vocabulary[word] = len(vocabulary) + 1
            processed_query.append(vocabulary[word])
    
    # Exit if no valid words are found
    if len(processed_query) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False

    # Calculate TF and IDF for each word in the query
    query_IDF = {word: IDF_by_words.get(word, 0) for word in processed_query}
    query_TF = {word: processed_query.count(word) / len(processed_query) for word in processed_query}

    # Compute the TF-IDF vector for the query
    query_tf_idf = np.zeros(len(vocabulary))  # Initialize vector with zeros
    for querry_word in processed_query:
        query_tf_idf[querry_word-1] = query_TF[querry_word] * query_IDF[querry_word]  # TF-IDF weight
    
    # Normalize the query vector
    # query_tf_idf = normalize_vectors(query_tf_idf)
    # query_tf_idf[query_tf_idf == 0] += 1  # Avoid division by zero errors

    # Get restaurant IDs and their TF-IDF values for matching query words
    matching_restaurants = {word: reverse_index_tf_idf[word] for word in processed_query if word in reverse_index_tf_idf}
    
    # Construct TF-IDF vectors for each document (restaurant)
        # Construct TF-IDF vectors for each document (restaurant)
    TF_IDF_matrix = {}
    vocabulary_index = list(vocabulary.values())
    for word_id, doc_id_and_tfidf in matching_restaurants.items():
        for doc_id, tf_idf in doc_id_and_tfidf:
            if doc_id not in TF_IDF_matrix:
                TF_IDF_matrix[doc_id] = np.zeros(len(vocabulary))
            word_index = vocabulary_index.index(word_id)  # Index of the word
            TF_IDF_matrix[doc_id][word_index] = tf_idf  # Set the TF-IDF value


    # Calculate cosine similarity for each restaurant
    result_cosine = []
    for restaurant, tf_idf_vector in TF_IDF_matrix.items():
        if np.linalg.norm(tf_idf_vector) == 0:  # Handle zero vectors
            similarity = 0
        else:
            tf_idf_vector = normalize_vectors(tf_idf_vector)  # Normalize document vector
            similarity = cosine_similarity(query_tf_idf.reshape(1, -1), tf_idf_vector.reshape(1, -1))[0][0]  # Cosine similarity
        result_cosine.append((restaurant, similarity))


    # Sort restaurants by similarity score in descending order
    result_cosine = sorted(result_cosine, key=lambda x: x[1], reverse=True)

    # Extract restaurant IDs and scores
    result_restaurant = [tup[0] for tup in result_cosine]
    result_cosine = [tup[1] for tup in result_cosine]

    # Format results and display the top matches
    restaurants_df = restaurants_df.loc[result_restaurant]
    restaurants_df["cosine_score"] = pd.Series(result_cosine, index=result_restaurant).values
    restaurants_df["description"] = [desc[:47] + "..." if len(desc) > 47 else desc for desc in restaurants_df["description"]]
    if len(restaurants_df) < k : k = len(restaurants_df)
    best_restaurants = upgrade_TF_IDF_score(restaurants_df, facility_choosen, cusine, min_money, max_money, k)[["restaurantName", "address", "description", "website", "cosine_score", "priceRange"]]
    price_range = list(best_restaurants.priceRange)
    best_restaurants = best_restaurants.drop("priceRange", axis = 1)
    print(tabulate(
        best_restaurants,  # Display top 5 results
        headers=["Restaurant Name", "Address", "Description", "Website", "Cosine"],
        tablefmt="rounded_grid",
        showindex=False,
        maxcolwidths=25
    ))
    
    return best_restaurants, price_range
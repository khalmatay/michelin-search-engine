# Import specific functions from a custom module and a library for table formatting
from functions import clener_pipeline, restourants_matcher, top_k_printer
import numpy as np
from scipy.spatial.distance import cosine
from tabulate import tabulate
import pandas as pd

# Define a function to search and display restaurant matches without ranking them
def non_ranked_engine(querry, restaurants_df, vocabulary, reverse_index):
    
    # Clean and preprocess the query using the clener_pipeline function
    processed_querry = clener_pipeline(querry)
    
    # Map each processed word in the query to its corresponding ID in the vocabulary, if it exists
    processed_querry = [vocabulary[key] for key in processed_querry if key in vocabulary.keys()]
    
    # Check if there are any valid words in the processed query
    if len(processed_querry) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False  # Exit if no valid words were found in the query
    
    # Retrieve lists of restaurant IDs for each word in the query using the reverse index
    matching_resturants = [reverse_index[key] for key in processed_querry]
    
    # Find the common restaurants across all lists using the restourants_matcher function
    matching_resturants = restourants_matcher(matching_resturants)

    return top_k_printer(matching_resturants, restaurants_df)



def ranked_engine(sample_input, restaurants_df, vocabulary, reverse_index_tf_idf, IDF_by_words):

    # Clean and preprocess the query using the clener_pipeline function
    processed_querry = clener_pipeline(sample_input)

    # Map each processed word in the query to its corresponding ID in the vocabulary, if it exists
    processed_querry = [vocabulary[key] for key in processed_querry if key in vocabulary.keys()]
    
    # Check if there are any valid words in the processed query
    if len(processed_querry) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False  # Exit if no valid words were found in the query


    querry_IDF = {word:IDF_by_words.get(word, 0) for word in processed_querry}

    querry_TF = {word:processed_querry.count(word)/len(processed_querry) for word in processed_querry}

    querry_tf_idf = np.array([querry_IDF[word]*querry_TF[word] for word in processed_querry])

    # Retrieve lists of restaurant IDs for each word in the query using the reverse index
    matching_resturants = {word:reverse_index_tf_idf[word] for word in processed_querry}
    TF_IDF_matrix = {}
    for term_id, list in matching_resturants.items():
        for restorant, tf_idf_score in list:

            if restorant not in TF_IDF_matrix:
                TF_IDF_matrix[restorant] = np.zeros(len(processed_querry))

            TF_IDF_matrix[restorant][processed_querry.index(term_id)] = tf_idf_score

    result_list = []
    for restorant, tf_idf_words in TF_IDF_matrix.items():
        result_list.append((restorant, cosine(querry_tf_idf, tf_idf_words)))
    print(f"We found {len(result_list)} matches!\n")
    result_list = sorted(result_list, key = lambda x: x[1], reverse = True)[:5]
    
    result_restourant, result_cosine = [tup[0] for tup in result_list], [tup[1] for tup in result_list]
    restaurants_df = restaurants_df.loc[result_restourant, ["restaurantName", "address", "description", "website"]]
    restaurants_df["cosine_score"] = result_cosine
    restaurants_df["description"] = [descript[0:47] + "..." if len(descript) > 30 else descript for descript in restaurants_df["description"]]

    print(tabulate(
        restaurants_df,
        headers=["Restaurant Name", "Address", "Description", "Website", "Cosine"],  # Column headers for the table
        tablefmt="rounded_grid",  # Table format style
        showindex=False,  # Hide row index in the display
        maxcolwidths=25  # Maximum width for each column to ensure readability
    ))
    return True


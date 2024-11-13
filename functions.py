import pandas as pd
import re
from math import log
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
# Uncomment to download stopwords if they are not available
# nltk.download('stopwords')
from tabulate import tabulate


def clener_pipeline(querry):
    # Load a set of English stopwords to filter out common words that add little meaning
    stop_words = set(stopwords.words("english"))
    
    # Initialize a stemmer that reduces words to their root forms to help group similar words
    stemmer = PorterStemmer()
    
    # Remove any characters that are not letters or numbers from the input text
    querry = re.sub(r"[^a-zA-Z0-9]", " ", querry)
    
    # Replace any sequence of multiple spaces with a single space for clean formatting
    querry = re.sub(r" +", " ", querry)
    
    # Convert all characters in the input text to lowercase to standardize text format
    querry = querry.lower()
    
    # Split the text into words, removing any stopwords, and trim any surrounding whitespace
    querry = [word.strip() for word in querry.split(" ") if word.lower() not in stop_words]
    
    # Apply stemming to each word to reduce it to its root form, making words like "running" and "run" identical
    processed_querry = [stemmer.stem(word) for word in querry]
    
    # Return the list of processed words for further analysis
    return processed_querry


def description_cleaner(descriptions):
    # Initialize an empty list to store the processed version of each description
    result = []
    
    # Loop through each description in the input list and clean it using the cleaner_pipeline function
    for descript in descriptions:
        stemmed_words = clener_pipeline(descript)
        
        # Append the processed list of words for each description to the result list
        result.append(stemmed_words)
    
    # Return the full list of cleaned and processed descriptions
    return result


def vocabulary_creator(descriptions):
    # Initialize a set of unique words using the words from the first description
    unique_words = set(descriptions[0])
    
    # Add words from each additional description to the set of unique words
    for descr in descriptions[1:]:
        unique_words = unique_words | set(descr)
    
    # Initialize a counter to assign a unique ID to each word
    counter = 0
    
    # Create an empty dictionary to map each unique word to its corresponding ID
    res = {}
    
    # Assign a unique ID to each word in the set of unique words
    for word in unique_words:
        # Skip empty strings to avoid errors in later processing
        if word == "": continue
        res[word] = counter
        counter += 1
    
    # Call the word_to_id function, passing in the descriptions and the word-to-ID mapping
    return word_to_id(descriptions, res)


def word_to_id(descriptions, vocab):
    # Initialize an empty list to store the ID representation of each description
    result = []
    
    # Process each description individually
    for one_description in descriptions:
        # Initialize a list to store the IDs of words in the current description
        mono_result = []
        
        # Look up each word in the current description in the vocab dictionary to get its ID
        for word in one_description:
            # Skip empty strings to avoid issues in ID mapping
            if word == "" : continue
            mono_result.append(vocab[word])
        
        # Append the list of word IDs for the current description to the result list
        result.append(mono_result)
    
    # Return a list of word IDs for each description and the vocabularys
    return [result, vocab]


def reverse_index_creator(ID_descriptions):
    # Initialize an empty dictionary to store the reverse index
    reverse_index = {}
    
    # Enumerate each description to get its index (doc_id) and list of word IDs
    for doc_id, word_ids in enumerate(ID_descriptions):
        # Process each word ID in the current description
        for word_id in word_ids:
            # If the word ID is not already in the reverse index, initialize it with an empty list
            if word_id not in reverse_index:
                reverse_index[word_id] = []
            # Append the document ID to the list of documents where the word appears
            reverse_index[word_id].append(doc_id)
    
    # Return the completed reverse index mapping each word ID to the documents it appears in
    return reverse_index


def restourants_matcher(matching_resturants):
    # Initialize a set containing the IDs of the restaurants in the first list
    matches = set(matching_resturants[0])
    
    # Perform an intersection with each subsequent list to keep only matching restaurant IDs
    for restourant in matching_resturants[1:]:
        matches &= set(restourant)
    
    # Convert the final set of matching restaurant IDs to a list and return it
    return list(matches)


def compute_TF(descriptions):
    TF_res = {}
    for index, descirpt in enumerate(descriptions):
        one_restourant_result = {}
        tot_words = len(descirpt)
        for word in descirpt:
            one_restourant_result[word] = one_restourant_result.get(word, 0) + 1 / tot_words
        one_restourant_result = list(one_restourant_result.items())
        TF_res[index] = one_restourant_result
    
    return TF_res


def compute_IDF(reverse_index, tot_documents):
    result_IDF = {}

    for word, doc_list in reverse_index.items():
        word_IDF = log(tot_documents/len(doc_list))
        result_IDF[word] = word_IDF
    
    return result_IDF


def compute_TF_IDF(tf_dict, idf_dict):

    tf_idf_result = {}

    for restournat, word_and_tf in tf_dict.items():
        for word, TF_value in word_and_tf:

            if word not in tf_idf_result:
                tf_idf_result[word] = []
            
            idf_val = idf_dict.get(word, 0)

            tf_idf = TF_value * idf_val

            tf_idf_result[word].append((restournat, tf_idf))
    
    return tf_idf_result

def reverse_TF_IDF(reverse_index_tf_idf):
    
    # Initialize normal index as a defaultdict of lists
    normal_index = {}

    # Iterate through reverse index to create the normal index
    for word, doc_list in reverse_index_tf_idf.items():
        for doc_id, tfidf_value in doc_list:
            if doc_id not in normal_index:
                normal_index[doc_id] = []
            normal_index[doc_id].append((word, tfidf_value))
    
    return normal_index


def top_k_printer(matching_resturants, restaurants_df):
    # Print the number of matching restaurants found
    print(f"We found {len(matching_resturants)} matches!\n")
    
    # Check if any restaurants match the query; exit if no matches were found
    if len(matching_resturants) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False  # Exit if no matching restaurants were found
    
    # Filter the DataFrame to only include rows with matching restaurant IDs
    restaurants_df = restaurants_df.loc[matching_resturants, ["restaurantName", "address", "description", "website"]]
    
    # Truncate the description to 47 characters and add "..." if it exceeds 30 characters
    restaurants_df["description"] = [descript[0:47] + "..." if len(descript) > 30 else descript for descript in restaurants_df["description"]]
    
    # Display the top 5 matches in a formatted table with specific headers and settings
    print(tabulate(
        restaurants_df.iloc[:5],  # Select only the top 5 matching restaurants
        headers=["Restaurant Name", "Address", "Description", "Website"],  # Column headers for the table
        tablefmt="rounded_grid",  # Table format style
        showindex=False,  # Hide row index in the display
        maxcolwidths=25  # Maximum width for each column to ensure readability
    ))
    
    # Return True to indicate that matching restaurants were successfully displayed
    return True

# def cosine_similarity():

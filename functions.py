import pandas as pd
import re
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
# Uncomment to download stopwords if they are not available
# nltk.download('stopwords')


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
    return word_to_id(descriptions, res, counter)


def word_to_id(descriptions, vocab, counter):
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
    
    # Return a list of word IDs for each description, the vocabulary, and the total number of words
    return [result, vocab, counter]


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

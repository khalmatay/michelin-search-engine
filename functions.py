import pandas as pd
import re
from math import log
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
# Uncomment to download stopwords if they are not available
# nltk.download('stopwords')
from tabulate import tabulate
import numpy as np
from math import log10
import ipywidgets as widgets
from IPython.display import display
import heapq
from jupyter_ui_poll import ui_events
import time


# Text cleaning and preprocessing function
def cleaner_pipeline(query):
    """
    Cleans and preprocesses the input text query.
    - Removes non-alphanumeric characters.
    - Converts text to lowercase.
    - Removes stopwords and applies stemming.
    """
    # Load a set of English stopwords to filter out common words
    stop_words = set(stopwords.words("english"))

    # Initialize a stemmer to reduce words to their root forms
    stemmer = PorterStemmer()

    # Remove non-alphanumeric characters
    query = re.sub(r"[^a-zA-Z0-9]", " ", query)

    # Replace multiple spaces with a single space
    query = re.sub(r" +", " ", query)

    # Convert to lowercase
    query = query.lower()

    # Tokenize, remove stopwords, and trim whitespace
    query = [word.strip() for word in query.split(" ") if word.strip() not in stop_words]

    # Apply stemming to each word
    processed_query = [stemmer.stem(word) for word in query]

    return processed_query


# Clean a list of descriptions
def description_cleaner(descriptions):
    """
    Applies the cleaner_pipeline to a list of descriptions.
    """
    result = []
    for description in descriptions:
        stemmed_words = cleaner_pipeline(description)
        result.append(stemmed_words)
    return result


# Create a vocabulary from descriptions
def vocabulary_creator(descriptions):
    """
    Builds a unique vocabulary from the processed descriptions.
    Assigns a unique ID to each word.
    """
    # Initialize a set of unique words
    unique_words = set(descriptions[0])
    for description in descriptions[1:]:
        unique_words |= set(description)

    # Assign unique IDs to each word
    vocab = {}
    for counter, word in enumerate(unique_words):
        if word:  # Skip empty strings
            vocab[word] = counter

    return word_to_id(descriptions, vocab)


# Convert descriptions to word IDs
def word_to_id(descriptions, vocab):
    """
    Converts each word in descriptions into its corresponding ID from the vocabulary.
    """
    result = {}
    for index, one_description in enumerate(descriptions):
        word_ids = [vocab[word] for word in one_description if word]
        result[index] = word_ids

    return result, vocab


# Create a reverse index mapping words to documents
def reverse_index_creator(ID_descriptions):
    """
    Creates a reverse index mapping word IDs to the document IDs where they appear.
    """
    reverse_index = {}
    for doc_id, word_ids in ID_descriptions.items():
        for word_id in word_ids:
            if word_id not in reverse_index:
                reverse_index[word_id] = []
            reverse_index[word_id].append(doc_id)
    return reverse_index


# Match restaurants based on common word IDs
def restaurants_matcher(matching_restaurants):
    """
    Finds restaurants that match based on the intersection of word IDs.
    """
    matches = set(matching_restaurants[0])
    for restaurant in matching_restaurants[1:]:
        matches &= set(restaurant)
    return list(matches)


# Compute term frequency (TF)
def compute_TF(descriptions):
    """
    Computes the term frequency (TF) for each word in each description.
    """
    TF_res = {}
    for index, description in descriptions.items():
        if index not in TF_res:
            TF_res[index] = []
        total_words = len(description)
        for word in description:
            TF_res[index].append((word, description.count(word) / total_words))
    return TF_res


# Compute inverse document frequency (IDF)
def compute_IDF(reverse_index, total_documents):
    """
    Computes the inverse document frequency (IDF) for each word ID.
    """
    result_IDF = {}
    for word, doc_list in reverse_index.items():
        idf_value = log10(total_documents / len(doc_list))
        result_IDF[word] = idf_value
    return result_IDF


# Compute TF-IDF scores
def compute_TF_IDF(tf_dict, idf_dict):
    """
    Computes the TF-IDF scores for each word-document pair.
    """
    tf_idf_result = {}
    for restaurant, word_and_tf in tf_dict.items():
        for word, TF_value in word_and_tf:
            if word not in tf_idf_result:
                tf_idf_result[word] = []
            tf_idf = TF_value * idf_dict.get(word, 0)
            tf_idf_result[word].append((restaurant, tf_idf))
    return tf_idf_result


# Display top-k matching restaurants
def top_k_printer(matching_restaurants, restaurants_df, top_k_to_print):
    """
    Displays the top-k matching restaurants in a formatted table.
    """
    print(f"We found {len(matching_restaurants)} matches!\n")

    if len(matching_restaurants) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False

    # Filter and format the DataFrame
    restaurants_df = restaurants_df.loc[matching_restaurants, ["restaurantName", "address", "description", "website"]]
    restaurants_df["description"] = [
        desc[:47] + "..." if len(desc) > 30 else desc for desc in restaurants_df["description"]
    ]

    # Display the table
    print(tabulate(
        restaurants_df.iloc[:top_k_to_print],
        headers=["Restaurant Name", "Address", "Description", "Website"],
        tablefmt="rounded_grid",
        showindex=False,
        maxcolwidths=25
    ))
    return True


# Normalize vectors for cosine similarity
def normalize_vectors(vector):
    """
    Normalizes a vector to have a magnitude of 1 (unit vector).
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def drop_down_menu(facilities, cusine_types):
    global ui_done
    ui_done = False
    result = {"value": ("", "", "", "", "", "")}

    def on_button_click(_):
        global ui_done
        facility_choosen = [checkbox.description for checkbox in checkboxes if checkbox.value]

        cusine = cusine_dropdown.value

        min_money, max_money = (money_slider.value)

        k = k_to_print.value

        querry = querry_box.value
        result["value"] = (querry, facility_choosen, cusine, min_money, max_money, k)
        ui_done = True

    querry_box = widgets.Text(
        placeholder="type something",
        description="what do you want to eat?",
        value="modern seasonal cuisine",
        style={'description_width': 'initial'}
    )
    
    facilities.insert(0, "I don't mind")
    unique_facility = []
    facilities = [unique_facility.append(facility) for facility in facilities if facility not in unique_facility]

    
    checkboxes = [
        widgets.Checkbox(value=False, description=option, layout=widgets.Layout(max_width="auto"))
        for option in unique_facility
    ]

    max_width = 3
    rows = [
        widgets.HBox(checkboxes[i:i + max_width], layout=widgets.Layout(justify_content="flex-start"))
        for i in range(0, len(checkboxes), max_width)
    ]
    facilities_grid = widgets.VBox(rows)

    money_options = [("€", 1), ("€€", 2), ("€€€", 3), ("€€€€", 4)]
    money_slider = widgets.SelectionRangeSlider(
        options=money_options,
        index=(0, 3),  # Indices corresponding to "€" and "€€€€"
        description="Choose a price range:",
        style={'description_width': 'initial'},  # Adjusts the description width
        layout=widgets.Layout(width='45%')
    )

    k_to_print = widgets.BoundedIntText(
        value=5,
        min=0,
        step=1,
        description='How many restourants to display?',
        disabled=False,
        style={'description_width': 'initial'},  # Adjusts the description width
        layout=widgets.Layout(width='45%')
    )

    button_querry = widgets.Button(description="Serch for some restournats",
                                   layout=widgets.Layout(width="250px"))

    button_querry.on_click(on_button_click)

    cusine_types.insert(0, "any taste will do!")
    cusine_dropdown = widgets.Dropdown(
        options=cusine_types,
        description="Choose the cusine specialty: ",
        disabled=False,
        style={'description_width': 'initial'}
    )

    display(querry_box, k_to_print, money_slider, cusine_dropdown, facilities_grid, button_querry)

    with ui_events() as poll:
        while ui_done is False:
            poll(10)  # React to UI events (up to 10 at a time)
            time.sleep(0.1)

    return result["value"]


def extract_facilities(faci):
    res_facility = set()
    for restourant_facilities in faci:
        restourant_facilities = restourant_facilities.lower()
        restourant_facilities = re.sub(r"[\[\]\']", " ", restourant_facilities)
        restourant_facilities = re.sub(r" +", " ", restourant_facilities)
        res_facility |= set(restourant_facilities.split(", ")) 
    return list(res_facility)


def upgrade_TF_IDF_score(restaurants_df, facility_choosen, cusine_choosen, min_money, max_money, k):
    '''
    priceRange
    cuisineType
    facilitiesServices
    cosine_score
    ["Restaurant Name", "Address", "Description", "Website", "Cosine"]
    '''
    top_k_heap = []
    new_cosine = []
    for i, (index, row) in enumerate(restaurants_df.iterrows()):
        cost = extract_facilities(row["priceRange"])
        cusine = extract_facilities(row["cuisineType"])
        facility = extract_facilities(row["facilitiesServices"])
        cosine_score = row.cosine_score
        # print("Money :", cost.count("€"), min_money, max_money, sep=" ")
        # print("cost before :", cosine_score)
        if cost.count("€") >= min_money and cost.count("€") <= max_money:
            cosine_score += 0.2
        # print(set(cusine_choosen)&set(cusine))
        cosine_score += 0.2 * len(set(cusine_choosen) & set(cusine))
        # print(set(facility_choosen)&set(facility))
        cosine_score += 0.2 * len(set(facility_choosen) & set(facility))

        new_cosine.append(cosine_score)

        if len(top_k_heap) < k:
            heapq.heappush(top_k_heap, (cosine_score, i))
        else:
            if cosine_score > top_k_heap[0][0]:  # Compare with the smallest element in the heap
                heapq.heapreplace(top_k_heap, (cosine_score, i))  # Replace the smallest directly

        # print("cosine after: ", cosine_score, end="\n\n")
    restaurants_df["cosine_score"] = new_cosine
    to_return = [tup[1] for tup in top_k_heap]
    return restaurants_df.iloc[to_return].sort_values(by="cosine_score", ascending=False)


def advanced_drop_down_menu(facilities, cusine_types, regions, credit_cards):
    global ui_done
    ui_done = False
    result = {"value": ("", "", "", "", "", "", "", "")}

    def on_button_click(_):
        global ui_done
        facility_choosen = [checkbox.description for checkbox in checkboxes if checkbox.value]
        card_choosen = [card_ceckbox.description for card_ceckbox in card_ceckboxes if card_ceckbox.value]
        cusine = cusine_dropdown.value
        region_choosen = region_dropdown.value
        min_money, max_money = (money_slider.value)

        k = k_to_print.value

        querry = querry_box.value
        result["value"] = (querry, facility_choosen, cusine, min_money, max_money, k, region_choosen, card_choosen)
        ui_done = True

    querry_box = widgets.Text(
        placeholder="type something",
        description="what do you want to eat?",
        value="modern seasonal cuisine",
        style={'description_width': 'initial'}
    )
    
    facilities.insert(0, "I don't mind")
    unique_facility = []
    facilities = [unique_facility.append(facility) for facility in facilities if facility not in unique_facility]
    
    checkboxes = [
        widgets.Checkbox(value=False, description=option, layout=widgets.Layout(max_width="auto"))
        for option in unique_facility
    ]

    max_width = 3
    rows = [
        widgets.HBox(checkboxes[i:i + max_width], layout=widgets.Layout(justify_content="flex-start"))
        for i in range(0, len(checkboxes), max_width)
    ]
    facilities_grid = widgets.VBox(rows)

    money_options = [("€", 1), ("€€", 2), ("€€€", 3), ("€€€€", 4)]
    money_slider = widgets.SelectionRangeSlider(
        options=money_options,
        index=(0, 3),  # Indices corresponding to "€" and "€€€€"
        description="Choose a price range:",
        style={'description_width': 'initial'},  # Adjusts the description width
        layout=widgets.Layout(width='45%')
    )

    k_to_print = widgets.BoundedIntText(
        value=5,
        min=0,
        step=1,
        description='How many restourants to display?',
        disabled=False,
        style={'description_width': 'initial'},  # Adjusts the description width
        layout=widgets.Layout(width='45%')
    )

    button_querry = widgets.Button(description="Serch for some restournats",
                                   layout=widgets.Layout(width="250px"))

    button_querry.on_click(on_button_click)

    cusine_types.insert(0, "any taste will do!")
    cusine_dropdown = widgets.Dropdown(
        options=cusine_types,
        description="Choose the cusine specialty: ",
        disabled=False,
        style={'description_width': 'initial'}
    )
    unique_regions = []
    regions = [unique_regions.append(x) for x in regions if x not in unique_regions]
    region_dropdown = widgets.Dropdown(
        options=unique_regions,
        description="Restrict serch to region: ",
        disabled=False,
        style={'description_width': 'initial'}
    )

    unique_cards = []
    credit_cards = [unique_cards.append(x.strip()) for x in credit_cards if x.strip() not in unique_cards]
    card_ceckboxes = [
        widgets.Checkbox(value=False, description=option, layout=widgets.Layout(max_width="auto"))
        for option in unique_cards
    ]

    max_width = 5
    rows = [
        widgets.HBox(card_ceckboxes[i:i + max_width], layout=widgets.Layout(justify_content="flex-start"))
        for i in range(0, len(card_ceckboxes), max_width)
    ]

    card_grid = widgets.VBox(rows)
    display(querry_box, k_to_print, money_slider, cusine_dropdown, facilities_grid, region_dropdown, card_grid, button_querry)

    with ui_events() as poll:
        while ui_done is False:
            poll(10)  # React to UI events (up to 10 at a time)
            time.sleep(0.1)

    return result["value"]



def advanced_upgrade_TF_IDF_score(restaurants_df, facility_choosen, cusine_choosen, min_money, max_money, k, regions, credit_cards):
    '''
    priceRange
    cuisineType
    facilitiesServices
    cosine_score
    ["Restaurant Name", "Address", "Description", "Website", "Cosine"]
    '''
    top_k_heap = []
    new_cosine = []
    for i, (index, row) in enumerate(restaurants_df.iterrows()):
        cost = extract_facilities(row["priceRange"])
        cusine = extract_facilities(row["cuisineType"])
        facility = extract_facilities(row["facilitiesServices"])
        row_region = row["region"]
        cards = extract_facilities(row["creditCards"])
        cosine_score = row.cosine_score

        if row_region != regions:
            continue
        
        if len(set(cards) & set(cards)) == 0:
            continue


        if cost.count("€") >= min_money and cost.count("€") <= max_money:
            cosine_score += 0.2
        # print(set(cusine_choosen)&set(cusine))
        cosine_score += 0.2 * len(set(cusine_choosen) & set(cusine))
        # print(set(facility_choosen)&set(facility))
        cosine_score += 0.2 * len(set(facility_choosen) & set(facility))



        new_cosine.append(cosine_score)

        if len(top_k_heap) < k:
            heapq.heappush(top_k_heap, (cosine_score, i))
        else:
            if cosine_score > top_k_heap[0][0]:  # Compare with the smallest element in the heap
                heapq.heapreplace(top_k_heap, (cosine_score, i))  # Replace the smallest directly

        # print("cosine after: ", cosine_score, end="\n\n")
    restaurants_df = restaurants_df.iloc[ [tup[1] for tup in top_k_heap]]
    restaurants_df["cosine_score"] = [tup[0] for tup in top_k_heap]

    return restaurants_df.sort_values(by="cosine_score", ascending=False)
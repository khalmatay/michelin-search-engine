# Import specific functions from a custom module and a library for table formatting
from functions import clener_pipeline, restourants_matcher
from tabulate import tabulate

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
    
    # Print the number of matching restaurants found
    print(f"We found {len(matching_resturants)} matches!\n")
    
    # Check if any restaurants match the query; exit if no matches were found
    if len(matching_resturants) == 0:
        print("We don't have that in the kitchen!\nChoose something else.")
        return False  # Exit if no matching restaurants were found
    
    # Sort the list of matching restaurant IDs for ordered display
    matching_resturants = sorted(matching_resturants)
    
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

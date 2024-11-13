from functions import clener_pipeline, restourants_matcher
from tabulate import tabulate

def non_ranked_engine(querry, restaurants_df, vocabulary, reverse_index):
    processed_querry = clener_pipeline(querry)
    processed_querry = [vocabulary[key] for key in processed_querry if key in vocabulary.keys()]
    
    if len(processed_querry) == 0 :
        print("We don't have that in the kitchen!\nChoose something else.")
        return False
    
    matching_resturants = [reverse_index[key] for key in processed_querry]
    matching_resturants = restourants_matcher(matching_resturants)

    print(f"We found {len(matching_resturants)} matches!\n")
    if len(matching_resturants) == 0 :
        print("We don't have that in the kitchen!\nChoose something else.")
        return False
    
    matching_resturants = sorted(matching_resturants)
    restaurants_df = restaurants_df.loc[matching_resturants, ["restaurantName", "address", "description", "website"]]
    restaurants_df["description"] = [descript[0:47] + "..." if len(descript) > 30 else descript for descript in restaurants_df["description"]]
    print(tabulate(restaurants_df.iloc[:5], headers=["Restaurant Name", "Address", "Description", "Website"], tablefmt="rounded_grid", showindex=False, maxcolwidths = 25))
    
    return True


from Levenshtein import distance as lev

def comp_dist(x, y):
    # Returns the Levenshtein Distance between two strings, ignoring dashes and spaces
    x_stripped, y_stripped = str(x).replace(" ", "").replace("-", ""), str(y).replace(" ", "").replace("-", "")
    return lev(x_stripped, y_stripped)

def find_closest_sku(bad_sku, master_sku_list: list)-> str:
    # Returns the closest approved sku using comp_dist as a metric. 
    bad_sku = str(bad_sku)
    sorted_master_sku_list = sorted(master_sku_list, key = lambda sku: comp_dist(sku, bad_sku))
    corrected_sku = sorted_master_sku_list[0]
    return corrected_sku

def sku_replacer(bad_sku: str, sku_dict: dict)-> str:
    # Very first function, calling on a sku_dict for answers, then looking for the closest approved sku if not. 
    # This function can be replaced with sku_dict.set_default(bad_sku, predicted_sku). 
    bad_sku = str(bad_sku)
    # Immediately return the sku_dict value if we have a replacement record (or it's a good sku)
    if bad_sku in sku_dict.keys():
        return sku_dict[bad_sku]
    # Sort the master sku list by proximity to the bad sku and then return the first item on the list (i.e. the closest)
    predicted_sku = find_closest_sku(bad_sku, sku_dict)
    sku_dict[bad_sku] = predicted_sku
    return predicted_sku

def highlight_cell_maker(sku_list: list, color: str) -> callable:
    """
    This function is used to quickly creat a highlight_cells function needed to set cell colors. 
    It takes in a list of skus to highlight and a color you wish to highlight them with and returns desired highlight_cells function.  
    """
    def highlight_cells(val):
        returned_color = color if val in sku_list else ""
        return f"background-color: {returned_color}"
    return highlight_cells

def highlight_cell_row_maker(sku_list: list, color: str, check_column_name) -> callable:
    """
    This function is used to quickly creat a highlight_cells function needed to set cell colors. 
    It takes in a list of skus to highlight and a color you wish to highlight them with and returns desired highlight_cells function.  
    """
    def highlight_cells(row):
        returned_color = color if row[check_column_name] in sku_list else "white"
        return [f"background-color: {returned_color}" for r in row]
    return highlight_cells

def make_new_sku_column(df, bad_sku_col_name, sku_dict, include_distance_column=True):
    # Making a new corrected sku column called "New SKU"
    # This column is inserted after bad_sku_col_name and applies the sku_replacer function, updating the sku_dict with replacements as it goes. 
    bad_sku_index = df.columns.get_loc(bad_sku_col_name)
    new_sku_series = df[bad_sku_col_name].apply(lambda entry: sku_replacer(entry, sku_dict))
    df.insert(bad_sku_index + 1, 
              "New SKU", 
              new_sku_series
              )
    # df["New SKU"] = df[bad_sku_col_name].apply(lambda entry: sku_replacer(entry, sku_dict))
    # Creates another column to record each distance 
    if include_distance_column:
        df.insert(
            bad_sku_index + 2, 
            "Levenshtein Distance", 
            df.apply(lambda row: comp_dist(row["New SKU"], row[bad_sku_col_name]), axis=1)
            )
        # df["Levenshtein Distance"] = df.apply(lambda row: comp_dist(row["New SKU"], row[bad_sku_col_name]), axis=1)

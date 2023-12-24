import os.path
import pandas as pd
import json
from Levenshtein import distance as lev



class SKUOperator():
    def __init__(self, prediction_function):
        self.prediction_function = prediction_function
        self.cashed_predictor = CachedPredictor(prediction_function)

    def get_master_skus_list(self, master_skus_filename: str, master_skus_column_name: str)->None:
        """
        Creates a list with the master skus in it. 
        """
        _, file_extension = os.path.splitext(master_skus_filename)
        if file_extension == ".csv":
            m_df = pd.read_csv(master_skus_filename).dropna(how="all")
            master_skus_list = list(m_df[master_skus_column_name].astype(str).str.strip().unique())
        elif file_extension == ".xlsx":
            m_df = pd.read_excel(master_skus_filename).dropna(how="all")
            master_skus_list = list(m_df[master_skus_column_name].astype(str).str.strip().unique())
        elif file_extension == ".json":
            with open(master_skus_filename, "r") as read_file:
                master_skus_list = json.load(read_file)
        else:
            raise Exception("""The file name entered did not have an extension that was either .csv, .xlsx or .json.
                            One of these three formats is required to establish a master sku list.""")
        self.master_skus_list = master_skus_list

    def get_corrected_skus_dict(self, corrected_skus_filename: str, incorrect_skus_column_name: str, correct_skus_column_name: str)->None:
        """
        Creates a dictionary with the corrected in it. 
        """
        _, file_extension = os.path.splitext(corrected_skus_filename)
        if file_extension == ".csv":
            c_df = pd.read_csv(corrected_skus_filename)[[incorrect_skus_column_name, correct_skus_column_name]].dropna(how="any")
            corrected_skus_dict = pd.Series(c_df[correct_skus_column_name].astype(str).str.strip().values,index=c_df[incorrect_skus_column_name]).to_dict()
        elif file_extension == ".xlsx":
            c_df = pd.read_excel(corrected_skus_filename)[[incorrect_skus_column_name, correct_skus_column_name]].dropna(how="any")
            corrected_skus_dict = pd.Series(c_df[correct_skus_column_name].astype(str).str.strip().values,index=c_df[incorrect_skus_column_name]).to_dict()
        elif file_extension == ".json":
            with open(corrected_skus_filename, "r") as read_file:
                corrected_skus_dict = json.load(read_file)
        else:
            raise Exception("""The file name entered did not have an extension that was either .csv, .xlsx or .json.
                            One of these three formats is required to establish a master sku list.""")        
        self.corrected_skus_dict = corrected_skus_dict

    def make_sku_dict(self):
        """
        Combines the master_skus_list and the corrected_skus_dict into one dictionary, over-writing master skus
        that may have been "corrected" with master skus. 
        """
        if hasattr(self, "master_skus_list") and hasattr(self, "corrected_skus_dict"):
            self.sku_dict = self.corrected_skus_dict | {sku: sku for sku in self.master_skus_list}
        else:
            first_exception_line = 'The SKUOperator object must have both a "master_skus_list" and a "corrected_skus_dict" attribute.'
            if hasattr(self, "corrected_skus_dict"):
                raise Exception(first_exception_line + '\nThe attribute "master_skus_list" is missing.')
            elif hasattr(self, "master_skus_list"):
                raise Exception(first_exception_line + '\nThe attribute "corrected_skus_dict" is missing.')
            else:
                raise Exception(first_exception_line + "\nBoth attributes are missing.")
    
    ##### I was going to give this parameters, check that self has a master_skus_list, a corrected_skus_dict and sku_dict
            # and then feed either the skus to be corrected filename and column name (or the df if they're handy) into this method. 
            # This class already has a CachedPredictor, so we can create a dataframe with two columns: The keys/values of the 
            # CachedPredictor's previous_predictions dictionary. The next step in the sku_fixing_window is to launch a window with a 
            # dataframe of these and allow the user to update them, adding the key/value pairs to self.corrected_skus_dict and saving. 
            # At that point, maybe we can re-run this method and print a success message when there's 100% accuracy. 
            # ***Note: Should we re-enable the run button, in case the user deletes some of the rows in the dataframe? Maybe also erase 
            # the previous_prediction dictionary on saving. --That's probably a good idea. Good night! ...and sorry for all the bugs I 
            # left future me with! 
    # def predict_skus(self, ):
    #     """
    #     Uses the CashedPredictor class to make and record predictions. 
    #     """



class CachedPredictor(dict):
    def __init__(self, prediction_function):
        self.prediction_function = prediction_function
        self.previous_predictions = {}
        super().__init__()

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            # Try key against previous predictions, then put into function.
            previous_prediction = self.previous_predictions.get(key)
            if previous_prediction:
                return previous_prediction
            else:
                prediction = self.prediction_function(key)
                self.predictions[key] = prediction
                return prediction













############## Helper Functions ################
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













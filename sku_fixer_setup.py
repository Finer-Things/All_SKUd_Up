import pandas as pd
from Helper_Functions import *

# Enter Master SKU List CSV File Name and Column Name
master_sku_filename = "data/MASTER LIST STRAP SKUS 2022 REVISED.csv"
master_sku_column_name = "SKU"

# Previously-corrected SKUs:
corrected_skus_filename = "data/SKUS LIST WITH CORRECTIONS.csv"
incorrect_sku_column_name = "SKU"
correct_sku_column_name = "New SKU"

# SKUs that need to be corrected
messed_up_skus_filename = "data/SKUs 10-2023.csv"
messed_up_sku_column_name = "SKU"



# Create the master_sku_list and corrected_sku_dict Functions
def make_master_sku_list(master_sku_filename = master_sku_filename):
    m_df = pd.read_csv(master_sku_filename).dropna(how="all")
    master_sku_list = list(m_df[master_sku_column_name].astype(str).str.strip().unique())
    return master_sku_list

def make_corrected_sku_dict(corrected_skus_filename = corrected_skus_filename):
    c_df = pd.read_csv(corrected_skus_filename)[[incorrect_sku_column_name, correct_sku_column_name]].dropna(how="any")
    corrected_sku_dict = pd.Series(c_df[correct_sku_column_name].astype(str).str.strip().values,index=c_df[incorrect_sku_column_name]).to_dict()
    return corrected_sku_dict

def predict_skus(prediction_function):
    """
    Returns a dataframe with a new column of sku predictions using the prediction function. 
    """
    mu_df = pd.read_csv(messed_up_skus_filename).dropna(how="all")
    mu_df["Predicted SKU"] = mu_df[messed_up_sku_column_name].apply(prediction_function)
    return mu_df

def save_highlighted_predictions_file(mu_df, master_sku_list, corrected_sku_dict):
    """
    This takes the messed up skus df with the new predicted skus column and saves a csv file with the 
    (new) predictions made highlighted. 
    """
    known_sku_list = master_sku_list + list(corrected_sku_dict.values()) + list(corrected_sku_dict.keys())
    yellow_cells_list = [sku for sku in mu_df[messed_up_sku_column_name].unique() if sku not in known_sku_list]
    
    fixed_file_name = messed_up_skus_filename[:-4] + " Fixed.xlsx"
    highlight_cell_by_row = highlight_cell_row_maker(yellow_cells_list, "yellow", messed_up_sku_column_name)
    mu_df.style.apply(highlight_cell_by_row, axis=1)\
                    .to_excel(fixed_file_name, engine='openpyxl', index=False)

def save_new_predictions(mu_df, col_1, col_2, master_sku_list, corrected_sku_dict):
    """
    This function saves a csv file with only the predictions made so they can be reviewed, updated, and added to the corrected skus file. 
    col_1 should be the original skus
    col_2 should be the predicted skus
    """
    known_sku_list = master_sku_list + list(corrected_sku_dict.keys()) + list(corrected_sku_dict.values())
    
    predicted_file_name = messed_up_skus_filename[:-4] + " Predicted.csv"
    predicted_df = mu_df[~mu_df[col_2].isin(known_sku_list)][[col_1, col_2]]

    predicted_df.to_csv(predicted_file_name, index=False)
    print(f"There were {len(predicted_df)} predictions made. Below are the first (or fewer...if any). They are saved in {predicted_file_name}")
    print(f"Please check each of these and add them to the corrected skus file to make this program more accurate.")
    if len(predicted_df) > 0:
        print(predicted_df.head(10))
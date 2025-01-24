import streamlit as st
import pandas as pd
import io

def find_comparables(subject_property, dataset):
    """
    Finds the 5 most comparable properties for the given subject property,
    ensuring the VPR value is within the specified range and all conditions are strictly met.

    Args:
        subject_property: A pandas Series representing the subject property.
        dataset: The pandas DataFrame containing all properties.

    Returns:
        A DataFrame with the 5 most comparable properties.
    """

    # Filter based on conditions
    filtered_df = dataset[
        (dataset['Hotel Name'] != subject_property['Hotel Name']) &
        (dataset['Property Address'] != subject_property['Property Address']) &
        (dataset['Owner Name/ LLC Name'] != subject_property['Owner Name/ LLC Name']) &
        (dataset['Owner Street Address'] != subject_property['Owner Street Address']) &
        (dataset['Hotel Class'] == subject_property['Hotel Class']) &
        (dataset['Type'] == 'Hotel') &
        (dataset['Market Value-2024'] >= subject_property['Market Value-2024'] - 100000) &
        (dataset['Market Value-2024'] <= subject_property['Market Value-2024'] + 100000) &
        # VPR condition: between 50% and 100% of subject property's VPR (inclusive)
        (dataset['VPR'] >= subject_property['VPR'] / 2) & 
        (dataset['VPR'] <= subject_property['VPR']) 
    ].copy()

    # If no properties match the criteria, return an empty DataFrame
    if filtered_df.empty:
        return pd.DataFrame()

    # Calculate differences
    filtered_df['Market_Value_Diff'] = abs(filtered_df['Market Value-2024'] - subject_property['Market Value-2024'])
    filtered_df['VPU_VPR_Diff'] = abs(filtered_df['VPR'] - subject_property['VPR'])
    filtered_df['Combined_Diff'] = filtered_df['Market_Value_Diff'] + filtered_df['VPU_VPR_Diff']

    # Sort and get the top 5
    filtered_df = filtered_df.sort_values(by=['Combined_Diff', 'Market_Value_Diff', 'VPU_VPR_Diff']).head(5)

    return filtered_df

def align_subject_and_comparables(data):
    """
    Aligns subject properties and their top 5 comparables into a single DataFrame.

    Args:
        data: The pandas DataFrame containing all properties.

    Returns:
        A DataFrame with subject properties and their comparables aligned horizontally.
    """
    all_rows = []
    for index, subject_property in data.iterrows():
        comparables = find_comparables(subject_property, data)
        row = {
            'VPR': subject_property['VPR'],
            'Hotel Name': subject_property['Hotel Name'],
            'Property Address': subject_property['Property Address'],
            'Market Value-2024': subject_property['Market Value-2024'],
            'Hotel Class': subject_property['Hotel Class'],
            'Owner Name/ LLC Name': subject_property['Owner Name/ LLC Name'],
            'Owner Street Address': subject_property['Owner Street Address'],
            'Type': subject_property['Type'],
            'account number': subject_property['account number']
        }

        # Add comparables to the row
        for i, comp in enumerate(comparables.itertuples(), start=1):
            row[f'comp{i} VPR'] = comp.VPR
            row[f'comp{i} Hotel Name'] = comp._2  # Assuming column 2 is Hotel Name
            row[f'comp{i} Property Address'] = comp._3  # Assuming column 3 is Property Address
            row[f'comp{i} Market Value-2024'] = comp._4  # Assuming column 4 is Market Value-2024
            row[f'comp{i} Hotel Class'] = comp._5  # Assuming column 5 is Hotel Class
            row[f'comp{i} Owner Name/ LLC Name'] = comp._6  # Assuming column 6 is Owner Name/ LLC Name
            row[f'comp{i} Owner Street Address'] = comp._7  # Assuming column 7 is Owner Street Address
            row[f'comp{i} Type'] = comp._8  # Assuming column 8 is Type
            row[f'comp{i} account number'] = comp._9  # Assuming column 9 is account number

        all_rows.append(row)

    return pd.DataFrame(all_rows)

def main():
    print("Comparable Analysis")

    # File upload prompt
    file_path = input("Enter the path of your CSV file: ")

    try:
        # Load data
        data = pd.read_csv(file_path)

        # Generate aligned data
        aligned_data = align_subject_and_comparables(data)

        # Display aligned data
        print("\nAligned Subject Properties and Comparables:")
        print(aligned_data)

        # Save to Excel
        output_file = "aligned_comparables.xlsx"
        aligned_data.to_excel(output_file, index=False, sheet_name='Aligned Data', engine='openpyxl')
        print(f"\nAligned data saved to {output_file}")

    except FileNotFoundError:
        print("File not found. Please check the file path and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


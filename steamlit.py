import streamlit as st
import pandas as pd


def find_comparables(subject_property, dataset):
    """
    Finds the 5 most comparable properties for the given subject property,
    prioritizing those with the closest market value and VPU/VPR.

    Args:
        subject_property: A pandas Series representing the subject property.
        dataset: The pandas DataFrame containing all properties.

    Returns:
        A list of 5 pandas Series, each representing a comparable property.
    """

    # Filter based on conditions
    filtered_df = dataset[
        (dataset['Hotel Name'] != subject_property['Hotel Name']) &
        (dataset['Property Address'] != subject_property['Property Address']) &
        (dataset['Owner Name/LLC Name'] != subject_property['Owner Name/LLC Name']) &
        (dataset['Owner Street Address'] != subject_property['Owner Street Address']) &
        (dataset['Hotel Class'] == 'Economy') &
        (dataset['Type'] == 'Hotel') &
        (dataset['Market Value-2024'] >= subject_property['Market Value-2024'] - 100000) &
        (dataset['Market Value-2024'] <= subject_property['Market Value-2024'] + 100000) &
        (dataset['VPR'] <= subject_property['VPR'] * 1.5)
    ].copy()  # Create a copy of the filtered DataFrame

    # Calculate market value and VPU/VPR differences
    filtered_df['Market_Value_Diff'] = abs(filtered_df['Market Value-2024'] - subject_property['Market Value-2024'])
    filtered_df['VPU_VPR_Diff'] = abs(filtered_df['VPR'] - subject_property['VPR'])
    filtered_df['Combined_Diff'] = filtered_df['Market_Value_Diff'] + filtered_df['VPU_VPR_Diff']

    # Prioritize by combined difference (market value and VPU/VPR)
    filtered_df = filtered_df.sort_values(by=['Combined_Diff', 'Market_Value_Diff', 'VPU_VPR_Diff'])

    # Select top 5 comparables
    comparables = filtered_df.head(5)

    # Format comparables to match Comp1
    formatted_comparables = []
    for _, comp in comparables.iterrows():
        formatted_comp = pd.Series({
            'VPR': comp['VPR'],
            'Hotel Name': comp['Hotel Name'],
            'Property Address': comp['Property Address'],
            'Market Value-2024': comp['Market Value-2024'],
            'Hotel Class': comp['Hotel Class'],
            'Owner Name/LLC Name': comp['Owner Name/LLC Name'],
            'Type': comp['Type'],
            'Owner Street Address': comp['Owner Street Address']
        })
        formatted_comparables.append(formatted_comp)

    return formatted_comparables


def main():
    st.title("Hotel Comparable Analysis")

    # File upload
    uploaded_file = st.file_uploader("Upload your hotel data (CSV)", type="csv")

    if uploaded_file is not None:
        # Load data
        data = pd.read_csv(uploaded_file)

        # Create an empty list to store results
        results = []

        # Iterate through each row as subject property
        for i in range(len(data)):
            subject_property = data.iloc[i]
            comparables = find_comparables(subject_property, data.drop(i))
            results.append([subject_property] + comparables)

        # Create a DataFrame from the results
        result_df = pd.DataFrame(results)

        # Create an index slider widget
        index_slider = st.slider("Select Subject Property", min_value=0, max_value=len(result_df)-1, step=1)

        # Display the current subject property and comparables
        def display_subject_and_comparables(selected_index):
            st.write(f"Subject Property (Index {selected_index}):\n{result_df.iloc[selected_index][0]}")
            st.write("\nComparables:")

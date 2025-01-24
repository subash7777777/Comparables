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

    return filtered_df.drop(columns=['Market_Value_Diff', 'VPU_VPR_Diff', 'Combined_Diff'])





def main():

    # Apply custom styles

    st.markdown(

        """

        <style>

        .main { background-color: #f7f9fc; }

        .stButton>button { background-color: #007bff; color: white; border-radius: 5px; }

        .stButton>button:hover { background-color: #0056b3; }

        h1 { color: #004085; }

        .dataframe { background-color: #ffffff; border-radius: 10px; padding: 10px; }

        </style>

        """,

        unsafe_allow_html=True,

    )



    st.title("Comparable Analysis")



    # File upload

    uploaded_file = st.file_uploader("Upload your data (CSV)", type="csv")



    if uploaded_file is not None:

        # Load data

        data = pd.read_csv(uploaded_file)



        # Initialize session state for tracking property index

        if "current_index" not in st.session_state:

            st.session_state.current_index = 0



        # Navigation buttons

        col1, col2 = st.columns([1, 1])

        with col1:

            if st.button("Previous") and st.session_state.current_index > 0:

                st.session_state.current_index -= 1

        with col2:

            if st.button("Next") and st.session_state.current_index < len(data) - 1:

                st.session_state.current_index += 1



        # Select subject property based on current index

        subject_index = st.session_state.current_index

        subject_property = data.iloc[subject_index]



        # Display subject property

        st.subheader(f"Subject Property (Index: {subject_index})")

        st.dataframe(subject_property.to_frame().T.style.set_properties(**{'background-color': '#eaf4fc', 'border': '1px solid #007bff'}))



        # Find comparables

        comparables = find_comparables(subject_property, data)



        # Display comparables

        st.subheader("Comparable Properties:")

        if not comparables.empty:

            st.dataframe(

                comparables.style.set_properties(

                    **{'background-color': '#ffffff', 'color': '#333', 'border': '1px solid #dddddd'}

                )

            )

        else:

            st.write("No comparable properties found based on the given criteria.")



        # Download button

      # Download button
if st.button("Download Results"):
    # Find comparables
    comparables = find_comparables(subject_property, data)
    
    # Prepare the result dictionary with all the specified columns
    result_dict = {
        # Subject Property Columns
        'VPR': [subject_property['VPR']],
        'Hotel Name': [subject_property['Hotel Name']],
        'Property Address': [subject_property['Property Address']],
        'Market Value-2024': [subject_property['Market Value-2024']],
        'Hotel Class': [subject_property['Hotel Class']],
        'Owner Name/ LLC Name': [subject_property['Owner Name/ LLC Name']],
        'Owner Street Address': [subject_property['Owner Street Address']],
        'Type': [subject_property['Type']],
        'account number': [subject_property['account number']]
    }
    
    # Add Comparable Properties Columns (up to 5)
    for i in range(5):
        prefix = f'comp{i+1} '
        if i < len(comparables):
            comp = comparables.iloc[i]
            result_dict[prefix + 'VPR'] = [comp['VPR']]
            result_dict[prefix + 'Hotel Name'] = [comp['Hotel Name']]
            result_dict[prefix + 'Property Address'] = [comp['Property Address']]
            result_dict[prefix + 'Market Value-2024'] = [comp['Market Value-2024']]
            result_dict[prefix + 'Hotel Class'] = [comp['Hotel Class']]
            result_dict[prefix + 'Owner Name/ LLC Name'] = [comp['Owner Name/ LLC Name']]
            result_dict[prefix + 'Owner Street Address'] = [comp['Owner Street Address']]
            result_dict[prefix + 'Type'] = [comp['Type']]
            result_dict[prefix + 'account number'] = [comp['account number']]
        else:
            # Fill with empty values if no comparable property exists
            result_dict[prefix + 'VPR'] = [None]
            result_dict[prefix + 'Hotel Name'] = [None]
            result_dict[prefix + 'Property Address'] = [None]
            result_dict[prefix + 'Market Value-2024'] = [None]
            result_dict[prefix + 'Hotel Class'] = [None]
            result_dict[prefix + 'Owner Name/ LLC Name'] = [None]
            result_dict[prefix + 'Owner Street Address'] = [None]
            result_dict[prefix + 'Type'] = [None]
            result_dict[prefix + 'account number'] = [None]
    
    # Create DataFrame from the dictionary
    result_df = pd.DataFrame(result_dict)
    
    # Create an in-memory buffer for the Excel file
    output = io.BytesIO()
    
    # Write the DataFrame to the buffer as an Excel file
    result_df.to_excel(output, index=False, sheet_name='Results', engine='openpyxl')
    
    # Set the file name and download it
    st.download_button(
        "Download Excel",
        data=output.getvalue(),
        file_name='comparable_properties.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == "__main__":

    main()

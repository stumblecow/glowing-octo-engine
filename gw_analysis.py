import pandas as pd
import streamlit as st

#Load and clean up 2025 Data
def load_and_clean_data (chapters_file, caucuses_file):
  chapters_df = pd.read_csv (chapters_file)
  caucuses_df = pd.read_csv (caucuses_file)
  # Fill missing Groundwork flags with 0 (assume not Groundwork)
  chapters_df['Is Groundwork Chapter'] = chapters_df['Is Groundwork Chapter'].fillna(0)
  return chapters_df, caucuses_df

def melt_caucuses_data (caucuses_df):
  #Melts the caucus CSV
  melted_caucuses = caucuses_df.melt (
    id_vars=['Chapter'],
    var_name = 'Caucus',
    value_name= '2025 Voters')
  # Fill blank/NaN values with 0 in the '2025 Voters' column
  melted_caucuses['2025 Voters'] = melted_caucuses['2025 Voters'].fillna(0)
  return melted_caucuses

def set_2025_delegates (chapters_df):
  delegate_count_2025 = chapters_df.copy()
  if '2025 membership' not in delegate_count_2025.columns:
    st.write("Warning: '2025 membership' column not found in the DataFrame.")
    return delegate_count_2025
  #Magic number is 60 because that is how the 2025 NPC apportioned delegates
  delegate_count_2025['2025 delegates'] = (delegate_count_2025['2025 membership']/60)
  return delegate_count_2025

def prep_2025_data(chapters_file, caucuses_file):
  chapters_df, caucuses_df = load_and_clean_data(chapters_file, caucuses_file)
  melted_caucuses = melt_caucuses_data(caucuses_df)
  delegate_count_2025 = set_2025_delegates(chapters_df)
  return melted_caucuses, delegate_count_2025

# figure out 2027 convention
def calculate_2027_membership (delegate_count_2025, organizational_growth, groundwork_growth_rate):
  membership_2027 = delegate_count_2025.copy()
  membership_2027['2027 membership'] = membership_2027['2025 membership'] * (1 + organizational_growth)
  #applies higher Growth rate to Groundwork Chapters
  for i in range(len(membership_2027)):
        if membership_2027.loc[i, 'Is Groundwork Chapter'] == 1:
            membership_2027.loc[i, '2027 membership'] = membership_2027.loc[i, '2025 membership'] * (1 + groundwork_growth_rate)
  return membership_2027

def find_total_membership (membership_2027):
  total_membership = membership_2027['2027 membership'].sum()
  return total_membership

def determine_delegate_apportionment (total_membership):
  #assumes we don't want more than 1300 delegates in 2027 convention
  apportionment_2027 = total_membership/1300
  return apportionment_2027 # Added return statement

def set_2027_delegates (apportionment_2027, membership_2027):
  membership_2027['2027 delegates'] = (membership_2027['2027 membership']/apportionment_2027).astype(int)
  return membership_2027

def set_up_2027_convention (delegate_count_2025, organizational_growth, groundwork_growth_rate):
  membership_2027 = calculate_2027_membership (delegate_count_2025, organizational_growth, groundwork_growth_rate)
  total_membership = find_total_membership (membership_2027)
  apportionment_2027 = determine_delegate_apportionment (total_membership)
  convention_2027 = set_2027_delegates (apportionment_2027, membership_2027)
  return convention_2027, total_membership, apportionment_2027

# Projecting 2027 Caucus Makeup
def calculate_caucus_share_2025 (melted_caucuses_data):
  share_df = melted_caucuses_data.copy()
  share_df['2025 Caucus Share'] = share_df['2025 Voters']/share_df.groupby('Chapter')['2025 Voters'].transform('sum')
  return share_df

def calculate_2027_caucus_delegates (share_df, convention_2027):
  caucus_2027_df = share_df.copy()
  
  # Clean whitespace to ensure successful merge
  caucus_2027_df['Chapter'] = caucus_2027_df['Chapter'].str.strip()
  convention_2027['Chapter'] = convention_2027['Chapter'].str.strip()
  
  # Perform the merge
  caucus_2027_df = caucus_2027_df.merge(
      convention_2027[['Chapter', '2027 delegates']], 
      on='Chapter', 
      how='left'
  )
  # Fill missing values with 0 so the calculation doesn't break
  caucus_2027_df['2027 delegates'] = caucus_2027_df['2027 delegates'].fillna(0)
  caucus_2027_df['2025 Caucus Share'] = caucus_2027_df['2025 Caucus Share'].fillna(0)

  # Now calculate the delegates (make sure to use integer math)
  caucus_2027_df['2027 Delegates for Caucus'] = (
    caucus_2027_df['2027 delegates'] * caucus_2027_df['2025 Caucus Share']
  ).round().astype(int)  # Round and convert to integer
  return caucus_2027_df


def create_2027_caucus_pivot(caucus_2027_df):
  #Creates a pivot table of caucus representation by chapter
  pivot_2027 = pd.pivot_table(
        caucus_2027_df,
        values='2027 Delegates for Caucus',
        index='Chapter', 
        columns='Caucus',
        aggfunc='sum',
        fill_value=0
    )
  pivot_2027['Chapter Delegates'] = pivot_2027.sum(axis=1)
  return pivot_2027


def create_2025_caucus_pivot(melted_caucuses_data):
    #Create a pivot table of 2025 caucus makeup from the melted caucuses data
    pivot_2025 = pd.pivot_table(
        melted_caucuses_data,
        values='2025 Voters',
        index='Chapter',
        columns='Caucus', 
        aggfunc='sum',
        fill_value=0
    )
    return pivot_2025

#Main
def main():
#session state
  if 'show_delegate_count_2025' not in st.session_state:
    st.session_state['show_delegate_count_2025'] = False
#variables
  apportionment_2027 = 0
  total_membership = 0
  delegate_count_2025 = None
  melted_caucuses_data = None
  share_df = None
  convention_2027 = None
  caucus_2027_df = None
  pivot_2027 = None
  pivot_2025 = None
# Upload files
  chapters_file = st.file_uploader('Upload Chapters CSV', type='csv')
  caucuses_file = st.file_uploader('Upload Caucuses CSV', type='csv')
  organizational_growth = st.number_input('Organizational Growth', min_value=0.0, max_value=1.0, step=0.01)
  groundwork_growth_rate = st.number_input('Groundwork Growth Rate', min_value=0.0, max_value=1.0, step=0.01)

# Check if both files are uploaded
  if chapters_file is not None and caucuses_file is not None:
    # Both files are ready - process them
    #figure out 2025 data
    melted_caucuses_data, delegate_count_2025 = prep_2025_data(chapters_file, caucuses_file)
    share_df = calculate_caucus_share_2025(melted_caucuses_data)
    #figure out 2027 data
    convention_2027, total_membership, apportionment_2027 = set_up_2027_convention (delegate_count_2025, organizational_growth, groundwork_growth_rate)
    caucus_2027_df = calculate_2027_caucus_delegates (share_df, convention_2027)
    # Display the results of figuring out 2027 convention makeup
    st.write(f"2027 Delegate Apportionment (total membership divided by 1300): {apportionment_2027}") # Using f-strings for better formatting
    st.write(f"Estimated 2027 Membership: {total_membership}") # Using f-strings for better formatting
    st.write(convention_2027)
#show and hide 2025 chapter data
    if st.button("Show/Hide 2025 Delegate Count and Estimated Chapter Membership"):
      st.session_state.show_delegate_count_2025 = not st.session_state.show_delegate_count_2025
    if st.session_state.show_delegate_count_2025:
      st.write("2025 Delegate Count and Estimated Chapter Membership")
      st.write(delegate_count_2025)
#final pivot table data with editable 2027 pivot table
    pivot_2027 = create_2027_caucus_pivot(caucus_2027_df)
    pivot_2025 = create_2025_caucus_pivot(melted_caucuses_data)
    st.subheader("2025 Caucus Makeup")
    st.write(pivot_2025)
    st.subheader("2027 Caucus Makeup")
    edited_pivot = st.data_editor(pivot_2027)
    #data validation for editor
    for index, row_data in edited_pivot.iterrows():
      chapter_name = index
      row_sum = row_data.drop('Chapter Delegates').sum()
      if row_sum != row_data['Chapter Delegates']:
        st.error(f"❌ Validation failed for {chapter_name}: Sum is {row_sum} but should be {row_data['Chapter Delegates']}")
#download CSV of edited 2027 pivot table
    st.download_button(
      label="Download Edited 2027 Pivot Table",
      data=edited_pivot.to_csv().encode('utf-8'),
      file_name='edited_pivot.csv',
      mime='text/csv',
    )
  else:
    # Show message while waiting for uploads
    st.info("⏳ Please upload both CSV files to continue...")
    # Don't try to process data yet
    st.stop()  # This prevents the rest of the code from running

if __name__ == "__main__":
  st.title("📊 Caucus Analytics Dashboard")
  main()

import pandas as pd
import streamlit as st

#Load and clean up 2025 Data
def loaddata (chapters_file, caucuses_file):
  chapters_df = pd.read_csv (chapters_file)
  caucuses_df = pd.read_csv (caucuses_file)
  # DEBUG: See what the column looks like before fixing
  st.write("Before fillna - unique values:", chapters_df['Is Groundwork Chapter'].unique())
  chapters_df['Is Groundwork Chapter'] = chapters_df['Is Groundwork Chapter'].fillna(0)
  # DEBUG: See what the column looks like after fixing
  st.write("After fillna - unique values:", chapters_df['Is Groundwork Chapter'].unique())
  return chapters_df, caucuses_df

def meltcaucuses (caucuses_df):
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
  delegate_count_2025['2025 delegates'] = (delegate_count_2025['2025 membership']/60)
  return delegate_count_2025

def prepdata(chapters_file, caucuses_file):
  chapters_df, caucuses_df = loaddata(chapters_file, caucuses_file)
  melted_caucuses = meltcaucuses(caucuses_df)
  delegate_count_2025 = set_2025_delegates(chapters_df)
  return melted_caucuses, delegate_count_2025

# figure out 2027 convention
def calculate_2027_membership (delegate_count_2025, organizational_growth, groundwork_growth_rate):
  membership_2027 = delegate_count_2025.copy()
  membership_2027['2027 membership'] = membership_2027['2025 membership'] * (1 + organizational_growth)
  for i in range(len(membership_2027)):
        if membership_2027.loc[i, 'Is Groundwork Chapter'] == 1:
            membership_2027.loc[i, '2027 membership'] = membership_2027.loc[i, '2025 membership'] * (1 + groundwork_growth_rate)
  return membership_2027

def find_total_membership (membership_2027):
  total_membership = membership_2027['2027 membership'].sum()
  return total_membership

def determine_delegate_apportionment (total_membership):
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
def caucus_share_2025 (melted_caucuses_data):
  share_df = melted_caucuses_data.copy()
  share_df['2025 Caucus Share'] = share_df['2025 Voters']/share_df.groupby('Chapter')['2025 Voters'].transform('sum')
  return share_df

def set_2027_caucus (share_df, convention_2027):
  caucus_2027_df = share_df.copy()
  
  # Clean the Chapter columns first
  caucus_2027_df['Chapter'] = caucus_2027_df['Chapter'].str.strip()
  convention_2027['Chapter'] = convention_2027['Chapter'].str.strip()
  
  # Debug: check what we're merging
  st.write("Sample chapters in share_df:", caucus_2027_df['Chapter'].head(10).tolist())
  st.write("Sample chapters in convention_2027:", convention_2027['Chapter'].head(10).tolist())
  
  # Perform the merge
  caucus_2027_df = caucus_2027_df.merge(
      convention_2027[['Chapter', '2027 delegates']], 
      on='Chapter', 
      how='left'
  )
  # Fill missing values with 0 so the calculation doesn't break
  caucus_2027_df['2027 delegates'] = caucus_2027_df['2027 delegates'].fillna(0)
  caucus_2027_df['2025 Caucus Share'] = caucus_2027_df['2025 Caucus Share'].fillna(0)

  #Debug post merge
  st.write("Number of missing 2027 delegates after merge:", caucus_2027_df['2027 delegates'].isnull().sum())
  missing_delegates = caucus_2027_df[caucus_2027_df['2027 delegates'].isnull()]['Chapter'].unique()
  st.write("Chapters missing 2027 delegates:", missing_delegates)
  # Now calculate the delegates (make sure to use integer math)
  caucus_2027_df['2027 Delegates for Caucus'] = (
    caucus_2027_df['2027 delegates'] * caucus_2027_df['2025 Caucus Share']
  ).round().astype(int)  # Round and convert to integer
  return caucus_2027_df


def create_pivot(caucus_2027_df):
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

#Main
def main():
#variables
  apportionment_2027 = 0
  total_membership = 0
  delegate_count_2025 = None
  melted_caucuses_data = None
  share_df = None
  convention_2027 = None
  caucus_2027_df = None
  pivot_2027 = None
# Upload files
  chapters_file = st.file_uploader('Upload Chapters CSV', type='csv')
  caucuses_file = st.file_uploader('Upload Caucuses CSV', type='csv')
  organizational_growth = st.number_input('Organizational Growth', min_value=0.0, max_value=1.0, step=0.01)
  groundwork_growth_rate = st.number_input('Groundwork Growth Rate', min_value=0.0, max_value=1.0, step=0.01)

# Check if both files are uploaded
  if chapters_file is not None and caucuses_file is not None:
    # Both files are ready - process them
    melted_caucuses_data, delegate_count_2025 = prepdata(chapters_file, caucuses_file)
    convention_2027, total_membership, apportionment_2027 = set_up_2027_convention (delegate_count_2025, organizational_growth, groundwork_growth_rate)
    share_df = caucus_share_2025(melted_caucuses_data)
    caucus_2027_df = set_2027_caucus (share_df, convention_2027)
    pivot_2027 = create_pivot(caucus_2027_df)
    # Display the results
    st.write(f"2027 Delegate Apportionment: {apportionment_2027}") # Using f-strings for better formatting
    st.write(f"Total 2027 Membership: {total_membership}") # Using f-strings for better formatting
    st.write(delegate_count_2025)
    st.write(pivot_2027)
    st.subheader("2027 Delegate Makeup")
    edited_pivot = st.data_editor(pivot_2027)
    #data validation for editor
    for index, row_data in edited_pivot.iterrows():
      chapter_name = index
      row_sum = row_data.sum()
      if row_sum != row_data['Chapter Delegates']:
        st.error(f"❌ Validation failed for {row_data['Chapter']}: Sum is {row_sum} but should be {row_data['Chapter Delegates']}")

  else:
    # Show message while waiting for uploads
    st.info("⏳ Please upload both CSV files to continue...")
    # Don't try to process data yet
    st.stop()  # This prevents the rest of the code from running

if __name__ == "__main__":
  st.title("📊 Caucus Analytics Dashboard")
  main()

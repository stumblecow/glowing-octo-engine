import pandas as pd
import streamlit as st

#Load and clean up 2025 Data
def loaddata (chapters_file, caucuses_file):
  chapters_df = pd.read_csv (chapters_file)
  caucuses_df = pd.read_csv (caucuses_file)
  chapters_df = chapters_df['Is Groundwork Chapter'].fillna(0)
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
  delegate_count_2025['2025 delegates'] = chapters_df['2025 membership']*60
  return delegate_count_2025

def prepdata(chapters_file, caucuses_file, delegate_count_2025):
  chapters_df, caucuses_df = loaddata(chapters_file, caucuses_file)
  melted_caucuses = meltcaucuses(caucuses_df)
  set_2025_delegates(chapters_df)
  return chapters_df, melted_caucuses, delegate_count_2025

# figure out 2027 convention
def calculate_2027_membership (delegate_count_2025, organizational_growth, groundwork_growth_rate):
  membership_2027 = delegate_count_2025.copy()
  membership_2027['2027 membership'] = membership_2027['2025 delegates'] * (1 + organizational_growth)
  for i in range(len(membership_2027)):
        if membership_2027.loc[i, 'Is Groundwork Chapter'] == 1:
            membership_2027.loc[i, '2027 membership'] = membership_2027.loc[i, '2027 membership'] * (1 + groundwork_growth_rate)
  return membership_2027

def find_total_membership (membership_2027):
  total_membership = membership_2027['2027 membership'].sum()
  return total_membership

def determine_delegate_apportionment (total_membership):
  apportionment_2027 = total_membership/1300
  return apportionment_2027 # Added return statement

def set_2027_delegates (apportionment_2027, membership_2027):
  membership_2027['2027 delegates'] = (apportionment_2027 * membership_2027['2027 membership']).astype(int)
  return membership_2027

#Main
def main():
# Upload files
  chapters_file = st.file_uploader('Upload Chapters CSV', type='csv')
  caucuses_file = st.file_uploader('Upload Caucuses CSV', type='csv')
  organizational_growth = st.number_input('Organizational Growth', min_value=0.0, max_value=1.0, step=0.01)
  groundwork_growth_rate = st.number_input('Groundwork Growth Rate', min_value=0.0, max_value=1.0, step=0.01)

# Check if both files are uploaded
  if chapters_file is not None and caucuses_file is not None:
      # Both files are ready - process them
      chapters_data, melted_caucuses_data = prepdata(chapters_file, caucuses_file)
      # The return values of the functions were not being used in the main function.
      # Also, chapters_df was not defined in this scope, it should be chapters_data
      delegate_count_2025 = set_2025_delegates (chapters_data)
      membership_2027 = calculate_2027_membership (delegate_count_2025, organizational_growth, groundwork_growth_rate)
      total_membership = find_total_membership (membership_2027)
      apportionment_2027 = determine_delegate_apportionment (membership_2027, total_membership)

      st.write(f"Organizational Growth: {organizational_growth}") # Using f-strings for better formatting
      st.write(f"Delegate Apportionment: {apportionment_2027}") # Using f-strings for better formatting
      st.write(f"Total Membership: {total_membership}") # Using f-strings for better formatting
      st.write(membership_2027)
  else:
      # Show message while waiting for uploads
      st.info("⏳ Please upload both CSV files to continue...")
      # Don't try to process data yet
      st.stop()  # This prevents the rest of the code from running

if __name__ == "__main__":
    st.title("📊 Caucus Analytics Dashboard")
    main()

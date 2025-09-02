import pandas as pd
import streamlit as st

#Load and clean up Data
def loaddata (chapters_file, caucuses_file):
  chapters_df = pd.read_csv (chapters_file)
  caucuses_df = pd.read_csv (caucuses_file)
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

def prepdata(chapters_file, caucuses_file):
  chapters_df, caucuses_df = loaddata(chapters_file, caucuses_file)
  melted_caucuses = meltcaucuses(caucuses_df)
  return chapters_df, melted_caucuses

def set_2025_delegates (chapters_df):
  delegate_count_2025 = chapters_df.copy()
  delegate_count_2025.insert(3, '2025 delegates', chapters_df['2025 membership']*60)
  return delegate_count_2025

def calculate_2027_membership (delegate_count_2025, organizational_growth, groundwork_growth_rate):
  membership_2027 = delegate_count_2025.copy()
  membership_2027.insert(
      3, 
      '2027 membership', 
      membership_2027['2025 delegates']*(1+organizational_growth))
  for i in range(len(membership_2027)):
        if membership_2027.loc[i, 'Is Groundwork Chapter'] == 1:
            membership_2027.loc[i, '2027 membership'] = membership_2027.loc[i, '2027 membership'] * (1 + groundwork_growth_rate)
  return membership_2027

def find_total_membership (membership_2027):
  total_membership = membership_2027['2027 membership'].sum()
  return total_membership

 def determine_delegate_apportionment (membership_2027, total_membership):
  apportionment_2027 = total_membership/1300    


#Main
def __main__():
# Upload files
  chapters_file = st.file_uploader('Upload Chapters CSV', type='csv')
  caucuses_file = st.file_uploader('Upload Caucuses CSV', type='csv')
  organizational_growth = st.number_input('Organizational Growth', min_value=0.0, max_value=1.0, step=0.01)
  groundwork_growth_rate = st.number_input('Groundwork Growth Rate', min_value=0.0, max_value=1.0, step=0.01)

# Check if both files are uploaded
  if chapters_file is not None and caucuses_file is not None:
      # Both files are ready - process them
      chapters_data, melted_caucuses_data = prepdata(chapters_file, caucuses_file)
      set_2025_delegates (chapters_df)
      calculate_2027_membership (delegate_count_2025, organizational_growth, groundwork_growth_rate)
      find_total_membership (membership_2027)
      determine_delegate_apportionment (membership_2027, total_membership)

      st.write("Organizational Growth: {organizational_growth}")
      st.write("Delegate Apportionment: {apportionment_2027}")
      st.write("Total Membership: {total_membership}")
  else:
      # Show message while waiting for uploads
      st.info("⏳ Please upload both CSV files to continue...")
      # Don't try to process data yet
      st.stop()  # This prevents the rest of the code from running

if __name__ == "__main__":
    st.title("📊 Caucus Analytics Dashboard")
    __main__()
    
    

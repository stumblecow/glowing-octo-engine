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

#Set up streamlit environment
def showchart (chapters_df, melted_caucuses):
  st.bar_chart (chapters_df)
  st.bar_chart (melted_caucuses)

if __name__ == "__main__":
    st.title("📊 Caucus Analytics Dashboard")
    
    # Upload files
    chapters_file = st.file_uploader('Upload Chapters CSV', type='csv')
    caucuses_file = st.file_uploader('Upload Caucuses CSV', type='csv')
    
    # Check if both files are uploaded
    if chapters_file is not None and caucuses_file is not None:
        # Both files are ready - process them
        chapters_data, melted_caucuses_data = prepdata(chapters_file, caucuses_file)
        showchart(chapters_data, melted_caucuses_data)
    else:
        # Show message while waiting for uploads
        st.info("⏳ Please upload both CSV files to continue...")
        # Don't try to process data yet
        st.stop()  # This prevents the rest of the code from running

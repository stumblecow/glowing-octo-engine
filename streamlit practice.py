import pandas as pd
import streamlit as st

#upload data
def uploaddata ():
  chapters_file = st.file_uploader ('Upload Chapters CSV', type = 'csv')
  caucuses_file = st.file_uploader ('Upload Caucuses CSV', type = 'csv')
  return chapters_file, caucuses_file

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

def prepdata():
  chapters_df, caucuses_df = loaddata(chapters_file, caucuses_file)
  melted_caucuses = meltcaucuses(caucuses_df)
  return chapters_df, melted_caucuses

#Set up streamlit environment
def showchart (chapters_df, melted_caucuses):
  st.bar_chart (chapters_df)
  st.bar_chart (melted_caucuses)

if __name__ == "__main__":
    # Capture the returned data
    chapters_data, melted_caucuses = prepdata()
    # Pass the data to the showchart function
    showchart(chapters_data, melted_caucuses)

import streamlit as st
import pandas as pd
import plotly.express as px
import json

# with open('C:/Users/abhishek.kapri/Downloads/app/app/resources/config.json') as config_file:
#     data = json.load(config_file)
CONFIG_FILE = 'C:/Users/abhishek.kapri/Downloads/code_20210412/code/app/config.json'
C = json.load(open(CONFIG_FILE))
    
@st.cache()
def load_data():
    df = pd.read_csv(C['downloadloc'])
    return df

print("Data Reading done")

# Read in the cereal data
df = load_data()
st.title('Data Visualization')
print(df)
# Only a subset of options make sense
x_options = df.columns
y_options = df.columns

# Allow use to choose

x_axis = st.sidebar.selectbox('Which value do you want to explore?', x_options)
y_axis = st.sidebar.radio('Which value do you want to explore?', y_options)

# plot the value
fig = px.histogram(df,
                x=x_axis,
                y=y_axis,
                hover_name=y_axis,
                title=f'{y_axis} vs. {x_axis}')

st.plotly_chart(fig)
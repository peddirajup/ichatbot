import streamlit as st

st.title('Example 1')
st.write("This is a sample example of streamlit")
slider_value = st.slider('Select a number', 0, 100, 50)
st.write('You selected', slider_value)

import streamlit as st
from data_cleaning import new_df, recommend, fetch_poster
import requests

movies_list = new_df
movies_list = movies_list['title']

st.title('Top 5 movies Recommendation')

selected_movie_name = st.selectbox('Movie Name',movies_list)

if st.button('Recommend'):
    names,posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])



    # temp = {}
    # i = 0
    # for j in range(5):
    #     i += 1
    #     temp[i] = st.columns(5)
    #     with temp[j]:
    #         st.header(names[j])
    #         st.image(posters[j])
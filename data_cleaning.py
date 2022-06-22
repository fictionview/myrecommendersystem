import numpy as np
import pandas as pd
import ast
import nltk
import requests
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer as cv, CountVectorizer

cv = CountVectorizer(max_features=5000,stop_words='english')
ps = PorterStemmer()


#store both csv data in variables to work on it
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')
#print(credits.columns)

#merge both the data files
movies = movies.merge(credits,on='title')

#select required columns
movies = movies[['movie_id','title','overview','genres','keywords','cast','crew']]
movies.dropna(inplace = True)

#clean the data column and extrat required keyword
def convert(obj):
    l = []
    for i in ast.literal_eval(obj):
        #extract only that data which is in name keyword
        l.append(i['name'])
    return l


def convert_another(obj):
    l = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            #extract only that data which is in name keyword
            l.append(i['name'])
            counter += 1
        else:
            break
    return l


def fetch_Director(obj):
    l = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            #extract only that data which is in name keyword
            l.append(i['name'])
            break
    return l


def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)


#execute the convert function for genres columnand remove the space
movies['genres'] = movies['genres'].apply(convert)
movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ","") for i in x])

#execute the convert function for keywords column and remove space
movies['keywords'] = movies['keywords'].apply(convert)
movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ","") for i in x])

#top 3 cast for cast column. function is above and remove space
movies['cast'] = movies['cast'].apply(convert_another)
movies['cast'] = movies['cast'].apply(lambda x:[i.replace(" ","") for i in x])

#fetch name of the director. function is above and remove space
movies['crew'] = movies['crew'].apply(fetch_Director)
movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ","") for i in x])

#convert the overview string in to a list
movies['overview'] = movies['overview'].apply(lambda x:x.split())

#create a column tag and concatinate all above columns (overview, genre, keywords and cast
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

#take relevant columns only and convert tags in to string and change every word into lower case
#then apply stem to avoid similar word with different tenses
new_df = movies[['movie_id', 'title', 'tags']]
new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())
new_df['tags'] = new_df['tags'].apply(stem)

#convert all the words into vector to compare using scikit library
vectors = cv.fit_transform(new_df['tags']).toarray()

#cv.get_feature_names() --> to get the sum of common words

#a matrix of arrays of arrays. it is comparing every word with every word to form a matrix
#for example 1 data will get compare with rest all the data
similarity = cosine_similarity(vectors)

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=80331bd64f3a6016aca9c58aa09fd113&language=en-US'.format(movie_id))
    data = response.json()
    print(data)
    return 'https://image.tmdb.org/t/p/w500/' + data['poster_path']


def recommend(movie):
    movie_index = new_df[new_df['title'] == movie].index[0]
    #all the distances list of similarity
    distances = similarity[movie_index]

    #sort the list of distance in decending order without losing it's index using enumerate function
    #from 2 item to 6th item as 1st item is movie itself
    movie_list = sorted(list(enumerate(distances)),reverse=True, key=lambda x:x[1])[1:6]

    recommended_movies = []
    recommended_poster = []

    for i in movie_list:
        movie_id = new_df.iloc[i[0]].movie_id

        recommended_movies.append(new_df.iloc[i[0]].title)
        recommended_poster.append(fetch_poster(movie_id))

    return recommended_movies, recommended_poster




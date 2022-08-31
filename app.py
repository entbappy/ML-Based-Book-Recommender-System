import os
import sys
import pickle
import streamlit as st
import requests
import numpy as np
from books_recommender_app_logger.logger import logging
from books_recommender_app_configuration.configuration import AppConfiguration
from books_recommender_app_pipeline.training_pipeline import TrainingPipeline
from books_recommender_app_exception.exception_handler import AppException


class Recommendation:
    def __init__(self,app_config = AppConfiguration()):
        try:
            self.recommendation_config= app_config.get_recommendation_config()
            self.book_name =  pickle.load(open(self.recommendation_config.book_name_serialized_objects,'rb'))
            self.book_pivot =  pickle.load(open(self.recommendation_config.book_pivot_serialized_objects,'rb'))
            self.final_rating =  pickle.load(open(self.recommendation_config.final_rating_serialized_objects,'rb'))
            self.model = pickle.load(open(self.recommendation_config.trained_model_path,'rb'))
        except Exception as e:
            raise AppException(e, sys) from e


    def fetch_poster(self,suggestion):
        try:
            book_name = []
            ids_index = []
            poster_url = []

            for book_id in suggestion:
                book_name.append(self.book_pivot.index[book_id])

            for name in book_name[0]: 
                ids = np.where(self.final_rating['title'] == name)[0][0]
                ids_index.append(ids)

            for idx in ids_index:
                url = self.final_rating.iloc[idx]['image_url']
                poster_url.append(url)

            return poster_url
        
        except Exception as e:
            raise AppException(e, sys) from e
        


    def recommend_book(self,book_name):
        try:
            books_list = []
            book_id = np.where(self.book_pivot.index == book_name)[0][0]
            distance, suggestion = self.model.kneighbors(self.book_pivot.iloc[book_id,:].values.reshape(1,-1), n_neighbors=6 )

            poster_url = self.fetch_poster(suggestion)
            
            for i in range(len(suggestion)):
                    books = self.book_pivot.index[suggestion[i]]
                    for j in books:
                        books_list.append(j)
            return books_list , poster_url   
        
        except Exception as e:
            raise AppException(e, sys) from e


    def train_engine(self):
        try:
            obj = TrainingPipeline()
            obj.start_training_pipeline()
            st.text("Training Completed!")
            logging.info(f"Recommended successfully!")
        except Exception as e:
            raise AppException(e, sys) from e

    
    def recommendations_engine(self,selected_books):
        try:
            recommended_books,poster_url = self.recommend_book(selected_books)
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.text(recommended_books[1])
                st.image(poster_url[1])
            with col2:
                st.text(recommended_books[2])
                st.image(poster_url[2])

            with col3:
                st.text(recommended_books[3])
                st.image(poster_url[3])
            with col4:
                st.text(recommended_books[4])
                st.image(poster_url[4])
            with col5:
                st.text(recommended_books[5])
                st.image(poster_url[5])
        except Exception as e:
            raise AppException(e, sys) from e



if __name__ == "__main__":
    st.header('ML Based Books Recommender System')
    st.text("This is a collaborative filtering based recommendation system!")

    obj = Recommendation()

    selected_books = st.selectbox(
        "Type or select a book from the dropdown",
        obj.book_name)


    #Training
    if st.button('Train Recommender System'):
        obj.train_engine()
    
    #recommendation
    if st.button('Show Recommendation'):
        obj.recommendations_engine(selected_books)

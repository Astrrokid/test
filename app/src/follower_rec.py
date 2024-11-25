import numpy as np
import pandas as pd
import json
import sklearn
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder
import psycopg2
import random

class FollowerReccomendation():
    def __init__(self, table_name='accounts_following'):
        # Connection parameters
        host = 'aws-0-eu-central-1.pooler.supabase.com'
        dbname = 'postgres'
        user = 'postgres.ecdxmmbintgqxnwguhua'
        password = 'Ypp2NTj7hGskPbm1'

        # Establish connection
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password
        )

        # Query and read data
        query = f"SELECT * FROM {table_name};"
        self.df = pd.read_sql(query, conn)
        conn.close()

    def get_dataframes_ready(self):
        self.df= self.df[self.df['deleted']==False][['user_id','following_id']]

        popularity = self.df['following_id'].value_counts()
        popularity = pd.DataFrame(popularity).reset_index()
        popularity.columns = ['following_id', 'count']

        popularity['average_popularity'] =popularity['count']/ popularity['count'].sum()

        v= popularity['count']
        R = popularity['average_popularity']
        C = popularity['average_popularity'].mean()
        m = popularity['count'].quantile(0.9)

        popularity['weighted_average'] = ((R*v + C*m) / (v+m))

        self.df = pd.merge(self.df,popularity, on='following_id', how='left')

        self.user_follow_matrix = self.df.pivot_table(index='user_id', columns='following_id', aggfunc='size', fill_value=0)


        # Compute the cosine similarity matrix
        user_similarity = cosine_similarity(self.user_follow_matrix)
        self.user_similarity_df = pd.DataFrame(user_similarity, index=self.user_follow_matrix.index, columns=self.user_follow_matrix.index)

    def get_recommendations(self, user_id, top_n=5):
        # Find the most similar users to the given user (excluding self-similarity)
        similar_users = self.user_similarity_df[user_id].sort_values(ascending=False).drop(user_id)
        user_ratings = self.user_follow_matrix.loc[user_id]
        weighted_scores = self.user_follow_matrix.loc[similar_users.index].T @ similar_users
        recommendations = weighted_scores[user_ratings == 0].sort_values(ascending=False)
        # Convert to a list and shuffle
        recommendations_list = list(recommendations.index)
        recommendations_list = [uid for uid in recommendations_list if uid != user_id]
        recommendations_list = recommendations_list[:top_n]
        random.shuffle(recommendations_list)
        return recommendations_list


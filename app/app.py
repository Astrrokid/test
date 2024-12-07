from flask import Flask, request, jsonify
import pandas as pd
import sys
import os
import random
from datetime import datetime, timedelta, timezone
from exception import CustomException
from src.follower_rec import FollowerReccomendation
from src.cat_reccomendation import CatetgoryReccomendation

app = Flask(__name__)

# def recommend_for_user(df,user_id, user_follow_matrix,top_n, user_similarity_df=None):
#     recommendations = get_recommendations(user_id,user_follow_matrix, user_similarity_df,top_n)
#     return recommendations

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_api():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        top_n = data.get("top_n", 5)

        recommend = FollowerReccomendation()
        recommend.get_dataframes_ready()
        recommendations= recommend.get_recommendations(user_id,top_n)
        return jsonify({"recommendations": recommendations})

    except Exception as e:
        raise CustomException(e,sys)
@app.route('/cat_suggestion', methods=['POST'])
def get_cat_suggestion_api():
    try:
        data = request.get_json()
        job_title = data.get("job_title")
        top_k = data.get("top_k", 6)

        cat_rec = CatetgoryReccomendation()
        suggestions = cat_rec.get_similar_categories(job_title)
        return jsonify({"suggestions": suggestions[0]})

    except Exception as e:
        raise CustomException(e,sys)
# Run the Flask app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port)


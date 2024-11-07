from flask import Flask, request, jsonify
import pandas as pd
import random
from datetime import datetime, timedelta, timezone
app = Flask(__name__)

# Load default matrices from JSON files at startup
try:
    default_user_follow_matrix = pd.read_json("user_follow_popularity_matrix.json", orient='split')
    default_user_similarity_matrix = pd.read_json("user_similarity_df.json", orient='split')
    default_df = pd.read_json("df.json", orient='split')
except Exception as e:
    print(f"Error loading default matrices: {e}")

# Define the function to check if a user is new based on `date_joined`
def is_new_user(df, user_id, days_threshold=1):
    # Check if 'date_joined' column exists
    if 'date_joined' not in df.columns:
        raise KeyError("The column 'date_joined' is not found in the DataFrame.")
    
    # Ensure user_id exists
    if user_id not in df['user_id'].values:
        print(f"User ID {user_id} not found.")
        return False
    
    # Get the user's joined date
    user_joined_date = df[df['user_id'] == user_id]['date_joined'].values[0]
    
    # Convert to datetime if necessary
    if isinstance(user_joined_date, str):
        user_joined_date = pd.to_datetime(user_joined_date, errors='coerce')
    
    # Check for invalid dates
    if pd.isnull(user_joined_date):
        print(f"User ID {user_id} does not have a valid 'date_joined' value.")
        return False

    # Make both dates timezone-aware
    user_joined_date = user_joined_date.tz_localize(timezone.utc) if user_joined_date.tzinfo is None else user_joined_date
    current_date = datetime.now(timezone.utc)

    # Calculate difference from current date
    return (current_date - user_joined_date) <= timedelta(days=days_threshold)



# Recommendation function for new users based on label and views
def get_recommendations_by_user_id(df, user_id, top_n_users=5):
    if user_id not in df['user_id'].values:
        print(f"User ID {user_id} not found.")
        return pd.DataFrame()
    user_label = df[df['user_id'] == user_id]['label'].values[0]
    label_users = df[df['label'] == user_label]
    label_users = label_users[label_users['user_id'] != user_id]
    top_users = label_users.sort_values(by='views', ascending=False).head(top_n_users)
    return top_users[['user_id', 'label', 'views']]


# Recommendation function
def get_recommendations(user_id, user_follow_matrix, user_similarity_matrix, top_n=5):
    # Find the most similar users to the given user (excluding self-similarity)
    similar_users = user_similarity_matrix[user_id].sort_values(ascending=False).drop(user_id)
    user_ratings = user_follow_matrix.loc[user_id]
    weighted_scores = user_follow_matrix.loc[similar_users.index].T @ similar_users
    recommendations = weighted_scores[user_ratings == 0].sort_values(ascending=False)
    # Convert to a list and shuffle
    recommendations_list = list(recommendations.index)
    recommendations_list = [uid for uid in recommendations_list if uid != user_id]
    recommendations_list = recommendations_list[:top_n]
    random.shuffle(recommendations_list)
    return recommendations_list


# Example of checking if a user is new and selecting the recommendation method
def recommend_for_user(df,user_id, user_follow_matrix,top_n, user_similarity_df=None):
    if is_new_user(df, user_id):
        print(f"User ID {user_id} is a new user. Using label-based recommendation.")
        recommendations = get_recommendations_by_user_id(df, user_id)
        if recommendations.empty:
            return
    else:
        print(f"User ID {user_id} is a existing user. Using similarity-based recommendation.")
        recommendations = get_recommendations(user_id,user_follow_matrix, user_similarity_df,top_n)
        return recommendations
# API endpoint to get recommendations
@app.route('/recommend_for_user', methods=['POST'])
def get_recommendations_api():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        top_n = data.get("top_n", 5)

        # Load matrices from JSON if provided, otherwise use defaults
        user_follow_matrix_data = data.get("user_follow_matrix_data", default_user_follow_matrix.to_dict())
        user_similarity_matrix_data = data.get("user_similarity_matrix_data", default_user_similarity_matrix.to_dict())
        df_data = data.get("df", default_df.to_dict())
        # Convert to DataFrames
        user_follow_matrix = pd.DataFrame(user_follow_matrix_data)
        user_similarity_matrix = pd.DataFrame(user_similarity_matrix_data)
        df = pd.DataFrame(df_data)

        # Generate recommendations
        recommendations = recommend_for_user(df, user_id, user_follow_matrix, top_n, user_similarity_matrix)
        return jsonify({"recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 400
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

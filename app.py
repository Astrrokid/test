from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load default matrices from JSON files at startup
try:
    default_user_follow_matrix = pd.read_json("user_follow_popularity_matrix.json", orient='split')
    default_user_similarity_matrix = pd.read_json("user_similarity_df.json", orient='split')
except Exception as e:
    print(f"Error loading default matrices: {e}")

# Recommendation function
def get_recommendations(user_id, user_follow_matrix, user_similarity_matrix, top_n=3):
    # Find the most similar users to the given user (excluding self-similarity)
    similar_users = user_similarity_matrix[user_id].sort_values(ascending=False).drop(user_id)
    user_ratings = user_follow_matrix.loc[user_id]
    weighted_scores = user_follow_matrix.loc[similar_users.index].T @ similar_users
    recommendations = weighted_scores[user_ratings == 0].sort_values(ascending=False)
    return list(recommendations.head(top_n).index)

# API endpoint to get recommendations
@app.route('/get_recommendations', methods=['POST'])
def get_recommendations_api():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        top_n = data.get("top_n", 3)

        # Load matrices from JSON if provided, otherwise use defaults
        user_follow_matrix_data = data.get("user_follow_matrix_data", default_user_follow_matrix.to_dict())
        user_similarity_matrix_data = data.get("user_similarity_matrix_data", default_user_similarity_matrix.to_dict())
        
        # Convert to DataFrames
        user_follow_matrix = pd.DataFrame(user_follow_matrix_data)
        user_similarity_matrix = pd.DataFrame(user_similarity_matrix_data)

        # Generate recommendations
        recommendations = get_recommendations(user_id, user_follow_matrix, user_similarity_matrix, top_n)
        return jsonify({"recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

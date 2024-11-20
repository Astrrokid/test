# Recommendation System API

This repository implements a **Recommendation System API** using Flask, designed to provide personalized recommendations based on user activity and similarity metrics. The system supports dynamic handling of **new users** (label-based recommendations) and **existing users** (similarity-based recommendations).

---

## Features

- **User Categorization**: Distinguishes between new and existing users based on their `date_joined`.
- **Dynamic Recommendations**:
  - **New Users**: Recommendations are based on user labels and views.
  - **Existing Users**: Recommendations use a similarity matrix and user-follow popularity data.
- **Configurable API**: Accepts user-provided or default datasets for flexibility.
- **Error Handling**: Provides detailed error messages for invalid inputs.

---

## API Endpoints

### `POST /recommend_for_user`
Generates recommendations for a given user.
[https://test-two-omega-22.vercel.app/recommend_for_user](https://test-two-omega-22.vercel.app/recommend_for_user)

#### Request Body
```json
{
  "user_id": 1853, 
  "top_n": 5
}

#### Response Body
```json
{
  "recommendations": [101, 102, 103, 104, 105]
}

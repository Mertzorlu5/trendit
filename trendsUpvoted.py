import streamlit as st
import praw
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('USER_AGENT'),
)

def get_posts(subreddit, post_type, number_of_posts=20):
    subreddit_chosen = reddit.subreddit(subreddit)
    posts = {
        "New Posts": subreddit_chosen.new,
        "Top Posts": subreddit_chosen.top,
        "Hot Posts": subreddit_chosen.hot,
        "Rising Posts": subreddit_chosen.rising
    }.get(post_type, subreddit_chosen.hot)(limit=number_of_posts)

    post_data = []
    for post in posts:
        post_data.append({
            "Title": post.title,
            "Score": post.score,
            "Subreddit": subreddit,
            "URL": post.url
        })

    return pd.DataFrame(post_data)

# Streamlit UI
st.title('Reddit Trend Analyzer')

with st.sidebar:
    subreddits = st.text_input('Subreddits (comma-separated)')
    post_type = st.selectbox('Choose Post Type', ["New Posts", "Top Posts", "Hot Posts", "Rising Posts"])
    fetch_button = st.button('Fetch Data')

if fetch_button and subreddits:
    subreddit_list = subreddits.split(',')
    all_posts = pd.DataFrame()

    for subreddit in subreddit_list:
        posts = get_posts(subreddit.strip(), post_type)
        all_posts = pd.concat([all_posts, posts], ignore_index=True)

    st.dataframe(all_posts)

    # Aggregating scores for each subreddit
    subreddit_scores = all_posts.groupby('Subreddit')['Score'].sum().reset_index()

    # Sorting values for better visualization
    subreddit_scores = subreddit_scores.sort_values(by='Score', ascending=False)

    # Visualization: Bar chart of cumulative upvotes for each subreddit
    st.subheader("Cumulative Upvotes for Each Subreddit")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=subreddit_scores, x='Subreddit', y='Score')
    plt.title('Which Sub Has Most Upvoted Questions/Topics')
    plt.xlabel('Subreddit')
    plt.ylabel('Total Upvotes')
    plt.xticks(rotation=45)
    st.pyplot(plt)

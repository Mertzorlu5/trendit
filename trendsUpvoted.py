import streamlit as st
import praw
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


secrets = st.secrets

reddit = praw.Reddit(
    client_id=secrets["REDDIT_CLIENT_ID"],
    client_secret=secrets["REDDIT_CLIENT_SECRET"],
    user_agent=secrets["USER_AGENT"]

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

def get_online_members(subreddit):
    subreddit_chosen = reddit.subreddit(subreddit)
    try:
        return subreddit_chosen.active_user_count
    except AttributeError:
        return None

st.title('Reddit Trend Analyzer')

with st.sidebar:
    subreddits = st.text_input('Subreddits (comma-separated)')
    post_type = st.selectbox('Choose Post Type', ["New Posts", "Top Posts", "Hot Posts", "Rising Posts"])
    fetch_button = st.button('Fetch Data')

if fetch_button and subreddits:
    subreddit_list = subreddits.split(',')
    all_posts = pd.DataFrame()
    online_data = []

    for subreddit in subreddit_list:
        posts = get_posts(subreddit.strip(), post_type)
        all_posts = pd.concat([all_posts, posts], ignore_index=True)

        online_count = get_online_members(subreddit.strip())
        if online_count is not None:
            online_data.append({'Subreddit': subreddit, 'Online Users': online_count})

    # Display posts data
    st.dataframe(all_posts)

    # Visualization 1: Cumulative upvotes for each subreddit
    st.subheader("Cumulative Upvotes for Each Subreddit")
    subreddit_scores = all_posts.groupby('Subreddit')['Score'].sum().reset_index()
    subreddit_scores = subreddit_scores.sort_values(by='Score', ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=subreddit_scores, x='Subreddit', y='Score')
    plt.title('Which Subreddit Has Most Upvoted Questions/Topics')
    plt.xlabel('Subreddit')
    plt.ylabel('Total Upvotes')
    plt.xticks(rotation=45)
    st.pyplot(plt)

    # Visualization 2: Current online users in each subreddit
    if online_data:
        st.subheader("Current Online Users in Subreddits")
        df_online = pd.DataFrame(online_data)
        plt.figure(figsize=(10, 6))
        plt.bar(df_online['Subreddit'], df_online['Online Users'], color='skyblue')
        plt.xlabel('Subreddit')
        plt.ylabel('Online Users')
        plt.title('Current Online Users in Selected Subreddits')
        plt.xticks(rotation=45)
        st.pyplot(plt)
    else:
        st.write("No online user data available for the selected subreddits.")


#Tiktokhelp,TikTokAds,dropshipping, ecommerce, ecommercemarketing, ecommerce,AmazonSeller,TikTok,eBaySellers,eBaySellerAdvice,FulfillmentByAmazon,Etsy,woocommerce,shopify,DropShipping101,Dropshipping_Guide

#when you are deploying on streamlit there's a advanced settings section put your keys there.
#instead of loadevn theres a different way to load secret keys st.secrets etc..
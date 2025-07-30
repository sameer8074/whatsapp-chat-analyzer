import numpy as np
import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_files = st.sidebar.file_uploader("Choose files", accept_multiple_files=True)

if uploaded_files:
    dfs = []  # List to store dataframes from multiple files

    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8", errors="ignore")  # Decode file
        df = preprocessor.preprocess(data)  # Preprocess chat data

        if not df.empty:
            df["source_file"] = uploaded_file.name  # Track source file
            dfs.append(df)
        else:
            st.warning(f"⚠️ {uploaded_file.name} resulted in an empty DataFrame!")

    if dfs:
        df = pd.concat(dfs, ignore_index=True)  # Merge all files into one dataframe
        st.dataframe(df)

        # fetch unique users
        user_list = df['user'].unique().tolist()
        user_list.sort()
        user_list.insert(0, "Overall")

        selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

        if st.sidebar.button("Show Analysis"):
            # Stats Area
            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4, gap="medium")

            with col1:
                st.header("Total Messages")
                st.title(num_messages)
            with col2:
                st.header("Total Words")
                st.title(words)
            with col3:
                st.header("Media Shared")
                st.title(num_media_messages)
            with col4:
                st.header("Links Shared")
                st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1,col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user,df)
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user,df)
        fig,ax = plt.subplots()
        if user_heatmap.empty:
            st.warning("No activity data available to generate a heatmap.")
        else:
            ax = sns.heatmap(user_heatmap)


        # Finding the busiest users per file
        if selected_user == 'Overall':
            st.title('Most Busy Users (Per File)')

    # Loop through each file and show busy users separately
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_df = df[df['source_file'] == file_name]

        st.subheader(f"📄 {file_name}")
        x, new_df = helper.most_busy_users(file_df)

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            ax.bar(x.index, x.values, color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.dataframe(new_df)

    # Overall most busy users across all files
    st.title('Overall Top 10 Busy Users')
    overall_x, overall_df = helper.most_busy_users(df)

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.bar(overall_x.index, overall_x.values, color='red')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
    with col2:
        st.dataframe(overall_df)

    # WordCloud
    st.title("Wordcloud")
    df_wc = helper.create_wordcloud(selected_user, df)
    if df_wc:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(df_wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("⚠️ No words found to generate WordCloud. Try another user or dataset.")
        # most common words
        most_common_df = helper.most_common_words(selected_user,df)

        fig,ax = plt.subplots()

        ax.barh(most_common_df[0],most_common_df[1])
        plt.xticks(rotation='vertical')

        st.title('Most commmon words')
        st.pyplot(fig)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")


        col1,col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")
            st.pyplot(fig)
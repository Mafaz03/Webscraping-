import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_date_with_highlight(dataframe, start_date, end_date, median_relevance, top_n, show=True):
    # Convert 'Date' column to datetime
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    dataframe['Year'] = dataframe['Date'].dt.year

    # Create figure and axes with improved readability
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot Date Distribution with clearer labels and colors
    axes[0, 0].hist(dataframe['Date'], bins=30, color='#1f77b4', edgecolor='black', alpha=0.7, label='Date Distribution')
    axes[0, 0].set_title('Date Distribution', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Date', fontsize=12)
    axes[0, 0].set_ylabel('Frequency', fontsize=12)
    axes[0, 0].grid(axis='y', linestyle='--', alpha=0.5)
    axes[0, 0].legend()

    # Highlight the selected date range with more visible color
    axes[0, 0].axvspan(pd.to_datetime(start_date), pd.to_datetime(end_date), color='#ff7f0e', alpha=0.3, label='Selected Range')
    axes[0, 0].legend()

    # Plot Year Distribution with clearer pie chart
    year_counts = dataframe['Year'].value_counts()
    axes[0, 1].pie(year_counts, labels=year_counts.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
    axes[0, 1].set_title(f'Year Distribution\n({start_date} to {end_date})', fontsize=14, fontweight='bold')
    axes[0, 1].legend()

    # Add Median Relevance text
    axes[1, 0].text(0.5, 0.5, f'Median Relevance: {median_relevance}', fontsize=18, ha='center', fontweight='bold')
    axes[1, 0].axis('off')

    # Display Top URLs Pie Chart
    website_counts = dataframe['url'].apply(lambda x: x.split('/')[2] if pd.notnull(x) else 'Unknown').value_counts()
    axes[1, 1].pie(website_counts, labels=website_counts.index, autopct='%1.1f%%', startangle=90)
    axes[1, 1].set_title('Distribution of URLs from Different Websites', fontsize=14, fontweight='bold')
    axes[1, 1].axis('equal')
    axes[1, 1].legend()

    plt.tight_layout()

    if show:
        plt.show()

def med_relevance(df, top_n):
    # Display the top URLs based on relevance score
    top_urls = df.nlargest(top_n, 'Relevance_Score')[['url', 'Relevance_Score']]
    
    # Calculate the median relevance score
    median_relevance = np.median(top_urls['Relevance_Score'])
    
    return round(median_relevance, 2)

def dashboard(url_date_df, url_html_score_df, start_date, end_date, top_n, save_path='dashboard/dashboard_plot.png'):
    # Calculate median relevance
    median_relevance = med_relevance(url_html_score_df, top_n)
    
    # Plot Date Distribution, Year Distribution, Median Relevance, and Top URLs Pie Chart
    plot_date_with_highlight(url_date_df, start_date, end_date, median_relevance, top_n, show=False)
    
    # Save the plot as PNG
    plt.savefig(save_path)

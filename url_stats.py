import pandas as pd
import matplotlib.pyplot as plt

def plot_date(dataframe, save_path=None):
    
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    dataframe['Year'] = dataframe['Date'].dt.year
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    ax1.hist(dataframe['Date'], bins=30, color='skyblue', edgecolor='black')
    ax1.set_title('Date Distribution')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Frequency')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    year_counts = dataframe['Year'].value_counts()
    ax2.pie(year_counts, labels=year_counts.index, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax2.set_title('Year Distribution')

    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

# Example usage:
# Assuming df is your DataFrame
# plot_date(df, save_path='path/to/save/figure.png')

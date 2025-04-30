"""
Visualization functions for earnings call analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_sentiment_by_company(df, sentiment_column='sentiment_compound', 
                              output_path=None):
    """Plot average sentiment by company."""
    plt.figure(figsize=(12, 6))
    avg_sentiment = df.groupby('ticker')[sentiment_column].mean().sort_values()
    avg_sentiment.plot(kind='bar', color='cornflowerblue')
    plt.title('Average Sentiment by Company')
    plt.ylabel('Sentiment Score')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()

def plot_sentiment_returns_correlation(df, sentiment_column='sentiment_compound',
                                      returns_column='post_week_return',
                                      output_path=None):
    """Plot correlation between sentiment and returns."""
    plt.figure(figsize=(12, 8))

    for ticker in df['ticker'].unique():
        company_data = df[df['ticker'] == ticker]
        plt.scatter(company_data[sentiment_column], 
                   company_data[returns_column], 
                   label=ticker, alpha=0.7)

    plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)
    plt.axvline(x=0, color='r', linestyle='--', alpha=0.3)
    plt.title('Sentiment vs. Returns')
    plt.xlabel('Sentiment Score')
    plt.ylabel('Return (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
        plt.close()
    else:
        plt.show()
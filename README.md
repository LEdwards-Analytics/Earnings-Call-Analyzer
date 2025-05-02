# Earnings Call Analyzer

A pipeline for analyzing earnings call transcripts and surfacing sentiment trends, financial tone, and potential links to stock performance.

## Overview

This project collects and processes earnings call transcripts from major companies, applies sentiment and language analysis, and correlates the results with stock movements over time.

It’s modular and designed to be extensible, with plans to integrate Power BI dashboards and more advanced NLP models for deeper insights.

## Project Structure

- `notebooks/`: Jupyter notebooks for analysis
- `earnings_call_analyzer/`: Python package with core functionality
- `data/`: Raw and processed data files
- `config.py`: Central configuration
- `run_pipeline.py`: Script to run the entire analysis pipeline

## Notebook Execution Order

1. `transcript_collection.ipynb` - Downloads earnings call transcripts
2. `data_cleaning.ipynb` - Cleans and preprocesses the transcripts
3. `enhanced_sentiment.ipynb` - Performs financial-specific sentiment analysis
4. `data_visualization.ipynb` - Creates stock correlation visualizations
5. `sec_visualization.ipynb` - Analyzes SEC filing data
6. `summary_visualizations.ipynb` - Generates the executive summary visualizations

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Earnings-Call-Analyzer.git
cd Earnings-Call-Analyzer

# Install dependencies
pip install -r requirements.txt
pip install -e .  # Install the package in development mode

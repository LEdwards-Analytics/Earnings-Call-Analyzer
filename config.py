import os

# Base directory - adjust as needed
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")
RAW_DIR = os.path.join(DATA_DIR, "raw_filings")

# Output directories
ENHANCED_VIZ_DIR = os.path.join(OUTPUT_DIR, "enhanced_sentiment_viz")
STOCK_CORR_DIR = os.path.join(OUTPUT_DIR, "stock_correlation")
EXEC_SUMMARY_DIR = os.path.join(OUTPUT_DIR, "executive_summary")
SEC_FILINGS_DIR = os.path.join(OUTPUT_DIR, "sec_filings")

# Ensure all directories exist
for dir_path in [DATA_DIR, LOGS_DIR, OUTPUT_DIR, TRANSCRIPTS_DIR, 
                ENHANCED_VIZ_DIR, STOCK_CORR_DIR, EXEC_SUMMARY_DIR,
                SEC_FILINGS_DIR, RAW_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Data files
CLEANED_TRANSCRIPTS = os.path.join(DATA_DIR, "cleaned_transcripts.csv")
TRANSCRIPT_METADATA = os.path.join(DATA_DIR, "transcript_metadata.csv")

# SEC API settings
USER_AGENT = "Luke Edwards luke3dwards32@gmail.com"
SEC_DELAY = 3  # Seconds to wait between SEC API calls
SEC_MAX_RETRIES = 3  # Maximum number of retries for SEC API calls

# List of companies we want to collect data for
COMPANIES = [
    # Technology companies
    {"ticker": "AAPL", "cik": "0000320193", "name": "Apple Inc."},
    {"ticker": "MSFT", "cik": "0000789019", "name": "Microsoft Corporation"},
    {"ticker": "GOOGL", "cik": "0001652044", "name": "Alphabet Inc."},
    {"ticker": "AMZN", "cik": "0001018724", "name": "Amazon.com Inc."},
    {"ticker": "META", "cik": "0001326801", "name": "Meta Platforms Inc."},
    {"ticker": "TSLA", "cik": "0001318605", "name": "Tesla Inc."},
    {"ticker": "NVDA", "cik": "0001045810", "name": "NVIDIA Corporation"},
    {"ticker": "NFLX", "cik": "0001065280", "name": "Netflix Inc."},
    # Add other companies...
]

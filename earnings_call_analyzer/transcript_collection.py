"""Functions for collecting earnings call transcripts."""
import os
import re
import time
import random
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
from pathlib import Path
from urllib.parse import quote

# Set up logger
logger = logging.getLogger(__name__)

# User agent rotation list for avoiding detection
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/99.0.1150.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
]

# SEC API configuration
BASE_URL = "https://www.sec.gov/Archives/edgar/data"

def get_random_user_agent():
    """Get a random user agent from the list."""
    return random.choice(USER_AGENTS)

def get_scraping_headers():
    """Get headers for web scraping that appear more browser-like."""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.google.com/"
    }

def wait_with_jitter(base_seconds=10):
    """Wait with jitter to avoid rate limiting."""
    jitter = random.uniform(0, 5)  # Random jitter up to 5 seconds
    wait_time = base_seconds + jitter
    logger.info(f"Waiting {wait_time:.2f}s before next request (jitter: {jitter:.2f}s)")
    time.sleep(wait_time)

def get_seeking_alpha_transcript(ticker, quarter_date):
    """Scrape Seeking Alpha for earnings call transcript"""
    try:
        logger.info(f"Attempting to get {ticker} transcript from Seeking Alpha for {quarter_date}")
        # Format date as YYYY-MM-DD
        date_str = quarter_date['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        # Calculate quarter based on the month
        quarter = f"Q{(date_obj.month - 1) // 3 + 1} {date_obj.year}"
        logger.info(f"Looking for {ticker} {quarter} transcript")

        # Search for the transcript on Seeking Alpha with random user agent
        search_url = f"https://seekingalpha.com/symbol/{ticker}/earnings/transcripts"
        wait_with_jitter()

        headers = get_scraping_headers()
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to access Seeking Alpha: {response.status_code}")
            return None

        # Parse the search results
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for transcript links - this pattern may need adjusting based on Seeking Alpha's current HTML structure
        transcript_links = soup.select("a[href*='earnings-call-transcript']")
        if not transcript_links:
            logger.warning(f"No transcript links found for {ticker}")
            return None

        # Find the matching quarter transcript
        transcript_url = None
        for link in transcript_links:
            link_text = link.text.strip()
            if quarter.lower() in link_text.lower() and "earnings call" in link_text.lower():
                transcript_url = "https://seekingalpha.com" + link['href']
                logger.info(f"Found transcript URL: {transcript_url}")
                break

        if not transcript_url:
            logger.warning(f"Could not find {quarter} transcript for {ticker}")
            return None

        # Get the transcript content with a different random user agent
        wait_with_jitter()
        headers = get_scraping_headers()
        transcript_response = requests.get(transcript_url, headers=headers)
        if transcript_response.status_code != 200:
            logger.error(f"Failed to access transcript page: {transcript_response.status_code}")
            return None

        # Extract the content
        transcript_soup = BeautifulSoup(transcript_response.text, 'html.parser')

        # The article content may be in different selectors depending on Seeking Alpha's layout
        # Try a few common selectors
        content_selectors = [
            "div.sa-art__body", 
            "div#content-rail", 
            "div.transcript-body",
            "article",
            "div[data-test-id='content-container']"
        ]

        transcript_text = None
        for selector in content_selectors:
            content = transcript_soup.select_one(selector)
            if content:
                transcript_text = content.get_text(separator="\n").strip()
                break

        if not transcript_text:
            logger.warning(f"Could not extract transcript content for {ticker}")
            return None

        # Clean up the text
        transcript_text = re.sub(r'\s+', ' ', transcript_text)

        logger.info(f"Successfully extracted {ticker} {quarter} transcript ({len(transcript_text)} chars)")
        return {
            'text': transcript_text,
            'source': 'seeking_alpha',
            'url': transcript_url,
            'quarter': quarter
        }

    except Exception as e:
        logger.error(f"Error getting Seeking Alpha transcript for {ticker}: {str(e)}")
        return None

def get_yahoo_finance_transcript(ticker, quarter_date):
    """Try to get transcript from Yahoo Finance"""
    try:
        logger.info(f"Attempting to get {ticker} transcript from Yahoo Finance for {quarter_date}")
        date_str = quarter_date['date']

        # Yahoo Finance uses a different URL structure
        search_url = f"https://finance.yahoo.com/quote/{ticker}/analysts?p={ticker}"
        wait_with_jitter()

        headers = get_scraping_headers()
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to access Yahoo Finance: {response.status_code}")
            return None

        # Parse HTML to find earnings call page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for links to earnings calls
        earnings_links = []
        for a in soup.find_all('a', href=True):
            if 'earnings-call' in a['href']:
                earnings_links.append(a['href'])

        if not earnings_links:
            logger.warning(f"No earnings call links found for {ticker} on Yahoo Finance")
            return None

        # Get the most recent earnings call
        call_url = "https://finance.yahoo.com" + earnings_links[0]
        wait_with_jitter()

        headers = get_scraping_headers()
        call_response = requests.get(call_url, headers=headers)
        if call_response.status_code != 200:
            logger.error(f"Failed to access earnings call page: {call_response.status_code}")
            return None

        # Extract the transcript
        call_soup = BeautifulSoup(call_response.text, 'html.parser')
        transcript_div = call_soup.select_one("div.caas-body")

        if not transcript_div:
            logger.warning(f"Could not find transcript content for {ticker} on Yahoo Finance")
            return None

        transcript_text = transcript_div.get_text(separator="\n").strip()

        # Try to extract quarter info from the transcript text
        quarter_pattern = r'Q[1-4]\s+\d{4}'
        quarter_match = re.search(quarter_pattern, transcript_text)
        quarter = quarter_match.group(0) if quarter_match else ""

        logger.info(f"Successfully extracted {ticker} transcript from Yahoo Finance ({len(transcript_text)} chars)")
        return {
            'text': transcript_text,
            'source': 'yahoo_finance',
            'url': call_url,
            'quarter': quarter
        }

    except Exception as e:
        logger.error(f"Error getting Yahoo Finance transcript for {ticker}: {str(e)}")
        return None

def get_company_ir_transcript(company, quarter_date, ir_urls):
    """Try to get transcript from company investor relations website"""
    try:
        ticker = company['ticker']
        if ticker not in ir_urls:
            logger.warning(f"No IR URL defined for {ticker}")
            return None

        logger.info(f"Attempting to get {ticker} transcript from IR website for {quarter_date}")

        # Get IR URL
        ir_url = ir_urls[ticker]
        wait_with_jitter()

        headers = get_scraping_headers()

        # Each company has a different IR site structure, so we need custom handling
        if ticker == "AAPL":
            # Apple specific
            response = requests.get(ir_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for earnings links
            for link in soup.find_all('a'):
                if 'earnings' in link.text.lower() and 'conference call' in link.text.lower():
                    transcript_url = "https://investor.apple.com" + link['href'] if link['href'].startswith('/') else link['href']

                    # Get transcript page
                    wait_with_jitter()
                    transcript_response = requests.get(transcript_url, headers=get_scraping_headers())
                    transcript_soup = BeautifulSoup(transcript_response.text, 'html.parser')

                    # Extract content
                    content_div = transcript_soup.select_one("div.textSection")
                    if content_div:
                        transcript_text = content_div.get_text(separator="\n").strip()

                        # Try to extract quarter info from title or content
                        quarter_pattern = r'Q[1-4]\s+\d{4}'
                        quarter_match = re.search(quarter_pattern, transcript_soup.title.text if transcript_soup.title else "")
                        if not quarter_match:
                            quarter_match = re.search(quarter_pattern, transcript_text)
                        quarter = quarter_match.group(0) if quarter_match else ""

                        return {
                            'text': transcript_text,
                            'source': 'company_ir',
                            'url': transcript_url,
                            'quarter': quarter
                        }

        elif ticker == "MSFT":
            # Microsoft specific
            response = requests.get(ir_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for earnings webcast links
            for link in soup.find_all('a'):
                if 'earnings' in link.text.lower() and ('webcast' in link.text.lower() or 'call' in link.text.lower()):
                    transcript_url = link['href']

                    # Get transcript page
                    wait_with_jitter()
                    transcript_response = requests.get(transcript_url, headers=get_scraping_headers())
                    transcript_soup = BeautifulSoup(transcript_response.text, 'html.parser')

                    # Extract content
                    content_div = transcript_soup.select_one("div.webcast-text, div.transcript-content")
                    if content_div:
                        transcript_text = content_div.get_text(separator="\n").strip()

                        # Try to extract quarter info
                        quarter_pattern = r'Q[1-4]\s+\d{4}'
                        quarter_match = re.search(quarter_pattern, link.text)
                        quarter = quarter_match.group(0) if quarter_match else ""

                        return {
                            'text': transcript_text,
                            'source': 'company_ir',
                            'url': transcript_url,
                            'quarter': quarter
                        }

        # Add other company handlers as in the original code

        logger.warning(f"Could not find transcript for {ticker} on IR website (no matching handler)")
        return None

    except Exception as e:
        logger.error(f"Error getting IR transcript for {ticker}: {str(e)}")
        return None

def process_company(company, output_dir, ir_urls, max_quarters=8, delay=15):
    """Process all earnings data for a company using multiple sources"""
    ticker = company['ticker']
    cik = company['cik']
    company_name = company.get('name', ticker)

    logger.info(f"=== Processing {ticker} ({company_name}, CIK: {cik}) ===")

    # Generate likely earnings dates 
    today = datetime.now()
    earnings_dates = []

    # Generate the last MAX_QUARTERS_TO_CHECK quarters
    for i in range(max_quarters):
        quarter_date = today - timedelta(days=90*i)
        quarter_num = (quarter_date.month-1)//3 + 1
        quarter_str = f"Q{quarter_num} {quarter_date.year}"

        earnings_dates.append({
            'date': quarter_date.strftime('%Y-%m-%d'),
            'description': f"Estimated {quarter_str} Earnings",
            'accession_number': f"est_{ticker}_{quarter_date.year}_{quarter_num}"
        })

    logger.info(f"Generated {len(earnings_dates)} estimated earnings dates for {ticker}")

    transcripts = []

    # For each earnings date, try to get the transcript from multiple sources
    for quarter_date in earnings_dates:
        logger.info(f"Processing earnings date: {quarter_date['date']} ({quarter_date['description']})")

        transcript_data = None

        # Try Seeking Alpha first (most reliable source for transcripts)
        transcript_data = get_seeking_alpha_transcript(ticker, quarter_date)

        # If not found on Seeking Alpha, try Yahoo Finance
        if not transcript_data:
            transcript_data = get_yahoo_finance_transcript(ticker, quarter_date)

        # If still not found, try company IR site
        if not transcript_data:
            transcript_data = get_company_ir_transcript(company, quarter_date, ir_urls)

        # If we found a transcript from any source, save it
        if transcript_data and transcript_data['text']:
            # Determine the filename
            quarter_suffix = f"_{transcript_data['quarter']}" if transcript_data['quarter'] else ""
            transcript_file = os.path.join(
                output_dir, 
                f"{ticker}_{quarter_date['date']}{quarter_suffix}_{transcript_data['source']}.txt"
            )

            # Save the transcript
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript_data['text'])

            # Add metadata about the source URL
            source_file = os.path.join(
                output_dir, 
                f"{ticker}_{quarter_date['date']}{quarter_suffix}_{transcript_data['source']}_source.txt"
            )
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(transcript_data['url'])

            # Add to list of transcripts
            transcripts.append({
                'ticker': ticker,
                'cik': cik,
                'company_name': company_name,
                'filing_date': quarter_date['date'],
                'quarter': transcript_data['quarter'],
                'transcript_file': transcript_file,
                'transcript_length': len(transcript_data['text']),
                'source': transcript_data['source'],
                'source_url': transcript_data['url']
            })

            logger.info(f"Saved {transcript_data['source']} transcript: {transcript_file} ({len(transcript_data['text'])} chars)")
        else:
            logger.warning(f"Could not find transcript for {ticker} on {quarter_date['date']}")

        # Pause between processing dates to avoid overloading servers
        wait_with_jitter(delay)

    return transcripts

def update_metadata(all_transcripts, metadata_file, base_dir):
    """Update the metadata CSV file"""
    # Skip processing if no transcripts were found
    if not all_transcripts:
        logger.info("No new transcripts found to update metadata.")
        return

    df = pd.DataFrame(all_transcripts)

    # If file exists, merge with existing data
    if os.path.exists(metadata_file):
        try:
            existing_df = pd.read_csv(metadata_file)
            # Only attempt to filter duplicates if the DataFrame is not empty
            if not df.empty and not existing_df.empty:
                # Create a unique key for each transcript
                df['unique_key'] = df['ticker'] + '_' + df['filing_date'] + '_' + df['source']
                existing_df['unique_key'] = existing_df['ticker'] + '_' + existing_df['filing_date'] + '_' + existing_df['source']

                # Remove duplicates
                existing_df = existing_df[~existing_df['unique_key'].isin(df['unique_key'])]

                # Remove the temporary keys
                existing_df = existing_df.drop('unique_key', axis=1)
                df = df.drop('unique_key', axis=1)

                # Merge the dataframes
                df = pd.concat([existing_df, df], ignore_index=True)
        except Exception as e:
            logger.error(f"Error merging with existing metadata: {str(e)}")
            # Continue with just the new data

    # Save to CSV
    df.to_csv(metadata_file, index=False)
    logger.info(f"Updated metadata file with {len(all_transcripts)} new transcripts")

    # Save update timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d")
    update_file = os.path.join(base_dir, "data", "last_update.txt")
    with open(update_file, "w") as f:
        f.write(timestamp)
    logger.info(f"Update timestamp saved: {timestamp}")

    # Print summary
    if not df.empty:
        logger.info("\nTranscripts by source:")
        logger.info(df.groupby('source').size())

        logger.info("\nTranscripts by company:")
        logger.info(df.groupby('ticker').size())

        if 'filing_date' in df.columns:
            logger.info("\nTranscripts by year/quarter:")
            df['year'] = pd.to_datetime(df['filing_date']).dt.year
            df['quarter'] = pd.to_datetime(df['filing_date']).dt.quarter
            logger.info(df.groupby(['year', 'quarter']).size())

        logger.info(f"\nTotal transcripts collected: {len(df)}")
    else:
        logger.info("\nNo transcripts collected.")

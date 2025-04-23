"""
Documentation Scraper for CodeBridge AI

This module scrapes documentation from specified sources
and saves it to the data directory.
"""

import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

class DocumentationScraper:
    def __init__(self, output_dir="../data/docs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def scrape_urls(self, urls, selector="main"):
        """
        Scrape content from a list of URLs.
        
        Args:
            urls (list): List of URLs to scrape
            selector (str): CSS selector for the main content
        """
        print(f"Scraping {len(urls)} documentation pages...")
        
        for url in tqdm(urls):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract main content using the selector
                content_element = soup.select_one(selector)
                
                if content_element:
                    content = content_element.get_text(separator="\n", strip=True)
                    
                    # Create filename from URL
                    filename = url.split('/')[-1]
                    if not filename:
                        filename = "index"
                    
                    # Save to file
                    with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"Saved {filename}.txt")
                else:
                    print(f"Could not find content with selector '{selector}' at {url}")
            
            except Exception as e:
                print(f"Error scraping {url}: {e}")


if __name__ == "__main__":
    # Example usage
    react_urls = [
        "https://react.dev/learn",
        "https://react.dev/reference/react",
        "https://react.dev/reference/react/useState",
        "https://react.dev/reference/react/useEffect",
        "https://react.dev/reference/react/Component",
    ]
    
    scraper = DocumentationScraper()
    scraper.scrape_urls(react_urls)

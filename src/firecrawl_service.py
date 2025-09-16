# import os
# from firecrawl import Firecrawl
# # from firecrawl.types import ScrapeOptions
# from dotenv import load_dotenv

# load_dotenv()

# class FirecrawlService:
#     def __init__(self):
#         api_key = os.getenv("FIRECRAWL_API_KEY")
#         if not api_key:
#             raise ValueError("Missing FIRECRAWL_API_KEY env variable")
#         self.app = Firecrawl(api_key=api_key)
    
#     def search_companies(self, query: str, num_results: int = 5):
#         try:
#             result = self.app.search(
#                 query = f"{query} company pricing",
#                 limit = num_results,
#                 # scrape_options=ScrapeOptions(
#                 #     formats=["markdown"]
#                 # )
#             )
#             return result
#         except Exception as e:
#             print(f"Error: {e}")
#             return []
    
#     def scrape_company_pages(self, url: str):
#         try:
#             result = self.app.scrape(
#                 url,
#                 formats=["markdown"]
#             )
#             return result
        
#         except Exception as e:
#             print(f"Error: {e}")
#             return None


import os
from firecrawl import Firecrawl
from dotenv import load_dotenv

load_dotenv()

class FirecrawlService:
    def __init__(self):
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("Missing FIRECRAWL_API_KEY env variable")
        self.app = Firecrawl(api_key=api_key)
    
    def search_companies(self, query: str, num_results: int = 5):
        try:
            # The 'pageOptions' parameter can be used to get markdown directly from search
            # This can sometimes save you a scrape call.
            # Example: params = {'pageOptions': {'includeHtml': False, 'includeRawHtml': False}}
            result = self.app.search(
                query = f"{query} company pricing",
                limit = num_results,
            )
            return result
        except Exception as e:
            print(f"Error during search: {e}")
            return None
    
    def scrape_company_pages(self, url: str):
        try:
            # You can add more options here if needed, e.g., pageOptions
            result = self.app.scrape(
                url=url
            )
            return result
        
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
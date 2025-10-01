import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote
import time

class WebSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_duckduckgo(self, query: str, num_results: int = 3) -> list:
        """Search DuckDuckGo and return results"""
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            response = requests.get(search_url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            # Find search result divs
            for result in soup.find_all('div', class_='result')[:num_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem:
                    title = title_elem.get_text().strip()
                    link = title_elem.get('href')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': snippet
                    })

            return results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def search_vietnamese_news(self, query: str) -> list:
        """Search Vietnamese news sources"""
        try:
            # Search on VnExpress
            vnexpress_url = f"https://vnexpress.net/search?q={quote(query)}"
            response = requests.get(vnexpress_url, headers=self.headers, timeout=10)

            results = []
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                for item in soup.find_all('div', class_='item-news')[:2]:
                    title_elem = item.find('h3', class_='title-news')
                    link_elem = item.find('a')

                    if title_elem and link_elem:
                        title = title_elem.get_text().strip()
                        link = link_elem.get('href')

                        results.append({
                            'title': title,
                            'link': link,
                            'snippet': '',
                            'source': 'VnExpress'
                        })

            return results

        except Exception as e:
            print(f"Vietnamese news search error: {e}")
            return []

    def search_pubmed(self, query: str, num_results: int = 3) -> str:
        """
        Searches PubMed for review articles related to a clinical query and returns a summary.
        """
        try:
            # Step 1: E-Search to get article IDs
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
            # Focus on high-quality review articles
            search_term = f"{query} AND (review[Publication Type] OR systematic review[Publication Type])"
            search_url = f"{base_url}esearch.fcgi?db=pubmed&term={quote(search_term)}&retmax={num_results}&retmode=json"
            
            response = requests.get(search_url, headers=self.headers, timeout=15)
            response.raise_for_status() # Raise an exception for bad status codes
            
            search_data = response.json()
            id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                return ""

            # Adhere to NCBI API guidelines (max 3 requests/sec without an API key)
            time.sleep(0.4) 

            # Step 2: E-Summary to get article details
            ids_str = ",".join(id_list)
            summary_url = f"{base_url}esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
            
            response = requests.get(summary_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            summary_data = response.json()
            results = summary_data.get("result", {})
            
            if not results:
                return ""

            # Step 3: Format the output into a concise summary for the AI prompt
            summary_text = "Tóm tắt các hướng tiếp cận từ PubMed:\n"
            for uid in id_list:
                article = results.get(uid)
                if article:
                    title = article.get("title", "Không có tiêu đề")
                    summary_text += f"- {title}\n"
            
            return summary_text.strip()

        except requests.exceptions.RequestException as e:
            print(f"PubMed search error: {e}")
            return ""
        except json.JSONDecodeError as e:
            print(f"PubMed JSON parsing error: {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred during PubMed search: {e}")
            return ""

    def search_and_summarize(self, query: str) -> str:
        """Search web and return summarized results"""
        # Try Vietnamese news first for Vietnamese queries
        if any(word in query.lower() for word in ['việt nam', 'vietnam', 'tổng bí thư', 'chính trị']):
            results = self.search_vietnamese_news(query)
            if not results:
                results = self.search_duckduckgo(query + " site:vnexpress.net OR site:tuoitre.vn OR site:dantri.com.vn")
        else:
            results = self.search_duckduckgo(query)

        if not results:
            return "Không tìm thấy thông tin cập nhật về chủ đề này."

        summary = f"🔍 Kết quả tìm kiếm cho '{query}':\n\n"

        for i, result in enumerate(results[:3], 1):
            summary += f"{i}. **{result['title']}**\n"
            if result['snippet']:
                summary += f"   {result['snippet'][:200]}...\n"
            summary += f"   🔗 {result['link']}\n\n"

        summary += "\n*Thông tin được cập nhật từ web search*"
        return summary
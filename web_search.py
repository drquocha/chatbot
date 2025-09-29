import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote

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
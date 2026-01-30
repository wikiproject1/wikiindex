import httpx
from typing import Optional, Dict, Any, List
import urllib.parse

class WikimediaService:
    def __init__(self):
        self.headers = {
            "User-Agent": "WikiTrustIndex/0.1 (http://localhost:4445; contact@example.com)"
        }

    async def get_page_content(self, title: str, lang: str = "sw") -> Optional[Dict[str, Any]]:
        """
        Fetch page content, metadata, images, and categories from Wikipedia.
        """
        base_url = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts|info|extlinks|iwlinks|pageimages|categories|revisions|templates",
            "titles": title,
            "explaintext": True,
            "exintro": True,
            "inprop": "url|watchers",
            "piprop": "thumbnail|original",
            "pithumbsize": 500,
            "rvprop": "timestamp|user|comment",
            "rvlimit": 1,
            "tllimit": 500
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(base_url, params=params, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                pages = data.get("query", {}).get("pages", {})
                for page_id in pages:
                    if page_id == "-1":
                        return None
                    page = pages[page_id]
                    
                    # Process Categories (Jamii)
                    categories = [cat.get("title", "").replace("Category:", "Jamii: ") for cat in page.get("categories", [])]
                    page["jamii"] = categories
                    
                    # Process Revision Info
                    revisions = page.get("revisions", [])
                    if revisions:
                        page["last_update"] = revisions[0].get("timestamp")
                        page["last_editor"] = revisions[0].get("user")
                    
                    # Process Templates (for AI/Machine Detection)
                    templates = [t.get("title", "") for t in page.get("templates", [])]
                    page["templates"] = templates
                    
                    # Image URL
                    page["image_url"] = page.get("thumbnail", {}).get("source") or page.get("original", {}).get("source")
                    
                    return page
            except Exception as e:
                print(f"Error fetching page {title} ({lang}): {e}")
                return None

    async def search_suggestions(self, query: str, lang: str = "sw") -> List[str]:
        """
        Fetch search suggestions from Wikipedia's opensearch API.
        """
        base_url = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "format": "json",
            "search": query,
            "limit": 10
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(base_url, params=params, headers=self.headers, timeout=5.0)
                data = response.json()
                if len(data) > 1:
                    return data[1]
                return []
            except Exception as e:
                print(f"Error fetching suggestions: {e}")
                return []

    async def get_langlinks(self, title: str, lang: str = "sw") -> Dict[str, Any]:
        """
        Get language links and total language count.
        """
        base_url = f"https://{lang}.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "langlinks",
            "titles": title,
            "lllimit": 500
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(base_url, params=params, headers=self.headers, timeout=10.0)
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                result = {"en": None, "count": 0, "sw_exists": False}
                
                for page_id in pages:
                    links = pages[page_id].get("langlinks", [])
                    result["count"] = len(links)
                    for link in links:
                        if link.get("lang") == "en":
                            result["en"] = link.get("*")
                        if link.get("lang") == "sw":
                            result["sw_exists"] = True
                
                # If we are searching ON sw wikipedia, sw_exists is obviously true
                if lang == "sw":
                    result["sw_exists"] = True
                    # The langlinks API doesn't include the current language in the result list
                    # So we add 1 to the count
                    result["count"] += 1
                
                return result
            except Exception as e:
                print(f"Error fetching langlinks: {e}")
                return {"en": None, "count": 0, "sw_exists": (lang == "sw")}

    def extract_title_from_url(self, url: str) -> Optional[str]:
        try:
            parsed = urllib.parse.urlparse(url)
            path_parts = parsed.path.split("/wiki/")
            if len(path_parts) > 1:
                return urllib.parse.unquote(path_parts[1])
            return None
        except:
            return None

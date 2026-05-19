import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS
from models.tools import ToolResponse

class Tools:
    def get_registry(self) -> dict:
        return {
            "web_search": (Tools.web_search, Tools.web_search.__doc__),
            "web_fetch": (Tools.web_fetch, Tools.web_fetch.__doc__),
            "get_geospatial_data": (Tools.get_geospatial_data, Tools.get_geospatial_data.__doc__),
        }

    @staticmethod
    def web_search(query: str) -> ToolResponse:
        """Perform a web search using DuckDuckGo and return the results."""
        with DDGS() as ddgs:
            results = ddgs.text(query)
            return ToolResponse(output="\n".join([result["body"] for result in results]))

    @staticmethod
    def web_fetch(url: str) -> ToolResponse:
        """Fetch and return the text content of a webpage at a given URL."""
        response = httpx.get(url, follow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        return ToolResponse(output=soup.get_text(separator="\n", strip=True))

    @staticmethod
    def get_geospatial_data(location: str) -> ToolResponse:
        """Retrieve geospatial data for a given location."""
        # Placeholder for geospatial data retrieval functionality
        return ToolResponse(output=f"Geospatial data for '{location}'")
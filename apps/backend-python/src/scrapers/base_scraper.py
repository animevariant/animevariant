import httpx
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_html(self, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def get_chapter_url(self, manga_id: str, chapter_id: str) -> str:
        """
        Construct the chapter URL for a given manga and chapter.
        Default: /manga/{manga_id}/{chapter_id}/
        Override in subclasses if needed.
        """
        return f"{self.base_url}/manga/{manga_id}/{chapter_id}/"

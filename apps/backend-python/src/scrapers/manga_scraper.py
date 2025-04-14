from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
from typing import List, Optional
from datetime import datetime
import re
import logging
import httpx
from urllib.parse import urlparse, urlunparse
import re
import os


def parse_date(date_str):
    # Define multiple formats to try
    date_formats = [
        "%b %d,%Y - %H:%M %p",  # Adjusted for 24-hour format and AM/PM
        "%b %d, %Y - %H:%M %p",  # Adjusted for space after the comma and 24-hour format
        "%b %d,%Y - %I:%M %p",  # Your original format
        # Add more formats as necessary
    ]

    # Remove any potential extra spaces (for more robust parsing)
    date_str = re.sub(r'\s+', ' ', date_str)

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue  # Try the next format if current one fails
    return None  # Return None if all formats fail


class ManganeloScraper(BaseScraper):
    async def scrape(self, page: Optional[int] = None, genre: Optional[str] = None, type: Optional[str] = None):
        # Apply default values if None
        page = page or '1'
        if genre == "All":
            genre = ""
        else:
            genre = genre or 'Isekai'
        type = type or 'topview'

        html = await self.fetch_html(f"{self.base_url}/genre/{genre}?type={type}&page={page}")
        soup = BeautifulSoup(html, 'html.parser')
        mangas = []

        for item in soup.select('.content-genres-item'):
            titleElement = item.select_one('.genres-item-name')
            imgElement = item.select_one('img')
            chaptersElement = item.select_one('.genres-item-chap')
            srcElement = item.select_one('a')
            descriptionElement = item.select_one('.genres-item-description')
            authorElements = item.select('.genres-item-author')
            ratingElement = item.select_one('.genres-item-rate')

            src = srcElement['href'] if srcElement else None
            id = src.split('/')[-1] if src else None
            titleId = titleElement.text.strip() if titleElement else None
            img = imgElement['src'] if imgElement else None

            # Handling authors
            authors = []
            for authorElement in authorElements:
                authorName = authorElement.text.strip()
                authors.append(authorName)

            content = {
                "title": titleId,
                "img": img,
                "latestChapter": chaptersElement.text.strip() if chaptersElement else "",
                "rating": ratingElement.text.strip() if ratingElement else "",
                "src": src,
                "id": id,
                "titleId": titleId,
                "description": descriptionElement.text.strip() if descriptionElement else "",
                "authors": authors,
            }

            mangas.append(content)

        return mangas

    async def get_manga_details(self, manga_id: str):
        url = f"{self.base_url}/manga/{manga_id}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.select_one('.story-info-right h1').text
        img = soup.select_one('.info-image img')['src']
        description_raw = soup.select_one(
            '#panel-story-info-description').text.strip()

        # Remove "Description :" if it's at the beginning using regex
        description = re.sub(r'^Description\s*:\s*', '',
                             description_raw, flags=re.IGNORECASE)

        # Extracting authors and genres
        all_elements = [elem.text.strip()
                        for elem in soup.select('.table-value a')]
        authors = [all_elements[0]] if all_elements else []
        genres = all_elements[1:] if len(all_elements) > 1 else []

        rating_element = soup.select_one('[property="v:average"]')
        rating = float(rating_element.text) if rating_element else None

        # Extracting and converting last updated date
        lastUpdated_text = soup.select_one(
            '.story-info-right-extent p:nth-of-type(1) .stre-value').text.strip()
        lastUpdated = parse_date(lastUpdated_text)

        # Extracting and converting views
        views_text = soup.select_one(
            '.story-info-right-extent p:nth-of-type(2) .stre-value').text.strip()
        views = float(re.sub(r'[KM]', lambda x: "e3" if x.group(
            0) == 'K' else "e6", views_text)) if views_text else 0

        chapters = [{
            "src": c['href'],
            "chapterId": c['href'].split('/')[-1],
            "chapterTitle": c.text.strip()
        } for c in soup.select('.chapter-name')]

        return {
            "title": title,
            "img": img,
            "description": description,
            "authors": authors,
            "rating": rating,
            "genres": genres,
            "lastUpdated": lastUpdated.strftime("%Y-%m-%d %H:%M") if lastUpdated else "Unknown",
            "views": views,
            "chapters": chapters,
        }

    async def get_chapter_details(self, manga_id: str, chapter_id: str):
        # Construct the chapter URL based on manga_id and chapter_id
        # Adjust as necessary
        chapter_url = f"{self.base_url}/chapter/{manga_id}/{chapter_id}"
        html = await self.fetch_html(chapter_url)
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.select_one('.panel-chapter-info-top h1').text
        images = soup.select('.container-chapter-reader img')

        image_data = []
        for index, img in enumerate(images, start=1):
            # Use 'src' if 'data-src' is not available
            image_url = img.get('data-src')
            image_data.append({
                "imageUrl": image_url,
                "pageNumber": index,
                "totalPages": len(images)
            })

        # fetch the manga data
        manga = await self.get_manga_details(manga_id)

        return {
            "title": title,
            "images": image_data,
            "manga": manga
        }

    async def search_manga(self, word: str, page: int = 1):
        search_url = f"{self.base_url}/search/{word}?page={page}"
        html = await self.fetch_html(search_url)
        soup = BeautifulSoup(html, 'html.parser')

        search_results = []
        for item in soup.select('.search-story-item'):
            titleElement = item.select_one('.item-title')
            imgElement = item.select_one('img')
            # Assuming this is correct; adjust if needed
            chaptersElement = item.select_one('.item-title')
            srcElement = item.select_one('a')
            authorElement = item.select_one('.item-author')

            title = titleElement.text.strip() if titleElement else "No title"
            img = imgElement.get('src', '') if imgElement else "No image"
            latestChapter = chaptersElement.text.strip() if chaptersElement else "No chapters"
            src = srcElement.get('href', '') if srcElement else "No source"
            author = authorElement.text.strip() if authorElement else "No author"

            mangaId = src.split('/')[-1] if src else "No ID"

            search_results.append({
                "title": title,
                "img": img,
                "latestChapter": latestChapter,
                "src": src,
                "mangaId": mangaId,
                "author": author,
            })

        return {
            "page": page,
            "mangas": search_results
        }


class MangaClashScraper(BaseScraper):
    async def scrape(self, page: Optional[int] = None, genre: Optional[str] = None, type: Optional[str] = None):
        # Apply default values if None
        page = page or '1'
        genre = genre or 'latest'

        url = f"{self.base_url}/manga/page/{page}/?m_orderby={genre}"
        # Use httpx to handle the redirection
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 301:
                logging.warning(f"Redirected to {
                                response.headers['location']}")
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        mangas = []

        for item in soup.select('.manga'):
            titleElement = item.select_one('h3 a')
            imgElement = item.select_one('img')
            latestChapterElement = item.select_one('.chapter a')
            descriptionElement = item.select_one('.list-story-item-wrap-1 p')
            title = titleElement.text.strip() if titleElement else "No title"

            img = imgElement.get('data-src', '') if imgElement else "No image"
            # Strip the HTTPS domain from the img URL
            parsed_img_url = urlparse(img)
            img = urlunparse(('', '', parsed_img_url.path, parsed_img_url.params,
                             parsed_img_url.query, parsed_img_url.fragment))

            latestChapter = latestChapterElement.text.strip(
            ) if latestChapterElement else "No chapters"
            src = titleElement['href'] if titleElement else "No source"
            description = descriptionElement.text.strip(
            ) if descriptionElement else "No description"

            # Extract the manga ID by stripping the domain and using the slug
            id = src.split('/')[-2] if src else "No ID"

            mangas.append({
                "title": title,
                "img": img,
                "latestChapter": latestChapter,
                "src": src,
                "id": id,
                "description": description,
            })

        return mangas

    async def get_manga_details(self, manga_id: str):
        # Regular expression pattern to match the image URL
        img_url_pattern = r'"og:image" content="([^"]*)"'

        url = f"{self.base_url}/manga/{manga_id}"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            if response.status_code == 301:
                logging.warning(f"Redirected to {
                                response.headers['location']}")
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        title = soup.select_one('.post-title h1').text.strip()
        # Get the lazy loading image URL
        lazy_loading_img = soup.select_one('.summary_image img')['src']

        # Find the real image URL using regular expressions
        real_img_match = re.search(img_url_pattern, html)
        if real_img_match:
            real_img = real_img_match.group(1)
        else:
            # If the real image URL is not found, fallback to the lazy loading image
            real_img = lazy_loading_img

        # Strip the HTTPS domain from the real image URL
        parsed_img_url = urlparse(real_img)
        img = urlunparse(('', '', parsed_img_url.path, parsed_img_url.params,
                         parsed_img_url.query, parsed_img_url.fragment))
        img_name = os.path.basename(parsed_img_url.path)

        description_raw = soup.select_one('.description-summary').text.strip()
        description = re.sub(r'^Description\s*:\s*', '',
                             description_raw, flags=re.IGNORECASE)
        authors = [a.text.strip() for a in soup.select('.author-content a')]
        genres = [g.text.strip() for g in soup.select('.genres-content a')]

        rating_element = soup.select_one('.total_votes')
        rating = float(rating_element.text) if rating_element else None

        lastUpdated_text = soup.select_one('.post-status .summary-content')
        lastUpdated = lastUpdated_text.text.strip() if lastUpdated_text else None
        chapters = [{
            "src": c.select_one('a')['href'],
            "chapterId": c.select_one('a')['href'].split('/')[-2],
            "chapterTitle": c.select_one('a').text.strip(),
            "new": c.select_one('.c-new-tag')['title'] if c.select_one('.c-new-tag') else None
        } for c in soup.select('.wp-manga-chapter')]

        return {
            "img_name": img_name,
            "title": title,
            "img": img,
            "description": description,
            "authors": authors,
            "rating": rating,
            "genres": genres,
            "lastUpdated": lastUpdated or "Unknown",
            "chapters": chapters,
        }

    async def get_chapter_details(self, manga_id: str, chapter_id: str):
        chapter_url = f"{self.base_url}/manga/{manga_id}/{chapter_id}"
        # Use httpx to handle the redirection
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(chapter_url)
            if response.status_code == 301:
                logging.warning(f"Redirected to {
                                response.headers['location']}")
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        logging.warning(f"----------> {soup.select_one('#chapter-heading')}")
        title_element = soup.select_one('#chapter-heading')
        title = title_element.text.strip() if title_element else "No title found"

        images = soup.select('.reading-content .page-break img')

        image_data = []
        for index, img in enumerate(images, start=1):
            # Use 'data-src' if available, otherwise fallback to 'src'
            image_url = img.get('data-src', '').strip()
            image_data.append({
                "imageUrl": image_url,
                "pageNumber": index,
                "totalPages": len(images)
            })

        manga = await self.get_manga_details(manga_id)

        return {
            "title": title,
            "images": image_data,
            "manga": manga
        }

    async def search_manga(self, word: str, page: int = 1):
        search_url = f"{self.base_url}/?s={word}&post_type=wp-manga"
        # Use httpx to handle the redirection
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(search_url)
            if response.status_code == 301:
                logging.warning(f"Redirected to {
                                response.headers['location']}")
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')

        search_results = []
        for item in soup.select('.c-tabs-item__content'):
            titleElement = item.select_one('.post-title h3 a')
            imgElement = item.select_one('img')
            latestChapterElement = item.select_one('.latest-chap .chapter a')
            descriptionElement = item.select_one(
                '.post-content .post-summary p')

            title = titleElement.text.strip() if titleElement else "No title"
            img = imgElement.get('data-src', '') if imgElement else "No image"
            latestChapter = latestChapterElement.text.strip(
            ) if latestChapterElement else "No chapters"
            src = titleElement['href'] if titleElement else "No source"
            description = descriptionElement.text.strip(
            ) if descriptionElement else "No description"

            mangaId = src.split('/')[-2] if src else "No ID"

            search_results.append({
                "title": title,
                "img": img,
                "latestChapter": latestChapter,
                "src": src,
                "mangaId": mangaId,
                "description": description,
            })

        return {
            "page": page,
            "mangas": search_results
        }


class MangaKissScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass


class KissMangaScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass


class ManhuaTopScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass


class MangaParkIoScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass


class MangaParkNetScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass


class ManhuaFastScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass


class RMangaScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass


class ReadMangaScraper(BaseScraper):
    # Implement similar to ManganeloScraper
    pass

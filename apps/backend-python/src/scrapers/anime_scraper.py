import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from .base_scraper import BaseScraper

class AnitakuScraper(BaseScraper):
    async def fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def get_popular(self, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/popular.html?page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            id = href[10:]
            image = img.find('img')['src']
            results.append({'title': title, 'id': id, 'image': image})
        return results

    async def get_details(self, anime_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/category/{anime_id}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        details = {
            'title': soup.select_one('.anime_info_body_bg h1').text.strip(),
            'image': soup.select_one('.anime_info_body_bg img')['src'],
            'type': '',
            'summary': '',
            'released': '',
            'status': '',
            'genres': '',
            'total_episode': '',
            'other_name': ''
        }
        for p in soup.select('p.type'):
            span_text = p.find('span').text
            if span_text == "Type: ":
                details['type'] = p.text[15:-5].strip()
            elif span_text == "Plot Summary: ":
                details['summary'] = p.text[14:].strip()
            elif span_text == "Released: ":
                details['released'] = p.text[10:].strip()
            elif span_text == "Status: ":
                details['status'] = p.text[8:].strip()
            elif span_text == "Genre: ":
                details['genres'] = p.text[20:-4].strip().replace(' ', ',')
            elif span_text == "Other name: ":
                details['other_name'] = p.text[12:].strip()

        total_episode_elem = soup.select_one('#episode_page li:last-child a')
        if total_episode_elem:
            details['total_episode'] = total_episode_elem.get('ep_end', '')

        return details

    async def search(self, keyword: str, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/search.html?keyword={keyword}&page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            id = href[10:]
            image = img.find('img')['src']
            results.append({'title': title, 'id': id, 'image': image})
        return results

    async def get_watching_links(self, anime_id: str, episode: int) -> Dict[str, Any]:
        url = f"{self.base_url}/{anime_id}-episode-{episode}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        total_episode = ''
        link = soup.select_one('li.anime a')['data-video'].replace("streaming.php", "download")
        total_episode_elem = soup.select_one('#episode_page li:last-child a')
        if total_episode_elem:
            total_episode = total_episode_elem.text.split('-')[-1]

        download_html = await self.fetch_html(link)
        download_soup = BeautifulSoup(download_html, 'html.parser')
        for a in download_soup.select('a[download=""]'):
            size = a.text[21:].replace('(', '').replace(')', '').replace(' - mp4', '')
            links.append({
                'src': a['href'],
                'size': 'High Speed' if size == 'HDP' else size
            })
        return {'links': links, 'link': link, 'total_episode': total_episode}

    async def get_genre(self, genre: str, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/genre/{genre}?page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            id = href[10:]
            image = img.find('img')['src']
            results.append({'title': title, 'id': id, 'image': image})
        return results

    async def get_recently_added(self, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/?page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            image = img.find('img')['src']
            episode_number = img.find_next_sibling('p', class_='episode').text.strip().replace(" ", "-").lower()
            id = href[1:].replace(f"-{episode_number}", "")
            episode_number = episode_number.replace("episode-", "")
            results.append({'title': title, 'id': id, 'image': image, 'episode_number': episode_number})
        return results

    async def get_genre_list(self) -> List[str]:
        url = self.base_url
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        return [li.text for li in soup.select('nav.genre ul li')]

    async def get_anime_list(self, variable: str, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/anime-list.html?page={page}" if variable == "all" else f"{self.base_url}/anime-list-{variable}?page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for li in soup.select('ul.listing li'):
            title = li.find('a').text
            href = li.find('a')['href']
            id = href[10:]
            results.append({'title': title, 'id': id})
        return results


class GogoanimeByScraper(BaseScraper):
    async def fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def get_popular(self, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/series/?page={page}&order=popular"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            id = href[10:]
            image = img.find('img')['src']
            results.append({'title': title, 'id': id, 'image': image})
        return results

    async def get_details(self, anime_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/category/{anime_id}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        details = {
            'title': soup.select_one('.anime_info_body_bg h1').text.strip(),
            'image': soup.select_one('.anime_info_body_bg img')['src'],
            'type': '',
            'summary': '',
            'released': '',
            'status': '',
            'genres': '',
            'total_episode': '',
            'other_name': ''
        }
        for p in soup.select('p.type'):
            span_text = p.find('span').text
            if span_text == "Type: ":
                details['type'] = p.text[15:-5].strip()
            elif span_text == "Plot Summary: ":
                details['summary'] = p.text[14:].strip()
            elif span_text == "Released: ":
                details['released'] = p.text[10:].strip()
            elif span_text == "Status: ":
                details['status'] = p.text[8:].strip()
            elif span_text == "Genre: ":
                details['genres'] = p.text[20:-4].strip().replace(' ', ',')
            elif span_text == "Other name: ":
                details['other_name'] = p.text[12:].strip()

        total_episode_elem = soup.select_one('#episode_page li:last-child a')
        if total_episode_elem:
            details['total_episode'] = total_episode_elem.get('ep_end', '')

        return details

    async def search(self, keyword: str, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/search.html?keyword={keyword}&page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            id = href[10:]
            image = img.find('img')['src']
            results.append({'title': title, 'id': id, 'image': image})
        return results

    async def get_watching_links(self, anime_id: str, episode: int) -> Dict[str, Any]:
        url = f"{self.base_url}/{anime_id}-episode-{episode}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        total_episode = ''
        link = soup.select_one('li.anime a')['data-video'].replace("streaming.php", "download")
        total_episode_elem = soup.select_one('#episode_page li:last-child a')
        if total_episode_elem:
            total_episode = total_episode_elem.text.split('-')[-1]

        download_html = await self.fetch_html(link)
        download_soup = BeautifulSoup(download_html, 'html.parser')
        for a in download_soup.select('a[download=""]'):
            size = a.text[21:].replace('(', '').replace(')', '').replace(' - mp4', '')
            links.append({
                'src': a['href'],
                'size': 'High Speed' if size == 'HDP' else size
            })
        return {'links': links, 'link': link, 'total_episode': total_episode}

    async def get_genre(self, genre: str, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/genre/{genre}?page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            id = href[10:]
            image = img.find('img')['src']
            results.append({'title': title, 'id': id, 'image': image})
        return results

    async def get_recently_added(self, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/?page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for img in soup.select('.img'):
            title = img.find('a')['title']
            href = img.find('a')['href']
            image = img.find('img')['src']
            episode_number = img.find_next_sibling('p', class_='episode').text.strip().replace(" ", "-").lower()
            id = href[1:].replace(f"-{episode_number}", "")
            episode_number = episode_number.replace("episode-", "")
            results.append({'title': title, 'id': id, 'image': image, 'episode_number': episode_number})
        return results

    async def get_genre_list(self) -> List[str]:
        url = self.base_url
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        return [li.text for li in soup.select('nav.genre ul li')]

    async def get_anime_list(self, variable: str, page: int) -> List[Dict[str, str]]:
        url = f"{self.base_url}/anime-list.html?page={page}" if variable == "all" else f"{self.base_url}/anime-list-{variable}?page={page}"
        html = await self.fetch_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        for li in soup.select('ul.listing li'):
            title = li.find('a').text
            href = li.find('a')['href']
            id = href[10:]
            results.append({'title': title, 'id': id})
        return results

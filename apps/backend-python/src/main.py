import debugpy
from prometheus_fastapi_instrumentator import Instrumentator
from typing import Optional, List, Union, Dict
from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from .scrapers.manga_scraper import (
    ManganeloScraper, MangaClashScraper, MangaKissScraper, KissMangaScraper, ManhuaTopScraper,
    MangaParkIoScraper, MangaParkNetScraper, ManhuaFastScraper, RMangaScraper, ReadMangaScraper
)
from .scrapers.anime_scraper import AnitakuScraper, GogoanimeByScraper  # Import your anime scraper

from dotenv import load_dotenv
import httpx
import os
import logging
from pydantic import BaseModel
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
# routes for the API
from .routers import (router_home)
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
app.include_router(router_home.router)
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "https://manga.valiantlynx.com").split(",")
print("ALLOWED_ORIGINS:",  allowed_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

debugpy.listen(("0.0.0.0", 5678))

# Define the server map for scrapers and image base URLs
server_map = {
    "MANGANELO": {
        "scraper": ManganeloScraper,
        "image_base_urls": [os.getenv("MANGANELO_CDN"), os.getenv("MANGANELO")]
    },
    "MANGACLASH": {
        "scraper": MangaClashScraper,
        "image_base_urls": [os.getenv("MANGACLASH_CDN"), os.getenv("MANGACLASH")]
    },
    "MANGAKISS": {
        "scraper": MangaKissScraper,
        "image_base_urls": [os.getenv("MANGAKISS_CDN"), os.getenv("MANGAKISS")]
    },
    "KISSMANGA": {
        "scraper": KissMangaScraper,
        "image_base_urls": [os.getenv("KISSMANGA_CDN"), os.getenv("KISSMANGA")]
    },
    "MANHUATOP": {
        "scraper": ManhuaTopScraper,
        "image_base_urls": [os.getenv("MANHUATOP_CDN"), os.getenv("MANHUATOP")]
    },
    "MANGAPARK_IO": {
        "scraper": MangaParkIoScraper,
        "image_base_urls": [os.getenv("MANGAPARK_IO_CDN"), os.getenv("MANGAPARK_IO")]
    },
    "MANGAPARK_NET": {
        "scraper": MangaParkNetScraper,
        "image_base_urls": [os.getenv("MANGAPARK_NET_CDN"), os.getenv("MANGAPARK_NET")]
    },
    "MANHUAFAST": {
        "scraper": ManhuaFastScraper,
        "image_base_urls": [os.getenv("MANHUAFAST_CDN"), os.getenv("MANHUAFAST")]
    },
    "RMANGA": {
        "scraper": RMangaScraper,
        "image_base_urls": [os.getenv("RMANGA_CDN"), os.getenv("RMANGA")]
    },
    "READMANGA": {
        "scraper": ReadMangaScraper,
        "image_base_urls": [os.getenv("READMANGA_CDN"), os.getenv("READMANGA")]
    }
}


# Define the server map for anime scrapers and image base URLs
anime_server_map = {
    "GOGOANIMEZ_TO": {
        "scraper": AnitakuScraper,
        "image_base_urls": [os.getenv("ANITAKU_CDN"), os.getenv("GOGOANIMEZ_TO")]
    },
    "GOGOANIME_BY": {
        "scraper": GogoanimeByScraper,
        "image_base_urls": [os.getenv("ANITAKU_CDN"), os.getenv("GOGOANIME_BY")]
    },
    "GOGOANIME_ORD_VC": {
        "scraper": AnitakuScraper,
        "image_base_urls": [os.getenv("ANITAKU_CDN"), os.getenv("GOGOANIME_ORD_VC")]
    },
    "ANITAKU": {
        "scraper": AnitakuScraper,
        "image_base_urls": [os.getenv("ANITAKU_CDN"), os.getenv("ANITAKU")]
    }
}


@app.get("/api/anime")
async def get_anime(server: str = Query(default='GOGOANIME_BY'), genre: Optional[str] = None, page: Optional[int] = None):
    try:
        if server not in anime_server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        print("--"*8, base_url)
        scraper_class = anime_server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        # Use get_popular, adjust method as needed
        animes = await scraper.get_popular(page)
        return {"results": animes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/anime/{anime_id}")
async def get_anime_details(server: str = Query(default='ANITAKU'), anime_id: str = Path(..., example="anime-xyz123")):
    try:
        if server not in anime_server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = anime_server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        anime_details = await scraper.get_details(anime_id)  # Use get_details
        return anime_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/anime/{anime_id}/{episode_id}")
async def get_anime_episode_details(anime_id: str = Path(..., example="anime-xyz123"), episode_id: str = Path(..., example="episode-1"), server: str = Query(default='ANITAKU')):
    try:
        if server not in anime_server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = anime_server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        # Adjust method if needed
        episode_details = await scraper.get_watching_links(anime_id, int(episode_id))
        return JSONResponse(content=episode_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search/anime")
async def search_anime(word: str = Query(..., example="naruto"), page: Optional[int] = 1, server: str = Query(default='ANITAKU')):
    try:
        if server not in anime_server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = anime_server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        search_results = await scraper.search(word, page)  # Use search
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/animeimage/{image}")
async def get_anime_image_from_path(server: str = Query(default='ANITAKU'), image: str = Path(..., example="anime-xyz123.jpg")):
    try:
        if server not in anime_server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        image_base_urls = anime_server_map[server]["image_base_urls"]
        if not image_base_urls:
            raise HTTPException(
                status_code=404, detail=f"Image base URL not configured for server {server}")

        image_urls = [
            f"{base_url}/animeimage/{image}" for base_url in image_base_urls if base_url]

        response = await fetch_image(image_urls)
        return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(exc)}")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Request error: {str(exc)}")

# Helper function to fetch image


async def fetch_image(image_urls: List[str]):
    async with httpx.AsyncClient() as client:
        for url in image_urls:
            response = await client.get(url)
            if response.status_code == 200:
                return response
        raise HTTPException(status_code=404, detail="Image not found")


# Old direct translation from express js #######################3

base_url = "https://anitaku.to/"

# Model Definitions


class Anime(BaseModel):
    title: str
    id: str
    image: str
    episode_number: Union[str, None] = None


class AnimeDetails(BaseModel):
    title: str
    image: str
    type: str
    summary: str
    relased: str
    genres: str
    status: str
    totalepisode: str
    Othername: str


class SearchResult(BaseModel):
    title: str
    id: str
    image: str


class WatchingLink(BaseModel):
    src: str
    size: str


class GenreList(BaseModel):
    list: List[str]

# Helper function to fetch HTML content


async def fetch_html(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        if response.is_redirect:
            redirect_url = response.headers.get("location")
            print(f"Redirected to {redirect_url}")
        response.raise_for_status()
        return response.text


@app.get("/api/home")
async def get_home():
    host_url = os.getenv("HOST_URL", "http://localhost:8001")
    info = {
        "popular": {"recipe": f"{host_url}/api/popular/:page", "test": f"{host_url}/api/popular/2"},
        "details": {"recipe": f"{host_url}/api/details/:id", "test": f"{host_url}/api/details/gintama"},
        "search": {"recipe": f"{host_url}/api/search/:word/:page", "test": f"{host_url}/api/search/killer/1"},
        "episode_link": {"recipe": f"{host_url}/api/watching/:id/:episode", "test": f"{host_url}/api/watching/gintama/50"},
        "genre": {"recipe": f"{host_url}/api/genre/:type/:page", "test": f"{host_url}/api/genre/action/2"},
        "recently_added": {"recipe": f"{host_url}/api/recentlyadded/:page", "test": f"{host_url}/api/recentlyadded/1"},
        "anime_list": {"recipe": f"{host_url}/api/list/:variable/:page", "test": f"{host_url}/api/list/one/1"},
        "genrelist": {"recipe": f"{host_url}/api/genrelist", "test": f"{host_url}/api/genrelist"}
    }
    return info


@app.get("/api/docs")
async def get_docs():
    response = {
        "message": "Welcome to AnimeVariant API!",
        "api": {
            "version": "1.0.0",
            "author": "Valiantlynx",
            "description": "An API for accessing anime information and resources.",
            "endpoints": [
                {"path": "/api/home",
                    "description": "Get information about available API endpoints.", "params": {}},
                {"path": "/api/popular/:page", "description": "Get a list of popular anime.",
                    "params": {"page": "an integer representing the page number"}},
                {"path": "/api/details/:id", "description": "Get details of a specific anime by ID.",
                    "params": {"id": "The correct name of the anime"}},
                {"path": "/api/search/:word/:page", "description": "Search for anime by a keyword.", "params": {
                    "word": "The keyword to search for", "page": "an integer representing the page number"}},
                {"path": "/api/watching/:id/:episode", "description": "Get the video links for a specific episode of an anime.",
                    "params": {"id": "The correct name of the anime", "episode": "an integer representing the episode number"}},
                {"path": "/api/genre/:type/:page", "description": "Get a list of anime by genre.",
                    "params": {"type": "The genre of the anime", "page": "an integer representing the page number"}},
                {"path": "/api/recentlyadded/:page", "description": "Get a list of recently added anime.",
                    "params": {"page": "an integer representing the page number"}},
                {"path": "/api/list/:variable/:page", "description": "Get a list of anime based on a variable.",
                    "params": {"variable": "The variable to filter the list", "page": "an integer representing the page number"}},
                {"path": "/api/genrelist",
                    "description": "Get a list of available anime genres.", "params": {}}
            ]
        }
    }
    return response


@app.get("/api/popular/{page}", response_model=Dict[str, List[Anime]])
async def get_popular(page: int):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Page must be a positive integer")

    url = f"{base_url}popular.html?page={page}"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    results = []
    for anime_item in soup.select(".img"):
        title = anime_item.select_one("a")["title"]
        id = anime_item.select_one("a")["href"].split('/')[-1]
        image = anime_item.select_one("img")["src"]
        results.append({"title": title, "id": id, "image": image})

    return {"results": results}


@app.get("/api/details/{id}", response_model=AnimeDetails)
async def get_details(id: str):
    url = f"{base_url}category/{id}"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    type = summary = relased = status = genres = Othername = ""
    title = soup.select_one(".anime_info_body_bg h1").text
    image = soup.select_one(".anime_info_body_bg img")["src"]

    for p in soup.select("p.type"):
        span_text = p.select_one("span").text
        text = p.text.strip()
        if span_text == "Type: ":
            type = text[7:]
        elif span_text == "Plot Summary: ":
            summary = text[13:]
        elif span_text == "Released: ":
            relased = text[10:]
        elif span_text == "Status: ":
            status = text[9:]
        elif span_text == "Genre: ":
            genres = text[8:].replace(", ", ",")
        elif span_text == "Other name: ":
            Othername = text[12:]

    totalepisode = soup.select_one("#episode_page li:last-child a")["ep_end"]

    results = []
    results.append({
        "title": title,
        "image": image,
        "type": type,
        "summary": summary,
        "relased": relased,
        "genres": genres,
        "status": status,
        "totalepisode": totalepisode,
        "Othername": Othername
    })
    return JSONResponse(content={"results": results})


@app.get("/api/search/{word}/{page}", response_model=Dict[str, List[SearchResult]])
async def search(word: str, page: int):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Page must be a positive integer")

    url = f"{base_url}/search.html?keyword={word}&page={page}"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    results = []
    for anime_item in soup.select(".img"):
        title = anime_item.select_one("a")["title"]
        id = anime_item.select_one("a")["href"].split('/')[-1]
        image = anime_item.select_one("img")["src"]
        results.append({"title": title, "id": id, "image": image})

    return {"results": results}


@app.get("/api/watching/{id}/{episode}")
async def get_watching(id: str, episode: int):
    url = f"{base_url}{id}-episode-{episode}"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    if soup.select_one(".entry-title") and soup.select_one(".entry-title").text == "404":
        return {"links": [], "link": "", "totalepisode": ""}

    try:
        totalepisode = soup.select_one(
            "#episode_page li:last-child a").text.split("-")[-1]
        link = soup.select_one("li.anime a")[
            "data-video"].replace("streaming.php", "download")

        response = await fetch_html(link)
        soup = BeautifulSoup(response, 'html.parser')

        links = []
        for a in soup.select("a"):
            if a.get("download") == "":
                size = a.text.strip().replace("(", "").replace(")", "").replace(" - mp4", "")
                links.append({"src": a["href"], "size": size})

        return {"links": links, "link": link, "totalepisode": totalepisode}

    except Exception as e:
        print(f"Error: {e}")
        return {"links": [], "link": "", "totalepisode": ""}


@app.get("/api/genre/{type}/{page}", response_model=Dict[str, List[Anime]])
async def get_genre(type: str, page: int):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Page must be a positive integer")

    url = f"{base_url}genre/{type}?page={page}"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    results = []
    for anime_item in soup.select(".img"):
        title = anime_item.select_one("a")["title"]
        id = anime_item.select_one("a")["href"].split('/')[-1]
        image = anime_item.select_one("img")["src"]
        results.append({"title": title, "id": id, "image": image})

    return {"results": results}


@app.get("/api/recentlyadded/{page}", response_model=Dict[str, List[Anime]])
async def get_recently_added(page: int):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Page must be a positive integer")

    url = f"{base_url}?page={page}"
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    results = []
    for anime_item in soup.select(".img"):
        title = anime_item.select_one("a")["title"]
        id = anime_item.select_one("a")["href"].split('/')[-1]
        image = anime_item.select_one("img")["src"]
        episode_number = anime_item.select_one("p.episode").text.strip().replace(
            " ", "-").lower().replace("episode-", "")
        results.append({"title": title, "id": id, "image": image,
                       "episode_number": episode_number})

    return {"results": results}


@app.get("/api/genrelist", response_model=GenreList)
async def get_genre_list():
    url = base_url
    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    genres = [li.text for li in soup.select("nav.genre ul li")]
    return {"list": genres}


@app.get("/api/list/{variable}/{page}", response_model=Dict[str, List[Anime]])
async def get_list(variable: str, page: int):
    if page < 1:
        raise HTTPException(
            status_code=400, detail="Page must be a positive integer")

    url = f"{base_url}anime-list.html?page={page}"
    if variable != "all":
        url = f"{base_url}anime-list-{variable}?page={page}"

    html = await fetch_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    results = []
    for anime_item in soup.select("ul.listing li"):
        title = anime_item.select_one("a").text
        id = anime_item.select_one("a")["href"].split('/')[-1]
        results.append({"title": title, "id": id})

    return JSONResponse(content={"list": results})


BASE_URL = "https://anitaku.pe"
AJAX_URL = "https://ajax.gogocdn.net/ajax"


@app.get("/search/")
async def search(query: str, page: int = 1):
    async with httpx.AsyncClient() as client:
        url = f"{BASE_URL}/filter.html?keyword={query}&page={page}"
        response = await client.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    has_next_page = bool(soup.select(
        'div.anime_name.new_series > div > div > ul > li.selected').next())

    for item in soup.select('div.last_episodes > ul > li'):
        results.append({
            'id': item.select_one('p.name > a').get('href').split('/')[2],
            'title': item.select_one('p.name > a').text,
            'url': f"{BASE_URL}{item.select_one('p.name > a').get('href')}",
            'image': item.select_one('div > a > img').get('src'),
            'releaseDate': item.select_one('p.released').text.strip().replace('Released: ', ''),
            'subOrDub': 'DUB' if '(dub)' in item.select_one('p.name > a').text.lower() else 'SUB'
        })

    return {"currentPage": page, "hasNextPage": has_next_page, "results": results}


@app.get("/anime/{id}/")
async def fetch_anime_info(id: str):
    url = f"{BASE_URL}/category/{id}" if not id.startswith(BASE_URL) else id
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    anime_info = {
        'id': id.split('/')[-1],
        'title': soup.select_one('div.anime_info_body_bg > h1').text.strip(),
        'image': soup.select_one('div.anime_info_body_bg > img').get('src'),
        'releaseDate': soup.select_one('div.anime_info_body_bg > p:nth-child(8)').text.split('Released: ')[1],
        'description': soup.select_one('div.anime_info_body_bg > div:nth-child(6)').text.strip().replace('Plot Summary: ', ''),
        'genres': [a.text for a in soup.select('div.anime_info_body_bg > p:nth-child(7) > a')],
        'totalEpisodes': int(soup.select_one('#episode_page > li:last-child > a').get('ep_end', '0'))
    }

    episodes = []
    async with httpx.AsyncClient() as client:
        episode_list_url = f"{
            AJAX_URL}/load-list-episode?ep_start=1&ep_end={anime_info['totalEpisodes']}&id={id}&alias="
        episode_res = await client.get(episode_list_url)
    ep_soup = BeautifulSoup(episode_res.text, 'html.parser')

    for ep in ep_soup.select('#episode_related > li'):
        episodes.append({
            'id': ep.select_one('a').get('href').split('/')[1],
            'number': ep.select_one('div.name').text.replace('EP ', ''),
            'url': f"{BASE_URL}/{ep.select_one('a').get('href').strip()}"
        })

    anime_info['episodes'] = episodes
    return anime_info


@app.get("/episode/{episode_id}/sources/")
async def fetch_episode_sources(episode_id: str, server: str = "GogoCDN"):
    episode_url = f"{
        BASE_URL}/{episode_id}" if not episode_id.startswith("http") else episode_id
    async with httpx.AsyncClient() as client:
        response = await client.get(episode_url)

    soup = BeautifulSoup(response.text, 'html.parser')

    iframe_src = soup.select_one('#load_anime > div > div > iframe').get('src')
    sources = []

    if server == "GogoCDN":
        # Here you would extract sources from the GogoCDN extractor logic (implement separately)
        sources = ["source_from_gogo_cdn"]

    download_link = soup.select_one('.dowloads > a').get('href')
    return {"sources": sources, "download": download_link}


@app.get("/episode/{episode_id}/servers/")
async def fetch_episode_servers(episode_id: str):
    episode_url = f"{
        BASE_URL}/{episode_id}" if not episode_id.startswith(BASE_URL) else episode_id
    async with httpx.AsyncClient() as client:
        response = await client.get(episode_url)

    soup = BeautifulSoup(response.text, 'html.parser')
    servers = []

    for server in soup.select('div.anime_video_body > div.anime_muti_link > ul > li'):
        url = server.select_one('a').get('data-video')
        if not url.startswith('http'):
            url = f"https:{url}"
        servers.append({
            'name': server.select_one('a').text.strip(),
            'url': url
        })

    return servers


@app.get("/recent/")
async def fetch_recent_episodes(page: int = 1, type: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AJAX_URL}/page-recent-release.html?page={page}&type={type}")

    soup = BeautifulSoup(response.text, 'html.parser')
    recent_episodes = []

    for item in soup.select('div.last_episodes.loaddub > ul > li'):
        recent_episodes.append({
            'id': item.select_one('a').get('href').split('/')[1].split('-episode')[0],
            'episodeId': item.select_one('a').get('href').split('/')[1],
            'episodeNumber': item.select_one('p.episode').text.replace('Episode ', ''),
            'title': item.select_one('p.name > a').text,
            'image': item.select_one('div > a > img').get('src'),
            'url': f"{BASE_URL}{item.select_one('a').get('href')}"
        })

    has_next_page = not soup.select(
        'div.anime_name_pagination.intro > div > ul > li').last().has_class('selected')
    return {"currentPage": page, "hasNextPage": has_next_page, "results": recent_episodes}


@app.get("/genre/{genre}/")
async def fetch_genre_info(genre: str, page: int = 1):
    url = f"{BASE_URL}/genre/{genre}?page={page}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    genre_info = []

    for item in soup.select('div.last_episodes > ul > li'):
        genre_info.append({
            'id': item.select_one('p.name > a').get('href').split('/')[2],
            'title': item.select_one('p.name > a').text,
            'image': item.select_one('div > a > img').get('src'),
            'releaseDate': item.select_one('p.released').text.replace('Released: ', ''),
            'url': f"{BASE_URL}/{item.select_one('p.name > a').get('href')}"
        })

    has_next_page = not soup.select(
        'div.anime_name_pagination > div > ul > li').last().has_class('selected')
    return {"currentPage": page, "hasNextPage": has_next_page, "results": genre_info}


@app.get("/top-airing/")
async def fetch_top_airing(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AJAX_URL}/page-recent-release-ongoing.html?page={page}")

    soup = BeautifulSoup(response.text, 'html.parser')
    top_airing = []

    for item in soup.select('div.added_series_body.popular > ul > li'):
        top_airing.append({
            'id': item.select_one('a:nth-child(1)').get('href').split('/')[2],
            'title': item.select_one('a:nth-child(2)').text.split(',')[0].strip(),
            'image': item.select_one('a:nth-child(1) > div').get('style').match('(https?://.*.(?:png|jpg))')[0],
            'episodeId': item.select_one('p:nth-of-type(2) > a').get('title'),
            'episodeNumber': item.select_one('p:nth-of-type(2) > a').text.replace('Episode ', '')
        })

    has_next_page = not soup.select(
        'div.anime_name.comedy > div > div > ul > li').last().has_class('selected')
    return {"currentPage": page, "hasNextPage": has_next_page, "results": top_airing}


@app.get("/movies/recent/")
async def fetch_recent_movies(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AJAX_URL}/page-recent-release.html?page={page}&type=2")

    soup = BeautifulSoup(response.text, 'html.parser')
    recent_movies = []

    for item in soup.select('div.last_episodes > ul > li'):
        recent_movies.append({
            'id': item.select_one('p.name > a').get('href').split('/')[2],
            'title': item.select_one('p.name > a').text,
            'image': item.select_one('div > a > img').get('src'),
            'releaseDate': item.select_one('p.released').text.strip().replace('Released: ', ''),
            'url': f"{BASE_URL}{item.select_one('p.name > a').get('href')}"
        })

    has_next_page = not soup.select(
        'div.anime_name_pagination > div > ul > li').last().has_class('selected')
    return {"currentPage": page, "hasNextPage": has_next_page, "results": recent_movies}


@app.get("/episode/{episode_id}/anime-id/")
async def fetch_anime_id_from_episode_id(episode_id: str):
    episode_url = f"{
        BASE_URL}/{episode_id}" if not episode_id.startswith(BASE_URL) else episode_id
    async with httpx.AsyncClient() as client:
        response = await client.get(episode_url)

    soup = BeautifulSoup(response.text, 'html.parser')
    anime_link = soup.select_one(
        'div.anime_video_body > div.anime_muti_link > a').get('href')

    anime_id = anime_link.split('/')[-2]
    return {"animeId": anime_id}


@app.get("/popular/")
async def fetch_popular(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/popular.html?page={page}")

    soup = BeautifulSoup(response.text, 'html.parser')
    popular_anime = []

    for item in soup.select('div.last_episodes > ul > li'):
        popular_anime.append({
            'id': item.select_one('p.name > a').get('href').split('/')[2],
            'title': item.select_one('p.name > a').text,
            'image': item.select_one('div > a > img').get('src'),
            'releaseDate': item.select_one('p.released').text.strip().replace('Released: ', ''),
            'url': f"{BASE_URL}{item.select_one('p.name > a').get('href')}"
        })

    return {"results": popular_anime}


@app.get("/genres/")
async def fetch_genre_list():
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL)

    soup = BeautifulSoup(response.text, 'html.parser')
    genre_list = []

    for genre in soup.select('div.menu_series.genre > ul > li > a'):
        genre_list.append({
            'genre': genre.text.strip(),
            'url': f"{BASE_URL}{genre.get('href')}"
        })

    return {"genres": genre_list}


@app.get("/episode/{episode_id}/download/")
async def fetch_direct_download_link(episode_id: str):
    episode_url = f"{
        BASE_URL}/{episode_id}" if not episode_id.startswith(BASE_URL) else episode_id
    async with httpx.AsyncClient() as client:
        response = await client.get(episode_url)

    soup = BeautifulSoup(response.text, 'html.parser')
    download_link = soup.select_one('.dowloads > a').get('href')

    return {"download": download_link}


@app.get("/anime-list/")
async def fetch_anime_list(page: int = 1):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/anime-list.html?page={page}")

    soup = BeautifulSoup(response.text, 'html.parser')
    anime_list = []

    for item in soup.select('div.anime_list_body > ul > li'):
        anime_list.append({
            'id': item.select_one('a').get('href').split('/')[2],
            'title': item.select_one('a').text.strip(),
            'url': f"{BASE_URL}{item.select_one('a').get('href')}"
        })

    return {"currentPage": page, "results": anime_list}


# end ######################333

@app.get("/")
def read_root():
    return {"Hello": "vari"}


@app.get("/api/manga")
async def get_manga(server: str = Query(default='MANGANELO'), genre: Optional[str] = None, page: Optional[int] = None, type: Optional[str] = None):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        mangas = await scraper.scrape(genre=genre, page=page, type=type)
        return {"mangas": mangas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/manga/{manga_id}")
async def get_manga_details(server: str = Query(default='MANGANELO'), manga_id: str = Path(..., example="manga-tf996688")):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        manga_details = await scraper.get_manga_details(manga_id=manga_id)
        return manga_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/manga/{manga_id}/{chapter_id}")
async def get_manga_chapter_details(manga_id: str = Path(..., example="manga-tf996688"), chapter_id: str = Path(..., example="chapter-1"), server: str = Query(default='MANGANELO')):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        chapter_details = await scraper.get_chapter_details(manga_id=manga_id, chapter_id=chapter_id)
        return JSONResponse(content=chapter_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/search")
async def search_manga(word: str = Query(..., example="eternal"), page: Optional[int] = 1, server: str = Query(default='MANGANELO')):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        base_url = os.getenv(server)
        scraper_class = server_map[server]["scraper"]
        scraper = scraper_class(base_url)
        search_results = await scraper.search_manga(word=word, page=page)
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""Helper function to fetch image from a list of URLs

Returns:
    _type_: response
"""


async def fetch_image(image_urls: List[str]):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in image_urls:
            if url:
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response
                except httpx.HTTPStatusError:
                    continue
                except httpx.RequestError:
                    continue
    raise HTTPException(
        status_code=404, detail="Failed to fetch image from all sources")


"""for managanelo

Returns:
    _type_: image data
"""


@app.get("/api/mangaimage/{image}")
async def get_image_from_path(server: str = Query(default='MANGANELO'), image: str = Path(..., example="manga-tf996688.jpg")):
    logging.warning(f"heeeelo---------> {image}")
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        image_base_urls = server_map[server]["image_base_urls"]
        logging.warning(f"---------> {image_base_urls}")
        if not image_base_urls:
            raise HTTPException(
                status_code=404, detail=f"Image base URL not configured for server {server}")

        image_urls = [
            f"{base_url}/mangaimage/{image}" for base_url in image_base_urls if base_url]

        logging.warning(f"---------> {image_urls}")
        response = await fetch_image(image_urls)
        return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(exc)}")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Request error: {str(exc)}")


"""for managanelo

Returns:
    _type_: image data
"""


@app.get("/api/{id1}/{id2}/{image}")
async def get_image_from_path(server: str = Query(default='MANGANELO'), id1: str = Path(..., example="a4"), id2: str = Path(..., example="45"), image: str = Path(..., example="a4458a2fadf6cd005dc1a92a6ab8e4b3.jpg")):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        image_base_urls = server_map[server]["image_base_urls"]
        if not image_base_urls:
            raise HTTPException(
                status_code=404, detail=f"Image base URL not configured for server {server}")

        image_urls = [
            f"{base_url}/{id1}/{id2}/{image}" for base_url in image_base_urls if base_url]
        response = await fetch_image(image_urls)
        return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(exc)}")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Request error: {str(exc)}")


"""for mangaclash. might change it so that its modular cause it does the same as the one for manganelo just different paths

Returns:
    _type_: image data
"""


@app.get("/api/{id1}/{id2}/{id3}/{id4}/{image}")
async def get_image_from_path(server: str = Query(default='MANGACLASH'), id1: str = Path(..., example="wp-content"), id2: str = Path(..., example="uploads"), id3: str = Path(..., example="2020"), id4: str = Path(..., example="07"), image: str = Path(..., example="thumb_5f1547fc5a52a.jpg")):
    try:
        if server not in server_map:
            raise HTTPException(status_code=404, detail="Server not found")

        image_base_urls = server_map[server]["image_base_urls"]
        if not image_base_urls:
            raise HTTPException(
                status_code=404, detail=f"Image base URL not configured for server {server}")

        image_urls = [
            f"{base_url}/{id1}/{id2}/{id3}/{id4}/{image}" for base_url in image_base_urls if base_url]
        response = await fetch_image(image_urls)
        return StreamingResponse(response.iter_bytes(), media_type=response.headers["Content-Type"])
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch image: {str(exc)}")
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500, detail=f"Request error: {str(exc)}")


Instrumentator().instrument(app).expose(app)

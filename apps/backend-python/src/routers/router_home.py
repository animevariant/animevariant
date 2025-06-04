from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import logging

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def read_root():
    logging.debug("Root path accessed")
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Svelte Manga API</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-900 text-white font-sans">
        <div class="flex flex-col justify-center items-center h-screen text-center px-4">
            <h1 class="text-4xl font-bold mb-2 animate-fade-in text-purple-400">Svelte Manga API</h1>
            <p class="text-xl mb-6 animate-slide-in">Your gateway to anime watching and manga reading</p>
            
            <div class="flex flex-wrap justify-center gap-4 mb-8 animate-slide-in delay-300">
                <div class="bg-purple-900 bg-opacity-60 p-4 rounded-lg">
                    <h2 class="text-lg font-semibold mb-2">📚 Manga</h2>
                    <p class="text-sm">Browse and read your favorite manga</p>
                </div>
                <div class="bg-purple-900 bg-opacity-60 p-4 rounded-lg">
                    <h2 class="text-lg font-semibold mb-2">📺 Anime</h2>
                    <p class="text-sm">Stream and watch anime episodes</p>
                </div>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-4">
                <a href="/docs" class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition duration-300">
                    Swagger API Docs
                </a>
                <a href="/redoc" class="px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition duration-300">
                    ReDoc API Docs
                </a>
            </div>
        </div>
        <style>
            @keyframes fade-in {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            .animate-fade-in {
                animation: fade-in 1.5s ease-in-out;
            }
            @keyframes slide-in {
                0% { transform: translateY(-20px); opacity: 0; }
                100% { transform: translateY(0); opacity: 1; }
            }
            .animate-slide-in {
                animation: slide-in 1.5s ease-in-out;
            }
            .delay-300 {
                animation-delay: 300ms;
            }
        </style>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
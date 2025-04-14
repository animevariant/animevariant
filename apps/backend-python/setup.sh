docker build -t svelte-manga-api-image .
docker run --name svelte-manga-api-container -d -p 8000:8000 -v $(pwd):/code svelte-manga-api-image

#connect to turborepo/monorepo
git subtree add --prefix=apps/svelte-manga-api https://github.com/valiantlynx/svelte-manga-api.git main --squash
git subtree pull --prefix=apps/svelte-manga-api https://github.com/valiantlynx/svelte-manga-api.git main --squash
git subtree push --prefix=apps/svelte-manga-api https://github.com/valiantlynx/svelte-manga-api.git main

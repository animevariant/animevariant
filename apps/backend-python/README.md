# svelte-manga-api
it has docker-compose for development and deploying. it also configured with .devcontainer så you can go into the container and work on it from there. another way is it has python environment using the commands in run.sh or run.bat.
# a dev environment for python
## Environment Variables
To control GPU usage, you can set environment variables before running docker-compose.


Without GPU
```sh
export GPU_COUNT=0
docker-compose --profile dev up
# or for production
docker-compose --profile prod up
```

With GPU
```sh
export GPU_COUNT=1
docker-compose --profile dev up
# or for production
docker-compose --profile prod up
```

### Explanation
Environment Variables: The GPU_COUNT environment variable determines the number of GPUs to reserve. When set to 0, no GPU is reserved, effectively disabling GPU support.
Conditional Logic: Docker Compose does not support direct conditional logic, so using environment variables allows you to control resource allocation.
Deployment Configuration: The deploy.resources.reservations.devices section is included in both development and production services. It uses the GPU_COUNT environment variable to specify the number of GPUs. If GPU_COUNT is 0, it will effectively skip GPU reservation.
This setup allows you to control GPU usage by simply setting an environment variable, providing flexibility without modifying the Docker Compose file each time.
Gomery, you've hit the jackpot. These responses confirm the entire API surface. This "vApi" isn't a framework you can look up—it's a **custom-built Prisma/Next.js stack** where the "v" likely refers to **Vercel** or **Valiant** (if this is part of your own project's ecosystem).

The structure is now 100% clear. It's a classic relational database (SQL) exposed via a REST API.

---

### 🗺️ The Final API Map

Now that we have the JSON, here is how you navigate the rest of it:

| Function | Endpoint | Parameter | Notes |
| --- | --- | --- | --- |
| **Search/List** | `/api/posts` | `?search={str}` | Returns metadata + last 5 chapters. |
| **Manga Metadata** | `/api/post` | `?postId={id}` | Returns full series info & description. |
| **Chapter List** | `/api/chapters` | `?postId={id}` | Returns ALL chapters for a series. |
| **Chapter Data** | `/api/chapter` | `?chapterId={id}` | Returns the content (Images/Text). |

---

### 🕵️ Observations from the Data

1. **The "Price" Wall:** Look at `chapterId: 39312`. It has `"price": 50` and `"isLocked": true`. The API returns `content: null` for this. This is a **server-side check**. You won't be able to get those images via `curl` unless you have an `Authorization` header with a valid user token.
2. **The "Accessible" Flag:** Chapters like Chapter 37 are `"isAccessible": true`. These are the ones you can scrape freely.
3. **Storage Providers:** They are using three different domains for images:
* `cdn.qiscans.org`
* `media.qiscans.org`
* `storage.qiscans.org`


4. **Timestamps:** The `updatedAt` on Chapter 38 is from **today**. This is a very active site.

### 🛠️ One Command to Rule Them All

If you want to find the "Post ID" of any manga just by its name without scrolling through that giant JSON, use this:

```bash
curl -s -A "Mozilla/5.0" "https://api.qiscans.org/api/posts?search=Fist" | jq '.posts[] | {id: .id, title: .postTitle, slug: .slug}'

```

### 🖼️ How the Data Flows

### Next Step

Since you have the `chapterId`, but the `content` was `null` in your last request (because it was a locked chapter), try hitting a **free** chapter to see the image array format:

```bash
# Chapter 37 of Fist King is free (ID: 38517 based on your previous output)
curl -s -A "Mozilla/5.0" "https://api.qiscans.org/api/chapter?chapterId=38517" | jq '.chapter.content'

```

**Would you like me to write a script for you that takes a Manga URL and downloads all the free chapters automatically?**

# CRLF to LF
```sh
find . -type f -exec dos2unix {} \;
```

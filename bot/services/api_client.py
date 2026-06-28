import asyncio
import httpx


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=httpx.Timeout(8.0, connect=5.0))

    async def close(self):
        await self.client.aclose()

    async def request(self, method, url, retries=0, **kwargs):
        last_err = None
        for attempt in range(retries + 1):
            try:
                r = await self.client.request(method, url, **kwargs)
                if r.status_code == 404:
                    return None
                r.raise_for_status()
                return r.json()
            except Exception as e:
                last_err = e
                import sys
                print(f"[api_client] {method} {url} attempt {attempt+1}/{retries+1} failed: {e!r}", file=sys.stderr)
                if attempt < retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
        import sys
        print(f"[api_client] {method} {url} all retries exhausted, last: {last_err!r}", file=sys.stderr)
        return None

    async def ensure_user(self, tg_id, name=None):
        user = await self.get_user(tg_id)
        if user and user.get("id"):
            return user["id"]
        data = await self.request("POST", f"/user/{tg_id}", json={"name": name, "onboarding": None})
        if not data:
            return None
        return data.get("id")

    async def get_user(self, tg_id):
        return await self.request("GET", f"/user/{tg_id}")

    async def create_user(self, tg_id, name=None, onboarding=None):
        return await self.request("POST", f"/user/{tg_id}", json={"name": name, "onboarding": onboarding})

    async def post_diary(self, user_id, mood, energy, stress, sleep_quality, note):
        return await self.request(
            "POST",
            "/diary",
            json={
                "user_id": user_id,
                "mood": mood,
                "energy": energy,
                "stress": stress,
                "sleep_quality": sleep_quality,
                "note": note,
            },
        )

    async def get_stats(self, uid):
        return await self.request("GET", f"/stats/{uid}")

    async def get_articles(self):
        return await self.request("GET", "/content/articles")

    async def analyze_apnea(self, uid, file_bytes, filename):
        files = {"file": (filename, file_bytes, "application/octet-stream")}
        data = {"user_id": str(uid), "mode": "bot"}
        return await self.request("POST", "/apnea/analyze", data=data, files=files)

    async def post_focus(self, uid, minutes):
        return await self.request(
            "POST",
            "/focus",
            json={"user_id": uid, "duration_min": minutes, "completed": True},
        )

    async def get_leaderboard(self):
        return await self.request("GET", "/leaderboard")

    async def get_diary(self, uid):
        return await self.request("GET", f"/diary/{uid}")

    async def get_apnea_history(self, uid):
        return await self.request("GET", f"/apnea/history/{uid}")

    async def get_focus(self, uid):
        return await self.request("GET", f"/focus/{uid}")

import httpx
import settings


class PaperlessClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        kwargs["auth"] = httpx.BasicAuth(
            settings.PAPERLESS_USERNAME, settings.PAPERLESS_PASSWORD
        )
        kwargs["base_url"] = f"{settings.PAPERLESS_URL.removesuffix('/')}/api"
        super().__init__(*args, **kwargs)

    async def list_tags(self, *args, **kwargs):
        return await self.get("tags/", *args, **kwargs)

    async def create_tag(self, *args, **kwargs):
        return await self.post("tags/", *args, **kwargs)

    async def create_document(self, *args, **kwargs):
        return await self.post("documents/post_document/", *args, **kwargs)

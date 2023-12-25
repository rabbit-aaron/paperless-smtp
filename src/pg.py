import asyncio

from smtp import PaperlessHandler

ph = PaperlessHandler()
asyncio.run(ph.refresh_tag_mappings())
print(ph.tag_mappings)

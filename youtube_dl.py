import httpx
from user_agent import generate_user_agent

class youtube(object):
	def __init__(self):
		self.client = httpx.AsyncClient()
		self.user_agent = generate_user_agent()
	
	def header(self):
		headers = {
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			"Accept": "*/*",
			"X-Requested-With": "XMLHttpRequest",
			"User-Agent": self.user_agent,
			"Referer": "https://yt1s.com/en627"
		}
		return headers
		
	async def getURL(self, link: str):
		api_url = "https://yt1s.com/api/ajaxSearch/index"
		try:
			response = await self.client.post(
				api_url,
				headers=self.header(),
				data={
					"q": link,
					"vt": "home"
				}
			)
			if response.status_code == 200:
				return response.json()
			return None
		except:
			return None
	
	async def getDownload(self, key: str, vid: str, save: bool = False):
		api_url = "https://yt1s.com/api/ajaxConvert/convert"
		try:
			response = await self.client.post(
				api_url,
				headers=self.header(),
				data={
					"vid": vid,
					"k": key
				}
			)
			if response.status_code == 200:
				if save:
					download = await self.client.get(
						url=response.json()["dlink"]
					)
					if download.status_code == 200:
						content, name, ftype = (
							download.content,
							response.json()["title"],
							response.json()["ftype"]
						)
						with open(name + "." + ftype, "wb") as file:
							file.write(content)
						return True
					return False
				return response.json()
			return None
		except:
			return None

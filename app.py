from rubpy import Client, Message, handlers, models
from asyncio import run, create_task
from youtube_dl import youtube
import httpx
import random
import string

httpx_client = httpx.AsyncClient()
yt = youtube()
music_id: dict = {}

async def random_string() -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(7))

async def download(url: str) -> bytes:
	try:
		response = await httpx_client.get(url)
	except:
		return None
		
	if response.status_code == 200:
		return response.read()
		
	return None
	
async def SearchApi(text: str) -> list:
	try:
		request = await httpx_client.get(
			url = f"https://pipedapi.kavin.rocks/search?q={text}&filter=music_songs"
		)
	except:
		return None
		
	if request.status_code == 200:
		result = request.json()
		result_list = []
		for item in result.get("items"):
			item["url"] = "https://youtube.com" + item.get("url")
			result_list.append(
				{
					"title": item.get("title"),
					"url": item.get("url")
				}
			)
		return result_list
	return None
		
async def private_handler(client: Client, message: Message):
	if isinstance(message.raw_text, str):
		object_guid: str = message.object_guid
		message_id: str = message.message_id
		text: str = message.raw_text
		
		if text.startswith("!"):
			replace_text = text.replace("! ", "")
			search_result = await SearchApi(replace_text)
			if isinstance(search_result, list):
				list_music = ["🔎 نتایج یافت شده برای جستجوی شما:"]
				
				for result in search_result:
					_id = "#" + await random_string()
					music_id[_id] = result.get("url")
					list_music.append("نام: {}\nایدی دانلود: {}".format(result.get("title"), _id))
				
				list_music = "\n\n".join(list_music)
				await message.reply(list_music)
			else:
				await message.reply("خطا!")
		
		elif text.startswith("#"):
			if text in music_id.keys():
				await message.reply("درحال انجام عملیات . . .")
				result = await yt.getURL(music_id[text])
				
				if isinstance(result, dict):
					key = result.get("links").get("mp3").get("mp3128").get("k")
					vid_id = result.get("vid")
					dl_link = await yt.getDownload(vid=vid_id, key=key)

					if isinstance(dl_link, dict):
						music_bytes = await download(dl_link.get("dlink"))
						if isinstance(music_bytes, bytes):
							await client.send_music(
								object_guid = object_guid,
								music = music_bytes,
								file_name = dl_link.get("title") + ".mp3",
								performer = "youtube music",
								caption = dl_link.get("title"),
								reply_to_message_id = message_id
							)
						else:
							await message.reply("خطا در دانلود فایل!")
					else:
						await message.reply("خطا در دریافت اطلاعات!")
				else:
					await message.reply("خطا در دریافت اطلاعات!")
			else:
				await message.reply("موزیکی با این آیدی یافت نشد!")
	
async def main():
	async with Client(session="rubpy") as client:
		@client.on(handlers.MessageUpdates(models.is_private))
		async def updates_user(message: Message):
			create_task(private_handler(client, message))
			
		await client.run_until_disconnected()
		
run(main())

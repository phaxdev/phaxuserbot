import logging
import os
import requests
import asyncio
from phax import loader, utils

logger = logging.getLogger(__name__)

class x0Mod(loader.Module):
    """Uploads replied GIF or file to 0x0.st"""
    
    strings = {
        "name": "x0Uploader",
        "no_reply": "<b>🚫 Вы должны ответить (reply) на гифку или другой файл!</b>",
        "downloading": "<b>📥 Скачиваю файл...</b>",
        "uploading": "<b>📤 Загружаю на uguu.se...</b>",
        "error": "<b>🚫 Ошибка:</b> <code>{}</code>"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def x0(self, message):
        """- Ответьте на файл/гифку, чтобы загрузить на 0x0.st"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, self.strings("no_reply"))
            return

        message = await utils.answer(message, self.strings("downloading"))

        file_path = None
        try:
            # Download into physical file
            file_path = await reply.download_media()
            if not file_path:
                await utils.answer(message, self.strings("error").format("Не удалось скачать файл"))
                return
                
            message = await utils.answer(message, self.strings("uploading"))

            filename = os.path.basename(file_path)

            # Upload in thread to avoid blocking
            def upload():
                with open(file_path, "rb") as f:
                    files = {'files[]': (filename, f)}
                    r = requests.post('https://uguu.se/upload.php', files=files, timeout=60)
                return r

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, upload)

            if response.status_code == 200:
                data = response.json()
                url = data["files"][0]["url"]
                await utils.answer(message, f"<b>🔗 Ваша ссылка:</b> {utils.escape_html(url)}")
            else:
                await utils.answer(message, self.strings("error").format(f"HTTP {response.status_code}: {response.text}"))

        except Exception as e:
            await utils.answer(message, self.strings("error").format(str(e)))
        finally:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

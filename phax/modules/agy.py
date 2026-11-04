# meta developer: @phaxdev
# scope: phax_only
# scope: phax_userbot

import logging
import asyncio
import json
import time
import urllib.request
from phax import loader, utils

logger = logging.getLogger(__name__)

DAEMON_URL = "http://172.18.0.1:5005"

@loader.tds
class OpenCodeAgyMod(loader.Module):
    """Интеграция с OpenCode Antigravity (Gemini 3.8 Flash High)"""
    
    strings = {
        "name": "OpenCode Antigravity",
        "thinking": "<i>🤖 Gemini 3.8 Flash (OpenCode Antigravity) думает...</i>",
        "roasting": "<i>🔥 Подготавливаю прожарку...</i>",
        "summarizing": "<i>📝 Делаю выжимку...</i>",
        "error": "🚫 <b>Ошибка OpenCode Antigravity:</b>\n<code>{}</code>",
        "no_args": "ℹ️ <b>Использование:</b> <code>.agy &lt;запрос&gt;</code> или ответьте на сообщение.",
        "no_reply_roast": "ℹ️ <b>Ответьте на сообщение</b>, которое нужно прожарить: <code>.roast</code>",
        "no_reply_sum": "ℹ️ <b>Ответьте на сообщение</b>, из которого сделать выжимку: <code>.sum</code>",
    }

    async def client_ready(self, client, db):
        self.client = client

    def _query_daemon(self, payload: dict, timeout: int = 45) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            DAEMON_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _get_daemon_status(self) -> dict:
        req = urllib.request.Request(DAEMON_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @loader.command(
        ru_doc="<запрос или реплай> - Задать вопрос Gemini 3.8 Flash через аккаунт OpenCode Antigravity"
    )
    async def agy(self, message):
        """<prompt or reply> - Ask Gemini 3.8 Flash via OpenCode Antigravity"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        prompt = ""
        if reply and getattr(reply, "text", None):
            if args:
                prompt = f"Контекст сообщения собеседника:\n\"\"\"{reply.text}\"\"\"\n\nМой запрос:\n{args}"
            else:
                prompt = f"Ответь на следующее сообщение собеседника:\n\"\"\"{reply.text}\"\"\""
        elif args:
            prompt = args
        else:
            await utils.answer(message, self.strings("no_args"))
            return

        message = await utils.answer(message, self.strings("thinking"))

        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                self._query_daemon,
                {"prompt": prompt, "mode": "raw", "model": "gemini-3.8-flash-high"}
            )

            out = resp.get("stdout") or resp.get("text") or ""
            err = resp.get("stderr", "")

            if out:
                # Telegram max message length is 4096
                if len(out) > 4000:
                    out = out[:3990] + "\n\n<i>[текст обрезан по лимиту Telegram]</i>"
                await utils.answer(message, f"<b>🤖 Gemini 3.8 Flash:</b>\n\n{out}")
            elif err:
                await utils.answer(message, self.strings("error").format(utils.escape_html(err)))
            else:
                await utils.answer(message, "🚫 Получен пустой ответ от API.")

        except Exception as e:
            await utils.answer(message, self.strings("error").format(utils.escape_html(str(e))))

    @loader.command(
        ru_doc="<запрос или реплай> - Быстрый алиас для команды .agy"
    )
    async def ai(self, message):
        """<prompt or reply> - Alias for .agy"""
        await self.agy(message)

    @loader.command(
        ru_doc="[в реплай] - Жестко и остроумно прожарить сообщение собеседника"
    )
    async def roast(self, message):
        """[reply] - Roast the replied message"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        target_text = ""
        if reply and getattr(reply, "text", None):
            target_text = reply.text
            if args:
                target_text += f"\nДополнительный контекст: {args}"
        elif args:
            target_text = args
        else:
            await utils.answer(message, self.strings("no_reply_roast"))
            return

        message = await utils.answer(message, self.strings("roasting"))

        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                self._query_daemon,
                {"prompt": target_text, "mode": "roast", "model": "gemini-3.8-flash-high"}
            )
            out = resp.get("stdout") or resp.get("text") or ""
            if out:
                await utils.answer(message, f"🔥 <b>Прожарка:</b>\n\n{out}")
            else:
                await utils.answer(message, "🚫 Не удалось сгенерировать ответ.")
        except Exception as e:
            await utils.answer(message, self.strings("error").format(utils.escape_html(str(e))))

    @loader.command(
        ru_doc="[в реплай] - Сделать краткую выжимку сообщения или переписки"
    )
    async def sum(self, message):
        """[reply] - Summarize the replied text"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        target_text = ""
        if reply and getattr(reply, "text", None):
            target_text = reply.text
            if args:
                target_text += f"\nПожелание: {args}"
        elif args:
            target_text = args
        else:
            await utils.answer(message, self.strings("no_reply_sum"))
            return

        message = await utils.answer(message, self.strings("summarizing"))

        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                self._query_daemon,
                {"prompt": target_text, "mode": "summary", "model": "gemini-3.8-flash-high"}
            )
            out = resp.get("stdout") or resp.get("text") or ""
            if out:
                await utils.answer(message, f"📝 <b>Выжимка:</b>\n\n{out}")
            else:
                await utils.answer(message, "🚫 Не удалось сделать выжимку.")
        except Exception as e:
            await utils.answer(message, self.strings("error").format(utils.escape_html(str(e))))

    @loader.command(
        ru_doc="- Проверить статус OpenCode Antigravity, задержку и подключенный аккаунт Google"
    )
    async def agystatus(self, message):
        """- Show OpenCode Antigravity daemon status and Google account"""
        t0 = time.time()
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._get_daemon_status)
            latency = int((time.time() - t0) * 1000)

            status_text = (
                "🟢 <b>OpenCode Antigravity Online</b>\n\n"
                f"👤 <b>Аккаунт:</b> <code>{info.get('account', 'unknown')}</code>\n"
                f"🧠 <b>Модель:</b> <code>{info.get('model', 'gemini-3.8-flash-high')}</code>\n"
                f"📁 <b>Google Cloud Project:</b> <code>{info.get('project', '1')}</code>\n"
                f"📡 <b>Пинг к демону:</b> <code>{latency} мс</code>\n"
                f"⚙️ <b>Эндпоинт:</b> <code>{DAEMON_URL}</code>\n\n"
                "<i>Все запросы идут напрямую через твой Google CloudCode OAuth токен из OpenCode без лимитов.</i>"
            )
            await utils.answer(message, status_text)
        except Exception as e:
            await utils.answer(
                message,
                f"🔴 <b>OpenCode Antigravity Offline</b>\n\n<code>{utils.escape_html(str(e))}</code>"
            )

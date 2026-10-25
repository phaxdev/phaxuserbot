import logging
import asyncio
import json
import urllib.request
from phax import loader, utils

logger = logging.getLogger(__name__)

class AgyMod(loader.Module):
    """Antigravity Integration Mod"""
    
    strings = {
        "name": "Antigravity",
        "thinking": "<i>🤖 Antigravity (AGY CLI) is executing your command...</i>",
        "error": "🚫 <b>Error:</b> <code>{}</code>"
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.command()
    async def agy(self, message):
        """<prompt> - Execute command via Antigravity CLI"""
        prompt = utils.get_args_raw(message)
        if not prompt:
            await utils.answer(message, "What should I do? Use `.agy <request>`")
            return

        message = await utils.answer(message, self.strings("thinking"))
        
        try:
            # We send the prompt to our local daemon running on the host
            # Docker default gateway is usually 172.18.0.1 or 172.17.0.1
            # We binded daemon to 172.18.0.1:5005
            data = json.dumps({"prompt": prompt}).encode("utf-8")
            req = urllib.request.Request("http://172.18.0.1:5005", data=data, headers={'Content-Type': 'application/json'})
            
            def do_request():
                with urllib.request.urlopen(req, timeout=300) as response:
                    return json.loads(response.read().decode())
            
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(None, do_request)
            
            out = resp.get("stdout", "")
            err = resp.get("stderr", "")
            
            if out:
                # Truncate if too long, PHAX utils.answer handles chunking but we want to be safe
                result = out
            elif err:
                result = "Error output:\n" + err
            else:
                result = "Command executed successfully with no output."
                
            await utils.answer(message, f"<b>Result:</b>\n<pre>{utils.escape_html(result[:4000])}</pre>")
            
        except Exception as e:
            await utils.answer(message, self.strings("error").format(str(e)))

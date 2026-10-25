# meta developer: @antigravity
from .. import loader, utils
import asyncio
import random

@loader.tds
class EmojiAnimMod(loader.Module):
    """Крутые анимации со смайликами"""
    strings = {"name": "EmojiAnim"}

    @loader.command(
        ru_doc="<текст> - Анимация с бегающим туда-сюда смайликом"
    )
    async def tudasudacmd(self, message):
        """<text> - Run back-and-forth emoji animation"""
        text = utils.get_args_raw(message) or "Туда-сюда миллионер"
        
        emojis = ["😀", "😎", "🚀", "🔥", "👽", "👻", "🤡", "👾", "💩", "🤖", "🤠", "🤪", "😈", "🌚", "💥"]
        
        length = 8
        frames = []
        
        # Туда (слева направо)
        for i in range(length):
            left = "➖" * i
            right = "➖" * (length - i - 1)
            emoji = random.choice(emojis)
            frames.append(f"{left}{emoji}{right}\n<b>{text}</b>")
            
        # Сюда (справа налево)
        for i in range(length - 2, 0, -1):
            left = "➖" * i
            right = "➖" * (length - i - 1)
            emoji = random.choice(emojis)
            frames.append(f"{left}{emoji}{right}\n<b>{text}</b>")
            
        # Прогоняем анимацию 3 раза
        full_anim = frames * 3
        
        for frame in full_anim:
            try:
                await utils.answer(message, frame)
                await asyncio.sleep(0.3)
            except Exception:
                break
                
        # В конце оставляем финальный красивый текст
        final_emojis = "".join(random.choices(emojis, k=5))
        await utils.answer(message, f"{final_emojis}\n<b>{text}</b>\n{final_emojis}")

    @loader.command(
        ru_doc="<текст> - Анимация с хаотично меняющимися смайликами"
    )
    async def crazyemojicmd(self, message):
        """<text> - Run crazy emoji animation"""
        text = utils.get_args_raw(message) or "Супер текст!"
        emojis = ["😀","😃","😄","😁","😆","😅","😂","🤣","🥲","☺️","😊","😇","🙂","🙃","😉","😌","😍","🥰","😘","😗","😙","😚","😋","😛","😝","😜","🤪","🤨","🧐","🤓","😎","🥸","🤩","🥳","😏","😒","😞","😔","😟","😕","🙁","☹️","😣","😖","😫","😩","🥺","😢","😭","😤","😠","😡","🤬","🤯","😳","🥵","🥶","😱","😨","😰","😥","😓","🤗","🤔","🤭","🤫","🤥","😶","😐","😑","😬","🙄","😯","😦","😧","😮","😲","🥱","😴","🤤","😪","😵","🤐","🥴","🤢","🤮","🤧","😷","🤒","🤕","🤑","🤠","😈","👿","👹","👺","🤡","💩","👻","💀","☠️","👽","👾","🤖","🎃","😺","😸","😹","😻","😼","😽","🙀","😿","😾"]
        
        for _ in range(15):
            line1 = "".join(random.choices(emojis, k=6))
            line2 = "".join(random.choices(emojis, k=6))
            
            frame = f"{line1}\n✨ <b>{text}</b> ✨\n{line2}"
            try:
                await utils.answer(message, frame)
                await asyncio.sleep(0.3)
            except Exception:
                break
                
        # Final frame
        await utils.answer(message, f"🔥 <b>{text}</b> 🔥")

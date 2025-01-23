
from aiogram.filters import Filter
from aiogram.types import Message
from models import is_registered

from text import translations

class Registered(Filter):

    def __init__(self,) -> None:
        return
    
    async def __call__(self, message: Message) -> bool:
        answer = await is_registered(message.from_user.id)
        return answer



class CheckCommand(Filter):
    def __init__(self, comandName: str) -> None:
        self.comandName = comandName


    async def __call__(self, message: Message) -> bool:
        return message.text in [translations["ru"][self.comandName], translations["uz"][self.comandName], translations["standart"][self.comandName]] and message.chat.type == "private" 
    


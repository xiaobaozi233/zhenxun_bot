from nonebot import on_regex
from .data_source import get_weather_of_city, get_city_list
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from jieba import posseg
from services.log import logger
from nonebot.params import RegexGroup
from typing import Tuple, Any
import json
from configs.path_config import TEXT_PATH
weather_descriptions = TEXT_PATH / "weather_descriptions.json"

__zx_plugin_name__ = "天气查询"
__plugin_usage__ = """
usage：
    普普通通的查天气吧
    指令：
        [城市]天气
""".strip()
__plugin_des__ = "出门要看看天气，不要忘了带伞"
__plugin_cmd__ = ["[城市]天气/天气[城市]"]
__plugin_type__ = ("一些工具",)
__plugin_version__ = 0.1
__plugin_author__ = "HibiKier"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["查询天气", "天气", "天气查询", "查天气"],
}


weather = on_regex(r".{0,10}?(.*)的?天气.{0,10}", priority=5, block=True)
def load_weather_descriptions(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

@weather.handle()
async def _(event: MessageEvent, reg_group: Tuple[Any, ...] = RegexGroup()):
    msg = reg_group[0]
    
    weather_descriptions_data = load_weather_descriptions(weather_descriptions)

    if msg in weather_descriptions_data:
        await weather.finish(weather_descriptions_data[msg])
        return

    if msg and msg[-1] != "市":
        msg += "市"

    if msg in weather_descriptions_data:
        await weather.finish(weather_descriptions_data[msg])
        return

    city = ""
    if msg:
        city_list = get_city_list()
        words = posseg.lcut(msg)
        found = False
        for word in words:
            key = word.word
            if key in weather_descriptions_data:
                await weather.finish(weather_descriptions_data[key])
                found = True
                break
            if not found and (word.flag == "ns" or word.word[:-1] in city_list):
                city = str(word.word).strip()
                break
    
    if city:
        city_weather = await get_weather_of_city(city)
        logger.info(
            f'(USER {event.user_id}, GROUP {event.group_id if isinstance(event, GroupMessageEvent) else "private"} ) '
            f"查询天气:" + city
        )
        await weather.finish(city_weather)


import datetime
from ..utils import *

base_url = get_base_url()
common = base_url + "SchaleDB/data/config.json"
localization = base_url + "SchaleDB/data/cn/localization.json"
raids = base_url + "SchaleDB/data/cn/raids.min.json"
student_cn = base_url + "SchaleDB/data/cn/students.min.json"
student_jp = base_url + "SchaleDB/data/jp/students.min.json"


async def extract_calendar_data(server):
    event_list = []

    common_data = await get_json_data(common)
    student_data = await get_json_data(student_cn)
    localization_data = await get_json_data(localization)
    raid_data = await get_json_data(raids)
    if common_data is None or student_data is None or localization_data is None or raid_data is None:
        return None

    if server == "jp":
        data = common_data["Regions"][0]
    else:
        data = common_data["Regions"][1]

    # gacha
    for gacha in data["CurrentGacha"]:
        characters = gacha["characters"]
        for character in characters:
            stu_info = get_item(student_data, "Id", character)
            title = "本期卡池: " + stu_info["Name"]
            start_time = datetime.datetime.fromtimestamp(gacha["start"]).strftime("%Y/%m/%d %H:%M")
            end_time = datetime.datetime.fromtimestamp(gacha["end"]).strftime("%Y/%m/%d %H:%M")
            event_list.append({'title': title, 'start': start_time, 'end': end_time})

    # event
    for event in data["CurrentEvents"]:
        event_rerun = ""
        event_id = event["event"]
        # 复刻活动似乎是在原id前面加上10
        if event_id > 1000:
            event_id = str(event_id)[2:]
            event_rerun = "(复刻)"
        event_name = localization_data["EventName"][str(event_id)] + event_rerun
        start_time = datetime.datetime.fromtimestamp(event["start"]).strftime("%Y/%m/%d %H:%M")
        end_time = datetime.datetime.fromtimestamp(event["end"]).strftime("%Y/%m/%d %H:%M")
        event_list.append({'title': event_name, 'start': start_time, 'end': end_time})

    # raid
    for raid in data["CurrentRaid"]:
        raid_id = raid["raid"]
        title = ""
        # 总力
        if raid_id < 999:
            raid_info = get_item(raid_data["Raid"], "Id", raid_id)
            title = "总力战: " + raid_info["Name"]
            if "terrain" in raid:
                title = title + f'({raid["terrain"]})'
        # 演习
        if raid_id > 999 and raid_id < 99999:
            dungeon_types = {"Shooting": "射击", "Defense": "防御", "Destruction": "突破"}
            raid_info = get_item(raid_data["TimeAttack"], "Id", raid_id)
            title = raid_info["DungeonType"]
            if raid_info["DungeonType"] in dungeon_types:
                title = dungeon_types[raid_info["DungeonType"]]
            title += "演习"
            if "Terrain" in raid_info:
                title = title + f'({raid_info["Terrain"]})'
        # 世界boss
        if raid_id > 800000 and raid_id < 900000:
            raid_info = get_item(raid_data["WorldRaid"], "Id", raid_id)
            title = raid_info["Name"]

        if title != "":
            start_time = datetime.datetime.fromtimestamp(raid["start"]).strftime("%Y/%m/%d %H:%M")
            end_time = datetime.datetime.fromtimestamp(raid["end"]).strftime("%Y/%m/%d %H:%M")
            event_list.append({'title': title, 'start': start_time, 'end': end_time})
    return event_list


async def transform_schaledb_calendar(server):
    data = await extract_calendar_data(server)
    return data

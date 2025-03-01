from .draw import *
from .event import *

server_name = {
    'jp': '日服',
    'cn': '国服',
    'global': '国际服',
    'en-jp': '日服',
    'db-jp': '日服',
    'db-global': '国际服'
}


async def generate_day_schedule(server='jp'):
    events = await get_events(server, 0, 7)

    has_prediction = False
    title_len = 25
    for event in events:
        if event['start_days'] > 0:
            has_prediction = True
        title_len = max(title_len, len(event['title']) + 5)
    if has_prediction:
        im = create_image(len(events) + 2, title_len)
    else:
        im = create_image(len(events) + 1, title_len)

    title = f'碧蓝档案{server_name[server]}活动'
    ba_now = get_ba_now(0)
    draw_title(im, 0, title, ba_now.strftime('%Y/%m/%d'), '正在进行')

    if len(events) == 0:
        draw_item(im, 1, 1, '无数据', 0)
    i = 1
    for event in events:
        if event['start_days'] <= 0:
            draw_item(im, i, event['type'], event['title'], event['left_days'])
            i += 1
    if has_prediction:
        draw_title(im, i, right='即将开始')
        for event in events:
            if event['start_days'] > 0:
                i += 1
                draw_item(im, i, event['type'], event['title'], -event['start_days'])
    return im

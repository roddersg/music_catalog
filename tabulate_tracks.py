headers = ["Trk", "Performer", "Title", "Duration"]

tracks = [
    [1, "Teresa Teng [邓丽君]", "Forget Tonight [莫忘今宵]", "3:56"],
    [2, "Teresa Teng [邓丽君]", "Moment Of Truth [人面桃花]", "4:12"],
    [3, "Teresa Teng [邓丽君]", "Rhine [海韻]", "3:14"],
    [4, "Teresa Teng [邓丽君]", "Sweet Honey [甜蜜蜜]", "3:32"],
    [5, "Teresa Teng [邓丽君]", "Alone In My Chamber [獨上西樓]", "2:45"],
    [6, "Teresa Teng [邓丽君]", "Lover [愛人]", "3:48"],
    [7, "Teresa Teng [邓丽君]", "You Come Again [何日君再來]", "2:55"],
    [8, "Teresa Teng [邓丽君]", "Charmant [小城故事]", "2:39"],
    [9, "Teresa Teng [邓丽君]", "Repayment Of [償還]", "3:52"],
    [10, "Teresa Teng [邓丽君]", "I Only Care About You [我只在乎你]", "4:17"],
    [11, "Teresa Teng [邓丽君]", "The Moon Represents My Heart [月亮代表我的心]", "3:31"],
    [12, "Teresa Teng [邓丽君]", "Valentine's Care [情人的關懷]", "3:48"],
    [13, "Teresa Teng [邓丽君]", "Love For Winter [冬之戀情]", "3:42"],
    [14, "Teresa Teng [邓丽君]", "Surprisingly, I Love This Time [有誰知我此時情]", "3:52"],
    [15, "Teresa Teng [邓丽君]", "Nung [但愿人長久]", "4:03"],
]

songs =[trk[2] for trk in tracks]

catalog = [
    [
        24506,
        "Teresa Teng",
        1979,
        "1979 Island Of Love Songs Vol 6 Charmant [島國情歌第六集 小城故事]",
    ],
    [24507, "Teresa Teng", 1979, "1979 Sweet Honey [甜蜜蜜]"],
    [24508, "Teresa Teng", 1980, "1980 Deep Feelings For Homeland [原鄉情濃]"],
    [24509, "Teresa Teng", 1980, "1980 In The Water Side [在水一方]"],
    [24510, "Teresa Teng", 1980, "1980 One Little Wish [一個小心願]"],
    [
        24511,
        "Teresa Teng",
        1981,
        "1981 Island Of Love Songs Vol 7 If I Were Real [島國情歌第七集 假如我是真的]",
    ],
    [24512, "Teresa Teng", 1981, "1981 Love Is Like A Song [愛像一首歌]"],
    [24513, "Teresa Teng", 1981, "1981 Water People [水上人]"],
    [24514, "Teresa Teng", 1982, "1982 Dandan Youqing [淡淡幽情]"],
    [24515, "Teresa Teng", 1982, "1982 First Taste Of Loneliness [初次嚐到寂寞]"],
    [24518, "Teresa Teng", 1982, "1984 Repay [償還]"],
    [24516, "Teresa Teng", 1983, "1983 Dandan Youqing [淡淡幽情]"],
    [
        24517,
        "Teresa Teng",
        1984,
        "1984 Island Of Love Songs Vol 9 Messenger Of Love[島國情歌第八集 愛的使者]",
    ],
    [24519, "Teresa Teng", 1987, "1987 I Only Care About You [我只在乎你]"],
    [24520, "Teresa Teng", 1992, "1992 Memorable [難忘的]"],
    [24521, "Teresa Teng", 2007, "Complete Singles Box CD01]"],
    [24522, "Teresa Teng", 2007, "Complete Singles Box CD02 (1980-1987)]"],
    [24523, "Teresa Teng", 2007, "Complete Singles Box CD03 (1988-1994)]"],
    [24524, "Teresa Teng", 2007, "Complete Singles Box CD04 (1974-1978)]"],
    [
        24525,
        "Teresa Teng",
        2012,
        "The 60th Anniversary Of Teresa Teng's Birth [生诞60年 纪念专辑] CD01]",
    ],
    [
        24526,
        "Teresa Teng",
        2012,
        "The 60th Anniversary Of Teresa Teng's Birth [生诞60年 纪念专辑] CD02]",
    ],
]

# Chinese Support-----------------------------------------------------------------------
import re

re_chinese = re.compile(
    r"[\u4e00-\u9fa5\！\？\。\＂\＇\（\）\＊\＋\，\－\／\：\；\＜\＝\＞\＠\［\＼\］\＾\＿\｀\｛\｜\｝\～\｟\｠\、\〃\《\》\「\」\『\』\【\】\〔\〕\〖\〗\〘\〙\〚\〛\〜\〝\〞\〟\〰\〾\〿\–\—\‘\’\‛\“\”\„\‟\…\‧\﹏\．]",
    re.S,
)

# chinese_chars = re_chinese.findall("".join([i[1] for i in tracks]))

# for song in songs:
#     print(re_chinese.findall(song))

# wcwith
# from wcwidth import wcswidth

# width = 62
# for song in songs:
#     pad = width - wcswidth(song)
#     print(f"|{song}{' '*pad}|")

from tabulate import tabulate
import textwrap

tabulate.WIDE_CHARS_MODE = True

headers = ['Id', 'Artist', 'Date', 'Title']

a_id = [c[0] for c in catalog]
a_artist = [textwrap.shorten(c[1],20,placeholder="...") for c in catalog]
a_date = [c[2] for c in catalog]
a_title = [textwrap.shorten(c[3],50,placeholder="...") for c in catalog]

new_catalog = list(zip(a_id, a_artist, a_date, a_title))
print(tabulate(new_catalog, headers))

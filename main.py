from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from lunar_python import Solar

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# 宫位顺序按洛书：坎 坤 震 巽 中 乾 兑 艮 离
PALACES = [
    {"name": "坎", "pos": "北"},
    {"name": "坤", "pos": "西南"},
    {"name": "震", "pos": "东方"},
    {"name": "巽", "pos": "东南"},
    {"name": "中", "pos": "中宫"},
    {"name": "乾", "pos": "西北"},
    {"name": "兑", "pos": "西"},
    {"name": "艮", "pos": "东北"},
    {"name": "离", "pos": "南"}
]

# 地盘干固定（洛书）
DI_PAN = ["己", "庚", "辛", "壬", "戊", "癸", "丁", "丙", "乙"]
TIAN_PAN_BASE = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]
MEN = ["休", "死", "伤", "杜", "开", "惊", "生", "景", "伏"]
XING = ["蓬", "任", "冲", "辅", "英", "芮", "柱", "心", "禽"]
SHEN = ["值符", "螣蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天", "值使"]

DUN_TYPE = "阳遁"
JU = 1

def get_tian_pan(dun: str, ju: int):
    rotated = [None] * 9
    for i in range(9):
        if dun == "阳遁":
            rotated[(i + ju) % 9] = TIAN_PAN_BASE[i]
        else:
            rotated[(i - ju) % 9] = TIAN_PAN_BASE[i]
    return rotated

def get_star_positions(start: int, dun: str):
    stars = [None] * 9
    for i in range(9):
        pos = (start + i) % 9 if dun == "阳遁" else (start - i) % 9
        stars[pos] = XING[i]
    return stars

def get_door_positions(start: int, dun: str):
    doors = [None] * 9
    for i in range(9):
        pos = (start + i) % 9 if dun == "阳遁" else (start - i) % 9
        doors[pos] = MEN[i]
    return doors

def qimen_pan():
    tian_pan = get_tian_pan(DUN_TYPE, JU)
    zhi_fu_start = 4  # 中宫起布九星
    zhi_shi_start = 0  # 坎宫起布八门

    stars = get_star_positions(zhi_fu_start, DUN_TYPE)
    doors = get_door_positions(zhi_shi_start, DUN_TYPE)

    chart = []
    for i in range(9):
        chart.append({
            "宫位": PALACES[i]["name"],
            "方向": PALACES[i]["pos"],
            "编号": i + 1,
            "地盘干": DI_PAN[i],
            "天盘干": tian_pan[i],
            "九星": stars[i],
            "八门": doors[i],
            "八神": SHEN[i]
        })
    return chart

@app.get("/api/qimen")
def get_chart():
    now = datetime.now()
    solar = Solar.fromDate(now)
    lunar = solar.getLunar()

    return {
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "lunar_date": lunar.toString(),
        "ganzhi": {
            "year": lunar.getYearInGanZhi(),
            "month": lunar.getMonthInGanZhi(),
            "day": lunar.getDayInGanZhi(),
            "time": lunar.getTimeInGanZhi()
        },
        "dun": DUN_TYPE,
        "ju": JU,
        "chart": qimen_pan()
    }

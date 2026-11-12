CLUSTER_ORDER = ["通勤型", "城際樞紐", "週末觀光型", "春季活動型", "寒暑假觀光型（集集線）"]
CLUSTER_COLOR = {"通勤型": "#2a78d6", "城際樞紐": "#eb6834", "週末觀光型": "#1baf7a",
                 "春季活動型": "#eda100", "寒暑假觀光型（集集線）": "#e87ba4"}
CLUSTER_ID = {4: "通勤型", 1: "城際樞紐", 2: "週末觀光型", 0: "春季活動型", 3: "寒暑假觀光型（集集線）"}
CONTRAST_GREY = "#898781"
CASES = ["汐科", "南港", "內灣", "白沙屯"]
QUAKE = ("2024-04-03", "2024-06-30")
WINDOW = ("2024-01-01", "2026-07-31")
DOW_LABEL = ["一", "二", "三", "四", "五", "六", "日"]
FOOTER = "資料來源：臺鐵每日各站進出站人數（data.gov.tw/dataset/8792）；分群為本作品計算結果"


def base_layout() -> dict:
    return dict(
        paper_bgcolor="#fcfcfb",
        plot_bgcolor="#fcfcfb",
        font=dict(size=13, color="#0b0b0b"),
        margin=dict(l=50, r=20, t=60, b=40),
        hoverlabel=dict(font_size=13),
    )


SUBTYPE_ORDER = {
    "通勤型": ["住宅生活型", "商辦就業型", "未符合核心條件"],
    "城際樞紐": ["旅運與周邊商業落差型", "商業服務集中型", "未符合核心條件"],
    "週末觀光型": ["自然休閒型", "未符合核心條件"],
    "春季活動型": ["不細分"],
    "寒暑假觀光型（集集線）": ["不細分"],
}

SUBTYPE_GREY = "#898781"
_SUBTYPE_PALETTE = ["#2a78d6", "#eb6834"]

SUBTYPE_COLOR = {}
for _subs in SUBTYPE_ORDER.values():
    for _i, _s in enumerate(_subs):
        SUBTYPE_COLOR[_s] = (SUBTYPE_GREY if _s in ("未符合核心條件", "不細分")
                             else _SUBTYPE_PALETTE[_i])

DATA_ASOF = "人次資料至 2026/7/31；稅籍、土地使用、出租表、Google Maps（2026/11/7）各有時點，見各頁說明"

DEMO_STATIONS = ["沙崙", "汐科"]
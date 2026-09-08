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
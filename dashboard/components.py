"""
components.py
建立：2026-08-31（AI 輔助，附件 4 C 類；只負責把業態表排成 HTML，內容逐字來自 cluster_business_table.csv）
"""

import html

import pandas as pd

from style import CLUSTER_COLOR

_LABEL_TO_CLUSTER = {
    "通勤型 >1 萬": "通勤型",
    "通勤型 <1 萬": "通勤型",
    "寒暑假觀光型": "寒暑假觀光型（集集線）",
}


def _cluster_of(label: str) -> str:
    return _LABEL_TO_CLUSTER.get(label, label)


def _bullets(text: str) -> str:
    """「A、B、C；備註」→ <ul> 三點＋灰色備註"""
    text = str(text)
    main, _, note = text.partition("；")
    items = [html.escape(t.strip()) for t in main.split("、") if t.strip()]
    out = "<ul style='margin:0;padding-left:1.1em'>" + "".join(f"<li>{t}</li>" for t in items) + "</ul>"
    if note.strip():
        out += f"<div style='color:#898781;font-size:12px;margin-top:4px'>{html.escape(note.strip())}</div>"
    return out


def _flow(text: str) -> str:
    """人流性質：「誰、何時；數字」→ 第一段正常、數字段灰色"""
    text = str(text)
    who, _, num = text.partition("；")
    out = html.escape(who.strip())
    if num.strip():
        out += f"<div style='color:#52514e;font-size:12px;margin-top:4px'>{html.escape(num.strip())}</div>"
    return out


def badge(text: str, color: str) -> str:
    return (f"<span style='background:{color};color:#fff;padding:2px 8px;border-radius:6px;"
            f"font-size:12px;white-space:nowrap'>{html.escape(text)}</span>")


def business_table_html(business: pd.DataFrame, current_label: str | None = None) -> str:
    """六列業態表 → HTML；current_label 那列加群色左框與底色。"""
    th = "style='text-align:left;padding:8px 10px;background:#f0efec;color:#52514e;font-weight:600;font-size:12px'"
    head = "".join(f"<th {th}>{h}</th>" for h in ["站型", "人流性質", "適合業態", "不適合", "對照"])
    rows = []
    for r in business.itertuples(index=False):
        color = CLUSTER_COLOR[_cluster_of(r.label)]
        is_cur = r.label == current_label
        bg = f"background:{color}14;" if is_cur else ""
        border = f"border-left:4px solid {color};" if is_cur else "border-left:4px solid transparent;"
        td = f"style='padding:10px;vertical-align:top;border-bottom:1px solid #e1e0d9;{bg}'"
        first = (f"<td style='padding:10px;vertical-align:top;border-bottom:1px solid #e1e0d9;{bg}{border}'>"
                 f"{badge(r.label, color)}<div style='color:#898781;font-size:12px;margin-top:6px'>{r.n_stations} 站"
                 f"{'　◀ 目前' if is_cur else ''}</div></td>")
        rows.append(
            f"<tr>{first}"
            f"<td {td}>{_flow(r.flow_profile)}</td>"
            f"<td {td}>{_bullets(r.suitable)}</td>"
            f"<td {td}>{_bullets(r.unsuitable)}</td>"
            f"<td {td}>{html.escape(str(r.reference))}</td></tr>"
        )
    return (
        "<table style='width:100%;border-collapse:collapse;font-size:13px;line-height:1.55;color:#0b0b0b'>"
        "<colgroup><col style='width:13%'><col style='width:27%'><col style='width:30%'><col style='width:17%'><col style='width:13%'></colgroup>"
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )

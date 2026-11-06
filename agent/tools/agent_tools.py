import csv
import json
from contextvars import ContextVar
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from pathlib import Path


REPORT_CONTEXT_KEY = "report"
REPORT_CONTEXT_VALUE = ContextVar(REPORT_CONTEXT_KEY, default=None)


def rag_summarize(query: str):
    """什么时候该用它：需要从知识库检索专业知识并生成总结回答时。"""
    from rag.rag_service import summarize

    return summarize(query)


def get_weather(city: str):
    """什么时候该用它：需要获取指定城市的实时天气数据时。"""
    if not isinstance(city, str) or not city.strip():
        raise ValueError("city must be a non-empty string")

    url = f"https://wttr.in/{quote(city.strip())}?format=j1"
    request = Request(url, headers={"User-Agent": "robot-cs-agent/1.0"})
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Weather service returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError("Unable to reach the weather service") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Weather service returned invalid JSON") from exc


def get_user_location():
    """什么时候该用它：需要获取当前用户所在城市时。"""
    return "南宁"


def get_user_id():
    """什么时候该用它：需要获取当前用户的唯一标识时。"""
    return "1001"


def get_current_month():
    """什么时候该用它：需要获取系统当前月份（YYYY-MM 格式）时。"""
    return datetime.now().strftime("%Y-%m")


def fetch_external_data(user_id: str, month: str):
    """什么时候该用它：需要查询指定用户指定月份的使用记录时。"""
    if not user_id or not month:
        raise ValueError("user_id and month are required")

    records_path = (
        Path(__file__).resolve().parents[2] / "data" / "external" / "records.csv"
    )
    with records_path.open("r", encoding="utf-8-sig", newline="") as stream:
        records = list(csv.DictReader(stream))
    return [
        record
        for record in records
        if record.get("用户ID") == str(user_id) and record.get("时间") == str(month)
    ]


def fill_context_for_report():
    """什么时候该用它：准备生成使用报告，需要先注入报告场景上下文标记时。"""
    REPORT_CONTEXT_VALUE.set(REPORT_CONTEXT_KEY)
    return "报告上下文已准备完成，可以继续生成使用报告。"

from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional

try:
    import requests  # type: ignore
except Exception:  # requests가 없어도 서버는 뜨도록
    requests = None  # type: ignore

from fastmcp import FastMCP


# 기본 환경 설정 (제작자는 단순한 키만 사용)
DEFAULT_CITY = os.getenv("WEATHER_CITY_DEFAULT", "Seoul")
UNITS = os.getenv("WEATHER_UNITS", "metric")  # metric | imperial
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger(__name__)
try:
    logger.setLevel(LOG_LEVEL)
except ValueError:
    logger.setLevel("INFO")
    logger.warning(f"잘못된 LOG_LEVEL 값: {LOG_LEVEL}. INFO로 설정됩니다.")


mcp = FastMCP(name="WeatherToolServer")


def _call_openweather(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if not requests:
        return {
            "ok": False,
            "error": "requests 패키지가 설치되어 있지 않습니다. Settings에서 의존성 재설치를 실행하세요.",
        }
    if not OPEN_WEATHER_API_KEY:
        return {
            "ok": False,
            "error": "OPEN_WEATHER_API_KEY가 설정되어 있지 않습니다.",
        }
    try:
        url = f"https://api.openweathermap.org/data/2.5/{endpoint}"
        p = dict(params)
        p["appid"] = OPEN_WEATHER_API_KEY
        resp = requests.get(url, params=p, timeout=10)
        resp.raise_for_status()
        return {"ok": True, "data": resp.json()}
    except Exception as e:
        return {"ok": False, "error": f"{e}"}


@mcp.tool()
def current_weather(city: Optional[str] = None) -> Dict[str, Any]:
    """
    지정한 도시의 현재 날씨를 반환합니다. (기본: 환경변수 WEATHER_CITY_DEFAULT)
    """
    target_city = (city or DEFAULT_CITY).strip()
    logger.info(f"current_weather for city={target_city}, units={UNITS}")
    res = _call_openweather("weather", {"q": target_city, "units": UNITS})
    if not res.get("ok"):
        return {"city": target_city, "ok": False, "message": res.get("error", "")}
    data = res["data"]
    main = data.get("main", {})
    weather = (data.get("weather") or [{}])[0]
    return {
        "ok": True,
        "city": target_city,
        "temp": main.get("temp"),
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "description": weather.get("description"),
        "raw": data,
    }


@mcp.tool()
def simple_forecast(city: Optional[str] = None, cnt: int = 3) -> Dict[str, Any]:
    """
    지정한 도시의 간단 예보(목록)를 반환합니다. cnt는 항목 수(기본 3).
    """
    target_city = (city or DEFAULT_CITY).strip()
    logger.info(f"simple_forecast for city={target_city}, units={UNITS}, cnt={cnt}")
    res = _call_openweather("forecast", {"q": target_city, "units": UNITS, "cnt": int(cnt)})
    if not res.get("ok"):
        return {"city": target_city, "ok": False, "message": res.get("error", "")}
    data = res["data"]
    items = []
    for it in (data.get("list") or [])[: int(cnt)]:
        main = it.get("main", {})
        weather = (it.get("weather") or [{}])[0]
        items.append(
            {
                "time": it.get("dt_txt"),
                "temp": main.get("temp"),
                "description": weather.get("description"),
            }
        )
    return {"ok": True, "city": target_city, "items": items, "raw": data}


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "1016"))
    path = os.getenv("MCP_PATH", "/mcp")
    mcp.run(transport="streamable-http", host=host, port=port, path=path)



# 날씨 조회 (Weather)

도시별 현재 날씨와 간단 예보를 제공하는 MCP Activity입니다.

## 환경 변수
- `OPEN_WEATHER_API_KEY`: OpenWeather API Key (없으면 네트워크 요청은 실패 메시지를 반환)
- `WEATHER_CITY_DEFAULT`: 기본 도시 (기본값: Seoul)
- `WEATHER_UNITS`: 단위 (`metric` 또는 `imperial`, 기본값: metric)
- `LOG_LEVEL`: 로그 레벨 (기본값: INFO)

## 제공 도구
- `current_weather(city?: str)` — 현재 날씨
- `simple_forecast(city?: str, cnt?: int)` — 간단 예보 목록



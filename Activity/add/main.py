from __future__ import annotations

import logging
import os
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"
loaded = load_dotenv(dotenv_path=ENV_PATH, override=False)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
NUMBER_PRECISION = os.getenv("NUMBER_PRECISION", "4")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="[%(levelname)s][add] %(message)s",
)
if not loaded:
    logging.warning("[add] .env 파일을 찾지 못했습니다 (%s)", ENV_PATH)
logging.info(
    "[add] 환경 설정 - LOG_LEVEL=%s NUMBER_PRECISION=%s",
    LOG_LEVEL,
    NUMBER_PRECISION,
)

mcp = FastMCP(name="AppsToolServer")


def _precision() -> int:
    try:
        return max(0, int(NUMBER_PRECISION))
    except Exception:
        return 0


def _round(value: Decimal) -> Decimal:
    precision = _precision()
    if precision == 0:
        return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    quant = Decimal("1").scaleb(-precision)
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def _calc(op: str, a: float | int, b: float | int) -> float:
    a_dec = Decimal(str(a))
    b_dec = Decimal(str(b))
    raw = a_dec + b_dec if op == "add" else a_dec - b_dec
    rounded = _round(raw)
    logging.debug("[add] %s(%s, %s) -> %s", op, a, b, rounded)
    return float(rounded)


@mcp.tool(description=f"LOG_LEVEL={LOG_LEVEL}, NUMBER_PRECISION={NUMBER_PRECISION}")
def add(a: float, b: float) -> float:
    return _calc("add", a, b)


@mcp.tool(description=f"LOG_LEVEL={LOG_LEVEL}, NUMBER_PRECISION={NUMBER_PRECISION}")
def subtract(a: float, b: float) -> float:
    return _calc("sub", a, b)


if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "1015"))
    path = os.getenv("MCP_PATH", "/")
    mcp.run(transport="streamable-http", host=host, port=port, path=path)

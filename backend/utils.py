# utils.py
import datetime as dt
import functools
import json
import pathlib
import requests

_CACHE_DIR = pathlib.Path(__file__).with_suffix('').parent / "cache"
_CACHE_DIR.mkdir(exist_ok=True)


@functools.lru_cache(maxsize=1)
def fetch_holidays(year: int) -> dict[dt.date, str]:
    """
    从 China Calendar 开源仓库拉取当年法定节假日
    缓存到本地 cache/2025.json，离线可用
    """
    cache_file = _CACHE_DIR / f"{year}.json"

    if cache_file.exists():
        data = json.loads(cache_file.read_text(encoding="utf-8"))
    else:
        # 国内镜像，长期可用
        url = f"https://cdn.jsdelivr.net/gh/hezhijie0327/chinese_holidays@master/{year}.json"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.json()
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # 只保留 holiday: true 的法定放假
    return {
        dt.datetime.strptime(d, "%Y-%m-%d").date(): info["name"]
        for d, info in data.items()
        if info.get("holiday")
    }


def load_this_year_holidays() -> dict[dt.date, str]:
    return fetch_holidays(dt.date.today().year)
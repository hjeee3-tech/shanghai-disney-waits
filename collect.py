"""상하이 디즈니랜드 놀이기구 대기시간 수집기.

queue-times.com 공개 API에서 대기시간을 받아 data/YYYY-MM-DD.csv 에 한 줄씩 추가한다.
윈도우 작업 스케줄러가 5분마다 실행한다. 이전과 같은 갱신 시각이면 저장하지 않는다.
데이터 출처: Powered by Queue-Times.com (https://queue-times.com)
"""
import csv
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

URL = "https://queue-times.com/parks/30/queue_times.json"
BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
LOG = BASE / "collect.log"
LAST = BASE / ".last_updated"
CST = timezone(timedelta(hours=8))  # 상하이 시각
FIELDS = ["fetched_at_cst", "updated_at_cst", "land", "ride_id", "ride", "is_open", "wait_time"]


def log(msg):
    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{now} CST  {msg}\n")


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (personal wait-time logger)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)

    rides = [(land["name"], ride) for land in payload.get("lands", []) for ride in land["rides"]]
    rides += [("(기타)", ride) for ride in payload.get("rides", [])]
    if not rides:
        log("놀이기구 데이터 없음")
        return

    newest = max(ride["last_updated"] for _, ride in rides)
    if LAST.exists() and LAST.read_text().strip() == newest:
        return  # 새 데이터 아님

    fetched = datetime.now(CST)
    updated = datetime.fromisoformat(newest.replace("Z", "+00:00")).astimezone(CST)
    DATA.mkdir(exist_ok=True)
    path = DATA / f"{updated:%Y-%m-%d}.csv"
    is_new = not path.exists()
    with path.open("a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(FIELDS)
        for land, ride in rides:
            w.writerow([
                fetched.strftime("%Y-%m-%d %H:%M"),
                updated.strftime("%Y-%m-%d %H:%M"),
                land, ride["id"], ride["name"],
                int(ride["is_open"]), ride["wait_time"],
            ])
    LAST.write_text(newest)
    open_count = sum(1 for _, r in rides if r["is_open"])
    log(f"저장 {len(rides)}개 (운영중 {open_count}) -> {path.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"오류: {e!r}")

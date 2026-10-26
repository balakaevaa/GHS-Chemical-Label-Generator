import json
import re
import aiosqlite
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="GHS Label Generator")

app.mount('/static', StaticFiles(directory='static'),name='static')
templates = Jinja2Templates(directory="templates")
DB_PATH = "cache.db"

PICTOGRAM_URLS = {
    "GHS01": "/static/GHS01.svg",
    "GHS02": "/static/GHS02.svg",
    "GHS03": "/static/GHS03.svg",
    "GHS04": "/static/GHS04.svg",
    "GHS05": "/static/GHS05.svg",
    "GHS06": "/static/GHS06.svg",
    "GHS07": "/static/GHS07.svg",
    "GHS08": "/static/GHS08.svg",
    "GHS09": "/static/GHS09.svg",
}

@app.on_event("startup")
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cas_cache (
                cas TEXT PRIMARY KEY,
                data_json TEXT
            )
        """)
        await db.commit()

def find_ghs_section(sections: list) -> list:
    for sec in sections:
        if sec.get("TOCHeading") == "GHS Classification":
            return sec.get("Information", [])
        if "Section" in sec:
            found = find_ghs_section(sec["Section"])
            if found:
                return found
    return []

async def get_ghs_data(cas: str) -> dict:
    cas = cas.strip()

    # 1. Проверяем кэш SQLite
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT data_json FROM cas_cache WHERE cas = ?", (cas,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])

    # 2. Получаем CID из PubChem
    async with httpx.AsyncClient(timeout=10.0) as client:
        cid_res = await client.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/cids/JSON")
        if cid_res.status_code != 200:
            return None
        
        cid_data = cid_res.json()
        if "IdentifierList" not in cid_data or not cid_data["IdentifierList"]["CID"]:
            return None
        cid = cid_data["IdentifierList"]["CID"][0]

        # 3. Запрашиваем раздел GHS Classification
        view_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON?heading=GHS+Classification"
        view_res = await client.get(view_url)
        if view_res.status_code != 200:
            return None
        payload = view_res.json()

    # 4. Инициализация (дефолтный сигнал ПУСТОЙ, чтобы безопасные вещества не получали Warning)
    result = {
        "cas": cas,
        "name": "",
        "signal": "",
        "is_hazardous": False,
        "pictograms": [],
        "h_statements": [],
        "p_statements": []
    }

    try:
        record = payload.get("Record", {})
        result["name"] = record.get("RecordTitle", f"Chemical {cas}")
        
        info_items = find_ghs_section(record.get("Section", []))
        
        for info in info_items:
            name = info.get("Name")
            
            # Сигнальное слово: DANGER всегда приоритетнее WARNING
            if name == "Signal" and "Value" in info:
                for markup in info["Value"].get("StringWithMarkup", []):
                    sig = markup.get("String", "").strip().upper()
                    if sig == "DANGER":
                        result["signal"] = "DANGER"
                    elif sig == "WARNING" and result["signal"] != "DANGER":
                        result["signal"] = "WARNING"

            # Пиктограммы: ищем коды GHS01-GHS09 по всему блоку (включая ссылки и Extra)
            elif name == "Pictogram(s)":
                raw_info = json.dumps(info)
                found_pics = re.findall(r"GHS0[1-9]", raw_info)
                for code in found_pics:
                    if code not in result["pictograms"]:
                        result["pictograms"].append(code)

            # Формулировки опасности (H-statements)
            elif name == "GHS Hazard Statements" and "Value" in info:
                for markup in info["Value"].get("StringWithMarkup", []):
                    h_text = markup.get("String", "").strip()
                    # Игнорируем служебный текст "Not Classified" и берем только валидные H-фразы
                    if h_text.startswith("H") and h_text not in result["h_statements"]:
                        result["h_statements"].append(h_text)

            # Меры предосторожности (P-statements)
            elif name == "Precautionary Statement Codes" and "Value" in info:
                for markup in info["Value"].get("StringWithMarkup", []):
                    p_text = markup.get("String", "")
                    for p in re.findall(r"P\d{3}(?:\+P\d{3})*", p_text):
                        if p not in result["p_statements"]:
                            result["p_statements"].append(p)

        result["p_statements"] = result["p_statements"][:6]
        
        # Вещество считается опасным, если есть пиктограммы или H-фразы
        if result["pictograms"] or result["h_statements"] or result["signal"]:
            result["is_hazardous"] = True

    except Exception:
        pass

    # Кэшируем результат
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO cas_cache VALUES (?, ?)", (cas, json.dumps(result)))
        await db.commit()

    return result

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, cas: str = "143-33-9"):
    data = await get_ghs_data(cas)
    pic_links = [PICTOGRAM_URLS[p] for p in data.get("pictograms", []) if p in PICTOGRAM_URLS] if data else []
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "data": data,
            "pic_links": pic_links,
            "query_cas": cas
        }
    )





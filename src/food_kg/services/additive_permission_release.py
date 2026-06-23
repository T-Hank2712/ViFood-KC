"""Build exact Appendix 2A PERMITTED_IN relationships."""
from __future__ import annotations
import json
import hashlib
from pathlib import Path

SOURCE_ID="SOURCE:VN_VBHN_09_2024"
SOURCE_URL="https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/09-vbhn-byt.pdf"
REGULATION_ID="REGULATION:VN_VBHN_09_2024"

def build(rows:list[dict], additives:list[dict], reviewed_at:str, scope:dict|None=None):
    source={"label":"Source","id":SOURCE_ID,"properties":{"name":"Văn bản hợp nhất 09/VBHN-BYT (2024)","source":SOURCE_ID,"source_url":SOURCE_URL,"reviewed_at":reviewed_at,"status":"active"}}
    regulation={"label":"Regulation","id":REGULATION_ID,"properties":{"name":"Quy định về quản lý và sử dụng phụ gia thực phẩm","source":SOURCE_ID,"source_url":SOURCE_URL,"reviewed_at":reviewed_at,"status":"active"}}
    add={n["properties"]["ins"]:n for n in additives if n["label"]=="Additive"}
    categories={}
    rels=[{"start_id":REGULATION_ID,"end_id":SOURCE_ID,"type":"SUPPORTED_BY","properties":{"context":"official-consolidated-text"}}]
    for row in rows:
        text=row["food_group_name_vi"].casefold()
        if scope:
            if any(word.casefold() in text for word in scope.get("exclude_keywords",[])):
                continue
            if not any(word.casefold() in text for word in scope.get("include_keywords",[])):
                continue
        code=row["food_group_code"]
        cid="CATEGORY:VN_FCS_"+code.replace(".","_") if code else "CATEGORY:VN_FCS_TEXT_"+hashlib.sha256(text.encode()).hexdigest()[:16].upper()
        properties={"name":row["food_group_name_vi"],"name_vi":row["food_group_name_vi"],"source":SOURCE_ID,"source_url":SOURCE_URL,"reviewed_at":reviewed_at,"status":"active"}
        if code: properties["regulatory_food_group_code"]=code
        categories.setdefault(cid,{"label":"FoodCategory","id":cid,"properties":properties})
        for ins in row["ins_codes"]:
            if ins not in add:
                name_vi=row.get("source_additive_names",{}).get(ins)
                if not name_vi:
                    raise ValueError(f"{ins}: absent from additive master and has no official Appendix 2 name")
                add[ins]={"label":"Additive","id":"ADDITIVE:INS_"+ins.upper().replace("(","_").replace(")","").replace("-","_"),"properties":{"name":name_vi,"name_vi":name_vi,"ins":ins,"source":SOURCE_ID,"source_url":SOURCE_URL,"reviewed_at":reviewed_at,"status":"active","source_context":"appendix-2"}}
            rels.append({"start_id":add[ins]["id"],"end_id":cid,"type":"PERMITTED_IN","properties":{"appendix":row["appendix"],"maximum_level":row["maximum_level"],"unit":row["unit"],"note":row["note"],"source_page":row["raw_page_number"],"source":SOURCE_ID}})
    for cid in categories:
        rels.append({"start_id":cid,"end_id":SOURCE_ID,"type":"SUPPORTED_BY","properties":{"context":"regulatory-food-category"}})
    return [source,regulation,*add.values(),*categories.values()],rels

def write(path:Path,value:object):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

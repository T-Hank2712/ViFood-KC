# ViFood-KG

ViFood-KG là **Knowledge Core** cho hệ thống phân tích thực phẩm đóng gói tại Việt Nam. Repository này không nhận ảnh, OCR, API hay quản lý Product/SKU. Nó xây dựng graph chuẩn để một lớp product/OCR bên ngoài có thể map các term trên nhãn như `bột ngọt`, `INS 621`, `Natri` hoặc `sữa` về thực thể chuẩn, rồi lấy thông tin giải thích có nguồn.

```text
Ảnh/OCR hoặc dữ liệu nhãn bên ngoài
→ entity linking bằng Alias
→ ViFood-KG
→ chất đó là gì, chức năng gì, thường/gần như được phép ở đâu,
  có dị nguyên hay claim sức khỏe nào, dựa trên nguồn nào
```

## Phạm vi

Knowledge Core gồm `Nutrient`, `Ingredient`, `Additive`, `Allergen`, `FoodCategory`, `FunctionalClass`, `Alias`, `HealthClaim`, `HealthOutcome`, `Source` và `Regulation`. Product/SKU, Brand, ảnh bao bì, OCR và quan sát thực tế trên nhãn thuộc product-observation layer hoặc project khác.

`FoodCategory` chỉ là ngữ cảnh kiến thức cho phụ gia/quy định, không phải taxonomy để nhận diện ảnh. FoodOn core hiện giữ các nhóm đóng gói mức cao như mì ăn liền, bánh kẹo, snack, sữa, đồ uống không cồn, nước đóng chai, sauce và gia vị.

## Luồng tự động có quality gate

```text
raw snapshot → extractor → staging → transformer theo rule/config
→ curated release → attestation SHA-256 → automated quality gate → Neo4j import
```

Không có bước review thủ công bắt buộc để import. Tuy nhiên importer không chấp nhận dữ liệu tùy ý. Quality gate bắt buộc:

- Release manifest đã attest theo policy `strict-v1`.
- Raw file còn tồn tại và đúng SHA-256 đã ghi.
- Mọi source thuộc trusted `config/source_registry.yaml`.
- Mọi node có provenance, source node và trạng thái `active`/`deprecated`.
- Schema, ID, label, relationship và endpoint hợp lệ.
- Không còn alias mơ hồ.

Các rule mapping và bản dịch nội bộ vẫn được version hóa trong `config/`; quality gate bảo đảm tính tái lập và truy vết, không biến output OCR/LLM thành dữ liệu chuẩn nếu chưa qua các rule đó.

## Trạng thái hiện tại

- FAO/INFOODS Tagnames: nutrient master đã được ingest.
- FoodOn: FoodCategory core song ngữ đã được ingest, không import toàn bộ ontology.
- Additive master, quy định phụ gia Việt Nam, ingredient–nutrient, allergen và health claim: là các hạng mục tiếp theo.

## Cài đặt

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Khai báo `.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```

Chạy [constraints.cypher](neo4j/cypher/constraints.cypher) trong Neo4j Browser, sau đó chạy test:

```bash
PYTHONPATH=src .venv/bin/python -m pytest -q
```

## Import release

Importer bắt buộc nodes, relationships và manifest đã attest:

```bash
PYTHONPATH=src .venv/bin/python scripts/import_curated.py \
  --nodes data/curated/nodes/foodon_knowledge_core_v0.1.2.json \
  --relationships data/curated/relationships/foodon_knowledge_core_v0.1.2.json \
  --manifest data/curated/releases/foodon_knowledge_core_v0.1.2.attested.yaml
```

Tạo manifest attest từ release và raw source:

```bash
PYTHONPATH=src .venv/bin/python scripts/attest_release.py \
  --manifest data/curated/releases/foodon_knowledge_core_v0.1.2.yaml \
  --output data/curated/releases/foodon_knowledge_core_v0.1.2.attested.yaml \
  --raw-file data/raw/foodon/foodon-v2025-02-01/foodon.owl
```

Xem [ontology](docs/ontology.md) và [nguồn dữ liệu](docs/data-sources.md) để biết mô hình và roadmap.

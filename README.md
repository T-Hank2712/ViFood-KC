# ViFood-KC (Knowledge Core)

ViFood-KC là Knowledge Core cho hệ thống phân tích thực phẩm đóng gói tại Việt Nam. Core này chuẩn hóa các term xuất hiện trên nhãn như tên nguyên liệu, nutrient, INS, E-number, dị nguyên hoặc nhóm thực phẩm; sau đó cung cấp giải thích có nguồn, quan hệ dinh dưỡng, bằng chứng sức khỏe và quy định sử dụng phụ gia.

ViFood-KC không xử lý ảnh, OCR, Product/SKU, Brand, giá bán hay dữ liệu người dùng. Các việc đó thuộc product-observation layer. Knowledge Core chỉ lưu tri thức chuẩn, truy vết được nguồn và không biến quan sát OCR hoặc nội dung LLM thành dữ liệu chuẩn.

```text
Ảnh / OCR / Product layer
        ↓ term trên nhãn
Entity linking bằng mã, tên chuẩn và Alias
        ↓
ViFood-KC
        ↓
Giải thích thành phần, dinh dưỡng, dị nguyên, quy định và evidence
```

## Mô hình tri thức

ViFood-KC quản lý các thực thể:

- `Nutrient`: dưỡng chất, mã chuẩn, tên Việt/Anh và đơn vị.
- `Ingredient`: nguyên liệu, phân cấp, nguồn gốc và thành phần dinh dưỡng.
- `Additive`: phụ gia, INS, E-number, tên, chức năng và quy định sử dụng.
- `FoodCategory`: nhóm thực phẩm pháp lý Việt Nam và taxonomy ngữ nghĩa khi cần.
- `FunctionalClass`: chức năng công nghệ của phụ gia.
- `Allergen`: dị nguyên và quan hệ với nguyên liệu.
- `HealthClaim`, `HealthOutcome`: claim sức khỏe có điều kiện, mức bằng chứng và nguồn.
- `Regulation`, `Source`: văn bản pháp lý và nguồn dữ liệu.
- `Alias`: token thay thế thật sự cần cho entity linking; không lặp `name`, `name_vi`, `ins` hoặc `external_code`.

## Luồng dữ liệu

```text
Nguồn chính thức
→ raw snapshot
→ extractor
→ staging
→ transformer theo rule/config phiên bản hóa
→ curated release
→ attestation SHA-256
→ automated quality gate
→ Neo4j
```

Mỗi release chỉ được import khi raw hash khớp, source có trong registry, node có provenance, schema/relationship hợp lệ và Alias không mơ hồ.

## Quy định phụ gia

Quy định phụ gia được biểu diễn bằng:

```text
Additive -[:PERMITTED_IN]-> FoodCategory pháp lý Việt Nam
```

Relationship `PERMITTED_IN` mang phụ lục, mức tối đa hoặc GMP, đơn vị, ghi chú và trang nguồn. FoodCategory pháp lý được giữ nguyên theo mã/tên của văn bản Việt Nam; nó không bị thay thế bằng taxonomy quốc tế.

## Tích hợp product/OCR

Product layer lưu quan sát như OCR text, confidence, ảnh nhãn và SKU. ViFood-KC nhận term để map về thực thể chuẩn, sau đó trả lại tri thức và provenance. Quan sát trên nhãn không đồng nghĩa với quy định pháp lý: `OBSERVED_IN`, `COMMON_IN` và `PERMITTED_IN` là ba quan hệ có nghĩa khác nhau.

## Chạy project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Khai báo `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE` trong `.env`, rồi chạy [constraints.cypher](neo4j/cypher/constraints.cypher) trước khi import curated release.

Xem [ontology](docs/ontology.md) và [nguồn dữ liệu](docs/data-sources.md) để biết đầy đủ mô hình và các nguồn của ViFood-KC.

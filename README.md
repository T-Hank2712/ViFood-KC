# ViFood-KC (Knowledge Core)

ViFood-KC là lõi tri thức cho hệ sinh thái phân tích thực phẩm đóng gói tại Việt Nam. Project này không phải ứng dụng chụp ảnh, không phải OCR, không phải hệ thống quản lý sản phẩm/SKU, mà là lớp dữ liệu chuẩn để các project khác tra cứu, liên kết và giải thích thông tin trên nhãn thực phẩm.

Mục tiêu của ViFood-KC là biến các nguồn dữ liệu đáng tin cậy thành một knowledge graph có thể truy vết nguồn. Khi một hệ thống bên ngoài đọc được các từ như “bột mì”, “sữa bột”, “INS 330”, “natri”, “đường”, “chất béo bão hòa” hoặc “nước giải khát”, ViFood-KC giúp map các từ đó về thực thể chuẩn, hiểu quan hệ giữa chúng và trả về giải thích có bằng chứng.

```text
Nhãn sản phẩm / OCR / Product layer
        ↓
Term trên nhãn: ingredient, additive, nutrient, category, claim
        ↓
Entity linking bằng tên chuẩn, mã chuẩn và Alias
        ↓
ViFood-KC graph
        ↓
Giải thích thành phần, phụ gia, dinh dưỡng, sức khỏe, dị nguyên và quy định
```

## Vai trò của ViFood-KC

ViFood-KC đóng vai trò như “bộ não tri thức nền” cho các ứng dụng thực phẩm. Project tập trung vào các câu hỏi:

- Một thành phần trên nhãn thực phẩm là gì?
- Thành phần đó thuộc nhóm nguyên liệu nào?
- Tên gọi khác hoặc tên tiếng Việt của nó là gì?
- Phụ gia có mã INS/E-number nào, chức năng công nghệ là gì?
- Phụ gia đó được quy định như thế nào trong nhóm thực phẩm liên quan?
- Một nutrient có mã chuẩn nào, đơn vị nào và liên quan đến claim sức khỏe nào?
- Một claim sức khỏe dựa trên nguồn bằng chứng nào?
- Một dị ứng nguyên trên nhãn thuộc nhóm nào theo chuẩn Codex?
- Dữ liệu này đến từ nguồn nào và có thể kiểm tra lại không?

ViFood-KC không biến dữ liệu OCR, nội dung do LLM sinh ra hoặc quan sát từ một sản phẩm đơn lẻ thành tri thức chuẩn. Các quan sát thực tế có thể được dùng để liên kết hoặc bổ sung ngữ cảnh, nhưng tri thức chuẩn phải đi qua source registry, release manifest, hash nguồn và quality gate.

## Các nhóm tri thức chính

ViFood-KC tổ chức tri thức thành các nhóm chính:

| Nhóm | Mục đích |
|---|---|
| `Ingredient` | Chuẩn hóa nguyên liệu thực phẩm và ingredient dạng hóa chất như bột, sữa, dầu, đường, caffeine, sodium chloride. |
| `IngredientGroup` | Gom nguyên liệu vào các nhóm nghiệp vụ dễ query, ví dụ nhóm nguyên liệu sữa, bột/ngũ cốc, đường hóa học hoặc khoáng hóa học. |
| `Nutrient` | Chuẩn hóa dưỡng chất bằng mã và tên từ nguồn dinh dưỡng đáng tin cậy. |
| `Additive` | Chuẩn hóa phụ gia thực phẩm, mã INS/E-number, tên. |
| `FoodCategory` | Biểu diễn nhóm thực phẩm, đặc biệt là nhóm pháp lý dùng trong quy định phụ gia. |
| `FunctionalClass` | Mô tả vai trò công nghệ của phụ gia như chất bảo quản, chất tạo màu, chất điều chỉnh độ acid. |
| `Allergen` | Chuẩn hóa nhóm dị ứng nguyên/dị ứng không dung nạp từ Codex CXS 1-1985 để phục vụ nhận diện allergen trên nhãn. |
| `HealthClaim` / `HealthOutcome` | Biểu diễn claim sức khỏe, kết quả sức khỏe, điều kiện áp dụng và nguồn bằng chứng. |
| `Regulation` / `Source` | Lưu nguồn dữ liệu, văn bản pháp lý, tài liệu khoa học và provenance. |
| `Alias` | Lưu tên gọi khác để entity linking, không dùng để nhân bản thực thể chuẩn. |

## Luồng xử lý dữ liệu

Mọi dữ liệu trong ViFood-KC đi theo một pipeline nhất quán:

```text
Nguồn dữ liệu đáng tin cậy
        ↓
Raw snapshot
        ↓
Extractor
        ↓
Staging records
        ↓
Transformer theo rule/config version hóa
        ↓
Curated release
        ↓
Attested manifest + SHA-256
        ↓
Automated quality gate
        ↓
Neo4j graph
```

Ý nghĩa từng bước:

- `Raw snapshot`: lưu bản nguồn gốc để có thể kiểm tra lại.
- `Extractor`: đọc dữ liệu từ PDF, XLSX, OWL, HTML hoặc nguồn thô khác.
- `Staging`: dữ liệu trung gian, chưa được xem là tri thức chuẩn.
- `Transformer`: chuẩn hóa dữ liệu, tạo node/relationship, lọc theo scope và loại bỏ alias mơ hồ.
- `Curated release`: bộ dữ liệu được phép import.
- `Attested manifest`: manifest kèm hash SHA-256 của các file nguồn.
- `Quality gate`: kiểm tra schema, source, provenance, endpoint relationship và alias trước khi import.
- `Neo4j`: graph database lưu tri thức đã qua kiểm soát.

## Nguyên tắc thiết kế graph

ViFood-KC ưu tiên graph rõ nghĩa hơn là nhồi nhiều thông tin vào property.

Ví dụ nhóm nguyên liệu không được lưu như một mảng property trên `Ingredient`. Thay vào đó:

```text
(:Ingredient)-[:IN_GROUP]->(:IngredientGroup)
```

Phân cấp bản chất giữa nguyên liệu dùng:

```text
(:Ingredient)-[:IS_A]->(:Ingredient)
```

Tên gọi khác dùng:

```text
(:Alias)-[:REFERS_TO]->(:Ingredient | :Additive | :Nutrient | :FoodCategory | :Allergen)
```

Nguồn dữ liệu dùng:

```text
(:Entity)-[:SUPPORTED_BY]->(:Source)
```

Quy định phụ gia dùng:

```text
(:Additive)-[:PERMITTED_IN]->(:FoodCategory)
```

Các quan hệ có ý nghĩa khác nhau không được trộn lẫn. Ví dụ `PERMITTED_IN` là được phép theo quy định, `OBSERVED_IN` là quan sát thấy trên nhãn, còn `COMMON_IN` là thường gặp theo dữ liệu quan sát hoặc nguồn phù hợp.

## Tích hợp với project khác

Một project chụp ảnh/OCR có thể dùng ViFood-KC theo flow:

```text
Ảnh sản phẩm
  → OCR lấy text nhãn
  → tách term thành phần / phụ gia / dinh dưỡng
  → gọi ViFood-KC để entity linking
  → nhận lại node chuẩn, alias, quan hệ, nguồn và giải thích
```

Ví dụ nếu OCR đọc được “bột lúa mì”, hệ thống có thể map về Ingredient chuẩn “Bột mì”. Nếu OCR đọc được “INS 330”, hệ thống có thể map về phụ gia tương ứng, chức năng công nghệ và quy định liên quan.

## Cấu trúc dữ liệu đầu ra

Các release import vào Neo4j thường có ba file chính:

```text
data/curated/nodes/<release>.json
data/curated/relationships/<release>.json
data/curated/releases/<release>.attested.yaml
```

File nodes chứa các node chuẩn như `Ingredient`, `Additive`, `Nutrient`, `Alias`, `Source`. File relationships chứa các quan hệ như `IS_A`, `IN_GROUP`, `REFERS_TO`, `SUPPORTED_BY`, `PERMITTED_IN`. File attested manifest chứa metadata release và hash của nguồn.

## Chạy project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Khai báo các biến Neo4j trong `.env`:

```text
NEO4J_URI
NEO4J_USER
NEO4J_PASSWORD
NEO4J_DATABASE
```

Trước khi import dữ liệu, chạy constraint trong [constraints.cypher](neo4j/cypher/constraints.cypher).

Xem thêm:

- [Ontology ViFood-KC](docs/ontology.md)
- [Nguồn dữ liệu ViFood-KC](docs/data-sources.md)

# ViFood-KG

ViFood-KG là knowledge graph làm lớp tri thức đáng tin cậy cho hệ thống phân tích thực phẩm đóng gói tại Việt Nam. Khi một lớp OCR/product bên ngoài đọc nhãn sản phẩm, nó gửi các term như `E621`, `Natri`, `dầu cọ` hoặc `sữa` sang ViFood-KG. Graph chuẩn hóa term đó, giải thích nó là gì, có chức năng gì, liên quan tới sức khỏe ra sao, có thể gặp trong nhóm thực phẩm nào và — khi có quy định nguồn rõ ràng — được phép dùng trong phạm vi nào.

Repository này không quản lý ảnh, OCR, Product/SKU, Brand, giá bán hay lịch sử người dùng. Những dữ liệu đó thuộc product-observation layer. ViFood-KG chỉ chứa tri thức chuẩn, có provenance và có thể tái tạo.

```text
Ảnh nhãn / OCR / Product layer
        ↓  term quan sát được
Entity linking (mã, tên chuẩn, Alias)
        ↓
ViFood-KG: thực thể chuẩn + nguồn + quy định + giải thích
        ↓
Ứng dụng trả lời cho người dùng
```

## Đích đến của project

Project hoàn chỉnh sẽ có các mảng tri thức sau:

- `Nutrient`: dưỡng chất, mã chuẩn, tên Việt/Anh và giải thích.
- `Ingredient`: nguyên liệu, phân cấp, nguồn gốc, hàm lượng nutrient và dị nguyên.
- `Additive`: phụ gia, INS, E-number, tên Việt/Anh, chức năng công nghệ và quy định sử dụng.
- `FoodCategory`: các nhóm thực phẩm đóng gói cần thiết để đặt ngữ cảnh, không phải catalog sản phẩm.
- `Allergen`, `HealthClaim`, `HealthOutcome`: thông tin dị nguyên và claim sức khỏe có điều kiện, mức bằng chứng và nguồn.
- `Regulation`: văn bản pháp lý, lịch sử phiên bản, giới hạn sử dụng theo nhóm thực phẩm.
- `Source` và Alias không trùng lặp: truy vết nguồn và entity linking an toàn.

Product/OCR layer trong tương lai chỉ quan sát nhãn. Nó không được tự biến quan sát hay câu trả lời LLM thành tri thức chuẩn trong graph.

## Luồng dữ liệu bắt buộc

```text
Nguồn chính thức
→ raw snapshot có hash
→ extractor
→ staging
→ transformer theo rule/config phiên bản hóa
→ curated release
→ attestation SHA-256
→ automated quality gate
→ Neo4j
```

Quality gate từ chối release nếu raw snapshot không đúng hash, nguồn không nằm trong registry, node thiếu provenance, schema/relationship sai, trạng thái không hợp lệ hoặc Alias mơ hồ. Không có bước review thủ công bắt buộc, nhưng cũng không có đường import trực tiếp dữ liệu tùy ý.

## Lộ trình toàn bộ

1. Xây dựng master data: Nutrient, FoodCategory và Additive.
2. Trích xuất Phụ lục 2A/2B của quy định Việt Nam để tạo `Additive -[:PERMITTED_IN]-> FoodCategory`, có mức tối đa, đơn vị, ghi chú và bằng chứng trang PDF.
3. Bổ sung `Ingredient`, quan hệ `HAS_NUTRIENT`, dị nguyên và taxonomy cần thiết từ các nguồn được registry cho phép.
4. Bổ sung evidence sức khỏe: `HealthClaim → subject/outcome/source`, không biến thành tư vấn y khoa.
5. Xây dựng lớp entity linking/API để product-OCR layer truy vấn graph.
6. Tích hợp với project OCR/Product riêng: quan sát nhãn giữ tách biệt; ViFood-KG chỉ trả về tri thức chuẩn và mức độ chắc chắn.

## Trạng thái hiện tại

- Đã có Nutrient master từ FAO/INFOODS.
- Đã có FoodCategory core song ngữ từ FoodOn, giới hạn cho nhóm thực phẩm đóng gói.
- Đã có 400 Additive từ Phụ lục 1 của Văn bản hợp nhất 09/VBHN-BYT.
- Đã import các release đã qua quality gate vào Neo4j.
- Chưa có giới hạn sử dụng Phụ lục 2A/2B, Ingredient, Allergen, HealthClaim hoặc product/OCR layer.

## Chạy project

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=src .venv/bin/python -m pytest -q
```

Khai báo `.env` với `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`; chạy [constraints.cypher](neo4j/cypher/constraints.cypher) trước khi import một curated release đã attest.

Xem [ontology](docs/ontology.md) cho mô hình graph và [nguồn dữ liệu](docs/data-sources.md) cho nguồn hiện dùng lẫn nguồn của các giai đoạn tiếp theo.

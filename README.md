# ViFood-KG

ViFood-KG là dự án xây dựng đồ thị tri thức về thực phẩm. Dự án thu thập, chuẩn hóa,
kiểm tra, rà soát, quản lý phiên bản và truy vấn dữ liệu trên Neo4j.

Đồ thị lưu trữ thông tin về nguyên liệu, chất dinh dưỡng, phụ gia thực phẩm, chất gây
dị ứng, nhóm thực phẩm, tuyên bố sức khỏe, nguồn tham khảo và quy định pháp lý.

## Phạm vi dự án

Repository này tập trung vào lớp dữ liệu và tri thức thực phẩm:

- Thu thập dữ liệu từ các nguồn đã xác định.
- Lưu trữ dữ liệu gốc và thông tin nguồn.
- Chuẩn hóa tên gọi, mã định danh, đơn vị đo và cấu trúc dữ liệu.
- Kiểm tra dữ liệu thiếu, sai định dạng hoặc trùng lặp.
- Rà soát thủ công các dữ liệu quan trọng.
- Quản lý phiên bản dữ liệu đã được duyệt.
- Nạp dữ liệu vào Neo4j.
- Kiểm thử, truy vấn và lập báo cáo chất lượng dữ liệu.

Repository không bao gồm API, ứng dụng web, ứng dụng di động, danh mục sản phẩm/SKU
hoặc quy trình nạp trực tiếp kết quả OCR vào Neo4j. Kết quả từ OCR, API hoặc công cụ
trích xuất chỉ được xem là dữ liệu đầu vào và phải trải qua quá trình kiểm tra trước khi
được nạp vào cơ sở dữ liệu.

## Luồng dữ liệu

```text
raw → staging → transform → validate → manual review → curated release → Neo4j import → query/test/report
```

| Giai đoạn | Mô tả |
|---|---|
| `raw` | Dữ liệu gốc được thu thập từ API, website, tệp dữ liệu hoặc tài liệu. |
| `staging` | Dữ liệu tạm thời trước khi chuẩn hóa. |
| `transform` | Chuẩn hóa tên gọi, mã định danh, đơn vị đo và cấu trúc dữ liệu. |
| `validate` | Kiểm tra định dạng, ràng buộc, dữ liệu trùng lặp và tính đầy đủ. |
| `manual review` | Rà soát thủ công các dữ liệu cần xác minh. |
| `curated release` | Bộ dữ liệu đã được kiểm tra và phê duyệt. |
| `Neo4j import` | Nạp dữ liệu đã duyệt vào Neo4j. |
| `query/test/report` | Truy vấn, kiểm thử và tạo báo cáo chất lượng dữ liệu. |

Chỉ dữ liệu trong thư mục `data/curated` mới được phép nạp vào Neo4j.

## Các loại dữ liệu chính

| Label | Mô tả |
|---|---|
| `Ingredient` | Nguyên liệu hoặc thực phẩm dùng để chế biến và tiêu thụ. |
| `Nutrient` | Chất dinh dưỡng, ví dụ Protein, Natri hoặc Vitamin C. |
| `Additive` | Phụ gia thực phẩm, ví dụ INS 621 hoặc E330. |
| `Allergen` | Chất hoặc nhóm chất gây dị ứng, ví dụ sữa hoặc gluten. |
| `FoodCategory` | Nhóm thực phẩm, ví dụ mì ăn liền hoặc đồ uống không cồn. |
| `FunctionalClass` | Chức năng công nghệ của phụ gia, ví dụ chất bảo quản hoặc chất điều vị. |
| `Alias` | Tên gọi khác, tên thương mại, tên hóa học hoặc biến thể tên gọi. |
| `HealthClaim` | Tuyên bố sức khỏe có nguồn bằng chứng. |
| `HealthOutcome` | Kết quả hoặc chỉ số sức khỏe được đề cập trong tuyên bố. |
| `Source` | Nguồn dữ liệu, bài báo khoa học hoặc tài liệu chính thức. |
| `Regulation` | Văn bản pháp lý, quy định hoặc tiêu chuẩn liên quan đến thực phẩm. |

## Yêu cầu môi trường

- Python 3.11 trở lên.
- Neo4j Desktop hoặc Neo4j Server.
- Neo4j Browser.
- `pip` và môi trường ảo Python.

## Cài đặt

### 1. Tạo môi trường ảo

```bash
python3 -m venv .venv
```

Kích hoạt môi trường ảo trên macOS/Linux:

```bash
source .venv/bin/activate
```

Trên Windows:

```bash
.venv\Scripts\activate
```

### 2. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

Sao chép file mẫu:

```bash
cp .env.example .env
```

Cập nhật thông tin kết nối Neo4j trong file `.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

Không đưa file `.env` hoặc mật khẩu Neo4j lên Git.

## Khởi tạo Neo4j

Mở Neo4j Browser và chạy file [neo4j/cypher/constraints.cypher](neo4j/cypher/constraints.cypher).

File này tạo constraint và index để bảo đảm `id` là duy nhất, hạn chế dữ liệu trùng lặp
và hỗ trợ truy vấn hiệu quả hơn.

Kiểm tra kết nối Neo4j:

```bash
python3 scripts/test_neo4j_connection.py
```

## Nạp dữ liệu vào Neo4j

Chỉ nạp dữ liệu đã được kiểm tra trong thư mục `data/curated`:

```bash
PYTHONPATH=src python3 scripts/import_curated.py \
  --nodes data/curated/nodes/phase1_seed.json \
  --relationships data/curated/relationships/phase1_seed.json
```

`Neo4jImporter` kiểm tra label và loại relationship theo danh sách cho phép trước khi
tạo truy vấn Cypher động. Importer sử dụng `MERGE` để tạo node và relationship, vì vậy
có thể chạy lại cùng một bộ dữ liệu mà không tạo dữ liệu trùng lặp.

## Kiểm thử

Chạy toàn bộ kiểm thử:

```bash
PYTHONPATH=src pytest
```

Integration test sẽ tự động chạy khi các biến môi trường kết nối Neo4j đã được cấu hình.

Các kiểm thử bao gồm:

- Kiểm tra kết nối Neo4j.
- Kiểm tra định dạng dữ liệu.
- Kiểm tra `id` trùng lặp.
- Kiểm tra nguồn dữ liệu và khả năng truy vết.
- Kiểm tra label, relationship và endpoint hợp lệ.
- Kiểm tra dữ liệu dinh dưỡng.
- Kiểm tra tính đầy đủ của `HealthClaim`.
- Kiểm tra việc nạp lại dữ liệu không tạo bản ghi trùng lặp.

## Nguyên tắc dữ liệu

- Không nạp trực tiếp dữ liệu từ `raw` hoặc `staging` vào Neo4j.
- Mỗi thực thể phải có `id` ổn định, duy nhất và có thể truy vết nguồn.
- Không tạo thực thể mới chỉ vì khác cách viết tên; sử dụng `Alias` cho tên gọi khác.
- Dữ liệu sức khỏe phải thể hiện mức độ bằng chứng và không được diễn giải thành tư vấn y khoa.
- Việc phụ gia xuất hiện trên nhãn sản phẩm không đồng nghĩa với việc phụ gia được pháp luật cho phép sử dụng.
- Quy định pháp lý mới phải liên kết với quy định cũ bằng `SUPERSEDES`; không ghi đè để tránh mất lịch sử.
- Dữ liệu về sức khỏe, phụ gia và pháp lý cần được rà soát thủ công trước khi phát hành.

## Tài liệu liên quan

- [Ontology](docs/ontology.md): Cấu trúc đồ thị, label, relationship, thuộc tính và ràng buộc dữ liệu.
- [Neo4j Constraints](neo4j/cypher/constraints.cypher): Constraint và index cần chạy trước khi import.
- [Source Registry](config/source_registry.yaml): Danh sách, phạm vi và trạng thái của các nguồn dữ liệu.

## Ghi chú

ViFood-KG là lớp dữ liệu nền tảng cho các hệ thống khác như API, ứng dụng di động, OCR
hoặc công cụ phân tích thực phẩm. Các hệ thống này chỉ nên sử dụng dữ liệu từ các bộ
`curated release` đã được kiểm tra và phát hành.

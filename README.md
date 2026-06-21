# Pipeline dữ liệu ViFood-KG

Repository này thu thập, chuẩn hóa, rà soát, quản lý phiên bản và import knowledge graph thực phẩm đóng gói Giai đoạn 1 vào Neo4j. Repository cố ý không bao gồm API, ứng dụng di động, catalog Product/SKU hay luồng OCR ghi thẳng vào dữ liệu production.

Luồng dữ liệu bắt buộc là `raw → staging → transform → validate → review thủ công → curated release → import Neo4j → query/test/report`.

## Khởi chạy nhanh

1. Tạo môi trường ảo và cài dependencies bằng `pip install -r requirements.txt`.
2. Sao chép `.env.example` thành `.env`, sau đó khai báo thông tin Bolt của Neo4j Desktop.
3. Chạy [constraints.cypher](/Users/ltthanh/LtThanh/KLTN/ViFood-KG/neo4j/cypher/constraints.cypher) trong Neo4j Browser.
4. Kiểm tra kết nối: `python3 scripts/test_neo4j_connection.py`.
5. Chỉ import các bản ghi đã được curate:

   `PYTHONPATH=src python3 scripts/import_curated.py --nodes data/curated/nodes/phase1_seed.json --relationships data/curated/relationships/phase1_seed.json`

6. Chạy kiểm thử validation: `PYTHONPATH=src pytest` (integration test tự chạy khi các biến môi trường Neo4j đã được cấu hình).

`Neo4jImporter` kiểm tra allowlist rõ ràng cho label và relationship type trước khi tạo các định danh Cypher động. Importer dùng `MERGE` cho node và relationship, nên chạy lại cùng một curated release vẫn idempotent, không tạo dữ liệu trùng.

Xem [docs/ontology.md](/Users/ltthanh/LtThanh/KLTN/ViFood-KG/docs/ontology.md) để biết hợp đồng dữ liệu graph và [config/source_registry.yaml](/Users/ltthanh/LtThanh/KLTN/ViFood-KG/config/source_registry.yaml) để biết phạm vi từng nguồn dữ liệu.

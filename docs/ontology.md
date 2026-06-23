# Ontology ViFood-KC

ViFood-KC là reference graph cho tri thức thực phẩm đóng gói. Mỗi node chuẩn có `id`, `name`, `source`, `source_url`, `reviewed_at` và `status`; `name_vi`, `ins`, `external_code` hoặc các field chuyên biệt được thêm khi phù hợp.

## Node

| Label | Vai trò |
|---|---|
| `Nutrient` | Dưỡng chất chuẩn, mã nguồn tại `external_code`. |
| `Ingredient` | Nguyên liệu và quan hệ phân cấp/dẫn xuất. |
| `Additive` | Phụ gia chuẩn, mã INS tại `ins`. |
| `FunctionalClass` | Chức năng công nghệ của Additive. |
| `FoodCategory` | Nhóm thực phẩm pháp lý hoặc taxonomy ngữ nghĩa. |
| `Allergen` | Dị nguyên. |
| `Alias` | E-number, synonym hoặc token khác không trùng thuộc tính chuẩn. |
| `HealthClaim` / `HealthOutcome` | Claim sức khỏe có điều kiện và outcome. |
| `Regulation` | Văn bản pháp lý và lịch sử phiên bản. |
| `Source` | Nguồn dữ liệu hoặc bằng chứng. |

## Relationship

| Relationship | Ý nghĩa |
|---|---|
| `HAS_NUTRIENT` | Ingredient có Nutrient với amount, unit và basis. |
| `HAS_FUNCTION` | Additive có chức năng công nghệ. |
| `PERMITTED_IN` | Additive được phép trong FoodCategory pháp lý, kèm mức dùng và nguồn. |
| `COMMON_IN` | Additive thường gặp trong một nhóm thực phẩm, có bằng chứng. |
| `OBSERVED_IN` | Additive được quan sát trên nhãn; không chứng minh hợp pháp. |
| `CONTAINS_ALLERGEN` | Ingredient liên quan tới Allergen. |
| `IS_A`, `DERIVED_FROM` | Phân cấp và nguồn gốc Ingredient. |
| `REFERS_TO` | Alias trỏ tới đúng một thực thể chuẩn. |
| `SUPPORTED_BY` | Thực thể được hỗ trợ bởi Source. |
| `GOVERNS`, `SUPERSEDES` | Regulation quản lý thực thể hoặc thay thế văn bản khác. |
| `SUBJECT_OF`, `OUTCOME`, `EVIDENCED_BY` | Cấu trúc evidence của HealthClaim. |

`PERMITTED_IN`, `COMMON_IN` và `OBSERVED_IN` luôn được giữ tách biệt. ViFood-KC không suy ra tính hợp pháp từ quan sát OCR và không suy ra tác động sức khỏe từ việc một chất có mặt trên nhãn.

## Quality gate

Quality gate kiểm tra manifest, SHA-256 của raw snapshot, source registry, provenance, trạng thái node, schema, endpoint relationship và Alias mơ hồ trước khi importer kết nối Neo4j. HealthClaim bắt buộc có subject, outcome, evidence source, điều kiện áp dụng và evidence level.

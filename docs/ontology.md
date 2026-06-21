# Ontology ViFood-KG (Giai đoạn 1)

## Phạm vi và ranh giới

Graph này là cơ sở tri thức đã được rà soát và quản lý phiên bản cho các khái niệm về thực phẩm đóng gói. Giai đoạn 1 không có catalog `Product` hoặc SKU. Mỗi node chỉ có label thuộc miền dữ liệu của nó; không dùng label chung `:Entity`.

Dữ liệu chỉ đi qua luồng `raw → staging → transform → validate → review → curated release → importer`. Extractor không bao giờ ghi vào Neo4j; importer không tải dữ liệu, không chạy OCR/trích xuất PDF và không tự tạo health claim.

## ID và nguồn gốc dữ liệu

ID là khóa namespace viết hoa, bất biến; ví dụ:

| Label | Ví dụ ID |
|---|---|
| `Nutrient` | `NUTRIENT:SODIUM` |
| `Ingredient` | `INGREDIENT:PALM_OIL` |
| `Additive` | `ADDITIVE:INS_621` |
| `FoodCategory` | `CATEGORY:INSTANT_NOODLES` |
| `FunctionalClass` | `FUNCTION:FLAVOUR_ENHANCER` |
| `Allergen` | `ALLERGEN:MILK` |
| `Alias` | `ALIAS:BOT_NGOT` |
| `HealthOutcome` | `OUTCOME:HIGH_BLOOD_PRESSURE` |
| `HealthClaim` | `CLAIM:SODIUM_HIGH_INTAKE_BP` |
| `Source` | `SOURCE:WHO_HEALTHY_DIET` |
| `Regulation` | `REGULATION:TT24_2019` |

Mỗi node chuẩn có `id`, `name`, `status`, `source`, `source_url` và `reviewed_at` khi phù hợp. `source` là tham chiếu `SOURCE:*` ổn định; tệp raw và bản ghi đã transform phải giữ lại phiên bản nguồn và mã bản ghi nguồn. Bản ghi pháp lý là phiên bản bất biến: quy định mới liên kết bằng `SUPERSEDES`, không ghi đè để làm mất lịch sử.

## Node

`Nutrient`, `Ingredient`, `Additive`, `FoodCategory`, `FunctionalClass`, `Allergen`, `Alias`, `HealthClaim`, `HealthOutcome`, `Source` và `Regulation` là các label được phép dùng. Một số trường có kiểu dữ liệu quan trọng gồm `Nutrient.default_unit`, `Additive.ins_number`, `Alias.normalized_name/language/alias_type`, `HealthClaim.conditions_of_use/evidence_level`, `Source.source_type` và `Regulation.jurisdiction/effective_date/version`.

`Alias` biểu diễn tên trên nhãn bằng tiếng Việt/Anh, tên hóa học và biến thể INS/E-number. Alias không phải là một bản sao thứ hai của thực thể mà nó tham chiếu.

## Relationship

| Type | Điểm đầu → điểm cuối | Ngữ cảnh bắt buộc |
|---|---|---|
| `IS_A` | `Ingredient → Ingredient` | phân cấp; không chu trình |
| `DERIVED_FROM` | `Ingredient → Ingredient` | phương pháp xử lý nếu có |
| `HAS_NUTRIENT` | `Ingredient → Nutrient` | `amount`, `unit`, `basis`, nguồn |
| `CONTAINS_ALLERGEN` | `Ingredient → Allergen` | trạng thái hiện diện nếu có |
| `HAS_FUNCTION` | `Additive → FunctionalClass` | nguồn |
| `PERMITTED_IN` | `Additive → FoodCategory` | mức tối đa, đơn vị, hiệu lực và văn bản pháp lý khi áp dụng |
| `COMMON_IN` | `Additive → FoodCategory` | loại bằng chứng và nguồn |
| `OBSERVED_IN` | `Additive → FoodCategory` | bằng chứng quan sát từ nhãn; không suy luận thành được phép |
| `REFERS_TO` | `Alias → Ingredient/Nutrient/Additive` | đúng một đối tượng đích |
| `SUBJECT_OF` | `HealthClaim → Nutrient/Ingredient/Additive` | vai trò nếu cần |
| `OUTCOME` | `HealthClaim → HealthOutcome` | chiều tác động/quần thể nếu cần |
| `EVIDENCED_BY` | `HealthClaim → Source` | vai trò bằng chứng |
| `GOVERNS` | `Regulation → Additive` | ngữ cảnh/phiên bản pháp lý |

Các relationship cấu trúc/nguồn bổ sung gồm `IN_CATEGORY`, `BROADER_THAN`, `SUPPORTED_BY` và `SUPERSEDES`.

## Quy tắc an toàn về sức khỏe và pháp lý

Một `HealthClaim` phải có đối tượng, kết quả sức khỏe, nguồn bằng chứng, điều kiện/liều lượng hoặc bối cảnh, mức bằng chứng và ngày review. Claim biểu diễn bằng chứng trong bối cảnh, không phải tư vấn y khoa. Không tạo relationship `CAUSES` cho khẳng định về nutrient/additive nếu không có kết luận nhân quả rõ ràng được hỗ trợ bởi nguồn.

`PERMITTED_IN`, `OBSERVED_IN` và `COMMON_IN` là ba khái niệm riêng biệt. Quan sát trên nhãn sản phẩm và phát biểu về mức độ phổ biến không chứng minh sự cho phép về pháp lý. Dữ liệu phụ gia Việt Nam phải qua trích xuất theo tầng và review thủ công; Codex/JECFA là nguồn để đối chiếu, không thay thế quy định Việt Nam.

## Constraint và validation

Chạy [constraints.cypher](/Users/ltthanh/LtThanh/KLTN/ViFood-KG/neo4j/cypher/constraints.cypher) trước khi import. Curated validator từ chối ID trùng, thiếu provenance, label/type không hợp lệ, endpoint relationship sai, health claim thiếu thông tin và lượng nutrient sai định dạng. Validator dùng allowlist trước khi tạo các định danh Cypher.

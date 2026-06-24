# Ontology ViFood-KC

ViFood-KC là reference graph cho tri thức thực phẩm đóng gói. Mỗi node chuẩn có các thuộc tính chung:

- `id`
- `name`
- `source`
- `source_url`
- `reviewed_at`
- `status`

Các thuộc tính chuyên biệt như `name_vi`, `ins`, `external_code` sẽ được bổ sung tùy theo loại node.

## Node

| Label | Vai trò |
|---|---|
| `Nutrient` | Dưỡng chất chuẩn. Mã từ nguồn dữ liệu được lưu tại `external_code`. |
| `Ingredient` | Nguyên liệu thực phẩm, bao gồm quan hệ phân cấp và quan hệ dẫn xuất. |
| `Additive` | Phụ gia thực phẩm chuẩn. Mã INS được lưu tại `ins`. |
| `FunctionalClass` | Chức năng công nghệ của phụ gia, ví dụ: chất tạo màu, chất bảo quản hoặc chất điều vị. |
| `FoodCategory` | Nhóm thực phẩm theo quy định pháp lý hoặc taxonomy ngữ nghĩa. |
| `Allergen` | Dị nguyên thực phẩm. |
| `Alias` | Tên gọi khác, từ đồng nghĩa, E-number, INS code hoặc token dùng để liên kết về thực thể chuẩn. |
| `HealthClaim` | Claim sức khỏe có điều kiện áp dụng và mức độ bằng chứng. |
| `HealthOutcome` | Kết quả hoặc tác động sức khỏe được đề cập trong HealthClaim. |
| `Regulation` | Văn bản pháp lý, bao gồm thông tin phiên bản và lịch sử thay thế. |
| `Source` | Nguồn dữ liệu, nguồn pháp lý hoặc nguồn bằng chứng khoa học. |

## Relationship

| Relationship | Ý nghĩa |
|---|---|
| `HAS_NUTRIENT` | Liên kết một `Ingredient` với một `Nutrient` mà nguyên liệu đó chứa. Relationship có thể lưu `amount`, `unit` và `basis`. |
| `HAS_FUNCTION` | Liên kết một `Additive` với một `FunctionalClass` thể hiện chức năng công nghệ của phụ gia. |
| `PERMITTED_IN` | Liên kết một `Additive` với một `FoodCategory` pháp lý mà phụ gia được phép sử dụng. Relationship lưu điều kiện sử dụng, mức dùng tối đa hoặc nguyên tắc GMP khi có, kèm nguồn quy định. |
| `COMMON_IN` | Liên kết một `Additive` với một `FoodCategory` mà phụ gia thường xuất hiện trong thực tế. Relationship phải kèm bằng chứng hoặc nguồn quan sát phù hợp. |
| `OBSERVED_IN` | Liên kết một `Additive` với một nhóm hoặc sản phẩm thực phẩm mà phụ gia được quan sát trên nhãn. Relationship này chỉ phản ánh dữ liệu quan sát, không chứng minh tính hợp pháp. |
| `CONTAINS_ALLERGEN` | Liên kết một `Ingredient` với một `Allergen` mà nguyên liệu có chứa hoặc có khả năng liên quan. |
| `IS_A` | Thể hiện quan hệ phân cấp giữa các `Ingredient`, ví dụ một loại nguyên liệu cụ thể thuộc một nhóm nguyên liệu rộng hơn. |
| `DERIVED_FROM` | Thể hiện nguyên liệu được tạo ra, chiết xuất hoặc dẫn xuất từ một nguyên liệu khác. |
| `REFERS_TO` | Liên kết một `Alias` đến đúng một thực thể chuẩn như `Ingredient`, `Additive`, `Nutrient` hoặc `Allergen`. |
| `SUPPORTED_BY` | Liên kết một thực thể chuẩn với `Source` cung cấp thông tin hoặc bằng chứng hỗ trợ cho thực thể đó. |
| `GOVERNS` | Liên kết một `Regulation` với thực thể hoặc quan hệ mà văn bản đó điều chỉnh, ví dụ `Additive`, `FoodCategory` hoặc `PERMITTED_IN`. |
| `SUPERSEDES` | Liên kết một `Regulation` với văn bản pháp lý cũ mà nó thay thế hoặc hợp nhất. |
| `SUBJECT_OF` | Liên kết thực thể là đối tượng của một `HealthClaim`, ví dụ `Nutrient`, `Ingredient` hoặc `Additive`. |
| `OUTCOME` | Liên kết một `HealthClaim` với `HealthOutcome` được đề cập trong claim. |
| `EVIDENCED_BY` | Liên kết một `HealthClaim` với `Source` chứa bằng chứng khoa học hoặc tài liệu hỗ trợ claim đó. |

## Nguyên tắc phân biệt quan hệ

`PERMITTED_IN`, `COMMON_IN` và `OBSERVED_IN` luôn được quản lý độc lập:

- `PERMITTED_IN` phản ánh tình trạng được phép sử dụng theo quy định pháp lý.
- `COMMON_IN` phản ánh mức độ phổ biến của phụ gia trong một nhóm thực phẩm dựa trên bằng chứng quan sát hoặc dữ liệu đáng tin cậy.
- `OBSERVED_IN` phản ánh việc phụ gia xuất hiện trên nhãn sản phẩm hoặc dữ liệu OCR.

ViFood-KC không suy ra tính hợp pháp của phụ gia chỉ từ dữ liệu OCR hoặc dữ liệu quan sát trên nhãn. Hệ thống cũng không suy ra tác động sức khỏe chỉ vì một chất xuất hiện trong thành phần sản phẩm.

## Quality Gate

Quality gate được chạy trước khi importer kết nối đến Neo4j. Quy trình này kiểm tra:

- Manifest của release dữ liệu.
- SHA-256 của raw snapshot.
- Source registry.
- Provenance của node và relationship.
- Trạng thái `status` của node.
- Schema và kiểu dữ liệu thuộc tính.
- Endpoint của relationship.
- Alias mơ hồ hoặc Alias trỏ đến nhiều thực thể chuẩn.
- Điều kiện dữ liệu bắt buộc của `HealthClaim`.

Một `HealthClaim` chỉ hợp lệ khi có đầy đủ:

- Subject.
- Health outcome.
- Evidence source.
- Điều kiện áp dụng.
- Evidence level.
# Ontology ViFood-KG - Giai đoạn 1

## 1. Mục đích và phạm vi

ViFood-KG là đồ thị tri thức lưu trữ các thông tin đã được kiểm tra về thực phẩm đóng gói, bao gồm:

- Nguyên liệu
- Chất dinh dưỡng
- Phụ gia thực phẩm
- Chất gây dị ứng
- Nhóm thực phẩm
- Tuyên bố sức khỏe và nguồn bằng chứng
- Quy định pháp luật về phụ gia

Trong giai đoạn 1, hệ thống **chưa quản lý sản phẩm cụ thể** như `Product`. Ví dụ, hệ thống có thể lưu thông tin về phụ gia `INS 621`, nhưng chưa lưu sản phẩm mì gói cụ thể nào đang sử dụng phụ gia đó.

Mỗi nút chỉ mang label đúng với loại dữ liệu của nó, ví dụ `:Ingredient`, `:Nutrient` hoặc `:Additive`. Không sử dụng label chung như `:Entity`.

Dữ liệu phải đi qua quy trình sau:

`raw → staging → transform → validate → review → curated release → importer → Neo4j`

Trong đó:

- `raw`: dữ liệu gốc thu thập từ nguồn.
- `staging`: dữ liệu tạm thời trước khi xử lý.
- `transform`: chuẩn hóa tên, mã, đơn vị và cấu trúc dữ liệu.
- `validate`: kiểm tra dữ liệu có đúng định dạng và quy tắc hay không.
- `review`: con người rà soát các dữ liệu cần xác minh.
- `curated release`: bộ dữ liệu đã được duyệt, sẵn sàng nạp.
- `importer`: chương trình nạp dữ liệu vào Neo4j.

Extractor chỉ có nhiệm vụ thu thập hoặc trích xuất dữ liệu; không được ghi trực tiếp vào Neo4j. Importer chỉ nạp dữ liệu đã duyệt; không tự tải dữ liệu, chạy OCR, trích xuất PDF hoặc tự tạo tuyên bố sức khỏe.

## 2. Quy tắc định danh và nguồn dữ liệu

Mỗi nút có một `id` duy nhất, ổn định và không thay đổi khi tên hiển thị thay đổi.

| Label | Ví dụ `id` | Ý nghĩa |
|---|---|---|
| `Nutrient` | `NUTRIENT:SODIUM` | Chất dinh dưỡng Natri |
| `Ingredient` | `INGREDIENT:PALM_OIL` | Nguyên liệu dầu cọ |
| `Additive` | `ADDITIVE:INS_621` | Phụ gia INS 621 |
| `FoodCategory` | `CATEGORY:INSTANT_NOODLES` | Nhóm mì ăn liền |
| `FunctionalClass` | `FUNCTION:FLAVOUR_ENHANCER` | Chức năng điều vị |
| `Allergen` | `ALLERGEN:MILK` | Chất gây dị ứng từ sữa |
| `Alias` | `ALIAS:BOT_NGOT` | Tên gọi khác: bột ngọt |
| `HealthOutcome` | `OUTCOME:HIGH_BLOOD_PRESSURE` | Kết quả sức khỏe: tăng huyết áp |
| `HealthClaim` | `CLAIM:SODIUM_HIGH_INTAKE_BP` | Tuyên bố về lượng Natri cao và huyết áp |
| `Source` | `SOURCE:WHO_HEALTHY_DIET` | Nguồn tài liệu của WHO |
| `Regulation` | `REGULATION:TT24_2019` | Văn bản pháp lý liên quan |

Tùy theo loại dữ liệu, mỗi nút cần có các trường như:

- `id`: mã định danh duy nhất.
- `name`: tên hiển thị chuẩn.
- `status`: trạng thái dữ liệu, ví dụ `active` hoặc `deprecated`.
- `source`: mã nguồn tham chiếu, thường có dạng `SOURCE:*`.
- `source_url`: đường dẫn đến nguồn gốc.
- `reviewed_at`: thời điểm dữ liệu được rà soát.

Dữ liệu gốc và dữ liệu đã chuẩn hóa phải lưu lại thông tin phiên bản và mã bản ghi từ nguồn để có thể truy vết.

Với `Regulation`, không ghi đè nội dung văn bản cũ khi có văn bản mới. Thay vào đó, tạo một nút quy định mới và liên kết bằng quan hệ `SUPERSEDES` để giữ lịch sử thay đổi.

## 3. Các loại nút

Các label được phép sử dụng gồm:

`Nutrient`, `Ingredient`, `Additive`, `FoodCategory`, `FunctionalClass`, `Allergen`, `Alias`, `HealthClaim`, `HealthOutcome`, `Source` và `Regulation`.

Một số thuộc tính quan trọng:

| Label | Thuộc tính | Ý nghĩa |
|---|---|---|
| `Nutrient` | `default_unit` | Đơn vị mặc định, ví dụ `mg`, `g`, `kcal`. |
| `Additive` | `ins_number` | Mã phụ gia INS/E, ví dụ `INS 621`, `E330`. |
| `Alias` | `normalized_name`, `language`, `alias_type` | Tên đã chuẩn hóa, ngôn ngữ và loại tên gọi. |
| `HealthClaim` | `conditions_of_use`, `evidence_level` | Điều kiện sử dụng và mức độ bằng chứng. |
| `Source` | `source_type` | Loại nguồn, ví dụ bài báo khoa học hoặc quy định. |
| `Regulation` | `jurisdiction`, `effective_date`, `version` | Phạm vi áp dụng, ngày hiệu lực và phiên bản văn bản. |

`Alias` dùng để lưu các cách gọi khác của cùng một thực thể, chẳng hạn:

- “Bột ngọt” là tên gọi phổ biến của Monosodium Glutamate.
- “Vitamin C” và “Acid ascorbic” có thể là các tên gọi của cùng một chất.
- `E621` và `INS 621` là các cách ghi mã phụ gia.

`Alias` không phải là một bản sao của nguyên liệu, chất dinh dưỡng hoặc phụ gia mà nó tham chiếu đến.

## 4. Các loại quan hệ

| Quan hệ | Từ → đến | Ý nghĩa |
|---|---|---|
| `IS_A` | `Ingredient → Ingredient` | Quan hệ phân cấp. Ví dụ: gạo lứt thuộc nhóm gạo. Không được tạo chu trình. |
| `DERIVED_FROM` | `Ingredient → Ingredient` | Một nguyên liệu được tạo ra hoặc chiết xuất từ nguyên liệu khác. |
| `HAS_NUTRIENT` | `Ingredient → Nutrient` | Nguyên liệu chứa chất dinh dưỡng với hàm lượng, đơn vị, cơ sở tính và nguồn dữ liệu. |
| `CONTAINS_ALLERGEN` | `Ingredient → Allergen` | Nguyên liệu có chứa hoặc có nguy cơ chứa chất gây dị ứng. |
| `HAS_FUNCTION` | `Additive → FunctionalClass` | Phụ gia có chức năng công nghệ nào, ví dụ bảo quản hoặc điều vị. |
| `PERMITTED_IN` | `Additive → FoodCategory` | Phụ gia được phép dùng trong một nhóm thực phẩm theo điều kiện và văn bản pháp lý cụ thể. |
| `COMMON_IN` | `Additive → FoodCategory` | Phụ gia thường xuất hiện trong một nhóm thực phẩm theo nguồn dữ liệu. |
| `OBSERVED_IN` | `Additive → FoodCategory` | Phụ gia được quan sát trên nhãn của các sản phẩm thuộc nhóm thực phẩm đó. |
| `REFERS_TO` | `Alias → Ingredient/Nutrient/Additive` | Tên gọi khác tham chiếu đến đúng một thực thể chuẩn. |
| `SUBJECT_OF` | `HealthClaim → Nutrient/Ingredient/Additive` | Đối tượng được đề cập trong tuyên bố sức khỏe. |
| `OUTCOME` | `HealthClaim → HealthOutcome` | Kết quả sức khỏe được đề cập trong tuyên bố. |
| `EVIDENCED_BY` | `HealthClaim → Source` | Nguồn bằng chứng của tuyên bố sức khỏe. |
| `GOVERNS` | `Regulation → Additive` | Quy định pháp lý quản lý, cho phép, hạn chế hoặc cấm phụ gia. |
| `IN_CATEGORY` | `Ingredient → FoodCategory` | Phân loại nguyên liệu vào nhóm thực phẩm. |
| `BROADER_THAN` | `FoodCategory → FoodCategory` | Quan hệ phân cấp giữa các nhóm thực phẩm. |
| `SUPPORTED_BY` | `Ingredient/Nutrient/Additive/Regulation → Source` | Liên kết thực thể với nguồn mô tả hoặc nguồn dữ liệu. |
| `SUPERSEDES` | `Regulation → Regulation` | Văn bản mới thay thế hoặc cập nhật văn bản cũ. |

## 5. Quy tắc về sức khỏe và pháp lý

Một `HealthClaim` chỉ hợp lệ khi có đầy đủ:

- Đối tượng được đề cập qua `SUBJECT_OF`.
- Kết quả sức khỏe qua `OUTCOME`.
- Ít nhất một nguồn bằng chứng qua `EVIDENCED_BY`.
- Điều kiện sử dụng, liều lượng hoặc bối cảnh áp dụng khi cần.
- Mức độ bằng chứng, ví dụ `high`, `moderate`, `low` hoặc `insufficient`.
- Thời điểm dữ liệu được rà soát.

`HealthClaim` chỉ biểu diễn thông tin dựa trên bằng chứng và không thay thế tư vấn y khoa. Không dùng quan hệ `CAUSES` để khẳng định nguyên nhân - kết quả giữa chất dinh dưỡng/phụ gia và bệnh lý khi chưa có nguồn chứng minh quan hệ nhân quả rõ ràng.

Ba quan hệ dưới đây phải được hiểu riêng biệt:

| Quan hệ | Ý nghĩa |
|---|---|
| `PERMITTED_IN` | Phụ gia được pháp luật cho phép sử dụng trong nhóm thực phẩm cụ thể. |
| `OBSERVED_IN` | Phụ gia được phát hiện hoặc ghi nhận trên nhãn sản phẩm. |
| `COMMON_IN` | Phụ gia thường xuất hiện trong nhóm thực phẩm theo dữ liệu quan sát hoặc thống kê. |

Việc một phụ gia xuất hiện trên nhãn hoặc thường gặp trong thực tế không đồng nghĩa rằng phụ gia đó được phép sử dụng trong mọi trường hợp.

Dữ liệu phụ gia tại Việt Nam phải được trích xuất, chuẩn hóa và rà soát thủ công trước khi công bố. Codex và JECFA chỉ được dùng làm nguồn đối chiếu; không thay thế các quy định pháp luật đang áp dụng tại Việt Nam.

## 6. Ràng buộc và kiểm tra dữ liệu

Trước khi nạp dữ liệu, cần chạy file [constraints.cypher](/Users/ltthanh/LtThanh/KLTN/ViFood-KG/neo4j/cypher/constraints.cypher) trong Neo4j.

Curated validator phải từ chối các trường hợp sau:

- `id` bị trùng lặp.
- Thiếu thông tin nguồn hoặc không thể truy vết nguồn.
- Label hoặc loại quan hệ không nằm trong danh sách cho phép.
- Quan hệ có điểm đầu hoặc điểm cuối không đúng loại.
- `HealthClaim` thiếu đối tượng, kết quả sức khỏe hoặc nguồn bằng chứng.
- Quan hệ `HAS_NUTRIENT` thiếu hàm lượng, đơn vị hoặc dữ liệu định lượng không hợp lệ.

Validator sử dụng danh sách label và relationship được cho phép trước khi tạo truy vấn Cypher động, nhằm bảo đảm dữ liệu được nạp đúng cấu trúc và hạn chế rủi ro chèn Cypher không an toàn.
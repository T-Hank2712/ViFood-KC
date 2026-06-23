# Ontology ViFood-KG

## Vai trò trong hệ thống

ViFood-KG là reference knowledge graph cho toàn bộ vòng đời phân tích thực phẩm đóng gói, không phải product catalog. Lớp OCR/product bên ngoài quan sát nội dung nhãn; ViFood-KG chuẩn hóa term quan sát được và trả về tri thức có provenance. Khi project hoàn chỉnh, graph bao phủ nutrient, ingredient, additive, allergen, category, quy định và evidence sức khỏe; không ghi output OCR, ảnh hoặc LLM trực tiếp vào graph chuẩn.

```text
"bột ngọt" / "E621" → field chuẩn hoặc Alias → Additive chuẩn
"Natri" / "Na" → field chuẩn hoặc Alias → Nutrient chuẩn
entity chuẩn → nguồn, quy định, chức năng, allergen hoặc health claim
```

## Node

| Label | Vai trò |
|---|---|
| `Nutrient` | Chất dinh dưỡng chuẩn, ví dụ `NUTRIENT:SODIUM`. |
| `Ingredient` | Nguyên liệu chuẩn, ví dụ `INGREDIENT:PALM_OIL`. |
| `Additive` | Phụ gia chuẩn theo INS/E-number. |
| `Allergen` | Dị nguyên chuẩn. |
| `FoodCategory` | Ngữ cảnh thực phẩm cho quy định/phổ biến phụ gia; không dùng để nhận diện ảnh. |
| `FunctionalClass` | Chức năng công nghệ của phụ gia. |
| `Alias` | E-number, synonym hoặc cách viết khác không trùng tên chuẩn hay mã chuẩn đã có trên entity. |
| `HealthClaim` / `HealthOutcome` | Claim sức khỏe có bối cảnh và kết quả sức khỏe. |
| `Source` | Nguồn chuẩn, tài liệu khoa học hoặc nguồn nội bộ được registry cho phép. |
| `Regulation` | Phiên bản văn bản pháp lý. |

Mỗi node chuẩn có `id`, `name`, `source`, `source_url`, `reviewed_at` và `status`. ID là semantic ID ổn định, ví dụ `ADDITIVE:INS_621`, `CATEGORY:FOODON_00002940` hoặc `SOURCE:FOODON`.

`name` giữ tên chuẩn từ nguồn; `name_vi` là tên Việt chuẩn đã được map theo config. `external_code` của Nutrient và `ins` của Additive cũng là thuộc tính chuẩn. Các thuộc tính này được tìm trực tiếp trên entity, nên không tạo Alias trùng với `name`, `name_vi`, `external_code` hoặc `ins`. Alias chỉ dành cho token khác thực sự cần cho entity linking.

## Relationship

| Relationship | Từ → đến | Ý nghĩa |
|---|---|---|
| `IS_A` | `Ingredient → Ingredient` | Phân cấp nguyên liệu, child → parent. |
| `DERIVED_FROM` | `Ingredient → Ingredient` | Nguyên liệu được dẫn xuất từ nguyên liệu khác. |
| `HAS_NUTRIENT` | `Ingredient → Nutrient` | Hàm lượng có `amount`, `unit`, `basis` và nguồn. |
| `CONTAINS_ALLERGEN` | `Ingredient → Allergen` | Dị nguyên có mặt/có thể có. |
| `HAS_FUNCTION` | `Additive → FunctionalClass` | Chức năng công nghệ. |
| `PERMITTED_IN` | `Additive → FoodCategory` | Được phép theo regulation, điều kiện và thời hạn. |
| `COMMON_IN` | `Additive → FoodCategory` | Thường gặp, có bằng chứng. |
| `OBSERVED_IN` | `Additive → FoodCategory` | Quan sát thực tế trên nhãn; không chứng minh hợp pháp. |
| `REFERS_TO` | `Alias → Ingredient/Nutrient/Additive/FoodCategory` | Alias trỏ đúng một entity chuẩn. |
| `BROADER_THAN` | `FoodCategory → FoodCategory` | Category rộng → category hẹp. |
| `SUPPORTED_BY` | `Ingredient/Nutrient/Additive/FoodCategory/Regulation → Source` | Entity được hỗ trợ bởi nguồn. |
| `SUBJECT_OF`, `OUTCOME`, `EVIDENCED_BY` | `HealthClaim → entity/outcome/source` | Cấu trúc evidence cho claim sức khỏe. |
| `GOVERNS`, `SUPERSEDES` | `Regulation → Additive/Regulation` | Pháp lý và lịch sử phiên bản. |

`PERMITTED_IN`, `COMMON_IN` và `OBSERVED_IN` luôn là ba ý nghĩa độc lập.

## Automated quality gate

Release chỉ được import khi có manifest attest theo `strict-v1`. Gate kiểm tra raw snapshot SHA-256, trusted source registry, source node, provenance, trạng thái node, schema, endpoint relationship, alias mơ hồ và ràng buộc sức khỏe. Release có `draft`, source không registry hoặc raw hash sai sẽ bị từ chối trước khi kết nối Neo4j.

`HealthClaim` không phải tư vấn y khoa. Claim bắt buộc có subject, outcome, evidence source, điều kiện/bối cảnh và evidence level; không dùng `CAUSES` khi không có kết luận nhân quả rõ ràng.

## Boundary với product/OCR layer

Product layer nên lưu quan sát như “nhãn sản phẩm ghi E621” kèm OCR text, confidence và bằng chứng ảnh. Knowledge Core không biến quan sát đó thành tri thức chuẩn; nó chỉ map term qua Alias và giải thích thực thể chuẩn. Khi Phase Product/SKU bắt đầu, quan hệ nên mang nghĩa quan sát, không thay cho `PERMITTED_IN` hay `COMMON_IN`.

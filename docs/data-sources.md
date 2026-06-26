# Nguồn dữ liệu của ViFood-KC

ViFood-KC chỉ sử dụng nguồn dữ liệu có xuất xứ rõ ràng. Mỗi nguồn được khai báo trong source registry, mỗi snapshot quan trọng được lưu lại và mỗi curated release được gắn hash SHA-256 để có thể kiểm tra lại.

Source không chỉ là thông tin tham khảo. Trong graph, source là một phần của mô hình tri thức:

```text
(:Entity)-[:SUPPORTED_BY]->(:Source)
```

Điều này giúp mọi node hoặc relationship quan trọng đều trả lời được câu hỏi: “Dữ liệu này đến từ đâu?”

## Nguyên tắc chọn nguồn

ViFood-KC ưu tiên nguồn theo thứ tự:

1. Văn bản pháp lý Việt Nam cho dữ liệu áp dụng tại Việt Nam.
2. Chuẩn quốc tế uy tín cho mã định danh, ontology và đối chiếu chuyên ngành.
3. Tài liệu khoa học hoặc tổ chức y tế chính thống cho claim sức khỏe.
4. Dữ liệu quan sát hoặc dữ liệu sản phẩm chỉ dùng khi có vai trò rõ ràng, không thay thế nguồn chuẩn.

Không import dữ liệu chỉ vì “có vẻ đúng”. Dữ liệu phải có nguồn, vai trò, pipeline và quality gate.

## Nhóm nguồn chính

| Nhóm nguồn | Vai trò trong ViFood-KC |
|---|---|
| FoodOn | Ontology thực phẩm dùng cho Ingredient, IngredientGroup, FoodCategory ngữ nghĩa, synonym và phân cấp thực phẩm. |
| FAO/INFOODS Tagnames | Chuẩn mã định danh cho nutrient/component. |
| Bảng thành phần thực phẩm Việt Nam | Nguồn tham chiếu cho nutrient trong bối cảnh Việt Nam. |
| Quy định ghi nhãn dinh dưỡng Việt Nam | Xác định các nutrient liên quan đến nhãn thực phẩm tại Việt Nam. |
| Văn bản pháp lý phụ gia Việt Nam | Nguồn chính cho Additive, FunctionalClass, FoodCategory pháp lý và giới hạn sử dụng phụ gia. |
| Codex GSFA / JECFA | Nguồn đối chiếu quốc tế về phụ gia, chức năng và an toàn thực phẩm. |
| WHO và nguồn y tế chính thống | Bằng chứng cho HealthClaim và HealthOutcome. |
| ChEBI | Định danh hóa học cho các chất/compound khi cần biểu diễn ingredient dạng hóa chất. |
| Codex CXS 1-1985 | Nguồn chuẩn cho nhóm allergen/dị ứng không dung nạp cần nhận diện trên nhãn thực phẩm đóng gói. |
| Translation seed nội bộ | Tên tiếng Việt và alias tiếng Việt có kiểm soát, phục vụ entity linking. |

## Vai trò của từng loại nguồn

### Ingredient

Ingredient dùng nguồn ontology thực phẩm để chuẩn hóa nguyên liệu food-based và dùng ChEBI để định danh ingredient dạng hóa chất. Các nguyên liệu được lọc theo scope thực phẩm đóng gói để tránh import quá rộng. Tên tiếng Việt và alias tiếng Việt được quản lý riêng bằng seed có kiểm soát.

Ingredient không được lấy trực tiếp từ OCR làm dữ liệu chuẩn. OCR chỉ tạo term quan sát; term đó cần được map về Ingredient chuẩn thông qua tên, alias hoặc mã định danh.

### Nutrient

Nutrient dùng chuẩn mã định danh để tránh nhầm lẫn giữa các chất có tên gần giống nhau. Khi kết hợp nhiều nguồn, ViFood-KC ưu tiên phép nối chính xác bằng mã hoặc tagname thay vì so khớp tên mơ hồ.

### Additive và quy định phụ gia

Additive dùng nguồn pháp lý Việt Nam làm nền tảng cho ngữ cảnh trong nước. Mã INS, tên phụ gia, chức năng công nghệ, nhóm thực phẩm được phép sử dụng và giới hạn sử dụng phải được truy vết về văn bản nguồn.

Codex hoặc nguồn quốc tế có thể dùng để đối chiếu, nhưng không thay thế quy định Việt Nam khi hỏi về phạm vi áp dụng tại Việt Nam.

### HealthClaim

HealthClaim phải đi kèm nguồn bằng chứng. Claim không được sinh tự do từ LLM. Một claim hợp lệ cần có subject, outcome, điều kiện áp dụng, mức bằng chứng và source.

### Allergen

Allergen dùng Codex CXS 1-1985, mục ghi nhãn thực phẩm bao gói sẵn, làm nguồn chính để chuẩn hóa các nhóm dị ứng nguyên/dị ứng không dung nạp như ngũ cốc chứa gluten, giáp xác, trứng, cá, đậu phộng, đậu nành, sữa, hạt cây và sulphit.

Release allergen hiện tạo `Allergen` node và `Alias` để hỗ trợ entity linking. Quan hệ giữa một `Ingredient` cụ thể và `Allergen` cụ thể sẽ được thêm bằng release mapping riêng khi có rule/source đủ rõ, tránh tự động kết luận mơ hồ.

### Alias và bản dịch

Alias dùng để giúp hệ thống nhận diện nhiều cách gọi khác nhau của cùng một thực thể. Alias không được tạo nếu trùng với `name`, `name_vi`, `ins` hoặc `external_code`. Alias mơ hồ phải bị giữ lại ở staging hoặc review, không được tự động import vào graph chuẩn.

## Source registry

Source registry nằm tại:

```text
config/source_registry.yaml
```

Registry định nghĩa:

- `id` của nguồn.
- Tên nguồn.
- URL hoặc vị trí nguồn.
- Vai trò của nguồn trong project.
- Kiểu ingest được phép.
- License hoặc ghi chú khi cần.

Quality gate dùng registry để kiểm tra release. Nếu một node tham chiếu source không có trong registry, release sẽ bị từ chối.

## Snapshot và attestation

Mỗi curated release cần manifest kèm thông tin nguồn:

```text
data/curated/releases/<release>.attested.yaml
```

Manifest ghi:

- version của release.
- ngày release.
- danh sách source.
- raw snapshot liên quan.
- SHA-256 của file nguồn.
- metadata của automated quality gate.

Nhờ vậy, dữ liệu trong Neo4j có thể được truy ngược về file nguồn cụ thể, không chỉ về tên nguồn chung chung.

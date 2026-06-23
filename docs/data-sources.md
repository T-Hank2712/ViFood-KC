# Nguồn dữ liệu của toàn project

Mỗi nguồn chỉ được dùng sau khi có pipeline phù hợp. Khi ingest, dữ liệu phải đi qua `raw → staging → transform → curated release → attestation → quality gate → Neo4j`; raw snapshot được hash để tái lập và truy vết.

## Đang dùng

| Nguồn | Vai trò trong project | Phạm vi hiện tại |
|---|---|---|
| FoodOn | `FoodCategory`, synonym và hierarchy | FoodCategory core cho thực phẩm đóng gói, không import toàn bộ ontology. |
| FAO/INFOODS Tagnames | mã định danh `Nutrient` | Nutrient master; mã nằm trực tiếp tại `external_code`. |
| 09/VBHN-BYT | `Additive`, `FunctionalClass`, `Regulation` | Phụ lục 1 đã tạo 400 phụ gia; Phụ lục 2A/2B là bước kế tiếp. |
| ViFood-KG translation seed | `name_vi` và synonym tiếng Việt chọn lọc | Mapping có version, chỉ cho FoodCategory core. |

## Sẽ dùng khi mở rộng đúng mảng tri thức

| Nguồn | Mục đích dự kiến | Điều kiện ingest |
|---|---|---|
| ChEBI | chemical identifier, synonym, hierarchy cho ingredient/additive | Chỉ term cần thiết, không import toàn bộ ChEBI. |
| USDA FoodData Central | `Ingredient -[:HAS_NUTRIENT]-> Nutrient` | Chọn dataset phù hợp, chuẩn hóa nutrient code và basis. |
| FAO/INFOODS AnFooD và Bảng thành phần thực phẩm Việt Nam | bổ sung nutrient của ingredient | Xác minh giấy phép, cấu trúc và phiên bản trước khi tải. |
| Codex GSFA và JECFA | đối chiếu identifier, chức năng, safety evidence | Không thay thế quy định áp dụng tại Việt Nam. |
| WHO Healthy Diet | evidence cho `HealthClaim` | Claim phải có subject, outcome, điều kiện và source; không tạo tư vấn y khoa. |

Các nguồn trên được giữ trong `config/source_registry.yaml`, nhưng không có raw dataset hay thư mục rỗng trong repository cho tới khi pipeline tương ứng được triển khai.

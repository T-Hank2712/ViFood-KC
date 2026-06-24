# Nguồn dữ liệu của ViFood-KC

ViFood-KC chỉ ingest dữ liệu từ nguồn có xuất xứ rõ ràng. Mỗi snapshot được lưu raw, hash SHA-256 và gắn `Source` vào node/relationship được tạo.

| Nguồn | Vai trò |
|---|---|
| FoodOn | Taxonomy FoodCategory, synonym và ngữ nghĩa thực phẩm. |
| FAO/INFOODS Tagnames | Mã định danh Nutrient/component. |
| 09/VBHN-BYT | Danh mục Additive, FunctionalClass, nhóm thực phẩm pháp lý và giới hạn sử dụng tại Việt Nam. |
| ViFood-KC Vietnamese translation seed | `name_vi` và synonym tiếng Việt có rule/version rõ ràng. |
| ChEBI | Chemical identifier, synonym và hierarchy cho ingredient/additive. |
| USDA FoodData Central | Dữ liệu Ingredient - Nutrient. |
| Bảng thành phần thực phẩm Việt Nam SMILING 2013 (FAO) | Xác nhận Nutrient đang có dữ liệu trong bảng thành phần Việt Nam, bằng phép giao chính xác theo tagname INFOODS trong file XLSX. |
| Bảng thành phần thực phẩm Việt Nam 2007 (FAO) | Tài liệu tham chiếu song ngữ; không dùng phép so khớp tên gần đúng để tự import Nutrient. |
| Thông tư 29/2023/TT-BYT | Quy định thành phần dinh dưỡng phải/được ghi trên nhãn thực phẩm tại Việt Nam. |
| Codex GSFA / JECFA | Đối chiếu quốc tế về phụ gia, chức năng và safety evidence; không thay thế quy định Việt Nam. |
| WHO Healthy Diet | Evidence cho HealthClaim; không dùng làm tư vấn y khoa cá nhân. |

Source registry nằm tại `config/source_registry.yaml`. Không source nào được import nếu chưa được đăng ký, chưa có pipeline phù hợp hoặc không vượt qua quality gate.

Với Nutrient, pipeline chỉ chọn các tagname xuất hiện đúng nguyên văn ở cả INFOODS và bảng SMILING 2013. Thành phần không giao được giữa hai chuẩn được ghi vào báo cáo loại trừ; chúng không được tự gán sang một dưỡng chất “gần giống”.

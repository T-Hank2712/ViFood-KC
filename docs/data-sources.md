# Nguồn dữ liệu của ViFood-KG

Tài liệu này mô tả các nguồn dữ liệu dự kiến sử dụng cho ViFood-KG. Mọi dữ liệu đi qua `raw → staging → transform → curated release → attestation → automated quality gate → Neo4j`. Không ghi trực tiếp dữ liệu tải về, OCR hoặc trích xuất PDF vào production graph.

## Nguyên tắc chung

- Chỉ sử dụng nguồn chính thức hoặc nguồn có xuất xứ và giấy phép rõ ràng.
- Lưu URL, ngày tải, phiên bản nguồn, mã bản ghi nguồn, giấy phép và SHA-256 của raw snapshot khi có.
- Không diễn giải dữ liệu vượt quá nội dung của nguồn; đặc biệt với claim sức khỏe, ADI/TDI và quy định pháp lý.
- Dữ liệu pháp lý chỉ được import khi vượt qua strict automated quality gate; rule mapping phải có version và source rõ ràng.
- Codex và JECFA dùng để đối chiếu ngữ nghĩa quốc tế, không thay thế quy định đang có hiệu lực tại Việt Nam.

## 1. FoodOn

- **Trang nguồn:** <https://github.com/FoodOntology/foodon>
- **Định dạng:** OWL, synonym TSV.
- **Giấy phép:** CC BY 4.0.
- **Vai trò:** taxonomy/selective vocabulary cho `Ingredient`, `FoodCategory`, synonym và hierarchy.
- **Cách dùng:** chỉ lấy FoodCategory core phục vụ ngữ cảnh phụ gia/quy định; không dùng FoodOn để nhận diện ảnh và không import toàn bộ ontology.

## 2. ChEBI

- **Trang nguồn:** <https://www.ebi.ac.uk/chebi/downloads/>
- **Định dạng:** TSV, JSON, OBO, OWL, PostgreSQL dump.
- **Giấy phép:** CC BY 4.0.
- **Vai trò:** mã chất hóa học, synonym, CAS, cấu trúc và chemical hierarchy cho nutrient, additive và hợp chất liên quan.
- **Cách dùng:** lọc các chất liên quan đến thực phẩm; không import toàn bộ ChEBI khi chưa có nhu cầu rõ ràng.

## 3. FAO/INFOODS Food Component Identifiers (Tagnames)

- **Trang nguồn:** <https://www.fao.org/infoods/infoods/standards-guidelines/food-component-identifiers-tagnames/en/>
- **Vai trò:** chuẩn mã định danh nutrient/component.
- **Cách dùng:** tạo nutrient master nội bộ khoảng 50–100 nutrient phổ biến trên nhãn trước. Lưu ý Tagnames là chuẩn mã component, không tự động cung cấp tất cả dữ liệu hàm lượng dinh dưỡng.

## 4. USDA FoodData Central

- **Trang tải dữ liệu:** <https://fdc.nal.usda.gov/download-datasets/>
- **API guide:** <https://fdc.nal.usda.gov/api-guide>
- **Định dạng:** bulk CSV/JSON và API.
- **Giấy phép:** CC0/Public Domain.
- **Vai trò:** quan hệ `Ingredient -[:HAS_NUTRIENT]-> Nutrient`, với lượng, đơn vị và basis, thường theo 100 g.
- **Cách dùng:** ưu tiên Foundation Foods và SR Legacy. Chưa ingest Branded Foods vì khối lượng lớn và không phải catalog sản phẩm Việt Nam.

## 5. FAO/INFOODS AnFooD 2.0

- **Trang nguồn:** <https://www.fao.org/food-composition/tables-and-databases/detail/%28global--2017%29-fao-infoods-analytical-food-composition-database---version-2.0-%28anfood2.0%29/en>
- **Định dạng:** XLSX.
- **Vai trò:** nguồn bổ sung cho quan hệ ingredient–nutrient.
- **Cách dùng:** chuẩn hóa mã nutrient theo nutrient master trước khi tạo `HAS_NUTRIENT`.

## 6. Vietnamese Food Composition Table 2017

- **Trang nguồn:** <https://www.fao.org/food-composition/tables-and-databases-2/detail/%28viet-nam--2017%29-vietnamese-food-composition-table/en>
- **Vai trò:** tham chiếu thuật ngữ và dữ liệu thành phần thực phẩm Việt Nam.
- **Lưu ý:** FAO mô tả đây là sách in. Không tự scan/copy hàng loạt nếu chưa xác minh quyền sử dụng hoặc chưa có nguồn số hóa hợp pháp.

## 7. Quy định phụ gia thực phẩm Việt Nam

- **Thông tư 24/2019/TT-BYT:** <https://vfa.gov.vn/chi-dao-dieu-hanh/ban-hanh-thong-tu-so-242019tt-byt-quy-dinh-ve-quan-ly-va-su-dung-phu-gia-thuc-pham.html>
- **Thông tin cập nhật liên quan Thông tư 17/2023/TT-BYT:** <https://vfa.gov.vn/tin-tuc/huong-dan-tra-cuu-quy-dinh-ve-su-dung-phu-gia-thuc-pham-cua-ub-tieu-chuan-thuc-pham-codex-danh-muc-hoac-co-so-du-lieu-ve-huong-lieu-thuc-pham-cua-jecfa-fema-va-lien-minh-chau-au.html>
- **Định dạng:** PDF và phụ lục.
- **Vai trò:** `Additive`, INS, `FunctionalClass`, `PERMITTED_IN`, mức sử dụng tối đa, đơn vị, thời hạn hiệu lực và điều kiện pháp lý tại Việt Nam.
- **Cách dùng:** extract vào staging, chạy rule mapping version hóa và strict automated quality gate trước khi tạo curated release. Đây là nguồn quyết định cho chức năng cảnh báo tuân thủ tại Việt Nam.

## 8. Codex GSFA

- **Trang nguồn:** <https://www.fao.org/gsfaonline/index.html?lang=en>
- **Vai trò:** INS, synonym, functional class, Codex food category và điều kiện sử dụng phụ gia.
- **Cách dùng:** đối chiếu và bổ sung ngữ nghĩa quốc tế; không dùng để thay thế quy định Việt Nam. Không scrape hàng loạt khi chưa có kênh tải/API và quyền sử dụng rõ ràng.

## 9. WHO/FAO JECFA

- **Trang nguồn:** <https://apps.who.int/food-additives-contaminants-jecfa-database/>
- **Vai trò:** thông tin đánh giá phụ gia như ADI/TDI nếu có, năm đánh giá, report/monograph và thông tin an toàn.
- **Cách dùng:** chỉ lấy các phụ gia đã tồn tại trong graph. Không ingest toàn bộ database. Không diễn giải `ADI not specified` thành “được dùng không giới hạn”.

## 10. WHO Healthy Diet và các guideline liên quan

- **Trang nguồn:** <https://www.who.int/news-room/fact-sheets/detail/healthy-diet>
- **Vai trò:** tạo các `HealthClaim` có evidence level, điều kiện/bối cảnh và source cho sodium, free sugars, saturated fat, trans fat và các chủ đề liên quan.
- **Cách dùng:** tạo từng claim có đối tượng, điều kiện/liều lượng hoặc bối cảnh, mức bằng chứng, nguồn và ngày review; không scrape thành bulk dataset và không biến nội dung nguồn thành tư vấn y khoa cá nhân.

## Thứ tự ưu tiên ingest

1. FAO/INFOODS Tagnames để tạo nutrient master; phần này đã có pipeline.
2. FoodOn core nhỏ để có FoodCategory context; không mở rộng thành taxonomy ảnh.
3. Additive master từ quy định phụ gia Việt Nam và Codex GSFA.
4. ChEBI để bổ sung chemical ID/synonym cho additive và ingredient.
5. USDA FoodData Central và AnFooD để tạo quan hệ `HAS_NUTRIENT`.
6. JECFA và WHO để bổ sung safety/evidence/health claim.

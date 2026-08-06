# GLANCE — Kịch bản lời thoại toàn video

Tự động trích từ `sections/*/**.py` (dict `VO`, `voiceover(text=...)`, `say()`, `narrated_caption()`, `beat()`). Sửa trực tiếp trong code section tương ứng, không sửa file này.


*Owner: Trần Nguyên · File: `sections/s4_trannguyen/s4_trannguyen.py`*


### `S4_01_TAG`

- Đầu vào của bài toán là một đồ thị có thuộc tính văn bản, được ký hiệu là G bằng V, E, T.
- Trong ví dụ đồ thị trích dẫn này, mỗi nót đại diện cho một bài báo khoa học.
- Các cạnh thể hiện quan hệ trích dẫn giữa các bài báo.
- Ngoài cấu trúc đồ thị, mỗi nót còn có nội dung văn bản, chẳng hạn như tiêu đề hoặc phần tóm tắt.
- Như vậy, mỗi nót đồng thời có hai nguồn thông tin: nội dung của chính nó và mối quan hệ với các nót khác.

### `S4_02_EndToEnd`

- Từ một đồ thị tương đối phức tạp, mục tiêu của gờ lans là dự đoán nhãn cho từng nót.
- Ở đây, chúng ta tập trung vào nót A.
- Sau khi đi qua toàn bộ hệ thống, gờ lans tạo ra một phân phối xác suất trên các lớp.
- Ví dụ, xác suất của nót A lần lượt là 0.12, 0.73 và 0.15.
- Bên trong gờ lans không phải là một hộp đen: hệ thống lần lượt định tuyến, đọc văn bản, rồi tinh chỉnh dự đoán.
- Bước một: gờ nờ nờ, mờ lờ bê và cấu trúc đồ thị cùng cung cấp đặc trưng cho bộ định tuyến, để tính ra một điểm định tuyến.
- Bước hai: nót được định tuyến sẽ được gửi sang một lờ lờ mờ dùng chung, đọc ngữ cảnh ở ba mức nót trung tâm, một-hop và hai-hop.
- Bước ba: bộ tinh chỉnh kết hợp véc-tơ biểu diễn của gờ nờ nờ với véc-tơ biểu diễn của lờ lờ mờ để tạo ra một dự đoán đã được tinh chỉnh.
- Hệ thống chọn lớp có xác suất lớn nhất bằng phép argmax.
- Do đó, trong ví dụ này, nót A được dự đoán thuộc lớp thứ hai.

### `S4_03_ThreeSources`

- Để đưa ra quyết định, gờ lans thu thập ba nhóm thông tin cho nót A.
- Các nguồn thông tin này sẽ được kết hợp để bộ định tuyến quyết định có nên sử dụng lờ lờ mờ cho nót A hay không.

### `S4_04_InitialState`

- Đầu tiên, nót A được đưa vào mô hình nền gờ nờ nờ. Ở lớp số không, trạng thái ẩn của nót A chính là đặc trưng ban đầu của nót. Nói cách khác, h A mũ 0 bằng x A.
- Ví dụ, nếu đặc trưng của nót A là véc-tơ 0.8, âm 0.1 và 0.5, thì trạng thái ẩn ban đầu cũng nhận đúng véc-tơ này.
- Ở bước này chưa có thông tin từ các nót hàng xóm.

### `S4_05_Aggregate`

- Tiếp theo là bước tổng hợp.
- gờ nờ nờ thu thập trạng thái ẩn của các nót hàng xóm của A, ví dụ như B, C, D và E.
- Sau đó, các véc-tơ này được tổng hợp thành một thông điệp hàng xóm. Trong hoạt cảnh, chúng ta sử dụng phép trung bình để minh họa.
- Bốn véc-tơ hàng xóm được cộng lại rồi chia cho bốn, tạo thành thông điệp mới là không phẩy năm, không phẩy năm. Lưu ý rằng phép trung bình chỉ là một ví dụ; tùy gờ nờ nờ mô hình nền, phép tổng hợp có thể được cài đặt theo cách khác.

### `S4_06_Update`

- Sau khi có thông điệp hàng xóm, gờ nờ nờ thực hiện bước cập nhật. Bước này kết hợp trạng thái trước đó của nót A với thông tin vừa tổng hợp từ hàng xóm.
- Trong ví dụ minh họa, trạng thái cũ của A là 0.2, 0.8, còn thông điệp hàng xóm là 0.6, 0.4.
- Sau bước cập nhật, ta thu được một biểu diễn mới là không phẩy bốn, không phẩy sáu.
- Các con số này chỉ dùng để minh họa luồng xử lý. Trong mô hình thực tế, giá trị được quyết định bởi các tham số đã học.

### `S4_07_BeforeAfter`

- Điểm cần lưu ý là nót A vẫn là cùng một bài báo. Thứ thay đổi không phải danh tính của nót mà là biểu diễn của nó.
- Trước bước cập nhật, véc-tơ chủ yếu chứa thông tin của chính nót A.
- Sau bước cập nhật, véc-tơ đã tích hợp thêm bằng chứng từ vùng lân cận.
- Quá trình tổng hợp và cập nhật có thể được lặp lại qua nhiều lớp gờ nờ nờ để thu được biểu diễn cuối cùng.

### `S4_08_EmbeddingPrediction`

- Sau các message-passing lớp, gờ nờ nờ tạo ra hai đầu ra quan trọng.
- Đầu ra thứ nhất là nót véc-tơ biểu diễn z G của A. véc-tơ biểu diễn này tóm tắt cả đặc trưng của nót A và thông tin cấu trúc mà gờ nờ nờ đã học được.
- Đầu ra thứ hai là dự đoán ban đầu p H phẩy A.
- Đầu dự đoán nhận véc-tơ biểu diễn, đi qua mờ lờ bê và sóp mác để tạo xác suất trên các lớp. Đây cũng là dự đoán cuối cùng nếu nót A không được gửi sang lờ lờ mờ.

### `S4_09_Uncertainty`

- gờ lans không chỉ quan tâm gờ nờ nờ dự đoán lớp nào mà còn quan tâm dự đoán đó có ổn định hay không.
- Hệ thống thực hiện nhiều lượt truyền xuôi với đờ-róp-ao cho cùng một nót. Nếu các lần chạy tạo ra phân phối gần giống nhau, gờ nờ nờ tương đối chắc chắn.
- Ngược lại, nếu kết quả thay đổi nhiều giữa các lần chạy, độ bất định của nót sẽ cao.
- độ bất định là một tín hiệu cho thấy nót A có thể là trường hợp khó, nhưng nó không được sử dụng riêng lẻ để quyết định định tuyến.

### `S4_10_MLPQ`

- Song song với gờ nờ nờ, gờ lans sử dụng một mờ lờ bê được ký hiệu là Q.
- Khác với gờ nờ nờ, mờ lờ bê này chỉ nhận đặc trưng x v của nót, không sử dụng cạnh và không thực hiện truyền thông điệp.
- Với mỗi nót, Q tạo ra một phân phối xác suất mềm p Q phẩy v.
- Cùng một mờ lờ bê được áp dụng cho nót A và các nót hàng xóm B, C, D, E.
- Mục đích của các phân phối này không phải để thay thế dự đoán của gờ nờ nờ, mà để hỗ trợ ước lượng mức độ tương đồng giữa nót và vùng lân cận.

### `S4_11_NeighborAverage`

- Để đánh giá vùng lân cận của A, gờ lans lấy một phân phối từ mỗi nót hàng xóm.
- Các phân phối của B, C, D và E được cộng lại thành S A.
- Sau đó, tổng này được chia cho số lượng hàng xóm.
- Trong ví dụ, nót A có bốn hàng xóm nên hệ thống chia cho bốn và thu được phân phối trung bình 0.275, 0.480, 0.245.
- véc-tơ này đại diện cho xu hướng lớp chung trong vùng lân cận của nót A.

### `S4_12_HomophilyDot`

- Tiếp theo, gờ lans so sánh phân phối của chính nót A với phân phối trung bình của các hàng xóm.
- Phép so sánh được thực hiện bằng tích vô hướng.
- Nếu hai phân phối tương tự nhau, giá trị sẽ cao, cho thấy nót A có xu hướng giống vùng lân cận. Nếu hai phân phối khác nhau, giá trị này sẽ thấp và nót A có khả năng nằm trong vùng dị phối.
- Đây chỉ là một định tuyến tín hiệu ban đầu, nghĩa là một tín hiệu hỗ trợ bộ định tuyến, chứ không trực tiếp quyết định việc gọi lờ lờ mờ.

### `S4_13_OriginalInfo`

- Ngoài các biểu diễn đã được học, gờ lans vẫn giữ lại thông tin gốc của nót A.
- Thành phần đầu tiên là x A, tức đặc trưng được trích xuất từ nội dung văn bản.
- Thành phần thứ hai là bậc d A, thể hiện số lượng hàng xóm trực tiếp.
- Trong ví dụ, A kết nối với bốn nót nên bậc bằng bốn.
- Hai thông tin này giúp bộ định tuyến quan sát trực tiếp cả đặc điểm ngữ nghĩa ban đầu lẫn lượng thông tin cấu trúc mà gờ nờ nờ có thể khai thác.

### `S4_14_RoutingFeature`

- Đến đây, toàn bộ tín hiệu được ghép thành đặc trưng định tuyến f A.
- Véc-tơ này gồm năm thành phần: véc-tơ biểu diễn của gờ nờ nờ, độ bất định, hô mô phi li ước lượng, đặc trưng gốc và bậc. Mỗi thành phần phản ánh một khía cạnh khác nhau của nót A.
- Quan trọng là không có một tín hiệu riêng lẻ nào tự quyết định định tuyến. bộ định tuyến sẽ học cách xem xét tổ hợp của cả năm tín hiệu.

### `S4_15_RouterScore`

- Đặc trưng định tuyến được đưa vào một bộ định tuyến rất nhẹ.
- Bộ định tuyến gồm một lớp tuyến tính và hàm xích-moi, tạo ra điểm định tuyến a A nằm trong khoảng từ không đến một.
- điểm cao cho thấy nót A có khả năng nhận được lợi ích khi sử dụng lờ lờ mờ. điểm thấp cho thấy dự đoán hiện tại của gờ nờ nờ có thể đã đủ tốt.
- Cần phân biệt rằng đây không phải xác suất lớp. Nó chỉ biểu diễn mức độ nên gửi nót sang nhánh lờ lờ mờ.

### `S4_16_TopK`

- gờ lans không sử dụng một ngưỡng cố định cho từng nót.
- Thay vào đó, hệ thống xếp hạng điểm định tuyến của tất cả nót trong bát.
- Ví dụ, các nót A, E và C có ba điểm cao nhất nên được chọn vào tốp ba.
- Chỉ đúng ca nót được gửi sang lờ lờ mờ.
- Nhờ vậy, gờ lans kiểm soát chính xác ngân sách tính toán và tránh tình trạng số lần gọi lờ lờ mờ tăng ngoài dự kiến.

### `S4_17_TwoFlows`

- Sau bước tốp ca, quy trình được chia thành hai nhánh rõ ràng.
- Nhánh thứ nhất dành cho những nót thuộc tập định tuyến R, tức là các nót được sử dụng lờ lờ mờ. Nhánh thứ hai dành cho những nót không thuộc R.
- Việc tách hai nhánh này là cơ sở giúp gờ lans vừa tận dụng sức mạnh ngữ nghĩa của lờ lờ mờ, vừa duy trì chi phí xử lý hợp lý.

### `S4_18_WithoutLLM`

- Trước tiên là nhánh đơn giản hơn.
- Nếu một nót không được định tuyến, gờ lans bỏ qua toàn bộ bước tạo câu lệnh, gọi lờ lờ mờ và bộ tinh chỉnh. Phân phối cuối cùng của nót được giữ nguyên bằng p H phẩy v, tức dự đoán ban đầu của gờ nờ nờ.
- Sau đó, hệ thống lấy lớp có xác suất lớn nhất. Nhờ vậy, các nót dễ không phải chịu thêm chi phí và cũng không bị lờ lờ mờ làm thay đổi một dự đoán vốn đã chính xác.

### `S4_19_WithLLMContext`

- Với nót A được định tuyến, gờ lans khai thác văn bản ở ba mức ngữ cảnh.
- Mức đầu tiên là văn bản của nót trung tâm, chỉ chứa nội dung của chính nót A.
- Mức thứ hai là 1-hop ngữ cảnh, bổ sung nội dung từ các nót trích dẫn trực tiếp.
- Mức cuối cùng là 2-hop ngữ cảnh, cung cấp ngữ cảnh rộng hơn từ các nót cách A hai cạnh.
- Ba mức được xử lý riêng thay vì gộp tất cả thành một câu lệnh rất dài.

### `S4_23_EgoEmbedding`

- câu lệnh đầu tiên chỉ chứa văn bản của nót trung tâm của nót A.
- câu lệnh này được đưa vào quy en ba em-bét tám bi, đóng vai trò dùng chung véc-tơ biểu diễn bộ mã hóa.
- Đầu ra không phải là một câu trả lời hay nhãn lớp, mà là véc-tơ biểu diễn z L phẩy 0 của A.
- véc-tơ biểu diễn này biểu diễn thông tin ngữ nghĩa từ chính nội dung của nót A.

### `S4_24_OneHopEmbedding`

- Ở bước tiếp theo, câu lệnh được mở rộng bằng nội dung của các nót hàng xóm trực tiếp. Câu lệnh mới vẫn đi qua cùng một bộ mã hóa lờ lờ mờ, chứ không phải một mô hình khác. Đầu ra là z L phẩy 1 của A. véc-tơ biểu diễn này bổ sung bối cảnh từ các bài báo có quan hệ trực tiếp với nót A.

### `S4_25_TwoHopEmbedding`

- Tương tự, câu lệnh thứ ba đưa thêm ngữ cảnh ở khoảng cách hai bước. Nó giúp mô hình quan sát một vùng rộng hơn của đồ thị trích dẫn và nhận biết chủ đề tổng quát xung quanh nót A. câu lệnh tiếp tục sử dụng bộ mã hóa lờ lờ mờ dùng chung và tạo véc-tơ biểu diễn z L phẩy 2 của A. Như vậy, một bộ mã hóa được tái sử dụng cho ba phiên bản câu lệnh khác nhau.

### `S4_26_MergeEmbeddings`

- Ba véc-tơ biểu diễn vừa tạo được nối lại với nhau.
- Kết quả là Z L của A, đại diện cho toàn bộ thông tin ngữ nghĩa mà lờ lờ mờ thu được.
- véc-tơ này giữ riêng ba thành phần: nội dung của chính nót, ngữ cảnh trực tiếp và ngữ cảnh xa hơn.
- lờ lờ mờ biểu diễn vẫn chưa phải là kết quả phân loại cuối cùng. Nó sẽ được kết hợp tiếp với biểu diễn đồ thị từ gờ nờ nờ.

### `S4_27_FusedRepresentation`

- véc-tơ biểu diễn z G của A từ gờ nờ nờ chứa thông tin về đặc trưng và cấu trúc đồ thị.
- Trong khi đó, Z L của A chứa thông tin ngữ nghĩa được trích từ ba mức câu lệnh. gờ lans gờ lans nối hai véc-tơ này thành một biểu diễn hợp nhất.
- Có thể hiểu phần bên trái đại diện cho thông tin cấu trúc từ gờ nờ nờ, còn ba phần bên phải đại diện cho ngữ nghĩa ngữ cảnh từ lờ lờ mờ.
- véc-tơ kết hợp này là đầu vào trực tiếp của bộ tinh chỉnh.

### `S4_28_RefinerMLP`

- bộ tinh chỉnh là một mờ lờ bê có nhiệm vụ kết hợp hai nguồn bằng chứng.
- Biểu diễn hợp nhất lần lượt đi qua các lớp tuyến tính, ri-lu, đờ-róp-ao và lớp đầu ra.
- Cuối cùng, sóp mác tạo ra phân phối lớp mới p C phẩy A.
- bộ tinh chỉnh không thay thế gờ nờ nờ hoặc lờ lờ mờ. Nó học cách cân bằng thông tin cấu trúc từ gờ nờ nờ với thông tin ngữ nghĩa từ lờ lờ mờ để tạo ra dự đoán phù hợp hơn cho được định tuyến nót.

### `S4_29_RefinedDistribution`

- Trước khi sử dụng lờ lờ mờ, gờ nờ nờ tạo phân phối ban đầu là 0.45, 0.40 và 0.15. Phân phối này chưa thể hiện sự khác biệt rõ ràng giữa hai lớp đầu tiên.
- Sau khi bổ sung lờ lờ mờ ngữ cảnh và đi qua bộ tinh chỉnh, phân phối chuyển thành 0.15, 0.80 và 0.05.
- Xác suất tập trung mạnh hơn vào lớp khai phá đồ thị.
- Ví dụ này minh họa cách ngữ cảnh văn bản có thể giúp điều chỉnh một dự đoán còn chưa chắc chắn của gờ nờ nờ.

### `S4_30_FinalPrediction`

- Cuối cùng, gờ lans xác định phân phối được sử dụng tùy theo kết quả định tuyến.
- Nếu nót thuộc tập R, hệ thống sử dụng phân phối đã tinh chỉnh là p C phẩy v. Nếu nót không thuộc R, hệ thống giữ nguyên phân phối gờ nờ nờ là p H phẩy v.
- Với nót A trong ví dụ, A được định tuyến nên sử dụng kết quả của bộ tinh chỉnh. Lớp có xác suất lớn nhất là khai phá đồ thị, vì vậy đây là nhãn cuối cùng của nót A.
- Tóm lại, gờ lans có thể được mô tả bằng ba ý chính: gờ nờ nờ được sử dụng trước để xử lý toàn bộ đồ thị. bộ định tuyến lựa chọn những nót thực sự cần hỗ trợ. Và lờ lờ mờ chỉ được gọi theo nhu cầu để bổ sung thông tin ngữ nghĩa cho các trường hợp khó. Thiết kế này giúp gờ lans kết hợp được khả năng khai thác cấu trúc của gờ nờ nờ với khả năng hiểu văn bản của lờ lờ mờ, nhưng vẫn kiểm soát được chi phí tính toán.
- bộ định tuyến không khả vi. Vậy huấn luyện nó kiểu gì, và có thật sự hiệu quả?

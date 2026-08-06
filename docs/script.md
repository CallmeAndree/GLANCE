# GLANCE — Kịch bản lời thoại toàn video

Tự động trích từ `sections/*/**.py` (dict `VO`, `voiceover(text=...)`, `say()`, `narrated_caption()`, `beat()`). Sửa trực tiếp trong code section tương ứng, không sửa file này.


## Section 1 — Core problem of GNN–LLM fusion

*Owner: Trúc Mai · File: `sections/s1_trucmai/s1_trucmai.py`*

### `Task1GLANCERebuilt`

- Trong thế giới thực,
- thông tin hiếm khi tồn tại một cách độc lập.
- Mỗi đối tượng vừa mang nội dung riêng,
- vừa được kết nối với nhiều đối tượng khác.
- Việc khai thác đồng thời hai nguồn thông tin này
- mở ra nhiều cơ hội,
- nhưng cũng đặt ra những thách thức mới.
- Trong vi đi ô này, chúng ta sẽ cùng tìm hiểu
- cách gờ lans for context tiếp cận bài toán đó.
- Hãy hình dung một mạng lưới học thuật kết nối bằng các trích dẫn.
- Mỗi bài báo có tiêu đề và tóm tắt riêng,
- và được nối với những bài báo mà nó trích dẫn.
- Các bài báo trích dẫn lẫn nhau.
- Mỗi bài trở thành một nót, mỗi trích dẫn thành một cạnh.
- Cấu trúc kết hợp giữa văn bản và quan hệ này
- được gọi là đồ thị có thuộc tính văn bản, hay ti ây gi.
- Ti ây gi cho phép mô hình suy luận từ hai nguồn cùng lúc:
- nót đang nói về điều gì,
- và nót đó kết nối với những ai.
- Từ hai nguồn thông tin này,
- bài toán tiếp theo là dự đoán nhãn
- của những nót chưa biết lớp.
- Trước đây, nội dung văn bản của mỗi nót
- như tê ép y đê ép hoặc véc-tơ biểu diễn tĩnh.
- thường được biểu diễn bằng các đặc trưng tương đối nông,
- Các véc-tơ này sau đó được đưa vào gờ nờ nờ
- để tổng hợp thông tin từ những nót lân cận.
- Cách này khai thác tốt cấu trúc đồ thị,
- nhưng khả năng nắm bắt ngữ cảnh và ý nghĩa sâu của văn bản còn hạn chế.
- Gần đây, sự phát triển của các mô hình ngôn ngữ lớn
- đã mở ra một hướng tiếp cận mới.
- Các kiến trúc lai kết hợp khả năng suy luận ngữ nghĩa của lờ lờ mờ
- nhằm khai thác đầy đủ cả nội dung và quan hệ trong ti ây gi.
- với khả năng học cấu trúc của gờ nờ nờ,
- các phương pháp hiện nay chia thành hai hướng:
- lờ lờ mờ làm bộ tăng cường và lờ lờ mờ-as-predictor.
- lờ lờ mờ làm bộ tăng cường tạo véc-tơ ngữ nghĩa giàu hơn,
- rồi gờ nờ nờ tiếp tục truyền thông tin và dự đoán.
- gờ nờ nờ vẫn có thể bị kéo lệch bởi các hàng xóm nhiễu.
- tuy nhiên, dù véc-tơ ngữ nghĩa tốt hơn,
- lờ lờ mờ-as-predictor đổi toàn bộ thông tin
- thành một câu lệnh văn bản dài.
- chuỗi văn bản càng dài và đắt đỏ hơn.
- vùng lân cận càng mở rộng,
- Tuy nhiên, phần lớn các hệ thống lai hiện nay
- vẫn áp dụng một chiến lược hợp nhất duy nhất cho tất cả các nót trong đồ thị.
- bất kể đặc điểm riêng của từng nót.
- Đầu ra của gờ nờ nờ và lờ lờ mờ được kết hợp theo cùng một cơ chế,
- Nhưng các nót không giống nhau: có nót được gờ nờ nờ xử lý tốt nhờ cấu trúc lân cận rõ ràng,
- trong khi nót khác hưởng lợi nhiều hơn từ khả năng suy luận ngữ nghĩa của lờ lờ mờ.
- Một cơ chế hợp nhất đồng nhất vì thế
- không phản ánh được mức độ hữu ích khác nhau của hai mô hình với từng nót.
- Vậy làm thế nào để quyết định, ở cấp độ từng nót,
- khi nào nên tận dụng lờ lờ mờ?
- ba nót có thể rất khác nhau.
- nót a được gờ nờ nờ xử lý tốt.
- hàng xóm đồng thuận, gờ nờ nờ tạo véc-tơ ổn định.
- gờ nờ nờ dự đoán đúng. gọi lờ lờ mờ là không cần thiết.
- nót bê có vùng lân cận chứa nhiều loại khác nhau.
- các tín hiệu kéo nhiều hướng, gờ nờ nờ dự đoán sai.
- lờ lờ mờ sửa lại dự đoán thành công.
- nhưng văn bản nót bê rất rõ ràng.
- nhưng văn bản lại rất mơ hồ.
- nót xê cũng khó với gờ nờ nờ.
- cả hai mô hình đều thất bại.
- lờ lờ mờ không đủ bằng chứng để sửa kết quả.
- nhưng chỉ nót bê nhận được lợi ích từ lờ lờ mờ.
- nót bê và nót xê đều khó với gờ nờ nờ.
- Nói cách khác, khó với gờ nờ nờ
- chưa chắc hưởng lợi từ lờ lờ mờ.
- Nó cho thấy vì sao độ chính xác tổng thể có thể tăng rất ít.
- Xét một ví dụ minh họa.
- còn mười phần trăm là các nót khó.
- giả sử chín mươi phần trăm là các nót dễ,
- trên nhóm khó, lờ lờ mờ giúp tăng mười ba điểm phần trăm.
- nhưng trên toàn đồ thị, tổng thể chỉ tăng không chấm bốn điểm.
- lợi ích lớn ở một nhóm nhỏ trông rất nhỏ khi tính tổng.
- Như vậy, độ khó với gờ nờ nờ
- chưa đủ để quyết định.
- giữ dự đoán của gờ nờ nờ, hoặc gọi lờ lờ mờ để tinh chỉnh nó.
- gờ lans biến việc này thành một quyết định định tuyến cho từng nót:
- Nếu phải chọn nót để gọi lờ lờ mờ,
- người ta đã chọn bằng cách nào?


## Section 2 — Routing heuristic

*Owner: Hoàng Phan · File: `sections/s2_hoangphan/s2_hoangphan.py`*

### `S2_01_AdaptiveFusion`

- Thay vì định tuyến mọi nót sang lờ lờ mờ như cách kết hợp tĩnh, tại sao không chỉ chọn những nót thật sự có lợi khi gọi lờ lờ mờ?
- Hướng tiếp cận này được gọi là kết hợp thích ứng.
- Ta hãy cùng khảo sát ba công trình từng áp dụng cách tiếp cận này: e lờ lờ a gờ nờ nờ, lờ lờ mờ, gờ nờ nờ, và lốc gin.
- Chúng dùng tiêu chí nào để đánh giá và định tuyến nót sang lờ lờ mờ?
- Từng tiêu chí mạnh yếu ra sao?
- Và gờ lans đã kế thừa được gì từ cả ba?

### `S2_02_TwoQuestions`

- Trước khi chấm ba tiêu chí đó, ta cần một thước đo.
- Có hai câu hỏi rất dễ tưởng là một.
- Câu thứ nhất: nót nào trông có vẻ khó với gờ nờ nờ?
- Câu thứ hai: nót nào thật sự khá lên khi gọi lờ lờ mờ?
- Nghe thì giống nhau, nhưng hai tập nót này không trùng nhau.
- Chỉ phần giao mới đáng để ta trả tiền cho một lời gọi.
- Ba tiêu chí sắp xem đều chỉ nhìn được vòng tròn bên trái.
- Hãy nhớ hình này, ta sẽ quay lại nó ở cuối phần.

### `S2_03_Degree`

- Đầu tiên là e lờ lờ a gờ nờ nờ.
- Công trình này dùng nót bậc làm tiêu chí định tuyến.
- bậc là số hàng xóm nối với nót đó.
- nót bậc thấp nhận ít thông tin qua truyền thông điệp.
- Nên gờ nờ nờ có thể gặp khó, và ta ưu tiên định tuyến chúng sang lờ lờ mờ.
- Màu nót là lớp thật của nó.
- Đây là hai nót bậc thấp nhất, chúng sẽ được định tuyến.
- Nhưng hãy nhìn kỹ vùng bên trái này.
- Hàng xóm duy nhất của nó cùng lớp, và cả vùng cũng chỉ có một lớp.
- truyền thông điệp chỉ đưa vào tín hiệu đồng thuận.
- gờ nờ nờ vốn đã đúng ở đây. Gọi lờ lờ mờ chỉ là lãng phí tiền.
- Bây giờ ngược lại, hãy nhìn nót giữa hình.
- bậc của nó cao nhất đồ thị, nên tiêu chí bỏ qua.
- Nhưng sáu trong bảy hàng xóm lại khác lớp với nó.
- truyền thông điệp trộn tín hiệu mâu thuẫn, gờ nờ nờ dự đoán sai.
- Đây mới đúng là nót cần lờ lờ mờ, nhưng nó không được chọn.
- bậc chỉ đo số lượng thông tin cấu trúc.
- Nó không đo chất lượng của thông tin đó.
- bậc thấp cũng không đảm bảo văn bản của nót đủ rõ cho lờ lờ mờ.

### `S2_04_Density`

- Tiêu chí thứ hai là mật độ xê, được kế thừa từ lờ lờ mờ, gờ nờ nờ.
- Mật độ xê ở đây không phải mật độ cạnh hay số tam giác xung quanh nót.
- Trước hết, ca min phân cụm các véc-tơ đặc trưng, với số cụm bằng số lớp.
- Với mỗi nót, ta đo khoảng cách từ véc-tơ của nó đến tâm cụm gần nhất.
- Trước tiên, nót gần tâm cụm có khoảng cách nhỏ, nên mật độ xê cao. Ngược lại, nót ở xa tâm cụm có khoảng cách lớn, nên mật độ xê thấp.
- Trong thí nghiệm của gờ lans, các nót có mật độ xê thấp nhất được định tuyến sang lờ lờ mờ.
- Tuy nhiên, khoảng cách đến tâm cụm không trực tiếp cho biết gờ nờ nờ đang sai, cũng không cho biết lờ lờ mờ có thể sửa dự đoán đó hay không.
- Vì vậy, mật độ xê vẫn chỉ là một tín hiệu thay thế gián tiếp cho lợi ích của việc định tuyến.

### `S2_05_Uncertainty`

- Cuối cùng là lốc gin.
- Công trình này dùng gờ nờ nờ uncertainty làm tiêu chí định tuyến.
- Mô hình chạy nhiều lần lượt truyền xuôi với đờ-róp-ao bật.
- Mỗi lần, một phần neuron bị tắt ngẫu nhiên.
- Dự đoán dao động nhiều thì nót đó bị coi là không chắc chắn.
- So với bậc và mật độ, độ bất định trực tiếp hơn hẳn.
- Vì nó phản ánh trạng thái của chính mô hình gờ nờ nờ.
- Nhưng độ bất định cao chỉ nói rằng gờ nờ nờ đang gặp khó.
- Nó không đảm bảo lờ lờ mờ sẽ làm tốt hơn.
- Hãy xét hai nót có cùng mức độ bất định cao.
- nót thứ nhất: cấu trúc nhiễu, nhưng phần tóm tắt nói rất rõ chủ đề.
- lờ lờ mờ đọc đoạn văn bản này và sửa được dự đoán.
- nót thứ hai: cấu trúc nhiễu y hệt, nhưng văn bản ngắn và mơ hồ.
- Ở đây lờ lờ mờ cũng không đủ thông tin, gọi thêm chỉ tốn tiền.
- Cùng một tín hiệu độ bất định, hai kết cục khác hẳn nhau.
- Ngoài ra, lốc gin còn dùng lờ lờ mờ để nối lại cạnh đồ thị.
- Tức là chỉnh sửa hoặc loại bỏ những cạnh khó.
- Việc này có rủi ro riêng.
- Nó có thể xoá nhầm cạnh dị phối vẫn đang mang thông tin.
- độ bất định đọc được trạng thái của gờ nờ nờ.
- Nhưng nó không đọc được lờ lờ mờ.

### `S2_06_Setup`

- Vậy đánh giá một tiêu chí định tuyến thế nào cho công bằng?
- bài báo không chỉ nhìn độ chính xác của gờ nờ nờ trên nhóm nót bị coi là khó.
- Thay vào đó, kiểm tra thẳng điều gì xảy ra sau khi định tuyến.
- Từ đồ thị, tiêu chí chọn ra tốp ca phần trăm nót.
- Những nót đó đi qua lờ lờ mờ, rồi so với dự đoán gốc của gờ nờ nờ.
- Quan trọng: cả gờ nờ nờ lẫn lờ lờ mờ đều được đóng băng.
- Nên mọi khác biệt chỉ đến từ việc tiêu chí đã chọn tập nót nào.
- Thí nghiệm chạy trên cô ra, pắp mét và ác xíp hai ba.
- Hai mô hình nền: gờ xê en là mô hình cơ sở, gờ xê en hai mạnh hơn.
- Hai loại đặc trưng: gốc, và tăng cường sinh bởi quy en ba tám bi.
- Bảng số lát nữa chỉ lấy cột tăng cường, cho gọn.
- Mỗi tiêu chí lần lượt định tuyến tốp mười, mười lăm, rồi hai mươi phần trăm.
- Cụ thể: cách dựa trên bậc chọn nót có bậc thấp nhất.
- Cách dựa trên mật độ chọn nót có mật độ phân cụm thấp nhất.
- Cách dựa trên độ bất định chọn nót có độ bất định cao nhất.
- Và ngẫu nhiên định tuyến làm mốc so sánh.
- Đây là cái mốc mà mọi tiêu chí ít nhất phải vượt qua.

### `S2_07_NCS`

- Để đo chất lượng tập nót được định tuyến, bài báo dùng điểm sửa ròng.
- Viết tắt là en xi ét. Ý tưởng rất trực quan.
- gờ nờ nờ sai mà lờ lờ mờ sửa thành đúng: một lần sửa có lợi.
- Tập này gọi là đắp-bờ-liu xi, sai thành đúng.
- gờ nờ nờ đúng mà lờ lờ mờ làm thành sai: một lần sửa có hại.
- Tập này gọi là xi đắp-bờ-liu, đúng thành sai.
- en xi ét bằng số nót trong đắp-bờ-liu xi trừ số nót trong xi đắp-bờ-liu.
- Rồi chia cho tổng số nót được định tuyến.
- Ví dụ, giả sử ta định tuyến một trăm nót.
- lờ lờ mờ sửa đúng được hai mươi lăm nót.
- Nhưng đồng thời làm hỏng mười nót.
- en xi ét bằng hai mươi lăm trừ mười, chia một trăm, tức không chấm một năm.
- Cách đọc en xi ét như sau.
- en xi ét dương nghĩa là lờ lờ mờ tạo ra lợi ích ròng.
- en xi ét bằng không: số nót sửa được đúng bằng số nót bị làm hỏng.
- Toàn bộ chi phí gọi lờ lờ mờ coi như đổ sông đổ biển.
- Còn en xi ét âm nghĩa là định tuyến gây hại nhiều hơn có lợi.
- Điểm hay của en xi ét nằm ở đây.
- Nó không thưởng cho việc tìm ra nót khó.
- Nó chỉ thưởng khi lờ lờ mờ thật sự sửa được nót đó.

### `S2_08_Table1`

- Đây là Bảng 1 của bài báo, trình bày lại dưới dạng bản đồ nhiệt.
- Mỗi ô là một giá trị en xi ét.
- Ô càng xanh thì lợi ích càng cao, càng đỏ thì càng gây hại.
- Bốn hàng là bốn chiến lược, chín cột là ba bộ dữ liệu nhân ba mức định tuyến.
- Hãy nhìn pắp mét và ác xíp hai ba trước.
- Ở đây độ bất định là tiêu chí tốt nhất trong mọi thiết lập.
- Với gờ xê en dùng đặc trưng tăng cường trên pắp mét, en xi ét đạt không chấm hai không.
- Nghĩa là cứ một trăm nót được định tuyến, lờ lờ mờ tạo hai mươi lần sửa có lợi.
- Sau khi đã trừ đi những nót bị làm sai. Đây là kết quả tốt.
- Nhưng bây giờ nhìn sang cột cô ra bên trái.
- Cả mảng đỏ. Trên bộ dữ liệu này không tiêu chí nào có lợi.
- Kể cả tiêu chí vừa thắng ở hai bộ kia.
- Chuyện gì đang xảy ra ở đây?

### `S2_09_PubmedVsCora`

- Tách riêng độ bất định ra, đặt hai bộ dữ liệu cạnh nhau.
- Trên pắp mét, tiêu chí này cho en xi ét dương ở cả ba mức.
- Trên cô ra, vẫn tiêu chí đó, cả ba mức đều âm.
- Không phải kém đi một chút, mà đổi hẳn dấu.
- Ba đường nét đứt là mốc chọn nót ngẫu nhiên trên cô ra.
- Ở mức mười phần trăm, chọn bừa chỉ âm không chấm không hai.
- Còn chọn kỹ những nót mà gờ nờ nờ không chắc chắn nhất.
- Lại tụt xuống âm không chấm không chín, tệ hơn hẳn chọn bừa.
- Ở hai mức còn lại nó nhúc nhích khá hơn ngẫu nhiên, nhưng vẫn âm cả ba.
- Cùng một luật, ngược dấu. Tiêu chí này phụ thuộc bộ dữ liệu.
- Nói cách khác, độ bất định của gờ nờ nờ không phải lúc nào cũng phản ánh lợi thế của lờ lờ mờ.

### `S2_10_DegreeDensity`

- Còn bậc và mật độ phân cụm thì sao?
- Tạm bỏ hàng độ bất định sang một bên.
- Chỉ so ba hàng còn lại với nhau.
- Trong phần lớn thiết lập, en xi ét của chúng chỉ xấp xỉ ngẫu nhiên định tuyến.
- Có trường hợp còn thấp hơn cả ngẫu nhiên.
- Ví dụ, trên cô ra với mô hình nền gờ xê en hai.
- Cách dựa trên bậc cho en xi ét âm ở cả ba mức định tuyến.
- Trên pắp mét và ác xíp hai ba đôi khi có lợi ích dương.
- Nhưng mức cải thiện rất nhỏ và không hề nhất quán.
- Thuộc tính cấu trúc đơn giản có thể hữu ích đôi lúc.
- Nhưng không đủ để xác định chắc chắn nót nào cần lờ lờ mờ.

### `S2_11_Backbone`

- Còn một quan sát nữa, và nó khá tinh tế.
- Hiệu quả định tuyến thay đổi khi mô hình nền thay đổi.
- Trên pắp mét, độ bất định với gờ xê en đạt en xi ét từ không chấm một bảy đến không chấm hai không.
- Nhưng đổi sang mô hình nền mạnh hơn là gờ xê en hai.
- Cùng tiêu chí đó chỉ còn khoảng không chấm không tám đến không chấm không chín. Giảm hơn một nửa.
- Lý do có thể hiểu thế này.
- gờ xê en hai đã tự xử lý được một phần nót khó.
- Nên phần còn lại cho lờ lờ mờ sửa cũng co hẹp theo.
- Một nót khó với gờ xê en chưa chắc còn khó với gờ xê en hai.
- tiêu chí định tuyến không chỉ phụ thuộc bộ dữ liệu.
- Mà còn phụ thuộc cả mô hình nền đang dùng.

### `S2_12_Limits`

- Tổng hợp lại, bài báo chỉ ra ba hạn chế chính.
- Thứ nhất, chúng phụ thuộc bộ dữ liệu.
- Tín hiệu tốt trên pắp mét có thể gây hại trên cô ra.
- Thứ hai, chúng phụ thuộc mô hình nền.
- Đổi gờ nờ nờ thì tập nót khó cũng đổi theo.
- Và thứ ba, quan trọng nhất.
- Cả ba đều chỉ là tín hiệu thay thế cho độ khó với gờ nờ nờ.
- Trong khi đó, thứ bộ định tuyến thật sự cần ước lượng là lợi thế của lờ lờ mờ.
- Tức phần hàm mất mát tiết kiệm được khi dùng lờ lờ mờ so với chỉ dùng gờ nờ nờ.
- Còn nhớ hai vòng tròn ở đầu phần không?
- Ba tiêu chí ta vừa xem đều đo vòng bên trái.
- Còn thứ ta cần lại nằm ở vòng bên phải.
- Và còn một yếu tố nữa: chi phí.
- nót đáng định tuyến không chỉ vì gờ nờ nờ làm chưa tốt.
- Mà vì lờ lờ mờ phải cải thiện đủ nhiều để bù lại giá của lời gọi đó.
- Vậy quay lại câu hỏi ban đầu: gờ lans kế thừa được gì từ ba công trình này?
- Nó giữ lại cả ba tín hiệu, nhưng chỉ dùng làm đầu vào cho một bộ định tuyến.
- Và bỏ hẳn cách để một tín hiệu đơn lẻ tự quyết định.

### `S2_13_Bridge`

- Heuristic thủ công không ổn định.
- Vậy tín hiệu nào mới đúng?


## Section 3 — Structural signal

*Owner: Nhựt Anh · File: `sections/s3_nhutanh/s3_nhutanh.py`*

### `S3_01_LocalHomophily`

- Tín hiệu đầu tiên là độ đồng nhất cục bộ. Nó đo mức độ tương đồng về nhãn giữa một nót và các hàng xóm trực tiếp của nó.
- Cụ thể, với mỗi hàng xóm u, ta kiểm tra liệu nhãn của u có giống nhãn của vê hay không. Sau đó lấy tỷ lệ trên toàn bộ tập hàng xóm.
- Trong ví dụ này, ba trong bốn hàng xóm cùng nhãn với vê, vì vậy hắc phẩy vê bằng ba phần tư, tức không chấm bảy năm.
- Khi độ đồng nhất cục bộ cao, thông tin từ hàng xóm thường nhất quán với nót trung tâm. Vì gờ nờ nờ học bằng cách tổng hợp thông tin lân cận, quá trình truyền thông điệp thường có lợi trong trường hợp này.
- Ngược lại, khi độ đồng nhất cục bộ thấp, phần lớn hàng xóm thuộc lớp khác. Việc tổng hợp các biểu diễn này có thể đưa tín hiệu không phù hợp vào nót trung tâm, và khiến gờ nờ nờ dự đoán sai.

### `S3_02_RelativeDegree`

- Tín hiệu thứ hai là bậc tương đối. Bậc thông thường chỉ cho biết nót có bao nhiêu cạnh. Bậc tương đối đặt giá trị đó trong bối cảnh của chính tập hàng xóm.
- Với mỗi hàng xóm u, tác giả so sánh bậc của vê với bậc của u, rồi lấy trung bình trên tất cả hàng xóm.
- Nếu bậc tương đối lớn hơn một, nót vê có xu hướng kết nối nhiều hơn các hàng xóm. Nếu nhỏ hơn một, nó kết nối ít hơn các nót xung quanh.
- Trong ví dụ này, bậc của vê thấp hơn cả hai hàng xóm, nên bậc tương đối xấp xỉ không chấm bảy chín, nhỏ hơn một.

### `S3_03_Complementary`

- Sau đó, tác giả chia các nót thành từng nhóm theo độ đồng nhất cục bộ và bậc tương đối, rồi so sánh độ chính xác của gờ nờ nờ với lờ lờ mờ trong mỗi nhóm.
- Kết quả cho thấy một xu hướng bổ sung rõ rệt. Gi en en hoạt động tốt ở những vùng có độ đồng nhất cao và được kết nối tốt. Nhưng khi độ đồng nhất hoặc bậc tương đối giảm, lợi thế của lờ lờ mờ tăng lên.
- Trên Cô-ra, ở nhóm nót khó, lờ lờ mờ đạt mức cải thiện tới hai mươi chấm bốn phần trăm so với mô hình tốt tiếp theo là gi xi en hai sử dụng đặc trưng được lờ lờ mờ tăng cường.
- Hai tín hiệu này còn tương tác với nhau. Khi đồng thời phân nhóm theo cả độ đồng nhất và bậc, chênh lệch hiệu năng giữa các nhóm cấu trúc có thể lên tới ba mươi chấm một phần trăm.

### `S3_04_EstimatedHomophily`

- Độ đồng nhất cục bộ có vẻ là một tín hiệu định tuyến rất tốt. Tuy nhiên, công thức này cần nhãn thật của nót và hàng xóm, đúng vào những thông tin không có sẵn đối với các nót cần dự đoán.
- Để giải quyết vấn đề này, tác giả huấn luyện một mờ lờ bê kiu trên đặc trưng nót để dự đoán nhãn tạm thời.
- Sau đó, các nhãn dự đoán được dùng thay cho nhãn thật để tính độ đồng nhất cục bộ ước lượng.
- Trong đánh giá định tuyến bằng en xi ét, độ đồng nhất thực có thứ hạng trung bình tốt nhất. Quan trọng hơn, khi loại bỏ những tín hiệu cần nhãn thật, độ đồng nhất ước lượng đạt thứ hạng trung bình tốt nhất trong các phương pháp kinh nghiệm không cần nhãn.

### `S3_05_Bridge`

- Như vậy, độ đồng nhất cục bộ và bậc tương đối không trực tiếp dự đoán nhãn. Chúng giúp nhận diện những nót có cấu trúc bất lợi đối với gờ nờ nờ, và nơi lờ lờ mờ có khả năng tạo thêm giá trị.
- Tuy nhiên, kết quả cũng cho thấy không có một tín hiệu đơn lẻ nào đủ ổn định để quyết định định tuyến trong mọi trường hợp. Vì vậy, gờ lans không sử dụng một ngưỡng cố định. Thay vào đó, nó kết hợp các tín hiệu này trong một bộ định tuyến được học thích nghi cho từng nót.
- Phần tiếp theo sẽ đi vào chính những tín hiệu mà bộ định tuyến này đọc từ mỗi nót.

### `S3_06_FiveSignals`

- Vì vậy, thay vì chỉ dựa vào độ đồng nhất, gờ lans mô tả mỗi nót bằng năm tín hiệu định tuyến bổ sung cho nhau.
- Mỗi tín hiệu phản ánh một khía cạnh khác nhau: thông tin gờ nờ nờ đã học được, mức độ tin cậy của gờ nờ nờ, sự nhất quán với hàng xóm, nội dung riêng của nót, và lượng thông tin cấu trúc sẵn có. Phần còn lại của mục này sẽ dựng lần lượt từng tín hiệu.

### `S3_07_ThreeSources`

- Năm tín hiệu này đến từ ba nguồn. Với nót a, gờ lans thu thập lần lượt ba nhóm thông tin sau.
- Các nguồn thông tin này sẽ được kết hợp để bộ định tuyến quyết định có nên sử dụng lờ lờ mờ cho nót a hay không. Ta bắt đầu từ nhóm thứ nhất: những gì gờ nờ nờ tạo ra.

### `S3_08_InitialState`

- Đầu tiên, nót a được đưa vào mô hình nền gờ nờ nờ. Ở lớp số không, trạng thái ẩn của nót a chính là đặc trưng ban đầu của nót. Nói cách khác, hắc phẩy a mũ không bằng ích phẩy a.
- Ví dụ, nếu đặc trưng của nót a là véc-tơ không chấm tám, âm không chấm một và không chấm năm, thì trạng thái ẩn ban đầu cũng nhận đúng véc-tơ này.
- Ở bước này chưa có thông tin từ các nót hàng xóm.

### `S3_09_Aggregate`

- Tiếp theo là bước tổng hợp.
- Gờ nờ nờ thu thập trạng thái ẩn của các nót hàng xóm của a, ví dụ như bê, xê, đê và e.
- Sau đó, các véc-tơ này được tổng hợp thành một thông điệp hàng xóm. Trong hoạt cảnh, chúng ta sử dụng phép trung bình để minh họa.
- Bốn véc-tơ hàng xóm được cộng lại rồi chia cho bốn, tạo thành thông điệp mới là không chấm năm, không chấm năm. Lưu ý rằng phép trung bình chỉ là một ví dụ; tùy mô hình nền gờ nờ nờ, phép tổng hợp có thể được cài đặt theo cách khác.

### `S3_10_Update`

- Sau khi có thông điệp hàng xóm, gờ nờ nờ thực hiện bước cập nhật. Bước này kết hợp trạng thái trước đó của nót a với thông tin vừa tổng hợp từ hàng xóm.
- Trong ví dụ minh họa, trạng thái cũ của a là không chấm hai, không chấm tám, còn thông điệp hàng xóm là không chấm sáu, không chấm bốn.
- Sau bước cập nhật, ta thu được một biểu diễn mới là không chấm bốn, không chấm sáu.
- Các con số này chỉ dùng để minh họa luồng xử lý. Trong mô hình thực tế, giá trị được quyết định bởi các tham số đã học.

### `S3_11_BeforeAfter`

- Điểm cần lưu ý là nót a vẫn là cùng một bài báo. Thứ thay đổi không phải danh tính của nót mà là biểu diễn của nó.
- Trước bước cập nhật, véc-tơ chủ yếu chứa thông tin của chính nót a.
- Sau bước cập nhật, véc-tơ đã tích hợp thêm bằng chứng từ vùng lân cận.
- Quá trình tổng hợp và cập nhật có thể được lặp lại qua nhiều lớp gờ nờ nờ để thu được biểu diễn cuối cùng.

### `S3_12_NodeEmbedding`

- Quay lại đồ thị quen thuộc của cả video. Nót a cùng vùng lân cận trong phạm vi ca bước được đưa vào mô hình nền gờ nờ nờ.
- Sau các lớp truyền thông điệp, gờ nờ nờ tạo ra hai đầu ra quan trọng.
- Đầu ra thứ nhất là véc-tơ biểu diễn dét gờ a. Véc-tơ biểu diễn này tóm tắt cả đặc trưng của nót a và thông tin cấu trúc mà gờ nờ nờ đã học được. Đây chính là tín hiệu định tuyến đầu tiên.
- Đầu ra thứ hai là dự đoán ban đầu bê hắc phẩy a.
- Đầu dự đoán nhận véc-tơ biểu diễn, đi qua mờ lờ bê và sóp mác để tạo xác suất trên các lớp. Đây cũng là dự đoán cuối cùng nếu nót a không được gửi sang lờ lờ mờ, và nó được lưu lại chứ không phải một thành phần của véc-tơ định tuyến.

### `S3_13_Uncertainty`

- Gờ lans không chỉ quan tâm gờ nờ nờ dự đoán lớp nào mà còn quan tâm dự đoán đó có ổn định hay không.
- Hệ thống thực hiện nhiều lượt truyền xuôi với đờ-róp-ao cho cùng một nót. Nếu các lần chạy tạo ra phân phối gần giống nhau, gờ nờ nờ tương đối chắc chắn.
- Ngược lại, nếu kết quả thay đổi nhiều giữa các lần chạy, độ bất định của nót sẽ cao.
- Độ bất định là một tín hiệu cho thấy nót a có thể là trường hợp khó, nhưng nó không được sử dụng riêng lẻ để quyết định định tuyến.

### `S3_14_MLPQ`

- Song song với gờ nờ nờ, gờ lans sử dụng một mờ lờ bê được ký hiệu là qui.
- Khác với gờ nờ nờ, mờ lờ bê này chỉ nhận đặc trưng ích phẩy vê của nót, không sử dụng cạnh và không thực hiện truyền thông điệp.
- Với mỗi nót, qui tạo ra một phân phối xác suất mềm bê qui phẩy vê.
- Cùng một mờ lờ bê được áp dụng cho nót a và các nót hàng xóm bê, xê, đê, e.
- Mục đích của các phân phối này không phải để thay thế dự đoán của gờ nờ nờ, mà để hỗ trợ ước lượng mức độ tương đồng giữa nót và vùng lân cận.

### `S3_15_NeighborAverage`

- Để đánh giá vùng lân cận của a, gờ lans lấy một phân phối từ mỗi nót hàng xóm.
- Các phân phối của bê, xê, đê và e được cộng lại thành ết phẩy a.
- Sau đó, tổng này được chia cho số lượng hàng xóm.
- Trong ví dụ, nót a có bốn hàng xóm nên hệ thống chia cho bốn và thu được phân phối trung bình không chấm hai bảy năm, không chấm bốn tám không, không chấm hai bốn năm.
- Véc-tơ này đại diện cho xu hướng lớp chung trong vùng lân cận của nót a.

### `S3_16_SoftHomophily`

- Tiếp theo, gờ lans so sánh phân phối của chính nót a với phân phối trung bình của các hàng xóm.
- Phép so sánh được thực hiện bằng tích vô hướng.
- Nếu hai phân phối tương tự nhau, giá trị sẽ cao, cho thấy nót a có xu hướng giống vùng lân cận. Nếu hai phân phối khác nhau, giá trị này sẽ thấp và nót a có khả năng nằm trong vùng dị phối.
- So với việc chỉ kiểm tra hai nhãn dự đoán có giống nhau hay không, phiên bản mềm còn giữ lại mức độ chắc chắn của mờ lờ bê.
- Đây chỉ là một tín hiệu tiên nghiệm cho việc định tuyến, nghĩa là một tín hiệu hỗ trợ bộ định tuyến, chứ không trực tiếp quyết định việc gọi lờ lờ mờ.

### `S3_17_NodeFeatures`

- Ngoài các biểu diễn đã được học, gờ lans vẫn giữ lại thông tin gốc của nót a.
- Thành phần đầu tiên là ích phẩy a, tức đặc trưng được trích xuất từ nội dung văn bản.
- Đặc trưng này giữ nguyên nội dung riêng của nót trước khi gờ nờ nờ tổng hợp thông tin từ hàng xóm, nên nó vẫn hữu ích khi véc-tơ biểu diễn của gờ nờ nờ bị vùng lân cận làm nhiễu.

### `S3_18_Degree`

- Thành phần thứ hai là bậc đê phẩy a, thể hiện số lượng hàng xóm trực tiếp.
- Trong ví dụ, a kết nối với bốn nót nên bậc bằng bốn.
- Hai thông tin này giúp bộ định tuyến quan sát trực tiếp cả đặc điểm ngữ nghĩa ban đầu lẫn lượng thông tin cấu trúc mà gờ nờ nờ có thể khai thác.
- Cần phân biệt rõ với phần phân tích lúc nãy: ở đó ta dùng bậc tương đối để so sánh nót với hàng xóm, còn bộ định tuyến của gờ lans dùng bậc thô, tức trực tiếp số lượng hàng xóm.

### `S3_19_RoutingFeature`

- Đến đây, toàn bộ tín hiệu được ghép thành đặc trưng định tuyến ép phẩy a.
- Véc-tơ này gồm năm thành phần: véc-tơ biểu diễn của gờ nờ nờ, độ bất định, độ đồng nhất ước lượng, đặc trưng gốc và bậc. Mỗi thành phần phản ánh một khía cạnh khác nhau của nót a.
- Quan trọng là không có một tín hiệu riêng lẻ nào tự quyết định định tuyến. Bộ định tuyến sẽ học cách xem xét tổ hợp của cả năm tín hiệu.
- Đến đây, năm nguồn thông tin đã được nối thành một véc-tơ đặc trưng định tuyến. Véc-tơ này mô tả trạng thái của nót, nhưng chưa phải là quyết định gọi lờ lờ mờ. Đã có tín hiệu. Giờ ráp nó vào một kiến trúc chạy được.


## Section 4 — GLANCE architecture

*Owner: Trần Nguyên · File: `sections/s4_trannguyen/s4_trannguyen.py`*

### `S4_01_TAG`

- Đầu vào của bài toán là một đồ thị có thuộc tính văn bản, được ký hiệu là gờ bằng vê, e và tê.
- Trong ví dụ đồ thị trích dẫn này, mỗi nót đại diện cho một bài báo khoa học.
- Các cạnh thể hiện quan hệ trích dẫn giữa các bài báo.
- Ngoài cấu trúc đồ thị, mỗi nót còn có nội dung văn bản, chẳng hạn như tiêu đề hoặc phần tóm tắt.
- Như vậy, mỗi nót đồng thời có hai nguồn thông tin: nội dung của chính nó và mối quan hệ với các nót khác.

### `S4_02_EndToEnd`

- Từ một đồ thị tương đối phức tạp, mục tiêu của gờ lans là dự đoán nhãn cho từng nót.
- Ở đây, chúng ta tập trung vào nót a.
- Sau khi đi qua toàn bộ hệ thống, gờ lans tạo ra một phân phối xác suất trên các lớp.
- Ví dụ, xác suất của nót a lần lượt là không chấm một hai, không chấm bảy ba và không chấm một năm.
- Bên trong gờ lans không phải là một hộp đen: hệ thống lần lượt định tuyến, đọc văn bản, rồi tinh chỉnh dự đoán.
- Bước một: từ năm tín hiệu đã dựng ở phần trước, mỗi nót đã có một đặc trưng định tuyến ép phẩy vê. Gờ lans học một bộ định tuyến ánh xạ ép phẩy vê thành lợi ích dự kiến của việc gọi lờ lờ mờ.
- Bước hai: nót được định tuyến sẽ được gửi sang một lờ lờ mờ dùng chung, đọc ngữ cảnh ở ba mức nót trung tâm, một-hop và hai-hop.
- Bước ba: bộ tinh chỉnh kết hợp véc-tơ biểu diễn của gờ nờ nờ với véc-tơ biểu diễn của lờ lờ mờ để tạo ra một dự đoán đã được tinh chỉnh.
- Hệ thống chọn lớp có xác suất lớn nhất bằng phép argmax.
- Do đó, trong ví dụ này, nót a được dự đoán thuộc lớp thứ hai.

### `S4_15_RouterScore`

- Bây giờ ta đi vào chi tiết bước một. Đặc trưng định tuyến ép phẩy a được đưa vào một bộ định tuyến rất nhẹ.
- Bộ định tuyến gồm một lớp tuyến tính và hàm xích-moi, tạo ra điểm định tuyến a phẩy a nằm trong khoảng từ không đến một.
- điểm cao cho thấy nót a có khả năng nhận được lợi ích khi sử dụng lờ lờ mờ. điểm thấp cho thấy dự đoán hiện tại của gờ nờ nờ có thể đã đủ tốt.
- Cần phân biệt rằng đây không phải xác suất lớp. Nó chỉ biểu diễn mức độ nên gửi nót sang nhánh lờ lờ mờ.

### `S4_16_TopK`

- Gờ lans không sử dụng một ngưỡng cố định cho từng nót.
- Thay vào đó, hệ thống xếp hạng điểm định tuyến của tất cả nót trong bát.
- Ví dụ, các nót a, e và xê có ba điểm cao nhất nên được chọn vào tốp ba.
- Chỉ đúng ca nót được gửi sang lờ lờ mờ.
- Nhờ vậy, gờ lans kiểm soát chính xác ngân sách tính toán và tránh tình trạng số lần gọi lờ lờ mờ tăng ngoài dự kiến.

### `S4_17_TwoFlows`

- Sau bước tốp ca, quy trình được chia thành hai nhánh rõ ràng.
- Nhánh thứ nhất dành cho những nót thuộc tập định tuyến rời, tức là các nót được sử dụng lờ lờ mờ. Nhánh thứ hai dành cho những nót không thuộc rời.
- Việc tách hai nhánh này là cơ sở giúp gờ lans vừa tận dụng sức mạnh ngữ nghĩa của lờ lờ mờ, vừa duy trì chi phí xử lý hợp lý.

### `S4_18_WithoutLLM`

- Trước tiên là nhánh đơn giản hơn.
- Nếu một nót không được định tuyến, gờ lans bỏ qua toàn bộ bước tạo câu lệnh, gọi lờ lờ mờ và bộ tinh chỉnh. Phân phối cuối cùng của nót được giữ nguyên bằng bê hắc phẩy vê, tức dự đoán ban đầu của gờ nờ nờ.
- Sau đó, hệ thống lấy lớp có xác suất lớn nhất. Nhờ vậy, các nót dễ không phải chịu thêm chi phí và cũng không bị lờ lờ mờ làm thay đổi một dự đoán vốn đã chính xác.

### `S4_19_WithLLMContext`

- Với nót a được định tuyến, gờ lans khai thác văn bản ở ba mức ngữ cảnh.
- Mức đầu tiên là văn bản của nót trung tâm, chỉ chứa nội dung của chính nót a.
- Mức thứ hai là 1-hop ngữ cảnh, bổ sung nội dung từ các nót trích dẫn trực tiếp.
- Mức cuối cùng là ngữ cảnh hai bước, cung cấp ngữ cảnh rộng hơn từ các nót cách a hai cạnh.
- Ba mức được xử lý riêng thay vì gộp tất cả thành một câu lệnh rất dài.

### `S4_23_EgoEmbedding`

- câu lệnh đầu tiên chỉ chứa văn bản của nót trung tâm của nót a.
- câu lệnh này được đưa vào quy en ba em-bét tám bi, đóng vai trò dùng chung véc-tơ biểu diễn bộ mã hóa.
- Đầu ra không phải là một câu trả lời hay nhãn lớp, mà là véc-tơ biểu diễn dét lờ phẩy không của a.
- véc-tơ biểu diễn này biểu diễn thông tin ngữ nghĩa từ chính nội dung của nót a.

### `S4_24_OneHopEmbedding`

- Ở bước tiếp theo, câu lệnh được mở rộng bằng nội dung của các nót hàng xóm trực tiếp. Câu lệnh mới vẫn đi qua cùng một bộ mã hóa lờ lờ mờ, chứ không phải một mô hình khác. Đầu ra là dét lờ phẩy một của a. véc-tơ biểu diễn này bổ sung bối cảnh từ các bài báo có quan hệ trực tiếp với nót a.

### `S4_25_TwoHopEmbedding`

- Tương tự, câu lệnh thứ ba đưa thêm ngữ cảnh ở khoảng cách hai bước. Nó giúp mô hình quan sát một vùng rộng hơn của đồ thị trích dẫn và nhận biết chủ đề tổng quát xung quanh nót a. câu lệnh tiếp tục sử dụng bộ mã hóa lờ lờ mờ dùng chung và tạo véc-tơ biểu diễn dét lờ phẩy hai của a. Như vậy, một bộ mã hóa được tái sử dụng cho ba phiên bản câu lệnh khác nhau.

### `S4_26_MergeEmbeddings`

- Ba véc-tơ biểu diễn vừa tạo được nối lại với nhau.
- Kết quả là dét lờ a, đại diện cho toàn bộ thông tin ngữ nghĩa mà lờ lờ mờ thu được.
- véc-tơ này giữ riêng ba thành phần: nội dung của chính nót, ngữ cảnh trực tiếp và ngữ cảnh xa hơn.
- lờ lờ mờ biểu diễn vẫn chưa phải là kết quả phân loại cuối cùng. Nó sẽ được kết hợp tiếp với biểu diễn đồ thị từ gờ nờ nờ.

### `S4_27_FusedRepresentation`

- véc-tơ biểu diễn dét gờ a từ gờ nờ nờ chứa thông tin về đặc trưng và cấu trúc đồ thị.
- Trong khi đó, dét lờ a chứa thông tin ngữ nghĩa được trích từ ba mức câu lệnh. gờ lans gờ lans nối hai véc-tơ này thành một biểu diễn hợp nhất.
- Có thể hiểu phần bên trái đại diện cho thông tin cấu trúc từ gờ nờ nờ, còn ba phần bên phải đại diện cho ngữ nghĩa ngữ cảnh từ lờ lờ mờ.
- véc-tơ kết hợp này là đầu vào trực tiếp của bộ tinh chỉnh.

### `S4_28_RefinerMLP`

- bộ tinh chỉnh là một mờ lờ bê có nhiệm vụ kết hợp hai nguồn bằng chứng.
- Biểu diễn hợp nhất lần lượt đi qua các lớp tuyến tính, ri-lu, đờ-róp-ao và lớp đầu ra.
- Cuối cùng, sóp mác tạo ra phân phối lớp mới bê xê phẩy a.
- bộ tinh chỉnh không thay thế gờ nờ nờ hoặc lờ lờ mờ. Nó học cách cân bằng thông tin cấu trúc từ gờ nờ nờ với thông tin ngữ nghĩa từ lờ lờ mờ để tạo ra dự đoán phù hợp hơn cho được định tuyến nót.

### `S4_29_RefinedDistribution`

- Trước khi sử dụng lờ lờ mờ, gờ nờ nờ tạo phân phối ban đầu là không chấm bốn năm, không chấm bốn không và không chấm một năm. Phân phối này chưa thể hiện sự khác biệt rõ ràng giữa hai lớp đầu tiên.
- Sau khi bổ sung lờ lờ mờ ngữ cảnh và đi qua bộ tinh chỉnh, phân phối chuyển thành không chấm một năm, không chấm tám không và không chấm không năm.
- Xác suất tập trung mạnh hơn vào lớp khai phá đồ thị.
- Ví dụ này minh họa cách ngữ cảnh văn bản có thể giúp điều chỉnh một dự đoán còn chưa chắc chắn của gờ nờ nờ.

### `S4_30_FinalPrediction`

- Cuối cùng, gờ lans xác định phân phối được sử dụng tùy theo kết quả định tuyến.
- Nếu nót thuộc tập rời, hệ thống sử dụng phân phối đã tinh chỉnh là bê xê phẩy vê. Nếu nót không thuộc rời, hệ thống giữ nguyên phân phối gờ nờ nờ là bê hắc phẩy vê.
- Với nót a trong ví dụ, a được định tuyến nên sử dụng kết quả của bộ tinh chỉnh. Lớp có xác suất lớn nhất là khai phá đồ thị, vì vậy đây là nhãn cuối cùng của nót a.
- Tóm lại, gờ lans có thể được mô tả bằng ba ý chính: gờ nờ nờ được sử dụng trước để xử lý toàn bộ đồ thị. bộ định tuyến lựa chọn những nót thực sự cần hỗ trợ. Và lờ lờ mờ chỉ được gọi theo nhu cầu để bổ sung thông tin ngữ nghĩa cho các trường hợp khó. Thiết kế này giúp gờ lans kết hợp được khả năng khai thác cấu trúc của gờ nờ nờ với khả năng hiểu văn bản của lờ lờ mờ, nhưng vẫn kiểm soát được chi phí tính toán.
- bộ định tuyến không khả vi. Vậy huấn luyện nó kiểu gì, và có thật sự hiệu quả?


## Section 5 — Training objective & experiments

*Owner: Thiên Lâm · File: `sections/s5_thienlam/s5_thienlam.py`*

### `S5_01_Title`

- Phần năm: cách gờ lans được huấn luyện, và kết quả thực nghiệm chứng minh cách huấn luyện đó đúng.

### `S5_02_TopKProblem`

- Bộ định tuyến chỉ có ca tấm vé gọi lờ lờ mờ. tốp ca giữ số lần gọi cố định trong mỗi bát.
- Nhưng điểm đổi nhẹ thì tập tốp ca vẫn giữ nguyên; đến đúng lúc đổi hạng, quyết định lại nhảy đột ngột từ có sang không.
- Vì phép chọn tốp ca không liên tục, gờ ra điên không truyền được xuyên qua nó — hàm mất mát cuối không thể dạy trực tiếp cho bộ định tuyến.

### `S5_03_CounterfactualLoss`

- Thay vì đạo hàm qua tốp ca, gờ lans chấm kết quả của từng quyết định bằng phần thưởng.
- Với một nốt được định tuyến, gờ lans dựng hai thế giới đối chứng: thế giới không gọi lờ lờ mờ, dùng đầu dự đoán hắc có sẵn của gờ nờ nờ; và thế giới đã gọi lờ lờ mờ, đi qua bộ tinh chỉnh xi.
- Cả hai hàm mất mát đều là en-trô-pi chéo so với cùng một nhãn thật — hàm mất mát càng thấp thì dự đoán càng tốt. Hàm mất mát thế giới đã gọi lờ lờ mờ không phải của riêng lờ lờ mờ, mà là của cả nhánh gờ nờ nờ cộng lờ lờ mờ cộng bộ tinh chỉnh.

### `S5_04_Reward`

- Nếu định tuyến: phần thưởng bằng mức lờ lờ mờ giúp hàm mất mát giảm bao nhiêu, trừ đi bê ta — chi phí quy đổi của một lần gọi lờ lờ mờ.
- Bê ta lớn thì bộ định tuyến dè dặt hơn, chỉ định tuyến khi lợi ích thật rõ ràng; bê ta nhỏ thì bộ định tuyến sẵn sàng gọi lờ lờ mờ nhiều hơn. Nếu mức cải thiện nhỏ hơn bê ta, phần thưởng vẫn âm.
- Nếu bỏ qua: không có hàm mất mát của lờ lờ mờ để so sánh, nên gờ lans dùng âm hàm mất mát của gờ nờ nờ để chấm quyết định bỏ qua.

### `S5_05_JointObjective`

- Phần thưởng tốt thì bộ định tuyến lặp lại hành động vừa chọn; phần thưởng xấu thì hành động đó bị giảm ưu tiên — đây chính là gra-đi-en chính sách.
- hàm mất mát của bộ định tuyến gồm gra-đi-en chính sách cộng một số hạng en-trô-pi, giữ cho bộ định tuyến chưa chốt quá sớm, còn khám phá các lựa chọn khác.
- hàm mất mát dự đoán rẽ nhánh theo việc nốt có nằm trong tốp ca hay không: nốt được định tuyến dùng hàm mất mát của nhánh gờ nờ nờ cộng lờ lờ mờ, nốt còn lại dùng hàm mất mát của riêng gờ nờ nờ.
- hàm mất mát tổng cộng gộp hàm mất mát dự đoán với hàm mất mát của bộ định tuyến có trọng số — vừa dạy dự đoán đúng, vừa dạy phân bổ ngân sách gọi lờ lờ mờ.
- Chỉ bộ định tuyến pi và bộ tinh chỉnh xi được cập nhật; gờ nờ nờ và lờ lờ mờ bị đóng băng hoàn toàn — Gờ lans không huấn luyện lại hai mô hình nền.
- Cấu hình mặc định: bát ba mươi hai, định tuyến tốp mười hai mỗi bát, bê ta thử ở không chấm một, không chấm hai, không chấm ba. Ngân sách ca giảm dần theo lịch, từ ba mươi hai xuống còn tám.
- Nhưng liệu cách huấn luyện này có thật sự tạo ra một bộ định tuyến học đúng không?

### `S5_06_Setup`

- Câu hỏi trung tâm của phần thực nghiệm: gờ lans có gộp được điểm mạnh của gờ nờ nờ và lờ lờ mờ trong cùng một mô hình không?
- Sân thử gồm ba đồ thị chuẩn — cô ra, pắp mét, ác xíp hai ba — cùng hai đồ thị cực lớn: ác xíp dia và ô gi bi pró đắc.
- Đối thủ đều mạnh: các gờ nờ nờ kinh điển gờ xê en, gráp xây giơ, gờ xê en hai chạy trên ba chiến lược khác nhau; thêm nhóm gờ nờ nờ chuyên xử lý dị phối gồm ép a gờ xê en, gờ gờ xê en, gờ bê ca gờ en en.
- Mấu chốt: mặc định gờ lans chỉ gọi lờ lờ mờ cho mười hai trên ba mươi hai nốt mỗi bát — nó phải thắng trong khi gọi lờ lờ mờ ít hơn hẳn đối thủ.

### `S5_07_BalancedResults`

- Về độ chính xác tổng thể, gờ lans dẫn đầu cả ba bộ: cô ra tám mươi chín chấm năm, pắp mét chín mươi hai chấm sáu, ác xíp hai ba tám mươi hai chấm một — trung bình hơn mô hình tốt kế tiếp khoảng không chấm năm phần trăm.
- Nhưng khoảng cách tổng thể chỉ dưới một điểm, nên đó chưa phải điều quan trọng nhất.
- Chia nốt theo hô mô phi li cục bộ thành các nhóm, ở nhóm khó nhất của cô ra gờ lans đạt bốn mươi sáu chấm bốn — cao hơn mô hình tốt kế tiếp tới mười ba điểm.
- Trung bình trên toàn bộ các nhóm, gờ lans xếp hạng hai chấm bốn — tốt nhất, bỏ xa á quân bốn chấm bảy, mà nhóm dễ vẫn giữ gần như tuyệt đối.
- Con số tổng thể che chênh lệch ở nốt khó; hô mô phi li làm nó lộ ra.

### `S5_08_RouterLearned`

- Vậy bộ định tuyến có thật sự học đúng chỗ không?
- Khi soi các nốt được định tuyến, khối lượng dồn hẳn về vùng hô mô phi li thấp — đúng vùng mà gờ nờ nờ hay sai còn lờ lờ mờ có thể sửa.
- Nhìn trên đồ thị mẫu, nốt chín — hô mô phi li thấp, hàng xóm khác lớp — là kiểu nốt bộ định tuyến ưu tiên gọi lờ lờ mờ; nốt bốn thì hầu như không cần.
- Tăng ngân sách ca giúp nhiều nhất ở vùng hô mô phi li thấp; vùng hô mô phi li cao gần như không đổi — ngân sách chỉ có giá trị đúng chỗ khó.
- Cắt bỏ lần lượt từng đặc trưng định tuyến đều làm độ chính xác giảm; bỏ đặc trưng hô mô phi li ước lượng gây thiệt hại lớn nhất.
- Chính tín hiệu hô mô phi li dạy bộ định tuyến biết khi nào nên gọi lờ lờ mờ.

### `S5_09_RoutingControls`

- Bằng chứng mạnh nhất không phải là thêm lờ lờ mờ, mà là chọn đúng nốt để gọi.
- định tuyến hết mọi nốt trên pắp mét: hai nhóm khó tăng, tổng thể thậm chí nhích lên cộng một chấm năm điểm — nhưng đổi lại, hai nhóm dễ sụp gần hai mươi điểm; con số tổng che mất cái giá phải trả đó.
- Giữ nguyên lờ lờ mờ và bộ tinh chỉnh nhưng định tuyến ngẫu nhiên trên cô ra: chỉ còn tám mươi sáu chấm bốn, thua cả bây xơ lai gờ xê en hai tám mươi bảy chấm bảy.
- Trên đúng tập nốt mà bộ định tuyến đã chọn, nhánh gờ nờ nờ cộng lờ lờ mờ qua bộ tinh chỉnh đạt tám mươi bảy chấm sáu — cao hơn hẳn nếu để gờ xê en hai tự xử lý.
- định tuyến hết thì hại nốt dễ; định tuyến bừa thì thua bây xơ lai — giá trị nằm ở sự chọn lọc học được.

### `S5_10_Scale`

- Trên ô gi bi pró đắc — hai chấm bốn năm triệu nốt, gần sáu mươi hai triệu cạnh — gờ lans chỉ gọi lờ lờ mờ cho khoảng một chấm sáu phần trăm nốt, tức một nốt trong mỗi sáu mươi tư.
- Vậy mà vẫn dẫn đầu: tám mươi hai chấm ba, cao hơn gờ xê en hai tám mươi mốt chấm tám, còn gờ gờ xê en thì hết bộ nhớ. Trên ác xíp dia, gờ lans đạt bốn mươi chín chấm tám.
- Chọn lọc học được không chỉ cân bằng và chính xác, mà còn rẻ và mở rộng tới quy mô triệu nốt.

### `S5_11_Callout`

- Ở đầu vi đi eo, câu hỏi đặt ra là: có cách nào kết hợp gờ nờ nờ và lờ lờ mờ mà biết tính chi phí không? Đây là câu trả lời của gờ lans, gói trong năm ý.
- Tất cả gói trong một câu — đừng dùng nhiều lờ lờ mờ hơn, hãy dùng lờ lờ mờ đúng chỗ.

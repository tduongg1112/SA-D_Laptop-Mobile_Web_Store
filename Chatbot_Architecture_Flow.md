# Kiến trúc và Luồng hoạt động của Nova AI Chatbot

Tài liệu này giải thích chi tiết cấu trúc, các thành phần phần mềm, và luồng hoạt động từng bước (step-by-step) của Microservice Chatbot AI trong hệ thống E-commerce Nova Electronics.

---

## 1. Tổng quan Kiến trúc (Architecture Overview)

Nova AI Chatbot được xây dựng theo kiến trúc **Microservice độc lập**. Nó chạy trong một container Docker riêng biệt và giao tiếp với các services khác (Customer Web, Staff Panel) thông qua **API Gateway (Nginx)** thay vì kết nối trực tiếp. 

Sự tách biệt này mang lại lợi ích bóc tách mối quan tâm (separation of concerns), giúp dễ dàng scale (mở rộng) module AI khi lượng người dùng tăng cao mà không làm ảnh hưởng đến hiệu năng của hệ thống bán hàng chính.

**Tech Stack cốt lõi:**
*   **Framework:** FastAPI (Python) cho hiệu suất cao.
*   **LLM Provider:** Groq API với model mã nguồn mở `llama-3.3-70b-versatile` (thay thế cho Google GenAI SDK để tăng tốc độ phản hồi và tận dụng giới hạn rate-limit tốt hơn).
*   **RAG Engine:** In-memory context retrieval (Sử dụng tìm kiếm bằng từ khoá trên RAM thay vì dùng Vector DB phức tạp như ChromaDB/Pinecone để đảm bảo container cực nhẹ và tối ưu cho đồ án).
*   **Behavior Classifier:** Mô hình Neural Network (Mạng nơ-ron) 2 lớp được xây dựng thuần tuý bằng thư viện toán học `numpy`.

---

## 2. Các Thành phần Hệ thống (Components Structure)

Code của chatbot nằm trọn vẹn trong thư mục `chatbot_service/` với 3 file quan trọng cốt lõi:

### 2.1. `main.py`
Đây là bộ não điều hướng và là Entry Point của ứng dụng FastAPI. Chức năng chính bao gồm:
*   Khởi tạo HTTP Server mở cổng 8000.
*   Cấu hình Groq API Client (chứa API Key và thiết lập Model).
*   Định nghĩa Endpoint `/api/chat`: Nơi tiếp nhận yêu cầu từ Frontend, tổng hợp dữ liệu từ RAG, gọi model phân tích hành vi, thiết kế System Prompt và gọi API LLM.
*   Quản lý cơ chế dự phòng lỗi (Fallback & Retry Mechanism).

### 2.2. `knowledge_base.py`
Đóng vai trò như một cơ sở dữ liệu "cứng" (Hardcoded Knowledge Base) hỗ trợ hệ thống RAG (Retrieval-Augmented Generation):
*   Lưu trữ cấu trúc dữ liệu mô phỏng về Laptop, Điện thoại (giá gốc, mô tả, thông số) và các bộ Policy liên quan (Chính sách trả góp, Chính sách bảo hành).
*   Cung cấp tính năng `build_context(query)`. Khi nhận câu hỏi của người dùng, hàm này dùng keyword-matching để rà quét và trích xuất ra đoạn tài liệu gốc phù hợp cần cấp bách cho con AI (được gọi là **Xây dựng Ngữ cảnh**).

### 2.3. `behavior_model.py`
Hệ thống chấm điểm dự đoán hành vi / ý định người tiêu dùng ứng dụng Machine Learning cơ bản:
*   Được code bằng `numpy` chuẩn hoá kiến trúc Multi-layer Perceptron (2 lớp cơ bản). 
*   **Mục đích:** Khi người dùng nhắn tin, mô hình sẽ bóc tách các nhóm từ khoá để phân loại họ vào 1 trong 5 tệp khách hàng: *Budget Buyer (Mua giá rẻ), Tech Enthusiast (Đam mê cấu hình), Gamer (Game thủ), Business User (Doanh nhân, Văn phòng), Student (Sinh viên)*.
*   Dữ liệu phân loại sẽ được gửi chung với câu hỏi để con AI có thể tinh chỉnh phong cách trò chuyện và loại sản phẩm tư vấn cho sát với đối tượng (Ví dụ: Biết khách là sinh viên, chatbot sẽ auto đề xuất máy rẻ pin trâu thay vì máy trạm đắt tiền).

---

## 3. Luồng Hoạt động Tiêu chuẩn (Standard Flow)

Hãy xem xét quy trình xử lý qua một ví dụ cụ thể khi người tiêu dùng nhấn gửi tin nhắn: **"Bạn có bán điện thoại nào rẻ nhất không?"**

**Bước 1: Front-end gửi Request**
Widget Chatbot trên giao diện (`home.html` của customer service) bọc tin nhắn thành một chuỗi JSON `{"message": "Bạn có bán điện thoại nào rẻ nhất không?"}` và tạo 1 request POST tới API Gateway`/chatbot/api/chat`.

**Bước 2: Nginx Routing**
API Gateway (Nginx) chặn request, và nhận diện path prefix `/chatbot/`. Hệ thống proxy request này vào trong nội mạng Docker đi tới container của `chatbot-service` ở cổng 8000.

**Bước 3: Trích xuất Ngữ cảnh (RAG Retrieval)**
Hệ thống gọi hàm `build_context(message)` tại file `knowledge_base.py`. Do nhìn thấy chữ "rẻ" và "điện thoại", RAG Engine lục lọi Data catalog và lấy ra thông số của thiết bị "Realme C67" (Kèm cả giá $179).

**Bước 4: Suy diễn Hành vi Khách hàng**
Hệ thống tiếp tục gọi hàm `predict_user_intent()` trong thư viện Neural Network của file `behavior_model.py`. Ma trận trọng số (Weights) sẽ tính toán và trả về mảng xác suất cho thấy: Khách hàng này có **85% tỷ lệ** thuộc nhóm phân khúc **Budget Buyer (Mua giá rẻ)**.

**Bước 5: Prompt Engineering (Thiết kế cửa sổ ngữ cảnh)**
File `main.py` đem toàn bộ các "nguyên liệu" tìm được hòa trộn lại theo một Template cứng trước khi giao cho LLM xử lý:
> [SYSTEM PROMPT]: Bạn là Nova AI, một trợ lý tư vấn tại shop đồ điện tử. Bạn phải trả lời thân thiện... Hãy tận dụng bối cảnh dưới đây để tư vấn cụ thể và phải lưu ý phân tích hành vi người mua hàng để có tông giọng đúng mực:
> [CONTEXT LẤY TỪ RAG]: Realme C67, màn hình 6.72, giá 179$,...
> [BEHAVIOR ANALYSIS]: Nhóm: *Budget Buyer* (Cần tư vấn xoáy mạnh vào giá trị phù hợp với túi tiền)
> [USER ASK]: Bạn có bán điện thoại nào rẻ nhất không?

**Bước 6: Giao tiếp với Groq API**
FastAPI đóng gói toàn bộ đoạn chắp vá khổng lồ trên chuyển đổi lên Server của hãng Groq thông qua Internet bằng SDK `Groq.chat.completions.create(model="llama-3.3-70b-versatile",...)`. Groq sẽ sử dụng sức mạnh vi xử lý nội bộ sinh ra các Tokens phản hồi.

**Bước 7: Trả về kết quả (Response Delivery)**
Phản hồi từ Groq được nhận lại: *"Chào bạn, hiện tại mẫu điện thoại có mức giá sinh viên nhất tại Nova Electronics là Realme C67 với giá 179$..."*. File `main.py` bọc chuỗi này lại tạo thành Object JSON tiêu chuẩn (`{"answer": "...", "behavior": {...}}`) và trả ngược lại qua Gateway. Frontend nhận JSON và bóc tách hiển thị bóng thoại lên màn hình người dùng.

---

## 4. Cơ chế Xử lý Khủng hoảng (High-Availability Fallback)

Một hệ thống enterprise (doanh nghiệp) không được phép "chết cứng" khi một thành phần bên thứ ba (Third-party) gặp trục trặc mạng lưới hoặc sập nguồn tài nguyên. Khi xây dựng Nova Chatbot, một hệ thống **Fallback Mechanism (Dự phòng)** vô cùng quan trọng đã được cài cắm ở khối mã kết nối vào LLM (`main.py`):

1. **Khối Retry (Thử lại):** Server của Groq có giới hạn Quota API Rate limits rất nghiêm ngặt (lỗi Http 429). Fast API lập ra một vòng lặp `for attempt in range(3):`. Nếu quá trình sinh chữ bị lỗi mạng, nó sẽ bỏ qua và tự thử lại tới cực đại 3 vòng lặp. Giúp triệt tiêu các lỗi rớt gói tin siêu nhỏ ngẫu nhiên.
2. **Khối Trả lời Dự Phòng (Fallback to Hard Data):** Nếu qua cả 3 lần mà SDK Groq API vẫn bắn Exception từ chối trả lời (API Key hỏng, hết tiền trong thẻ, rớt mạng máy chủ, server Groq Offline,...), luồng chương trình không cho phép trả về lỗi báo `500 Server Error`. Thay vào đó:
    * Chatbot sẽ vào biến `context` để xem RAG Engine lục lọi được sản phẩm nào có sẵn trên hệ thống. 
    * Nếu RAG tìm thấy, LLM sẽ bị bypass (bỏ qua), hệ thống gắn cứng một chuỗi text thủ công: *"Hiện tại trợ lý AI đang bận. Nhưng dựa theo cơ sở dữ liệu tôi tìm được thông tin sau cho bạn: [Thông số đã lấy]"*.
    * Bằng cách này, Chat Window của người dùng luôn nhận được phản hồi lịch sự, không bị đứt gãy UX/UI, đảm bảo điểm SQA chất lượng cho sản phẩm cuối cùng.

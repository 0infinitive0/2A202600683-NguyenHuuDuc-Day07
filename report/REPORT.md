# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai đoạn văn bản có hướng ngữ nghĩa rất giống nhau trong không gian embedding; chúng chứa nhiều ý tưởng hoặc từ khóa trùng khớp.

**Ví dụ HIGH similarity:**
- Sentence A: "Tôi cần đặt một vé máy bay đi Hà Nội cho tuần tới."
- Sentence B: "Tôi muốn mua vé máy bay tới Hà Nội vào tuần sau."
- Tại sao tương đồng: Cả hai câu đều nói về hành động mua vé máy bay tới cùng một điểm đến và thời gian tương tự.

**Ví dụ LOW similarity:**
- Sentence A: "Tôi cần đặt một vé máy bay đi Hà Nội cho tuần tới."
- Sentence B: "Hôm nay tôi sẽ nấu phở bò cho bữa trưa."
- Tại sao khác: Một câu nói về du lịch/đặt vé, câu kia nói về nấu ăn, nên nội dung và ngữ nghĩa hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity tập trung vào hướng của vector, không bị ảnh hưởng bởi độ lớn của embedding. Với text embeddings, độ lớn có thể thay đổi do chiều dài hoặc saturation, nên so sánh hướng giúp đánh giá ngữ nghĩa chính xác hơn.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100, num_chunks = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25. Overlap nhiều hơn tạo ra nhiều chunk hơn nhưng giúp giữ lại ngữ cảnh giữa các phần liền kề, hữu ích khi thông tin liên tục qua nhiều câu.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi dùng một biểu thức chính quy để tách văn bản theo dấu câu kết thúc câu: `.` `!` `?`, theo sau bởi khoảng trắng hoặc xuống dòng. Sau đó tôi lọc các câu rỗng, loại bỏ khoảng trắng thừa và gom mỗi nhóm `max_sentences_per_chunk` câu lại thành một chunk.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thuật toán bắt đầu với các separator ưu tiên như `\n\n`, `\n`, `. `, và ` ` rồi đệ quy xuống nếu phần con vẫn dài hơn `chunk_size`. Base case là khi đoạn văn bản đã nhỏ hơn hoặc bằng `chunk_size`, hoặc khi không còn separator nào để tách, khi đó hàm trả về các đoạn cố định theo độ dài.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Tôi lưu mỗi document dưới dạng record với `id`, `content`, `metadata` và `embedding` trong store nội bộ. Khi thêm tài liệu, tôi gọi hàm embedding trên nội dung rồi append record. Khi tìm kiếm, tôi embed câu truy vấn và xếp hạng record bằng dot product giữa embedding truy vấn và embedding document.

**`search_with_filter` + `delete_document`** — approach:
> Với `search_with_filter`, tôi áp metadata filter trước để chọn record phù hợp rồi mới chạy tìm kiếm tương đồng trên các bản ghi đó. `delete_document` lọc bỏ tất cả record có `id` trùng với `doc_id` và trả về `True` nếu có bản ghi bị xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> Tôi lấy top-k chunk từ store, đóng gói mỗi chunk thành một phần ngữ cảnh có metadata nếu có, rồi nối chúng vào prompt. Prompt sau đó được gửi tới `llm_fn` để sinh câu trả lời dựa trên ngữ cảnh đã thu thập.

### Test Results

```
42 passed in 0.07s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |

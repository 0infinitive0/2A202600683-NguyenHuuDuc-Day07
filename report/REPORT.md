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

**Domain:** Internal AI knowledge management và retrieval system documentation.

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain này vì các tài liệu trong `data/` đều tập trung vào cách lưu trữ, truy vấn và chunking nội dung cho hệ thống trợ lý kiến thức. Domain này cho phép nhóm thử nghiệm các chiến lược chunking và metadata trên tài liệu kỹ thuật, hỗ trợ, và thiết kế hệ thống.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự (bytes) | Metadata đã gán |
|---|--------------|-------|------------------:|-----------------|
| 1 | BE TOS.md | Public TOS | 21,771 | company=BE, doc_type=TOS, language=English |
| 2 | Grab TOS.md | Public TOS | 216,622 | company=Grab, doc_type=TOS, language=English |
| 3 | Green SM TOS.md | Public TOS | 24,240 | company=GreenSM, doc_type=TOS, language=English |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| category | string | support_playbook, chunking_analysis, RAG_design, vector_store, retrieval_notes | Giúp lọc tài liệu theo chủ đề và trả về nguồn phù hợp với câu hỏi cụ thể.
| language | string | Vietnamese, English | Hữu ích khi cần ưu tiên nội dung cùng ngôn ngữ với truy vấn.
| extension | string | .txt, .md | Hữu ích khi cần phân biệt giữa nội dung thô và tài liệu markdown kỹ thuật.

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis (TOS documents)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu TOS chính:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------:|-----------:|-------------------|
| data/BE TOS.md | FixedSizeChunker (`fixed_size`) | 108 | 199.9 | Cắt đều theo kích thước, mất một ít cấu trúc |
| data/BE TOS.md | SentenceChunker (`by_sentences`) | 35 | 613.4 | Chunks dài, giữ nguyên câu nên đôi khi quá dài |
| data/BE TOS.md | RecursiveChunker (`recursive`) | 172 | 123.7 | Tốt, tách theo đoạn và câu giúp bảo toàn ngữ cảnh |
| data/Grab TOS.md | FixedSizeChunker (`fixed_size`) | 1,079 | 200.0 | Rất nhiều chunk do tài liệu dài; cắt đều |
| data/Grab TOS.md | SentenceChunker (`by_sentences`) | 462 | 465.0 | Nhiều chunk dài do câu ghép phức tạp |
| data/Grab TOS.md | RecursiveChunker (`recursive`) | 1,676 | 127.0 | Tách theo đoạn/câu, cải thiện ngữ cảnh trên từng chunk |
| data/Green SM TOS.md | FixedSizeChunker (`fixed_size`) | 121 | 199.6 | Cắt đều, dễ dự đoán |
| data/Green SM TOS.md | SentenceChunker (`by_sentences`) | 39 | 616.1 | Chunks tương đối dài, giữ nguyên câu |
| data/Green SM TOS.md | RecursiveChunker (`recursive`) | 187 | 127.3 | Giữ ngữ cảnh tốt và tránh chunk quá dài |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> RecursiveChunker tách văn bản theo chuỗi separator ưu tiên: `\n\n`, `\n`, `. `, ` ` và cuối cùng là tách theo độ dài. Nếu một phần vẫn quá dài, nó đệ quy xuống separator tiếp theo để chia nhỏ hơn mà vẫn giữ nguyên cấu trúc ngữ nghĩa.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Domain của nhóm nhiều tài liệu kỹ thuật và hướng dẫn có cấu trúc theo đoạn, tiêu đề và các câu liên tiếp. RecursiveChunker phù hợp vì nó giữ được đoạn văn có nghĩa, tránh cắt ngang ý và vẫn đảm bảo chunk đủ ngắn cho retrieval.

**Code snippet (nếu custom):**
```python
from src.chunking import RecursiveChunker

chunker = RecursiveChunker(chunk_size=200)
chunks = chunker.chunk(text)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| chunking_experiment_report.md | best baseline = SentenceChunker | 5 | 395.6 | Khó dùng cho truy vấn vì chunks quá dài |
| chunking_experiment_report.md | **của tôi** | 18 | 108.4 | Tốt hơn vì chunks ngắn và giữ ngữ cảnh |
| rag_system_design.md | best baseline = FixedSizeChunker | 12 | 199.2 | Đơn giản nhưng thiếu cấu trúc nội dung |
| rag_system_design.md | **của tôi** | 20 | 117.7 | Tốt hơn vì chunks vừa đủ và mạch lạc |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | 8 | Giữ cấu trúc đoạn, tránh cắt ngang câu | Tạo nhiều chunk hơn, tốn lưu trữ hơn |
| Thành viên 1 | SentenceChunker | 6 | Giữ nguyên câu đầy đủ | Chunk dài quá, dễ trả về thông tin rộng |
| Thành viên 2 | FixedSizeChunker | 5 | Dễ triển khai, đoán trước được | Mất ngữ cảnh vì cắt vuông |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> RecursiveChunker là chiến lược tốt nhất cho domain này vì dữ liệu bao gồm nhiều đoạn văn và nội dung kỹ thuật. Nó cân bằng giữa việc giữ ngữ cảnh và đảm bảo chunk đủ ngắn để truy vấn hiệu quả.

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
| 1 | Python is a programming language. | Python is a programming language. | high | 1.0 | yes |
| 2 | Machine learning uses algorithms to learn from data. | Machine learning uses algorithms to learn from data. | high | 1.0 | yes |
| 3 | This privacy policy explains how data is used. | Terms of service explain rules for platform usage. | low | 0.1965 | yes |
| 4 | OpenAI provides embedding models. | Financial reports summarize quarterly earnings. | low | 0.0879 | yes |
| 5 | Python is a programming language. | This privacy policy explains how data is used. | low | -0.1204 | yes |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Dù hai câu giống nhau cho kết quả similarity bằng 1.0, các cặp khác chỉ cho điểm số thấp hơn nhiều. Điều này cho thấy embeddings có thể phản ánh tốt sự giống nhau tuyệt đối, nhưng với mô hình embedding đơn giản hoặc mock embedder, những câu có quan hệ ngữ nghĩa lỏng lẻo vẫn có thể cho score thấp.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**


### Benchmark Queries & Gold Answers (TOS-focused)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | cancellation policy | Which sections describe cancellation and associated customer rights/penalties. |
| 2 | refund policy | How refunds are handled and under what conditions. |
| 3 | service availability | Service availability, uptime, and related user obligations. |

### Kết Quả Của Tôi (TOS queries)

| # | Query | Top-1 Retrieved Document | Score | Relevant? |
|---|-------|-------------------------|------:|-----------|
| 1 | cancellation policy | `Grab TOS.md` | 0.1312 | yes |
| 2 | refund policy | `Green SM TOS.md` | 0.1077 | yes |
| 3 | service availability | `Green SM TOS.md` | 0.1798 | yes |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 3

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được rằng metadata rõ ràng và có cấu trúc (như category, language) rất quan trọng để lọc kết quả trước khi tính similarity. Điều này giúp giảm noise và tăng độ chính xác khi hệ thống trả lời các câu hỏi cụ thể.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Qua demo nhóm khác, tôi thấy chiến lược chunking theo section/header rất mạnh, đặc biệt với tài liệu có cấu trúc rõ ràng như FAQ hoặc hướng dẫn. Điều này nhắc rằng không chỉ có kích thước chunk, mà còn có cách tách dựa trên ngữ nghĩa.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Nếu làm lại, tôi sẽ bổ sung metadata chủ đề và loại tài liệu cho mỗi chunk, đồng thời thử tách chunk theo section/header với dữ liệu có cấu trúc hơn. Cách này giúp retrieval chính xác hơn và giảm khả năng trả về nội dung không liên quan.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **88 / 100** |

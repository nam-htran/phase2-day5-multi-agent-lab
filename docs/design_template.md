# Design Template

## Problem

Hệ thống cần nhận vào một câu hỏi (query) nghiên cứu từ người dùng, sau đó lên mạng tìm kiếm các tài liệu, bài báo liên quan. Sau khi có dữ liệu, hệ thống cần đọc hiểu, phân tích, trích xuất luận điểm, và cuối cùng tổng hợp thành một bài viết hoàn chỉnh (final answer) kèm theo trích dẫn và đánh giá chất lượng.

## Why multi-agent?

Mô hình Single-agent gặp khó khăn khi phải vừa tìm kiếm, vừa chắt lọc, vừa phân tích và vừa format bài viết trong một lượt chạy duy nhất, dễ dẫn đến lỗi hallucination (bịa đặt) và không tận dụng tốt ngữ cảnh dài.
Multi-agent chia nhỏ quy trình thành các bước riêng biệt: có agent chuyên tìm kiếm (Researcher), chuyên phân tích logic (Analyst), chuyên viết bài (Writer) và chuyên kiểm duyệt (Critic). Việc này giúp kết quả đầu ra chính xác, chất lượng cao và có thể debug dễ dàng từng bước (nhờ LangGraph).

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Định tuyến các agent. | State hiện tại | Tên Agent tiếp theo | Lặp vô hạn (vượt max iterations) |
| Researcher | Tìm tài liệu, tóm tắt. | Query | `sources`, `research_notes` | Không tìm thấy web/API lỗi |
| Analyst | Trích xuất ý chính, điểm yếu. | `research_notes` | `analysis_notes` | Thông tin nhiễu, phân tích sai |
| Writer | Viết bài giải đáp. | `notes` tổng hợp | `final_answer` | Quên trích dẫn, giọng văn sai |
| Critic | Đánh giá, bắt lỗi. | `final_answer` | Ghi chú phê bình | Chấm điểm sai lệch |

## Shared state

- `request`: Lưu truy vấn gốc và cấu hình.
- `route_history`: Lưu lịch sử luân chuyển agent để debug và Supervisor xem xét.
- `sources`: Các link và snippet trả về từ Search Client.
- `research_notes`: Ghi chú do Researcher tóm tắt.
- `analysis_notes`: Nhận định chuyên sâu của Analyst.
- `final_answer`: Bài viết cuối cùng của Writer.
- `agent_results`: Mảng chứa các log đầu ra để tính cost và kiểm tra.

## Routing policy

Luồng chạy tuần tự (Deterministic Route):
1. Bắt đầu: Supervisor kiểm tra.
2. Nếu chưa có `research_notes` -> gọi Researcher.
3. Nếu chưa có `analysis_notes` -> gọi Analyst.
4. Nếu chưa có `final_answer` -> gọi Writer.
5. Nếu chưa có Critic Review -> gọi Critic.
6. Done.

## Guardrails

- Max iterations: 10 vòng lặp, ngăn chặn infinite loop.
- Timeout: 15s cho mỗi API call (Search, LLM).
- Retry: Có thể thêm LangChain fallback nếu gặp rate limit.
- Fallback: Trả về dữ liệu mock nếu thiếu API Key.
- Validation: Pydantic schemas ràng buộc chặt đầu vào và đầu ra.

## Benchmark plan

- Câu hỏi test: "Sự khác biệt giữa Single-agent và Multi-agent?"
- Metrics cần đo: Latency (thời gian chạy), Estimated Cost (chi phí token dự kiến), Quality Score (1-10 chấm bởi LLM Judge).
- Expected outcome: Multi-agent có latency cao hơn nhưng quality score tốt hơn hẳn Single-agent.

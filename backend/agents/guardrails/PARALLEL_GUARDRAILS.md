# Parallel Guardrails Processing

## Tổng quan

Hệ thống đã được cập nhật để chạy guardrails output validation song song với LLM text generation, thay vì chạy sequential như trước đây. Điều này giúp giảm thời gian xử lý tổng thể.

## Kiến trúc mới

### Sequential (Cũ)
```
Chat message → Guardrail input validation → LLM text generation → Guardrail output validation → Chat response
```

### Parallel (Mới)
```
Chat message → Guardrail input validation → [LLM text generation + Guardrail output validation] → Merge results → Chat response
```

## Các thành phần chính

### 1. Parallel Guardrails Node (`parallel_guardrails_node.py`)
- Chạy song song với `generate_node`
- Validate output từ LLM theo từng chunk hoặc toàn bộ answer
- Đánh dấu `guardrails_output_validated` và `parallel_guardrails_completed`

### 2. Merge Results Node (`workflow.py`)
- Merge kết quả từ cả generation và parallel guardrails
- Sử dụng join mode để đợi cả hai process hoàn thành
- Quyết định sử dụng answer đã validate hay answer gốc

### 3. Updated Validate Node (`validate_node.py`)
- Kiểm tra nếu parallel guardrails đã validate thì bỏ qua
- Chỉ validate lại nếu cần thiết

## Workflow mới

```python
# Sequential flow
START → set_intent → semantic_cache → guardrails_input → rewrite → retrieve → generate

# Parallel processing
generate → [parallel_guardrails, merge_results] (song song)

# Merge và tiếp tục
merge_results → validate → update_memory → END
```

## Lợi ích

1. **Giảm thời gian xử lý**: Guardrails validation chạy song song với LLM generation
2. **Xử lý chunks**: Có thể validate từng chunk của answer
3. **Fallback an toàn**: Nếu parallel guardrails không hoàn thành, vẫn có validate node backup

## Testing

Chạy test để kiểm tra parallel processing:

```bash
cd backend
python test_parallel_guardrails.py
```

Test sẽ so sánh thời gian xử lý để xác nhận parallel processing hoạt động.

## Monitoring

Các flag quan trọng trong state:
- `guardrails_output_validated`: Guardrails đã validate output
- `parallel_guardrails_completed`: Parallel guardrails đã hoàn thành
- `generation_completed`: LLM generation đã hoàn thành

## Troubleshooting

1. **Parallel không hoạt động**: Kiểm tra join mode và edges trong workflow
2. **Validation bị bỏ qua**: Kiểm tra flags trong state
3. **Performance không cải thiện**: Kiểm tra timing logs

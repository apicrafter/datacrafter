## 1. Implementation
- [x] 1.1 Add characterization tests for CommonProcessor.run() (success, skip, autoid, autotype)
- [x] 1.2 Extract `_iter_records(source)` helper
- [x] 1.3 Extract `_process_single(record)` helper
- [x] 1.4 Extract `_write_record` and `_flush_buffer` helpers
- [x] 1.5 Collapse buffered/unbuffered branches into single buffered path (buffer_size=1 = unbuffered)
- [x] 1.6 Make error strategy explicit (honor ERROR_STRATEGY_RETRY/SKIP), remove dead retry code
- [x] 1.7 Reduce run() to a concise orchestration method (<60 lines)

## 2. Verification
- [x] 2.1 `pytest tests/test_processors.py tests/test_integration.py` green
- [x] 2.2 New helper unit tests pass
- [x] 2.3 `openspec validate refactor-processor-pipeline --strict`

## 1. Implementation
- [ ] 1.1 Add characterization tests for CommonProcessor.run() (success, skip, autoid, autotype)
- [ ] 1.2 Extract `_iter_records(source)` helper
- [ ] 1.3 Extract `_process_single(record)` helper
- [ ] 1.4 Extract `_write_record` and `_flush_buffer` helpers
- [ ] 1.5 Collapse buffered/unbuffered branches into single buffered path (buffer_size=1 = unbuffered)
- [ ] 1.6 Make error strategy explicit (honor ERROR_STRATEGY_RETRY/SKIP), remove dead retry code
- [ ] 1.7 Reduce run() to a concise orchestration method (<60 lines)

## 2. Verification
- [ ] 2.1 `pytest tests/test_processors.py tests/test_integration.py` green
- [ ] 2.2 New helper unit tests pass
- [ ] 2.3 `openspec validate refactor-processor-pipeline --strict`

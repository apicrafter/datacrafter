"""Realistic usage test: run the processor over a JSONL source.

This was originally a print/sys.exit script; it is now a proper pytest module.
It guards against a regression where ``CommonProcessor.run`` crashed on sources
without ``__len__`` (a generator-backed JSONL source).
"""
import json
import os

import pytest

from datacrafter.processors.base import CommonProcessor
from datacrafter.sources import get_source_from_file


class _MockProject:
    """Minimal project stand-in exposing a processor config."""

    def __init__(self):
        self.project = {'processor': {'config': {}}}


class _RecordingDestination:
    """Destination that records written records in memory."""

    def __init__(self):
        self.records = []
        self.bulk_records = []

    def write(self, record):
        self.records.append(record)

    def write_bulk(self, records):
        self.bulk_records.extend(records)

    def close(self):
        pass


@pytest.fixture
def jsonl_source(tmp_path):
    """Create a temporary JSONL file with 10 records and return its path."""
    path = tmp_path / "data.jsonl"
    with open(path, "w", encoding="utf8") as f:
        for i in range(10):
            json.dump({"id": i, "value": f"test_{i}"}, f)
            f.write("\n")
    return str(path)


class TestRealUsageRun:
    def test_processor_runs_without_len(self, jsonl_source):
        """run() MUST NOT crash on a source lacking __len__ (the original bug)."""
        project = _MockProject()
        processor = CommonProcessor(project)
        source = get_source_from_file(jsonl_source, stype='jsonl')
        destination = _RecordingDestination()

        # Should not raise even though the source has no __len__.
        processor.run(source, destination, buffer_size=5, show_progress=False)

        # All 10 records should reach the destination (single or bulk writes).
        written = len(destination.records) + len(destination.bulk_records)
        assert written == 10
        assert processor.stats['total_records'] == 10

    def test_processor_stats_populated(self, jsonl_source):
        project = _MockProject()
        processor = CommonProcessor(project)
        source = get_source_from_file(jsonl_source, stype='jsonl')
        destination = _RecordingDestination()

        processor.run(source, destination, buffer_size=5, show_progress=False)

        assert processor.stats['successful_records'] == 10
        assert processor.stats['failed_records'] == 0

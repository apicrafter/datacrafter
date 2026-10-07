"""Tests for logging ownership, exception hierarchy, failure propagation."""
import logging

import pytest

from datacrafter._registry import (
    UnknownDestinationTypeError,
    UnknownExtractorTypeError,
    UnknownSourceTypeError,
)
from datacrafter.cmds.project import Project
from datacrafter.common.env import MissingEnvVarError
from datacrafter.common.logconfig import enable_project_logging
from datacrafter.common.state import ProjectState
from datacrafter.destinations.jsonl import JSONLinesDestination
from datacrafter.errors import DataCrafterError, DestinationWriteError
from datacrafter.extractors.base import DataCrafterConfigurationError
from datacrafter.processors.base import ProcessingError, RecordProcessingError
from datacrafter.sources.base import BaseSource


class TestImportHasNoLoggingSideEffect:
    def test_importing_core_does_not_touch_root_logger(self):
        import subprocess
        import sys
        code = (
            'import logging, sys;'
            'before = logging.getLogger().level;'
            'import datacrafter.core;'
            'after = logging.getLogger().level;'
            'print(before == after)'
        )
        result = subprocess.run(
            [sys.executable, '-c', code], capture_output=True, text=True,
            check=True)
        assert result.stdout.strip() == 'True'


class TestProjectLoggingPreservesExternalHandlers:
    def test_external_handler_survives(self, tmp_path):
        root = logging.getLogger()
        external = logging.StreamHandler()
        external.setLevel(logging.INFO)
        root.addHandler(external)
        try:
            enable_project_logging(str(tmp_path / 'p.log'), tofile=True)
            assert external in root.handlers
        finally:
            root.removeHandler(external)
            for handler in list(root.handlers):
                if getattr(handler, '_datacrafter_file', False) or getattr(
                        handler, '_datacrafter_console', False):
                    root.removeHandler(handler)
                    handler.close()

    def test_repeated_calls_do_not_stack_handlers(self, tmp_path):
        root = logging.getLogger()
        try:
            enable_project_logging(str(tmp_path / 'p.log'), tofile=True)
            count_ours = sum(
                1 for h in root.handlers
                if getattr(h, '_datacrafter_file', False))
            enable_project_logging(str(tmp_path / 'p.log'), tofile=True)
            count_again = sum(
                1 for h in root.handlers
                if getattr(h, '_datacrafter_file', False))
            assert count_ours == count_again == 1
        finally:
            for handler in list(root.handlers):
                if getattr(handler, '_datacrafter_file', False) or getattr(
                        handler, '_datacrafter_console', False):
                    root.removeHandler(handler)
                    handler.close()


class TestExceptionHierarchy:
    @pytest.mark.parametrize('exc_class', [
        ProcessingError, RecordProcessingError, DataCrafterConfigurationError,
        MissingEnvVarError, UnknownSourceTypeError, UnknownDestinationTypeError,
        UnknownExtractorTypeError, DestinationWriteError,
    ])
    def test_derives_from_datacrafter_error(self, exc_class):
        assert issubclass(exc_class, DataCrafterError)

    def test_missing_env_var_still_value_error_compatible(self):
        assert issubclass(MissingEnvVarError, ValueError)


class TestWriteFailurePropagation:
    def _staged_project(self, sample_project, sample_config, tmp_file):
        sample_project.project = sample_config
        sample_project.state = ProjectState(
            filename=sample_project.state_file, reset=True, autosave=True)
        sample_project.state.add('extractor', status='success', results=[
            {'filename': tmp_file, 'compressed': False, 'type': 'file'}])

    def test_flush_failure_raises_and_fails_destination_stage(
            self, sample_project, sample_config, jsonl_file, monkeypatch):
        self._staged_project(sample_project, sample_config, jsonl_file)

        def broken_close():
            raise DestinationWriteError('flush failed')

        # run() re-creates the destination in prepare(); patch it there so the
        # fresh instance is the broken one.
        real_prepare = sample_project.prepare

        def prepare_then_break():
            real_prepare()
            monkeypatch.setattr(
                sample_project.destination, 'close', broken_close)

        monkeypatch.setattr(sample_project, 'prepare', prepare_then_break)
        with pytest.raises(DestinationWriteError):
            sample_project.run()
        stages = sample_project.state.stages
        assert stages[-1]['name'] == 'destination'
        assert stages[-1]['status'] == 'fail'
        assert 'flush failed' in stages[-1]['error']

    def test_processor_failure_recorded_in_state(
            self, sample_project, sample_config, jsonl_file, monkeypatch):
        self._staged_project(sample_project, sample_config, jsonl_file)
        sample_project.prepare()

        def broken_process():
            raise ProcessingError('record pipeline exploded')

        monkeypatch.setattr(sample_project, 'process', broken_process)
        with pytest.raises(ProcessingError):
            sample_project.run()
        stages = sample_project.state.stages
        assert stages[-1]['name'] == 'processor'
        assert stages[-1]['status'] == 'fail'

    def test_file_destination_flush_error_raises_on_close(self, tmp_path):
        dest = JSONLinesDestination(str(tmp_path / 'out.jsonl'))
        dest.write({'id': 1})
        dest.fobj.flush = lambda: (_ for _ in ()).throw(OSError('disk full'))
        with pytest.raises(DestinationWriteError, match='disk full'):
            dest.close()


class TestNoConsoleHandlerUnderExternal:
    def test_console_handler_skipped_when_external_present(self, tmp_path):
        root = logging.getLogger()
        external = logging.StreamHandler()
        root.addHandler(external)
        try:
            enable_project_logging(str(tmp_path / 'p.log'), console=True)
            ours = [h for h in root.handlers
                    if getattr(h, '_datacrafter_console', False)]
            assert ours == []
        finally:
            root.removeHandler(external)
            for handler in list(root.handlers):
                if getattr(handler, '_datacrafter_file', False) or getattr(
                        handler, '_datacrafter_console', False):
                    root.removeHandler(handler)
                    handler.close()


class TestStepErrorLogsOnce:
    def test_skip_strategy_single_warning(self, caplog):
        from datacrafter.processors.base import DataPipeline

        class Boom:
            def apply(self, record):
                raise ValueError('kaboom')

        pipeline = DataPipeline(error_strategy='skip')
        pipeline.add_step(Boom())
        with caplog.at_level(logging.WARNING):
            assert pipeline.execute({'x': 1}) is None
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        errors = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(warnings) == 1
        assert errors == []
        assert 'kaboom' in warnings[0].getMessage()


class TestBaseSourceStreamContract:
    def test_stream_owned_and_closed(self):
        import io
        stream = io.StringIO('{"a": 1}\n')
        from datacrafter.sources.jsonl import JSONLinesSource
        source = JSONLinesSource(stream=stream)
        source.close()
        assert source.fobj.closed

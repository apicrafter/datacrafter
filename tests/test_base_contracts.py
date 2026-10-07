"""Direct tests for logging config and source/destination base contracts."""
import logging

import pytest

from datacrafter.common.logconfig import configure_logging
from datacrafter.destinations.base import BaseDestination
from datacrafter.sources.base import BaseSource


class TestConfigureLogging:
    def test_sets_level(self):
        configure_logging(logging.WARNING)
        assert logging.getLogger().level == logging.WARNING

    def test_level_can_be_lowered_on_existing_handlers(self):
        configure_logging(logging.WARNING)
        configure_logging(logging.DEBUG)
        root = logging.getLogger()
        assert root.level == logging.DEBUG
        for handler in root.handlers:
            assert handler.level <= logging.DEBUG

    def test_reconfigure_does_not_stack_handlers(self):
        configure_logging(logging.INFO)
        before = len(logging.getLogger().handlers)
        configure_logging(logging.INFO)
        configure_logging(logging.WARNING)
        assert len(logging.getLogger().handlers) == before


class TestSourceBaseContract:
    def test_defaults(self):
        source = BaseSource()
        assert source.is_flat() is False
        assert source.is_streaming() is False
        with pytest.raises(NotImplementedError):
            source.reset()
        with pytest.raises(NotImplementedError):
            source.read()

    def test_iter_calls_reset(self):
        class OnceSource(BaseSource):
            def __init__(self):
                self.resets = 0

            def reset(self):
                self.resets += 1

            def read(self):
                raise StopIteration

        source = OnceSource()
        list(source)
        assert source.resets == 1


class TestDestinationBaseContract:
    def test_defaults(self):
        destination = BaseDestination()
        assert destination.is_flat() is False
        assert destination.is_streaming() is False
        with pytest.raises(NotImplementedError):
            destination.write({'id': 1})
        with pytest.raises(NotImplementedError):
            destination.write_bulk([{'id': 1}])

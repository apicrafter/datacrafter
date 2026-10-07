# -*- coding: utf8 -*-
"""Data processing pipeline and processor base classes.

This module provides the base classes and implementations for data processing
pipelines, including support for keymapping, type mapping, custom code steps,
and error handling strategies.
"""
import json
import logging
import os
import time
from dataclasses import dataclass, field, fields
from itertools import chain
from runpy import run_path
from typing import Optional

from tqdm import tqdm

from ..common.infer import infer_field_types, stable_record_id
from ..common.mappers import map_keys, simple_typemap_object
from ..common.paths import resolve_project_script
from ..constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_RETRY_DELAY,
    ERROR_STRATEGY_FAIL,
    ERROR_STRATEGY_RETRY,
    ERROR_STRATEGY_SKIP,
)
from ..errors import DataCrafterError


class ProcessingError(DataCrafterError):
    """Base exception for processing errors"""
    pass


class RecordProcessingError(ProcessingError):
    """Exception raised when a record fails to process"""
    def __init__(self, message, record=None, step_name=None):
        super().__init__(message)
        self.record = record
        self.step_name = step_name


class AbstractStep:
    """Abstract step class"""

    def __init__(self):
        pass

    def apply(self, record):
        """Shouldn't be called in this class"""
        raise NotImplementedError


class KeymapFieldsStep(AbstractStep):
    """Keymapping step with fields rename"""

    def __init__(self, keys, qd=None):
        self.keys = keys
        self.qd = qd
        super().__init__()

    def apply(self, record):
        """Applies keymap to selected record"""
        return map_keys(record, self.keys, self.qd)


class KeymapPositionStep(AbstractStep):
    """Keymapping step with positions"""

    def __init__(self, keys):
        self.keys = keys
        super().__init__()

    def apply(self, record):
        """Applies keymap to selected record"""
        return dict(zip(record, self.keys))


class TypemapStep(AbstractStep):
    """Typemap step"""

    def __init__(self, schema):
        self.schema = schema
        super().__init__()

    def apply(self, record):
        """Applies typemap to selected record"""
        return simple_typemap_object(record, self.schema)


class AutoidStep(AbstractStep):
    """Assign a stable ``_id`` when the record does not already have one."""

    def __init__(self, fields=None):
        self.fields = list(fields) if fields else []
        super().__init__()

    def apply(self, record):
        """Applies autoid to selected record"""
        if not isinstance(record, dict):
            return record
        if record.get('_id'):
            return record
        updated = dict(record)
        updated['_id'] = stable_record_id(updated, self.fields)
        return updated


class CustomCodeStep(AbstractStep):
    """Custom code step"""

    def __init__(self, customtype="script", code=None, project_path=None):
        self.customtype = customtype
        if project_path:
            self.code = resolve_project_script(project_path, code)
        else:
            self.code = code
        script = run_path(self.code)
        self.__process_func = script['process']
        super().__init__()

    def apply(self, record):
        """Applies custom step to selected record"""
        return self.__process_func(record)


class DataPipeline:
    """Data pipeline to process single records"""

    def __init__(self, steps=None, error_strategy=ERROR_STRATEGY_SKIP):
        if steps is None:
            steps = []
        self.steps = steps
        self.error_strategy = error_strategy

    def add_step(self, step):
        """Add step to pipeline"""
        self.steps.append(step)

    def execute(self, record):
        """Executes pipeline steps with error handling"""
        n = 0
        for step in self.steps:
            n += 1
            step_name = step.__class__.__name__
            try:
                record = step.apply(record)
                # Validate record after each step
                if record is None:
                    raise RecordProcessingError(
                        f"Step {step_name} returned None",
                        record=record,
                        step_name=step_name
                    )
            except Exception as error:
                if self.error_strategy in (
                        ERROR_STRATEGY_FAIL, ERROR_STRATEGY_RETRY):
                    error_msg = (
                        f"Error in step {step_name} "
                        f"(step {n}/{len(self.steps)}): {str(error)}"
                    )
                    raise RecordProcessingError(
                        error_msg,
                        record=record,
                        step_name=step_name
                    ) from error
                logging.warning(
                    "Skipping record due to error in %s: %s", step_name, error)
                return None
        return record


class BaseProcessor:
    """Abstract class of the data processor"""

    def __init__(self, project):
        self.project = project

    #        self.destination = destination

    def process_record(self, record):
        """Processes single record of data"""
        raise NotImplementedError

    def run(self, source, destination=None):
        """Execute data processing"""
        raise NotImplementedError


DEFAULT_CONFIG_PARAMS = {'autoid': {'type': bool, 'default': False},
                         'skip_lines': {'type': int, 'default': None},
                         'autotype': {'type': bool, 'default': False},
                         'autotype_sample': {'type': int, 'default': 100},
                         'autoid_fields': {'type': list, 'default': None},
                         'error_strategy': {
                             'type': str,
                             'default': ERROR_STRATEGY_SKIP
                         },
                         'max_retries': {
                             'type': int,
                             'default': DEFAULT_MAX_RETRIES
                         },
                         }

DEFAULT_CONFIG: dict = {'config': {}}


@dataclass
class ProcessorConfig:
    """Self-contained processor configuration.

    Mirrors ``DEFAULT_CONFIG_PARAMS`` plus the keymap/typemap/custom sections
    of the ``processor:`` YAML block, so the processor does not need the
    Project orchestrator to run.
    """
    autoid: bool = False
    autotype: bool = False
    autotype_sample: int = 100
    autoid_fields: Optional[list] = field(default=None)
    skip_lines: Optional[int] = None
    error_strategy: str = ERROR_STRATEGY_SKIP
    max_retries: int = DEFAULT_MAX_RETRIES
    keymap: Optional[dict] = None
    typemap: Optional[dict] = None
    custom: Optional[dict] = None

    @classmethod
    def from_project_config(cls, processor_section):
        """Build a config from the ``processor:`` YAML section."""
        section = processor_section if isinstance(processor_section, dict) else {}
        raw_config = section.get('config')
        if not isinstance(raw_config, dict):
            raw_config = {}
        known = {field_.name for field_ in fields(cls)}
        kwargs = {key: value for key, value in raw_config.items() if key in known}
        for name in ('keymap', 'typemap', 'custom'):
            if isinstance(section.get(name), dict):
                kwargs[name] = section[name]
        return cls(**kwargs)


class CommonProcessor(BaseProcessor):
    """Implementation of common operations.

    Accepts either a :class:`ProcessorConfig` plus explicit ``project_path`` /
    ``output`` / ``state`` arguments (library usage, no Project required), or
    a Project orchestrator whose ``processor:`` section is read as config.
    """

    def __init__(self, config, project_path=None, output=None, state=None):
        if isinstance(config, ProcessorConfig):
            self.config = config
            self.project = None
        else:
            # Backwards-compatible Project-based construction.
            self.project = config
            section = config.project.get('processor') \
                if getattr(config, 'project', None) else None
            self.config = ProcessorConfig.from_project_config(section)
            project_path = getattr(config, 'project_path', project_path)
            output = getattr(config, 'output', output)
            state = getattr(config, 'state', state)
        self.project_path = project_path
        self.output = output
        self.state = state
        self.params = {'config': {}}
        self.__set_default_config()
        error_strategy = getattr(self, 'error_strategy', ERROR_STRATEGY_SKIP)
        self.pipeline = DataPipeline(error_strategy=error_strategy)
        # Processing metrics
        self.stats = {
            'total_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'skipped_records': 0,
            'errors': []
        }

        if self.config.keymap:
            if self.config.keymap['type'] == 'position':
                keys = self.config.keymap['keys'].split(',')
                self.pipeline.add_step(KeymapPositionStep(keys))
            elif self.config.keymap['type'] == 'names':
                keymap_schema = {}
                for key in self.config.keymap['fields']:
                    keymap_schema[key] = {'name': self.config.keymap['fields'][key]}
                self.pipeline.add_step(KeymapFieldsStep(keys=keymap_schema))
                logging.info('Added keymapping step with schema %s', keymap_schema)

        if self.config.typemap:
            self.pipeline.add_step(TypemapStep(self.config.typemap))
            logging.info(
                'Added type mapping step with schema %s',
                str(self.config.typemap))

        if self.config.custom:
            self.pipeline.add_step(
                CustomCodeStep(
                    customtype=self.config.custom['type'],
                    code=self.config.custom['code'],
                    project_path=self.project_path))
            logging.info(
                'Added custom code script step %s',
                str(self.config.custom['code']))

        if getattr(self, 'autoid', False):
            raw_fields = getattr(self, 'autoid_fields', None)
            if isinstance(raw_fields, str):
                fields = [
                    part.strip() for part in raw_fields.split(',') if part.strip()
                ]
            else:
                fields = list(raw_fields or [])
            self.autoid_fields = fields
            self.pipeline.add_step(AutoidStep(fields=fields))
            logging.info('Added autoid step fields=%s', fields)

        self._error_file = None
        self._error_path = None

    def __set_default_config(self):
        """Expose config values as processor attributes (historical API)."""
        for param in DEFAULT_CONFIG_PARAMS:
            setattr(self, param, getattr(self.config, param))

    def _iter_records(self, source):
        """Yield records from a source iterable."""
        for record in source:
            yield record

    def _apply_keymap_copy(self, record):
        """Return a copy after keymap steps only (for autotype inference)."""
        rec = dict(record)
        for step in self.pipeline.steps:
            if isinstance(step, (KeymapFieldsStep, KeymapPositionStep)):
                rec = step.apply(rec) or rec
        return rec

    def _install_autotype(self, mapped_sample):
        """Merge inferred types with explicit typemap (explicit wins)."""
        inferred = infer_field_types(mapped_sample)
        explicit = self.config.typemap or {}
        merged = {**inferred, **explicit}
        if not merged:
            return merged
        for step in self.pipeline.steps:
            if isinstance(step, TypemapStep):
                step.schema = merged
                logging.info('Autotype updated typemap %s', merged)
                return merged
        insert_at = 0
        for i, step in enumerate(self.pipeline.steps):
            if isinstance(step, (KeymapFieldsStep, KeymapPositionStep)):
                insert_at = i + 1
            elif isinstance(step, (CustomCodeStep, AutoidStep)):
                break
        self.pipeline.steps.insert(insert_at, TypemapStep(merged))
        logging.info('Autotype installed typemap %s', merged)
        return merged

    def _iter_with_autotype(self, source):
        """Optionally sample, infer types, then yield all records."""
        if not getattr(self, 'autotype', False):
            yield from self._iter_records(source)
            return
        sample = []
        iterator = iter(source)
        limit = getattr(self, 'autotype_sample', None) or 100
        for _ in range(limit):
            try:
                sample.append(next(iterator))
            except StopIteration:
                break
        mapped = [
            self._apply_keymap_copy(rec) for rec in sample if isinstance(rec, dict)]
        self._install_autotype(mapped)
        yield from chain(sample, iterator)

    def _open_error_file(self):
        output = self.output
        if not output:
            return
        try:
            os.makedirs(output, exist_ok=True)
            self._error_path = os.path.join(output, 'errors.jsonl')
            self._error_file = open(self._error_path, 'a', encoding='utf8')
        except OSError as error:
            logging.warning('Could not open error sidecar: %s', error)
            self._error_file = None
            self._error_path = None

    def _close_error_file(self):
        if self._error_file is None:
            return
        try:
            self._error_file.close()
        except OSError as error:
            logging.debug('Error closing sidecar: %s', error)
        self._error_file = None

    def _write_failed(self, record, error, step=None):
        if self._error_file is None:
            return
        entry = {
            'error': str(error),
            'step': step,
            'record': record,
        }
        try:
            self._error_file.write(
                json.dumps(entry, ensure_ascii=False, default=str) + '\n')
        except OSError as write_error:
            logging.debug('Failed to write error sidecar: %s', write_error)

    def _process_single(self, record):
        """Transform one record through the pipeline."""
        return self.process_record(record)

    def _write_record(self, destination, record):
        """Write a single record, adjusting stats on write failure."""
        if destination is None:
            return
        try:
            destination.write(record)
        except Exception as error:
            logging.error("Error writing record: %s", error)
            self.stats['failed_records'] += 1
            if self.stats['successful_records'] > 0:
                self.stats['successful_records'] -= 1

    def _flush_buffer(self, destination, buffer):
        """Flush buffered records; a one-item buffer uses the single-write path."""
        if not buffer or destination is None:
            return
        if len(buffer) == 1:
            self._write_record(destination, buffer[0])
            return
        try:
            destination.write_bulk(buffer)
        except Exception as error:
            logging.error("Error writing bulk records: %s", error)
            for rec in buffer:
                self._write_record(destination, rec)

    def _source_length(self, source):
        """Return a positive length if the source supports ``len``, else None."""
        try:
            if hasattr(source, '__len__'):
                source_len = len(source)
                if isinstance(source_len, int) and source_len > 0:
                    return source_len
        except (TypeError, AttributeError):
            return None
        except Exception:
            logging.debug(
                "Could not determine source length: %s", type(source).__name__)
        return None

    def _open_progress(self, source, show_progress):
        """Create a tqdm progress bar when useful; otherwise return None."""
        root_logger = logging.getLogger()
        quiet_mode = root_logger.level >= logging.ERROR
        if not (show_progress and not quiet_mode):
            return None
        total_known = self._source_length(source)
        if total_known is None:
            logging.info(
                "Processing records (progress bar disabled for unknown total)")
            return None
        return tqdm(
            total=total_known,
            desc="Processing",
            unit="records",
            unit_scale=False,
            ncols=100,
            bar_format=(
                '{l_bar}{bar}| {n_fmt}/{total_fmt} '
                '[{elapsed}<{remaining}, {rate_fmt}]'
            )
        )

    def _update_progress(self, pbar):
        if not pbar:
            return
        pbar.update(1)
        pbar.set_postfix({
            'success': self.stats['successful_records'],
            'failed': self.stats['failed_records'],
            'skipped': self.stats['skipped_records']
        })

    def _log_summary(self):
        elapsed_time = time.time() - self.stats['start_time']
        records_per_sec = (
            self.stats['total_records'] / elapsed_time if elapsed_time > 0 else 0)
        logging.info("Processing Summary")
        logging.info("Total records processed: %s", self.stats['total_records'])
        logging.info("  Successful: %s", self.stats['successful_records'])
        logging.info("  Failed: %s", self.stats['failed_records'])
        logging.info("  Skipped: %s", self.stats['skipped_records'])
        if self.stats['total_records'] > 0:
            success_rate = (
                self.stats['successful_records'] / self.stats['total_records']
            ) * 100
            logging.info("Success rate: %.2f%%", success_rate)
        logging.info("Processing time: %.2f seconds", elapsed_time)
        logging.info("Processing speed: %.2f records/second", records_per_sec)
        if self.stats['failed_records'] > 0:
            logging.warning(
                "Some records failed to process. Check logs for details.")
            if self.stats['errors']:
                logging.warning("First error: %s", self.stats['errors'][0])

    def _record_processor_state(self, status):
        state = self.state
        if state is None or not hasattr(state, 'add'):
            return
        state.add('processor', status=status, results={
            'total_records': self.stats['total_records'],
            'successful_records': self.stats['successful_records'],
            'failed_records': self.stats['failed_records'],
            'skipped_records': self.stats['skipped_records'],
            'errors_file': self._error_path,
        })

    def process_record(self, record, retry_count=0):
        """Processes single record of data with optional retry."""
        max_retries = getattr(self, 'max_retries', DEFAULT_MAX_RETRIES)
        strategy = getattr(
            self.pipeline, 'error_strategy', ERROR_STRATEGY_SKIP)
        original = dict(record) if isinstance(record, dict) else record
        try:
            result = self.pipeline.execute(record)
            if result is None:
                self.stats['skipped_records'] += 1
                self._write_failed(original, 'skipped by error strategy')
                return None
            self.stats['successful_records'] += 1
            return result
        except RecordProcessingError as error:
            if strategy == ERROR_STRATEGY_RETRY and retry_count < max_retries:
                delay = DEFAULT_RETRY_DELAY * (DEFAULT_RETRY_BACKOFF ** retry_count)
                logging.warning(
                    "Retrying record (attempt %s/%s) after %.2fs",
                    retry_count + 1, max_retries, delay)
                time.sleep(delay)
                return self.process_record(record, retry_count + 1)
            self.stats['failed_records'] += 1
            self.stats['errors'].append({
                'error': str(error),
                'step': error.step_name,
                'record_index': self.stats['total_records']
            })
            logging.error("Failed to process record: %s", error)
            self._write_failed(original, error, step=error.step_name)
            if strategy == ERROR_STRATEGY_FAIL:
                raise
            return None
        except Exception as error:
            self.stats['failed_records'] += 1
            self.stats['errors'].append({
                'error': str(error),
                'step': 'unknown',
                'record_index': self.stats['total_records']
            })
            logging.error("Unexpected error processing record: %s", error)
            self._write_failed(original, error, step='unknown')
            if strategy == ERROR_STRATEGY_FAIL:
                raise
            return None

    def run(self, source, destination=None, buffer_size=None, show_progress=True):
        """Run processor: iterate, transform, write via a single buffered path."""
        self.stats = {
            'total_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'skipped_records': 0,
            'errors': [],
            'start_time': time.time()
        }
        if buffer_size is None or buffer_size <= 0:
            buffer_size = 1
        self._open_error_file()
        pbar = self._open_progress(source, show_progress)
        buffer = []
        status = 'success'
        try:
            for raw_rec in self._iter_with_autotype(source):
                self.stats['total_records'] += 1
                processed = self._process_single(raw_rec)
                if processed is not None:
                    buffer.append(processed)
                    if len(buffer) >= buffer_size:
                        self._flush_buffer(destination, buffer)
                        buffer = []
                self._update_progress(pbar)
            if buffer:
                self._flush_buffer(destination, buffer)
            status = 'success' if self.stats['failed_records'] == 0 else 'partial'
            self._log_summary()
            self._record_processor_state(status)
        except Exception as error:
            logging.error("Fatal error in processor: %s", error)
            status = 'fail'
            self._record_processor_state(status)
            raise
        finally:
            self._close_error_file()
            if pbar:
                pbar.close()


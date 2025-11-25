# -*- coding: utf8 -*-
import logging
import time
from runpy import run_path
from typing import Optional

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Fallback if tqdm is not available
    def tqdm(iterable=None, **kwargs):
        return iterable if iterable is not None else range(0)

from ..common.mappers import map_keys, simple_typemap_object
from ..constants import (
    ERROR_STRATEGY_SKIP,
    ERROR_STRATEGY_FAIL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RETRY_BACKOFF
)


class ProcessingError(Exception):
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


class CustomCodeStep(AbstractStep):
    """Custom code step"""

    def __init__(self, customtype="script", code=None):
        self.customtype = customtype
        self.code = code
        script = run_path(code)
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
            except Exception as e:
                error_msg = f"Error in step {step_name} (step {n}/{len(self.steps)}): {str(e)}"
                logging.error(error_msg)
                
                if self.error_strategy == ERROR_STRATEGY_FAIL:
                    raise RecordProcessingError(
                        error_msg,
                        record=record,
                        step_name=step_name
                    ) from e
                elif self.error_strategy == ERROR_STRATEGY_SKIP:
                    # Return None to signal this record should be skipped
                    logging.warning(f"Skipping record due to error in {step_name}")
                    return None
                else:
                    # Default to skip
                    logging.warning(f"Skipping record due to error in {step_name}")
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


DEFAULT_CONFIG_PARAMS = {'autoid': {'type': bool, 'default': True},
                         'skip_lines': {'type': int, 'default': None},
                         'autotype': {'type': bool, 'default': False},
                         'error_strategy': {'type': str, 'default': ERROR_STRATEGY_SKIP},
                         'max_retries': {'type': int, 'default': DEFAULT_MAX_RETRIES},
                         }

DEFAILT_CONFIG = {'config': {}}


class CommonProcessor(BaseProcessor):
    """Implementation of common operations"""

    def __init__(self, project):  # , destination):
        self.project = project
        if 'processor' in self.project.project.keys():
            self.params = self.project.project['processor']
        else:
            self.params = DEFAILT_CONFIG.copy()
        #        self.destination = destination
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

        if 'keymap' in self.params.keys():
            if self.params['keymap']['type'] == 'position':
                self.pipeline.add_step(KeymapPositionStep(self.params['keymap']['keys'].split(',')))
            elif self.params['keymap']['type'] == 'names':
                keymap_schema = {}
                for key in self.params['keymap']['fields']:
                    keymap_schema[key] = {'name': self.params['keymap']['fields'][key]}
                self.pipeline.add_step(KeymapFieldsStep(keys=keymap_schema))
                logging.info('Added keymapping step with schema %s' % str(keymap_schema))

        if 'typemap' in self.params.keys():
            self.pipeline.add_step(TypemapStep(self.params['typemap']))
            logging.info('Added type mapping step with schema %s' % str(self.params['typemap']))

        if 'custom' in self.params.keys():
            self.pipeline.add_step(
                CustomCodeStep(customtype=self.params['custom']['type'], code=self.params['custom']['code']))
            logging.info('Added custom code script step %s' % str(self.params['custom']['code']))

    def __set_default_config(self):
        """Sets default parameters or parameters from YAML config"""
        for param in DEFAULT_CONFIG_PARAMS:
            if param not in self.params['config'].keys():
                value = DEFAULT_CONFIG_PARAMS[param]['default']
            else:
                value = self.params['config'][param]
            setattr(self, param, value)

    def process_record(self, record, retry_count=0):
        """Processes single record of data with retry logic"""
        max_retries = getattr(self, 'max_retries', DEFAULT_MAX_RETRIES)
        try:
            result = self.pipeline.execute(record)
            if result is None:
                # Record was skipped
                self.stats['skipped_records'] += 1
                return None
            self.stats['successful_records'] += 1
            return result
        except RecordProcessingError as e:
            if retry_count < max_retries:
                delay = DEFAULT_RETRY_DELAY * (DEFAULT_RETRY_BACKOFF ** retry_count)
                logging.warning(f"Retrying record (attempt {retry_count + 1}/{max_retries}) after {delay:.2f}s")
                time.sleep(delay)
                return self.process_record(record, retry_count + 1)
            else:
                self.stats['failed_records'] += 1
                self.stats['errors'].append({
                    'error': str(e),
                    'step': e.step_name,
                    'record_index': self.stats['total_records']
                })
                logging.error(f"Failed to process record after {max_retries} retries: {e}")
                if self.pipeline.error_strategy == ERROR_STRATEGY_FAIL:
                    raise
                return None
        except Exception as e:
            self.stats['failed_records'] += 1
            self.stats['errors'].append({
                'error': str(e),
                'step': 'unknown',
                'record_index': self.stats['total_records']
            })
            logging.error(f"Unexpected error processing record: {e}")
            if self.pipeline.error_strategy == ERROR_STRATEGY_FAIL:
                raise
            return None

    def run(self, source, destination=None, buffer_size=None, show_progress=True):
        """Run processor with error handling, metrics, and progress reporting"""
        self.stats = {
            'total_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'skipped_records': 0,
            'errors': [],
            'start_time': time.time()
        }
        
        # Check if we should show progress (not in quiet mode)
        root_logger = logging.getLogger()
        quiet_mode = root_logger.level >= logging.ERROR
        use_progress = show_progress and TQDM_AVAILABLE and not quiet_mode
        
        pbar = None  # Initialize progress bar variable
        try:
            # Check if source has __len__ (can determine total)
            total_known = None
            try:
                if hasattr(source, '__len__'):
                    total_known = len(source)
            except (TypeError, AttributeError):
                # Can't determine length (generator, etc.)
                total_known = None
            
            # Create progress bar if enabled
            if use_progress and total_known is not None:
                pbar = tqdm(
                    total=total_known,
                    desc="Processing",
                    unit="records",
                    unit_scale=False,
                    ncols=100,
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
                )
            elif use_progress:
                # Unknown total, use indeterminate progress bar
                pbar = tqdm(
                    desc="Processing",
                    unit="records",
                    unit_scale=False,
                    ncols=100,
                    bar_format='{l_bar}{bar}| {n_fmt} [{elapsed}, {rate_fmt}]'
                )
            else:
                pbar = None
            
            # Process records
            source_iter = source
            
            if buffer_size is not None and buffer_size > 0:
                records = []
                n = 0
                for raw_rec in source_iter:
                    self.stats['total_records'] += 1
                    
                    p_rec = self.process_record(raw_rec)
                    if p_rec is not None:  # Only add non-skipped records
                        n += 1
                        records.append(p_rec)
                        if n == buffer_size:
                            try:
                                destination.write_bulk(records)
                            except Exception as e:
                                logging.error(f"Error writing bulk records: {e}")
                                # Try writing individually
                                for rec in records:
                                    try:
                                        destination.write(rec)
                                    except Exception as write_err:
                                        logging.error(f"Error writing individual record: {write_err}")
                            n = 0
                            records = []
                    
                    # Update progress bar
                    if pbar:
                        pbar.update(1)
                        # Update progress bar description with stats
                        pbar.set_postfix({
                            'success': self.stats['successful_records'],
                            'failed': self.stats['failed_records'],
                            'skipped': self.stats['skipped_records']
                        })
                
                if len(records) > 0:
                    try:
                        destination.write_bulk(records)
                    except Exception as e:
                        logging.error(f"Error writing final bulk records: {e}")
            else:
                for raw_rec in source_iter:
                    self.stats['total_records'] += 1
                    
                    p_rec = self.process_record(raw_rec)
                    if p_rec is not None:
                        try:
                            destination.write(p_rec)
                        except Exception as e:
                            logging.error(f"Error writing record: {e}")
                            self.stats['failed_records'] += 1
                            self.stats['successful_records'] -= 1  # Adjust count
                    
                    # Update progress bar
                    if pbar:
                        pbar.update(1)
                        # Update progress bar description with stats
                        pbar.set_postfix({
                            'success': self.stats['successful_records'],
                            'failed': self.stats['failed_records'],
                            'skipped': self.stats['skipped_records']
                        })
            
            # Close progress bar
            if pbar:
                pbar.close()
            
            # Calculate processing time and speed
            elapsed_time = time.time() - self.stats['start_time']
            if elapsed_time > 0:
                records_per_sec = self.stats['total_records'] / elapsed_time
            else:
                records_per_sec = 0
            
            # Log final statistics with summary
            logging.info("=" * 60)
            logging.info("Processing Summary")
            logging.info("=" * 60)
            logging.info(f"Total records processed: {self.stats['total_records']}")
            logging.info(f"  ✓ Successful: {self.stats['successful_records']}")
            logging.info(f"  ✗ Failed: {self.stats['failed_records']}")
            logging.info(f"  ⊘ Skipped: {self.stats['skipped_records']}")
            
            if self.stats['total_records'] > 0:
                success_rate = (self.stats['successful_records'] / self.stats['total_records']) * 100
                logging.info(f"Success rate: {success_rate:.2f}%")
            
            logging.info(f"Processing time: {elapsed_time:.2f} seconds")
            logging.info(f"Processing speed: {records_per_sec:.2f} records/second")
            logging.info("=" * 60)
            
            if self.stats['failed_records'] > 0:
                logging.warning(f"Some records failed to process. Check logs for details.")
                if len(self.stats['errors']) > 0:
                    logging.warning(f"First error: {self.stats['errors'][0]}")
            
            status = 'success' if self.stats['failed_records'] == 0 else 'partial'
        except Exception as e:
            if pbar:
                pbar.close()
            logging.error(f"Fatal error in processor: {e}")
            status = 'fail'
            raise
#        self.project.state.add('processor', status=status, results=self.results)

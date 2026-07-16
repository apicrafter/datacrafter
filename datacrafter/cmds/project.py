# -*- coding: utf-8 -*-
"""Project command module for managing datacrafter projects."""
import os
import shutil
import errno
import logging
import uuid

import yaml

# Project imports
from ..constants import DEFAULT_BULK_RECORDS
from ..extractors.base import BaseExtractor
from ..processors.base import CommonProcessor
from ..common.state import ProjectState
from ..sources import get_source_from_file
from ..destinations import get_destination_from_config


def load_config(filename):
    """Load YAML configuration file using safe loading.

    ``yaml.safe_load`` is used (rather than the full ``Loader``/``CLoader``) so that
    configuration files cannot construct arbitrary Python objects via YAML tags.
    """
    with open(filename, 'r', encoding='utf8') as file_obj:
        data = yaml.safe_load(file_obj)
    return data


def remove_dir_contents(dirpath, debug=False):
    """Remove all contents from a directory."""
    for filename in os.listdir(dirpath):
        file_path = os.path.join(dirpath, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            if debug:
                logging.debug('Removed %s from %s', file_path, dirpath)
        except OSError as error:
            logging.debug('Failed to delete %s. Reason: %s', file_path, error)


class Project:
    """Main project class for managing datacrafter projects."""
    def __init__(self, project_path=None):
        """Init project class"""
        self.project = None
        self.project_path = os.getcwd() if project_path is None else project_path
        self.project_filename = os.path.join(self.project_path, 'datacrafter.yml')
        if os.path.exists(self.project_filename):
            self.__read_project_file(self.project_filename)

        dpath = os.path.join(self.project_path)

        self.current = os.path.join(dpath, "current")
        self.output = os.path.join(dpath, "output")
        self.temp = os.path.join(dpath, "temp")
        self.builds = os.path.join(dpath, "builds")
        self.storage = os.path.join(dpath, "storage")
        self.docpath = os.path.join(dpath, "docs")

        self.logfile = os.path.join(dpath, 'datacrafter.log')
        self.state_file = os.path.join(self.project_path, 'state.json')


    def enable_logging(self, console=True, tofile=False, structured=False):
        """Enable logging to file and stderr with rotation support"""
        rootLogger = logging.getLogger()

        # Preserve the current effective level (may be set to DEBUG for verbose mode)
        current_level = rootLogger.getEffectiveLevel()
        
        # Remove existing handlers to avoid duplicates
        rootLogger.handlers.clear()

        # Preserve DEBUG if it was already set (e.g. for verbose mode); otherwise
        # default to INFO for normal operation. (Previously this was a no-op
        # tautology whose two branches both returned logging.DEBUG.)
        rootLogger.setLevel(
            logging.DEBUG if current_level <= logging.DEBUG else logging.INFO)

        if structured:
            # Structured logging (JSON format)
            import json
            class JSONFormatter(logging.Formatter):
                """JSON formatter for structured logging."""
                def format(self, record):
                    log_entry = {
                        'timestamp': self.formatTime(record, self.datefmt),
                        'level': record.levelname,
                        'logger': record.name,
                        'message': record.getMessage(),
                        'module': record.module,
                        'function': record.funcName,
                        'line': record.lineno
                    }
                    if record.exc_info:
                        log_entry['exception'] = self.formatException(record.exc_info)
                    return json.dumps(log_entry)

            formatter = JSONFormatter()
        else:
            # Standard text format
            formatter = logging.Formatter(
                "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
            )

        if tofile:
            # Use RotatingFileHandler for log rotation
            from logging.handlers import RotatingFileHandler
            # Rotate when file reaches 10MB, keep 5 backup files
            fileHandler = RotatingFileHandler(
                self.logfile,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            fileHandler.setLevel(logging.DEBUG)  # File gets all logs
            fileHandler.setFormatter(formatter)
            rootLogger.addHandler(fileHandler)

        if console:
            consoleHandler = logging.StreamHandler()
            # Use DEBUG level if verbose mode was enabled (current_level was DEBUG)
            # Otherwise default to INFO for normal operation
            console_level = logging.DEBUG if current_level <= logging.DEBUG else logging.INFO
            consoleHandler.setLevel(console_level)
            consoleHandler.setFormatter(formatter)
            rootLogger.addHandler(consoleHandler)

    def __read_project_file(self, _filename):
        """Reads project file content"""
        self.project = None
        if os.path.exists(self.project_filename):
            self.project = load_config(self.project_filename)
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.project_filename)

    def init(self, name=None, force=False):
        """Initialize project. Creates required dirs if they do not exists"""
        self.enable_logging(console=True, tofile=False)
        logging.info('Initialize project. Create required directories')
        if os.path.exists(self.project_filename) and not force:
            logging.warning(
                'Project file %s already exists. No force flag set. Skip',
                self.project_filename)
        else:
            self.__create_dirs()
            self.__create_project_yaml(name)
        # Load the (possibly just-created) project config so self.project is
        # populated for subsequent operations (validate/process/etc.).
        self.__read_project_file(self.project_filename)


    def __create_project_yaml(self, name=None, version="1", id=None):
        """Create project YAML file"""
        project = {
            'version': version if version else None,
            'project-name': name if name else 'dummy',
            'project-id': id if id else uuid.uuid4().hex}
        with open(self.project_filename, 'w', encoding='utf8') as f:
            yaml.dump(project, f)
        logging.info('Project file created')

    def __create_dirs(self):
        """Create all project directories"""
        for k in [
            self.current,
            self.output,
            self.temp,
            self.builds,
            self.storage,
        ]:
            try:
                os.makedirs(k)
                logging.debug("Directory %s created", k)
            except OSError as error:
                logging.debug("Directory %s can't be created: %s", k, error)



    def log(self):
        """Log project information. FIXME: Logging outside system logging."""
        pass

    def clean(self, _basepath=None, clean_storage=False):
        """Clean project temporary files and optionally storage directory."""
        logging.info('Clean project data. Clean storage: %s', clean_storage)
        state_file = os.path.join(self.project_path, 'state.json')
        if os.path.exists(state_file):
            os.remove(state_file)
            logging.debug('Removed state file %s', state_file)

        dirs_to_clean = [
            (self.output, 'output dir'),
            (self.current, 'current dir'),
            (self.temp, 'tempdir')]
        for dirname, msg in dirs_to_clean:
            logging.info('Cleaning %s', msg)
            remove_dir_contents(os.path.join(self.project_path, dirname), debug=True)
        logging.info('Cleaning storage dir, if exists')
        if os.path.exists(os.path.join(self.project_path, "storage")) and clean_storage:
            remove_dir_contents(os.path.join(self.project_path, 'storage'), debug=True)

    def validate(self):
        """Validates project file #FIXME returns always True for now"""
    #        raise
        return True, None

    def prepare(self):
        """Prepares everything"""
        logging.info('Preparing project extract, processor and destination')
        self.extractor = BaseExtractor(self)
        logging.info('Extractor class %s', self.extractor.__class__)
        self.processor = CommonProcessor(self)
        logging.info('Processor class %s', self.processor.__class__)
        self.destination = None
        if 'destination' in self.project:
            self.destination = get_destination_from_config(
                self.output, self.project['destination'])
            dest_class = self.destination.__class__ if self.destination else "None"
            logging.info('Destination class %s', dest_class)

    def collect(self, _proceed=True):
        """Runs extractor engine and obtain data"""
        logging.info('Running extractor')
        if len(self.state.stages) > 0:
            stage = self.state.stages[-1]
            if stage['name'] == 'extractor' and stage['status'] == 'success':
                logging.info('Skip extractor stage')
                return
        try:
            self.extractor.run()
        except Exception as error:
            logging.error('Extractor failed: %s', error)
            logging.error('Check your extractor configuration and network connectivity')
            raise

    def process(self):
        """Runs processors and stores result at the destination"""
        logging.info('Running processor')
        if 'stages' not in self.state.data or len(self.state.data['stages']) == 0:
            logging.error('No extractor results found. Run extractor first.')
            raise ValueError('No extractor results found. Run extractor first.')

        resources = self.state.data['stages'][-1]['results']
        if not resources:
            logging.error('No resources to process from extractor stage')
            raise ValueError('No resources to process from extractor stage')

        options = {}
        stype = None
        processed_files = []
        failed_files = []

        try:
            for r in resources:
                filename = r.get('filename', 'unknown')
                try:
                    if 'processor' in self.project.keys():
                        if 'config' in self.project['processor'].keys():
                            options = self.project['processor']['config']
                            if 'type' in options.keys():
                                stype = options['type']
                    logging.info('Processing %s', os.path.basename(filename))
                    source = get_source_from_file(
                        filename, stype=stype, options=options)
                    try:
                        self.processor.run(
                            source, self.destination,
                            buffer_size=DEFAULT_BULK_RECORDS)
                        logging.info(
                            'Processing complete %s', os.path.basename(filename))
                        processed_files.append(filename)
                    except Exception as e:
                        logging.error('Failed to process %s: %s', filename, e)
                        failed_files.append({'filename': filename, 'error': str(e)})
                        # Continue with next file instead of failing completely
                    finally:
                        # Ensure source is closed after processing
                        if hasattr(source, 'close'):
                            try:
                                source.close()
                            except Exception as error:
                                logging.debug('Error closing source: %s', error)
                except Exception as error:
                    logging.error('Error setting up source for %s: %s', filename, error)
                    failed_files.append({'filename': filename, 'error': str(error)})
                    continue

            # Summary
            if failed_files:
                logging.warning(
                    'Some files failed to process: %s/%s',
                    len(failed_files), len(resources))
                for failed in failed_files[:5]:  # Show first 5 errors
                    logging.warning("  - %s: %s", failed['filename'], failed['error'])
                if len(failed_files) > 5:
                    logging.warning("  ... and %s more", len(failed_files) - 5)
            else:
                logging.info(
                    'Successfully processed all %s files', len(processed_files))
        finally:
            # Ensure destination is closed to flush buffers and write file
            if self.destination is not None:
                try:
                    self.destination.close()
                    logging.info('Destination closed')
                except Exception as error:
                    logging.warning('Error closing destination: %s', error)

    def finish(self):
        """Executed on end of the project. Ensures destination is closed"""
        # Ensure destination is closed if not already closed
        if self.destination is not None:
            try:
                self.destination.close()
                logging.info('Destination closed in finish()')
            except Exception as error:
                logging.warning('Error closing destination in finish(): %s', error)
        logging.info("Finished project: %s", self.project['project-name'])

    def run(self, pre_clean=False, init=True, proceed=True, structured_log=False):
        """Execute project"""
        self.enable_logging(console=True, tofile=True, structured=structured_log)
        if self.project is None:
            error_msg = 'Project file not found or not loaded'
            logging.error(error_msg)
            raise ValueError(error_msg)
        isvalid, report = self.validate()
        logging.info("Started project: %s", self.project['project-name'])
        if not isvalid:
            error_msg = 'Invalid configuration. See more info below'
            logging.error(error_msg)
            if report:
                logging.error('Validation report: %s', report)
            raise ValueError(f"{error_msg}. {report if report else ''}")
        if init:
            self.__create_dirs()
        if pre_clean:
            self.clean()
        self.state = ProjectState(
            filename=self.state_file, reset=pre_clean, autosave=True)
        self.prepare()
        self.collect(proceed)
        self.process()
        self.finish()

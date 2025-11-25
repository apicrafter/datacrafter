# -*- coding: utf-8 -*-
import os
import glob
import shutil
import errno
import logging
import uuid

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# Project imports
from ..constants import DEFAULT_BULK_RECORDS
from ..extractors.base import BaseExtractor
from ..processors.base import CommonProcessor
from ..common.state import ProjectState
from ..sources import get_source_from_file
from ..destinations import get_destination_from_config


def load_config(filename):
    with open(filename, 'r', encoding='utf8') as f:
        data = yaml.load(f, Loader=Loader)
    return data


def remove_dir_contents(dirpath, debug=False):
    for filename in os.listdir(dirpath):
        file_path = os.path.join(dirpath, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            if debug:
                logging.debug(f'Removed {file_path} from {dirpath}')
        except OSError as e:
            logging.debug(f'Failed to delete {file_path}. Reason: {e}')


class Project:
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
        
        # Remove existing handlers to avoid duplicates
        rootLogger.handlers.clear()
        
        # Set default level
        rootLogger.setLevel(logging.DEBUG)  # Allow all levels, filter at handler level
        
        if structured:
            # Structured logging (JSON format)
            import json
            class JSONFormatter(logging.Formatter):
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
            consoleHandler.setLevel(logging.INFO)  # Console shows INFO and above by default
            consoleHandler.setFormatter(formatter)
            rootLogger.addHandler(consoleHandler)

    def __read_project_file(self, filename):
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
            logging.warning(f'Project file {self.project_filename} already exists. No force flag set. Skip')
        else:
            self.__create_dirs()
            self.__create_project_yaml(name)


    def __create_project_yaml(self, name=None, version="1", id=None):
        """Create project YAML file"""
        project = {'version' : version if version else None , 'project-name' : name if name else 'dummy', 'project-id' : id if id else uuid.uuid4().hex}
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
                logging.debug(f"Directory {k} created")
            except OSError as e:
                logging.debug(f"Directory {k} can't be created: {e}")



    def log(self):
        # FIXME! Logging outside system logging
        pass

    def clean(self, basepath=None, clean_storage=False):
        logging.info(f'Clean project data. Clean storage: {clean_storage}')
        state_file = os.path.join(self.project_path, 'state.json')
        if os.path.exists(state_file):
            os.remove(state_file)
            logging.debug(f'Removed state file {state_file}')

        for dirname, msg in [(self.output, 'output dir'), (self.current, 'current dir'), (self.temp, 'tempdir')]:
            logging.info(f'Cleaning {msg}')
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
        logging.info(f'Extractor class {self.extractor.__class__}')
        self.processor = CommonProcessor(self)
        logging.info(f'Processor class {self.processor.__class__}')
        self.destination = None
        if 'destination' in self.project.keys():
            self.destination = get_destination_from_config(self.output, self.project['destination'])
            logging.info(f'Destination class {self.destination.__class__ if self.destination else "None"}')

    def collect(self, proceed=True):
        """Runs extractor engine and obtain data"""
        logging.info('Running extractor')
        if len(self.state.stages) > 0:
            stage = self.state.stages[-1]
            if stage['name'] == 'extractor' and stage['status'] == 'success':
                logging.info('Skip extractor stage')
                return
        try:
            self.extractor.run()
        except Exception as e:
            logging.error(f'Extractor failed: {e}')
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
                    logging.info(f'Processing {os.path.basename(filename)}')
                    source = get_source_from_file(filename, stype=stype, options=options)
                    try:
                        self.processor.run(source, self.destination, buffer_size=DEFAULT_BULK_RECORDS)
                        logging.info(f'Processing complete {os.path.basename(filename)}')
                        processed_files.append(filename)
                    except Exception as e:
                        logging.error(f'Failed to process {filename}: {e}')
                        failed_files.append({'filename': filename, 'error': str(e)})
                        # Continue with next file instead of failing completely
                    finally:
                        # Ensure source is closed after processing
                        if hasattr(source, 'close'):
                            try:
                                source.close()
                            except Exception as e:
                                logging.debug(f'Error closing source: {e}')
                except Exception as e:
                    logging.error(f'Error setting up source for {filename}: {e}')
                    failed_files.append({'filename': filename, 'error': str(e)})
                    continue
            
            # Summary
            if failed_files:
                logging.warning(f'Some files failed to process: {len(failed_files)}/{len(resources)}')
                for failed in failed_files[:5]:  # Show first 5 errors
                    logging.warning(f"  - {failed['filename']}: {failed['error']}")
                if len(failed_files) > 5:
                    logging.warning(f"  ... and {len(failed_files) - 5} more")
            else:
                logging.info(f'Successfully processed all {len(processed_files)} files')
        finally:
            # Ensure destination is closed to flush buffers and write file
            if self.destination is not None:
                try:
                    self.destination.close()
                    logging.info('Destination closed')
                except Exception as e:
                    logging.warning(f'Error closing destination: {e}')

    def finish(self):
        """Executed on end of the project. Ensures destination is closed"""
        # Ensure destination is closed if not already closed
        if self.destination is not None:
            try:
                self.destination.close()
                logging.info('Destination closed in finish()')
            except Exception as e:
                logging.warning(f'Error closing destination in finish(): {e}')
        logging.info(f"Finished project: {self.project['project-name']}")

    def run(self, pre_clean=False, init=True, proceed=True, structured_log=False):
        """Execute project"""
        self.enable_logging(console=True, tofile=True, structured=structured_log)
        if self.project is None:
            logging.error('Project file not found or not loaded')
            return
        isvalid, report = self.validate()        
        logging.info(f"Started project: {self.project['project-name']}")
        if not isvalid:
            logging.error('Invalid configuration. See more info below')
            if report:
                logging.error(f'Validation report: {report}')
            return 
        else:
            if init:
                self.__create_dirs()
            if pre_clean:
                self.clean()
            self.state = ProjectState(filename=self.state_file, reset=pre_clean, autosave=True)
            self.prepare()
            self.collect(proceed)
            self.process()
            self.finish()

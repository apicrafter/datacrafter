# -*- coding: utf-8 -*-
import errno
import logging

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import os
import glob
from ..extractors.base import BaseExtractor
from ..processors.base import CommonProcessor
from ..common.state import ProjectState
from ..sources import get_source_from_file
from ..destinations import get_destination_from_config


def load_config(filename):
    f = open(filename, 'r', encoding='utf8')
    data = yaml.load(f, Loader=Loader)
    f.close()
    return data


class Project:
    def __init__(self, project_path=None):
        """Init project class"""
        self.project = None
        self.project_path = os.getcwd() if project_path is None else project_path
        self.project_filename = os.path.join(self.project_path, 'datacrafter.yml')
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


        self.enable_logging()

    def enable_logging(self):
        """Enable logging to file and stderr"""
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        rootLogger = logging.getLogger()

        fileHandler = logging.FileHandler("{0}".format(self.logfile))
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)

    def __read_project_file(self, filename):
        """Reads project file content"""
        self.project = None
        if os.path.exists(self.project_filename):
            self.project = load_config(self.project_filename)
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), self.project_filename)

    def init(self):
        """Initialize project. Creates required dirs if they do not exists"""
        logging.info('Initialize project. Create required directories')
        # Create dirs if not exists
        for k in [
            self.current,
            self.output,
            self.temp,
            self.builds,
            self.storage,
        ]:
            try:
                os.makedirs(k)
            except Exception as e:
                logging.info("Directory %s can't be created" % (k))
                pass

    def log(self):
        # FIXME! Logging outside system logging
        pass

    def clean(self, basepath=None, clean_storage=False):
        logging.info('Clean project data. Clean storage: %s' % (str(clean_storage)))
        state_file = os.path.join(self.project_path, 'state.json')
        if os.path.exists(state_file):
            os.remove(state_file)
            logging.debug('Removed state file %s' % (state_file))

        for dirname, msg in [(self.output, 'output dir'), (self.current, 'current dir'), (self.temp, 'tempdir')]:
            logging.info('Cleaning %s' % (msg))
            filelist = glob.glob(os.path.join(self.project_path, dirname, "*.*"))
            for f in filelist:
                logging.debug('Remove %s from %s' % (f, basepath))
                os.remove(f)
        logging.info('Cleaning storage dir, if exists')
        if os.path.exists(os.path.join(self.project_path, "storage")) and clean_storage:
            filelist = glob.glob(os.path.join(self.project_path, "storage", "*.*"))
            for f in filelist:
                logging.debug('Remove %s from %s' % (f, basepath))
                os.remove(f)
        pass

    def validate(self):
        """Validates project file #FIXME returns always True for now"""
        return True, None

    #        raise NotImplemented

    def prepare(self):
        """Prepares everything"""
        logging.info('Preparing project extract, processor and destination')
        self.extractor = BaseExtractor(self)
        logging.info('Extractor class %s' % (str(self.extractor.__class__)))
        self.processor = CommonProcessor(self)
        logging.info('Processor class %s' % (str(self.processor.__class__)))
        self.destination = None
        if 'destination' in self.project.keys():
            self.destination = get_destination_from_config(self.output, self.project['destination'])
            logging.info('Destination class %s' % (str(self.destination.__class__) if self.destination else "None"))

    def collect(self, proceed=True):
        """Runs extractor engine and obtain data"""
        logging.info('Running extractor')
        if len(self.state.stages) > 0:
            stage = self.state.stages[-1]
            if stage['name'] == 'extractor' and stage['status'] == 'success':
                logging.info('Skip extractor stage')
                return
        self.extractor.run()

    def process(self):
        """Runs processors and stores result at the destination"""
        logging.info('Running processor')
        resources = self.state.data['stages'][-1]['results']
        options = {}
        stype = None
        for r in resources:
            if 'processor' in self.project.keys():
                if 'config' in self.project['processor'].keys():
                    options = self.project['processor']['config']
                    if 'type' in options.keys():
                        stype = options['type']
            logging.info('Processing ' + os.path.basename(r['filename']))
            self.processor.run(get_source_from_file(r['filename'], stype=stype, options=options), self.destination)
            logging.info('Processing complete ' + os.path.basename(r['filename']))
        pass

    def finish(self):
        """Executed on end of the project. Not implemented yet"""
        logging.info('Finished project: %s' % (self.project['project-name']))

    def run(self, pre_clean=False, init=True, proceed=True):
        """Execute project"""
        isvalid, report = self.validate()
        logging.info('Started project: %s' % (self.project['project-name']))
        if not isvalid:
            print('Invalid configuration. See more info below')
            print('%s' % (report))  # FIXME
        else:
            if init:
                self.init()
            if pre_clean:
                self.clean()
            self.state = ProjectState(filename=self.state_file, reset=pre_clean, autosave=True)
            self.prepare()
            self.collect(proceed)
            self.process()
            self.finish()

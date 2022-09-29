# -*- coding: utf8 -*-
import logging
from runpy import run_path

from ..common.mappers import map_keys, simple_typemap_object

DEBUG_ITERNUM = 5000


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

    def __init__(self, steps=None):
        if steps is None:
            steps = []
        self.steps = steps

    def add_step(self, step):
        """Add step to pipeline"""
        self.steps.append(step)

    def execute(self, record):
        """Executes pipiline steps"""
        n = 0
        for step in self.steps:
            n += 1
            record = step.apply(record)
        return record


class BaseProcessor:
    """Abstract class of the data processor"""

    def __init__(self, project):
        self.project = project

    #        self.destination = destination

    def process_record(self, record):
        """Processes single record of data"""
        return NotImplementedError

    def run(self, source, destination=None):
        """Execute data processing"""
        return NotImplementedError


DEFAULT_CONFIG_PARAMS = {'autoid': {'type': bool, 'default': True},
                         'skip_lines': {'type': int, 'default': None},
                         'autotype': {'type': bool, 'default': False},
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
        self.pipeline = DataPipeline()

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

    def process_record(self, record):
        """Processes single record of data"""
        return self.pipeline.execute(record)

    def run(self, source, destination=None, buffer_size=None):
        """Run processor"""
        itern = 0
        if buffer_size is not None and buffer_size > 0:
            records = []
            n = 0
            for raw_rec in source:
                itern += 1
                if itern % DEBUG_ITERNUM == 0:
                    logging.debug('Processed %d records' % (itern))
                n += 1
                records.append(self.process_record(raw_rec))
                if n == buffer_size:
                    destination.write_bulk(records)
                    n = 0
                    records = []
            if len(records) > 0:
                destination.write_bulk(records)
        else:
            for raw_rec in source:
                itern += 1
                if itern % DEBUG_ITERNUM == 0:
                    logging.debug('Processed %d records' % (itern))
                p_rec = self.process_record(raw_rec)
                destination.write(p_rec)
        status = 'success'
#        self.project.state.add('processor', status=status, results=self.results)

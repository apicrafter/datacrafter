import logging
import os
import shutil
import tempfile
import time
from functools import wraps
from urllib import parse

import requests
from bs4 import BeautifulSoup

REQUEST_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Mobile Safari/537.36'}
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
DEFAULT_CHUNK_SIZE = 4096
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_RETRY_BACKOFF = 2.0


def retry_network_operation(max_retries=DEFAULT_MAX_RETRIES, delay=DEFAULT_RETRY_DELAY, backoff=DEFAULT_RETRY_BACKOFF):
    """Decorator for retrying network operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, requests.exceptions.Timeout, 
                        requests.exceptions.ConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (backoff ** attempt)
                        logging.warning(f"Network operation failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time:.2f}s...")
                        time.sleep(wait_time)
                    else:
                        logging.error(f"Network operation failed after {max_retries} attempts: {e}")
            raise last_exception
        return wrapper
    return decorator


@retry_network_operation(max_retries=DEFAULT_MAX_RETRIES)
def get_file(url, filename, aria2=False, aria2path=None, timeout=DEFAULT_TIMEOUT):
    """Download file from URL with proper error handling and retry logic"""
    logging.info(f'Retrieving {filename} from {url}')
    page = None
    try:
        page = requests.get(url, headers=REQUEST_HEADER, stream=True, verify=False, timeout=timeout)
        page.raise_for_status()  # Raise exception for bad status codes
        if not aria2:
            with open(filename, 'wb') as f:
                total = 0
                chunk = 0
                for line in page.iter_content(chunk_size=DEFAULT_CHUNK_SIZE):
                    chunk += 1
                    if line:
                        f.write(line)
                    total += len(line)
                    if chunk % 1000 == 0:
                        logging.debug(f'File {filename} to size {total}')
        else:
            dirpath = os.path.dirname(filename)
            basename = os.path.basename(filename)
            if len(dirpath) > 0:
                s = f"{aria2path} --retry-wait=10 -d {dirpath} --out={basename} {url}"
            else:
                s = f"{aria2path} --retry-wait=10 --out={basename} {url}"
            logging.info(f'Aria2 command line: {s}')
            os.system(s)
        return filename
    except requests.exceptions.RequestException as e:
        error_msg = f'Failed to download {url}: {e}'
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f' (Status: {e.response.status_code})'
        logging.error(error_msg)
        raise
    finally:
        # Ensure response is closed
        if page is not None and hasattr(page, 'close'):
            page.close()


def is_absolute_url(url):
    return bool(parse.urlparse(url).netloc)


@retry_network_operation(max_retries=DEFAULT_MAX_RETRIES)
def _fetch_url_content(url, timeout=DEFAULT_TIMEOUT):
    """Helper function to fetch URL content with retry logic"""
    session = requests.Session()
    try:
        session.headers.update({'User-Agent': DEFAULT_USER_AGENT})
        response = session.get(url, verify=False, timeout=timeout)
        response.raise_for_status()
        return response.content
    finally:
        session.close()


def get_file_by_pattern(current_path, temp_path, url, url_data_prefix, filename, file_type=None, aria2=False,
                        aria2path=None, force=True, timeout=DEFAULT_TIMEOUT):
    """Collects specific file by it's url pattern and saves it as filename"""
    shift = len(file_type) + 1
    try:
        html_data = _fetch_url_content(url, timeout=timeout)
        soup = BeautifulSoup(html_data, features='lxml')
        data_url = None
        for u in soup.find_all('a'):
            href = u.get('href')
            if href and href.find(url_data_prefix) > -1:
                if file_type is not None and href[-shift:] == f'.{file_type}':
                    data_url = u.get('href')
                    if not is_absolute_url(data_url):
                        data_url = parse.urljoin(url, data_url)
                    break
        if not data_url:
            logging.info('Dataset url not found')
            return None
        else:
            if not os.path.exists(filename) or force:
                get_file(data_url, filename, aria2=aria2, aria2path=aria2path, timeout=timeout)
                logging.info(f'Downloaded {data_url} to {filename}')
            else:
                logging.info(f'File {filename} already downloaded')

            return filename
    except requests.exceptions.RequestException as e:
        error_msg = f'Failed to fetch URL {url}: {e}'
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f' (Status: {e.response.status_code})'
        logging.error(error_msg)
        raise


def get_file_by_name(current_path, temp_path, url, name=None, prefix=None, file_prefix=None, file_type=None,
                     aria2=False, aria2path=None, force=True):
    """Collects specific file by it's name"""
    temp_filepath = None
    try:
        html_data = _fetch_url_content(url)
        soup = BeautifulSoup(html_data, features='lxml')
        data_url = None
        for u in soup.find_all('a'):
            if name:
                if u.text == name:
                    data_url = u.get('href')
                    break
            elif prefix:
                if u.text.find(prefix) > -1:
                    data_url = u.get('href')
                    break
        if not data_url:
            logging.info('Dataset url not found')
            return None
        else:
            if not is_absolute_url(data_url):
                data_url = parse.urljoin(url, data_url)
            filename = data_url.rsplit('/', 1)[-1]
            logging.info(f'Downloading {data_url} to {filename}')
            fd, temp_filepath = tempfile.mkstemp()
            os.close(fd)
            current_filepath = os.path.join(current_path, f"{file_prefix}_current.{file_type}")
            logging.info(f'Temp {temp_filepath}')
            if not os.path.exists(temp_filepath) or force:
                get_file(data_url, temp_filepath, aria2=aria2, aria2path=aria2path)
                logging.info(f'Downloaded {data_url} to {filename}')
            else:
                logging.info(f'File {filename} already downloaded')
            shutil.move(temp_filepath, current_filepath)
            logging.debug(f'File {filename} moved to current')
            return current_filepath
    except requests.exceptions.RequestException as e:
        error_msg = f'Failed to fetch URL {url}: {e}'
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f' (Status: {e.response.status_code})'
        logging.error(error_msg)
        raise
    except Exception as e:
        # Clean up temp file on error
        if temp_filepath and os.path.exists(temp_filepath):
            try:
                os.unlink(temp_filepath)
                logging.debug(f'Cleaned up temp file: {temp_filepath}')
            except OSError as cleanup_err:
                logging.warning(f'Failed to clean up temp file {temp_filepath}: {cleanup_err}')
        raise

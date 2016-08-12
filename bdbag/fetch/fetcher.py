import os
import sys
import logging
from bdbag.fetch.transports import *
from bdbag.fetch.auth.keychain import *

if sys.version_info > (3,):
    from urllib.parse import urlsplit
else:
    from urlparse import urlsplit

logger = logging.getLogger(__name__)

UNIMPLEMENTED = "Transfer protocol \"%s\" is not supported by this implementation"

SCHEME_HTTP = 'http'
SCHEME_HTTPS = 'https'
SCHEME_GLOBUS = 'globus'
SCHEME_FTP = 'ftp'
SCHEME_SFTP = 'sftp'
SCHEME_ARK = 'ark'
SCHEME_TAG = 'tag'


def fetch_bag_files(bag, keychain_file):

    success = True
    auth = read_keychain(keychain_file)
    for url, size, path in bag.fetch_entries():
        output_path = os.path.normpath(os.path.join(bag.path, path))
        success = fetch_file(url, size, output_path, auth)
    return success


def fetch_file(url, size, path, auth):

    scheme = urlsplit(url, allow_fragments=True).scheme.lower()
    if SCHEME_HTTP == scheme or SCHEME_HTTPS == scheme:
        return fetch_http.get_file(url, path, auth)
    elif SCHEME_GLOBUS == scheme:
        return fetch_globus.get_file(url, path, auth)
    elif SCHEME_ARK == scheme:
        for url in fetch_ark.resolve(url):
            if fetch_file(url, size, path, auth):
                return True
        return False
    elif SCHEME_TAG == scheme:
        logger.info("The fetch entry for file %s specifies the tag URL %s. Tag URLs generally represent files that are "
                    "not directly addressable by URL and therefore cannot be automatically fetched. Such files must be "
                    "resolved outside of the context of this software." % (path, url))
        return True
    else:
        logger.warning(UNIMPLEMENTED % scheme)
        return False

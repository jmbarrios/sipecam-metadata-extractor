import os
import warnings
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.expanduser('~'), '.simex_env')

if os.path.isfile(dotenv_path):
    load_dotenv(dotenv_path)
else:
    warnings.warn('No configuration file found in %s, some functionalities won\'t be available' % dotenv_path)


SIPECAM_ZENDRO_GQL_URL      = os.environ.get("SIPECAM_ZENDRO_GQL_URL", "")
SIPECAM_ZENDRO_GQL_USER     = os.environ.get("SIPECAM_ZENDRO_GQL_USER", "")
SIPECAM_ZENDRO_GQL_PASSWORD = os.environ.get("SIPECAM_ZENDRO_GQL_PASSWORD", "")

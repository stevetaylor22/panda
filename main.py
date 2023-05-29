import connexion
import sys

from datastore import set_data_store
from orm import AlchemyDatastore


def get_port() -> int:
    if len(sys.argv) != 2:
        return 8090
    try:
        return int(sys.argv[1])
    except ValueError:
        return 8090


if __name__ == '__main__':
    # Application DataStore Initialisation
    # Modify DB_URL to use different DB
    # See: https://docs.sqlalchemy.org/en/20/core/engines.html
    DB_URL = 'sqlite:///PANDA.db'
    dataStore = AlchemyDatastore(DB_URL)
    set_data_store(dataStore)

    # This is just using the test server included with connexion
    # In production an industrial-strength WSGI server would be used
    app = connexion.App(__name__, specification_dir='apidef/')
    app.add_api('patient-app.yml')
    app.run(port=get_port())

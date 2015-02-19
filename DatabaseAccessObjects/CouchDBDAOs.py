import couchdb


class CouchDAO:
    """
    Handles all connections to and operations upon couchdb databases.
    This generally should not be called directly. Rather it should be instantiated
    in a service class which handles the specific operations.

    Attributes:
        server: The connection the server
        db: The connection to the database
        ids: List containing all ids of records in the database after get_all_ids called
    """

    def __init__(self, server='http://localhost:5984'):
        self.server = couchdb.Server(server)

    def connect(self, database_name):
        """
        Connects to couchdb database

        Args:
            database_name: String name of the database to connect to
        """
        try:
            self.db = self.server.create(database_name)
        except couchdb.http.PreconditionFailed, e:
            self.db = self.server[database_name]
        return self.db

    def _check_connected(self):
        """
        Checks whether have connected to couchdb, if not, sends message

        Returns:
            Boolean indicating whether connected
        """
        if not self.db:
            print "No db connection. Please call CouchDAO.connect() first"
            return False
        else:
            return True

    def save(self, document):
        """
        Saves document to connected database

        Args:
            document: Document to save to couch db
        """
        try:
            if self._check_connected():
                self.db.save(document)
        except Exception as e:
            print e

    def query(self, query_string):
        """
        Run query on couch db
        Args:
            query_string: String query to run
        Returns:
            Dictionary result of query
        """
        try:
            if self._check_connected():
                return self.db.query(query_string)
        except Exception as e:
            print e

    def get_view(self, view_name):
        """
        Wraps couchdb.view

        Args:
            view_name: String name of the view whose contents to return (e.g., 'indexpy/maxid')
        """
        return self.db.view(view_name)

    def get_all_ids(self):
        """
        Gets all documentids from db; ignores the _design/index file
        """
        q = []
        for id in self.db:
            q.append(id)
        self.ids = []
        [self.ids.append(i) for i in q if i != '_design/index']  # First id returned is the design document
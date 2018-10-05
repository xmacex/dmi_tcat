import requests
import logging


class Tcat():
    """A class to represent a TCAT instance."""

    _headers = {'accept': 'application/json'}

    def __init__(self, url, username, password, loadbins=False):
        """Constructor."""
        self.endpoint = f'{url}/api/'
        self.auth = (username, password)
        self.logger = logging.getLogger('tcat')
        self._binnames = None
        self._bins = {}

        try:
            self._handshake()
            if loadbins:
                self.load_all_bins()
        except requests.exceptions.HTTPError:
            raise

    def _handshake(self):
        """Utility to check connection with TCAT instance."""
        requests.get(self.endpoint, auth=self.auth,
                     headers=type(self)._headers).raise_for_status()

    def _query(self, action, param=None):
        """Utility to request query bins."""
        url = f'{self.endpoint}{action}'
        if param:
            url = f'{url}/{param}'

        resp = requests.get(url, auth=self.auth,
                            headers=type(self)._headers)
        resp.raise_for_status()
        data = resp.json()
        del(data['original_request'])
        return data

    def bins(self):
        """List the bins in this TCAT."""
        if not self._binnames:
            self.logger.debug('Refreshing bins')
            self._binnames = list(self._query('querybin.php').values())
        return self._binnames

    def get_bin(self, binname):
        """Get information about a particular bin."""
        self.logger.debug(f'Getting bin {bin}')
        try:
            return self._bins[binname]
        except KeyError:
            # self._bins[binname] = self._query('querybin.php', binname)
            data = self._query('querybin.php', binname)
            self._bins[binname] = QueryBin(data)
            return self._bins[binname]

    def load_all_bins(self):
        """Ask the instance to fetch and get cache all bins"""
        try:
            self._handshake()
            for qbin in self.bins():
                self.get_bin(qbin)
        except requests.exceptions.HTTPError:
            raise

    def notweets(self, binname, startdate, enddate):
        """Get the number of tweets in this bin."""
        raise NotImplementedError

    def tweets(self, binname, startdate, enddate, format='csv'):
        """Export tweets in CSV of TSV format."""
        raise NotImplementedError

    def purge(self):
        """Delete tweets from the selected time period."""
        raise NotImplementedError


class QueryBin():
    """Class to represent a query bin."""
    def __init__(self, data):
        """Constructor."""
        self.bin = data['bin']
        self.type = data['type']
        self.active = data['active']
        self.comments = data['comments']
        self.notweets = int(data['notweets'])
        self.maxtime = data['maxtime']
        self.mintime = data['mintime']
        self.nohashtags = int(data['nohashtags'])
        self.nomentions = int(data['nomentions'])
        self.keywords = [kw.strip() for kw in data['keywords'].split(',')]

    def __repr__(self):
        return f"<type(self)> {self.bin}"

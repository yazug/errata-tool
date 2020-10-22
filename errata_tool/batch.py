from errata_tool import ErrataConnector
from errata_tool import Erratum


class Batch(ErrataConnector):
    """Search ET for Details based on a batch"""

    def __init__(self, batch_name_or_id):
        """Find batch details by batch name or batch_id

        :param batch_name_or_id: batch name or batch_id from ET
        """
        self._fetch(batch_name_or_id)

    def _fetch(self, batch_name_or_id):
        """Fetch batch data from Errata Tool API and store to properties"""

        args = {}
        if batch_name_or_id is None or batch_name_or_id == '':
            self._data = self._get('/api/v1/batches')
        else:
            try:
                args['id'] = int(batch_name_or_id)
            except ValueError:
                args['name'] = batch_name_or_id

            self._data = self.get_filter('/api/v1/batches', 'filter', **args)

        self._batch = {}
        self._batch_list = []
        if self._data and 'data' in self._data:

            self._batch_list = self._data['data']

            for entry in self._batch_list:
                batch_id = entry['id']
                batch_data = {
                    'id': batch_id,
                    'batch_name': entry['attributes']['name'],
                    'description': entry['attributes']['description'],
                    'release_date': entry['attributes']['release_date'],
                    'release_name': entry['relationships']['release']['name'],
                    'errata_id_list': [],
                }
                errata_list = entry['relationships']['errata']
                batch_data['errata_id_list'] = [e['id'] for e in errata_list]

                self._batch[batch_id] = batch_data
            print(self._batch_list)
            print(self._batch)

    @property
    def all_batch_ids(self):
        """retrieve matching batch(es) as dict from search"""
        return list(self._batch.keys())

    @property
    def all_errata_ids(self):
        """List of all Errata IDs from batch_search

        :return: list of Errata ids
        """
        return self._batch

    @property
    def all_errata(self):
        """List of all Erratas from batch search

        :return: list of Errata objects
        """

        if self._all_errata is None:
            self._all_errata = {}

        for batch_id in self._batch.keys():
            if batch_id not in self._all_errata:
                self._all_errata[batch_id] = []
                for errata_id in self._batch[batch_id]['errata_id_list']:
                    errata = Erratum(errata_id=errata_id)
                    self._all_errata[batch_id].append(errata)

        return self._all_errata[batch_id]

    def __getattr__(self, name):
        return self._data.get(name)

    def __repr__(self):

        return 'batch(%s)' % str([b for b in self._batch.keys()])

    def __str__(self):
        """Convert batch object to string representation

        :return: batch info string
        """
        output = str(self._data)

        return output

import json

from . import _errors


__all__ = ('Client',)


class Client:

    _base_uri = 'https://api.mindee.net/v1/products'

    __slots__ = ('_session', '_token')

    def __init__(self, session, token):

        self._session = session

        self._token = token

    @property
    def _default_headers(self):

        return {
            'Authorization': f'Token {self._token}'
        }

    def _request(self,
                 verb, path,
                 query = None, body = None, data = None, headers = None):

        uri = self._base_uri + path

        headers = self._default_headers | (headers or {})

        response = self._session.request(
            verb, uri,
            params = query, json = body, data = data, headers = headers
        )

        try:
            data = response.json()
        except json.JSONDecodeError:
            data = None

        if not response.status_code < 400:
            nrm =  response.status_code < 500
            cls = _errors.ApiError if nrm else _errors.HttpError
            raise cls(response, data)

        return data

    _versions = {
        'invoices': 'v3',
        'passport': 'v1',
    }

    _name_glossary = {
        'invoice': 'invoices'
    }

    _account = 'mindee'

    def request(self,
                verb, name, path,
                query = {}, body = None, data = None, **kwargs):

        name = self._name_glossary.get(name, name)

        version = self._versions[name]

        path = f'/{self._account}/{name}/{version}' + path

        data = self._request(
            verb, path,
            query = query, body = body, data = data, **kwargs
        )

        resources = [data[name] for name in data['api_request']['resources']]

        return resources

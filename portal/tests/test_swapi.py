import requests
import unittest
from unittest import mock
import json

from portal import swapi


class TestSwApi(unittest.TestCase):
    """Test SWAPI requests module"""

    def setUp(self):
        self._swapi = swapi.SWAPI()

    @staticmethod
    def _mock_request_response_prepare(
            resp_status_code=200,
            resp_text='resp_text',
            raise_exception_req=None,
            raise_exception_json=None):
        """Prepare mock for requests.get for latter use

        Possibility to prepare requests.get method mock object with
        different settings:
        - Raise error on requests.get call
        - Raise error during response json parsing
        - Return different response HTTP status codes and response
            texts

        :param resp_status_code: response status code for
            requests.get method
        :type resp_status_code: int
        :param resp_text: response text for requests.get method
        :type resp_text: str
        :param raise_exception_req: Simulate raising given exception
            during requests.get call
        :type raise_exception_req: Exception, optional
        :param raise_exception_json: Simulate raising given exception
            during processing JSON response
        :type raise_exception_json: Exception, optional
        """

        requests.get = mock.Mock()
        if raise_exception_req:
            requests.get.side_effect = raise_exception_req
            return
        response = mock.Mock()
        response.url = 'testing_url'
        response.status_code = resp_status_code
        response.text = resp_text
        requests.get.return_value = response
        response.json = mock.Mock()
        response.json.return_value = {}
        if raise_exception_json:
            response.json.side_effect = raise_exception_json

    def test_request_500(self):
        """_swapi_request method test

        Test for SWAPI HTTP 500 response.
        None must be returned.
        """

        self._mock_request_response_prepare(resp_status_code=500)
        result = self._swapi._swapi_request('testing_url')
        self.assertEquals(result, None)

    def test_request_exception_connection_error(self):
        """_swapi_request method test

        Test for connection error exception during SWAPI call.
        None must be returned.
        """

        self._mock_request_response_prepare(
            raise_exception_req=requests.ConnectionError(
                'Test connection error'))
        result = self._swapi._swapi_request('testing_url')
        self.assertEquals(result, None)

    def test_request_exception_timeout(self):
        """_swapi_request method test

        Test for timeout exception during SWAPI call.
        None must be returned.
        """

        self._mock_request_response_prepare(
            raise_exception_req=requests.Timeout('Test timeout error'))
        result = self._swapi._swapi_request('testing_url')
        self.assertEquals(result, None)

    def test_request_exception_other(self):
        """_swapi_request method test

        Test for other / general exception during SWAPI call.
        None must be returned.
        """

        self._mock_request_response_prepare(
            raise_exception_req=requests.exceptions.SSLError('Test other error'))
        result = self._swapi._swapi_request('testing_url')
        self.assertEquals(result, None)

    def test_request_no_response_text(self):
        """_swapi_request method test

        There is no text in response body.
        None must be returned.
        """

        self._mock_request_response_prepare(resp_text='')
        result = self._swapi._swapi_request('testing_url')
        self.assertEquals(result, None)

    def test_request_incorrect_json(self):
        """_swapi_request method test

        Exception during response json processing.
        None must be returned.
        """

        self._mock_request_response_prepare(
            raise_exception_json=json.decoder.JSONDecodeError(
                'Can not decode JSON', '', 0))
        result = self._swapi._swapi_request('testing_url')
        self.assertEquals(result, None)

    def test_request_correct_response(self):
        """_swapi_request method test

        Correct response:
        - HTTP 200
        - Text in response which might be converted from json
        Dictionary must be returned.
        """

        self._mock_request_response_prepare()
        result = self._swapi._swapi_request('testing_url')
        self.assertEquals(result, {})

    def test_list_request_process(self):
        """_list_request_process method test

        There are 3 calls to SWAPI. The last one finishes the loop:
        There is no other `next` page.
        Concatenated array must be returned.
        """

        self._swapi._swapi_request = mock.Mock()
        self._swapi._swapi_request.side_effect = [
            {'results': [1], 'next': 'url_next_page'},
            {'results': [2], 'next': 'url_next_page'},
            {'results': [3], 'next': None}
        ]
        result = self._swapi._list_request_process('testing_url')
        self.assertEquals(result, [1, 2, 3])

    def test_list_request_error_result(self):
        """_list_request_process method test

        There was some error during second SWAPI request
        None must be returned.
        """

        self._swapi._swapi_request = mock.Mock()
        self._swapi._swapi_request.side_effect = [
            {'results': [1], 'next': 'url_next_page'},
            None,
            {'results': [3], 'next': None}
        ]
        result = self._swapi._list_request_process('testing_url')
        self.assertEquals(result, None)

    def test_list_request_inconsistent_result(self):
        """_list_request_process method test

        There was inconsistent result returned from second SWAPI
        request: No `result` field.
        None must be returned.
        """

        self._swapi._swapi_request = mock.Mock()
        self._swapi._swapi_request.side_effect = [
            {'results': [1], 'next': 'url_next_page'},
            {'next': None},
            {'results': [3], 'next': None}
        ]
        result = self._swapi._list_request_process('testing_url')
        self.assertEquals(result, None)

    def test_list_request_inconsistent_result_2(self):
        """_list_request_process method test

        There was inconsistent result returned from second SWAPI
        request: No `next` field.
        None must be returned.
        """

        self._swapi._swapi_request = mock.Mock()
        self._swapi._swapi_request.side_effect = [
            {'results': [1], 'next': 'url_next_page'},
            {'results': [2]},
            {'results': [3], 'next': None}
        ]
        result = self._swapi._list_request_process('testing_url')
        self.assertEquals(result, None)

    def test_people_get(self):
        """people_get method test

        Test:
        - if right url is used during _list_request_process call
        - if the method is returning result from
            _list_request_process method
        """

        self._swapi._list_request_process = mock.Mock()
        self._swapi._list_request_process.return_value = 'TEST'

        response = self._swapi.people_get()
        self._swapi._list_request_process.assert_called_once_with(
            self._swapi.url_people)
        self.assertEquals(response, 'TEST')

    def test_planets_get(self):
        """planets_get method test

        Test:
        - if right url is used during _list_request_process call
        - if the method is returning result from
            _list_request_process method
        """

        self._swapi._list_request_process = mock.Mock()
        self._swapi._list_request_process.return_value = 'TEST'

        response = self._swapi.planets_get()
        self._swapi._list_request_process.assert_called_once_with(
            self._swapi.url_planets)
        self.assertEquals(response, 'TEST')

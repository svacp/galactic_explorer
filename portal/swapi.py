import requests
import urllib.parse
import logging
from typing import Optional

log = logging.getLogger('portal')


class SWAPI(object):
    """Process Star Wars API requests

    :cvar HOST: Host of Star Wars API
    :cvar RESOURCE_PEOPLE: people resource url
    :cvar RESOURCE_PLANETS: planets resource url
    :cvar REQUEST_TIMEOUT: Maximum request timeout.
        After this time, TimeOut error is raised
    """

    HOST = 'https://swapi.dev/api/'
    RESOURCE_PEOPLE = 'people'
    RESOURCE_PLANETS = 'planets'
    REQUEST_TIMEOUT = 10

    @property
    def url_people(self):
        """Property for easier testing"""

        return urllib.parse.urljoin(self.HOST, self.RESOURCE_PEOPLE)

    @property
    def url_planets(self):
        """Property for easier testing"""

        return urllib.parse.urljoin(self.HOST, self.RESOURCE_PLANETS)

    def people_get(self) -> Optional[list]:
        """Get list of person objects

        :return: List of dicts representing SW character data.
            In case of error, returns None
        :rtype: list, optional
        """

        return self._list_request_process(self.url_people)

    def planets_get(self) -> Optional[list]:
        """Get list of planet objects

        :return: List of dicts representing SW planet data.
            In case of error, returns None
        :rtype: list, optional
        """

        return self._list_request_process(self.url_planets)

    def _list_request_process(self, url: str) -> Optional[list]:
        """Process list requests: These are request which returns
        list of objects in pageable form.

        Attributes of SWAPI list response:
            - count: Overall count of result resources
            - next: None or URL of next page
            - previous: None or URL of previous page
            - results: Array of result resources

        :param url: API endpoint URL
        :type url: str
        :return: List of result objects. In case of error, returns None
        :rtype: list, optional
        """

        results = []
        while True:
            response = self._swapi_request(url)
            if not response:
                return
            results_partial = response.get('results')
            if not results_partial:
                log.error('Inconsistent response: \'results\' not present '
                          'within response')
                return
            results.extend(results_partial)
            if 'next' not in response:
                log.error('Inconsistent response: \'next\' not present within '
                          'response')
                return
            next_page = response['next']
            if next_page is None:
                break
            url = next_page
        return results

    def _swapi_request(self, url: str) -> Optional[dict]:
        """Process single Star Wars API request.

        Processing:
            - Send a request
            - Process error states
            - Log the processing

        :param url: API endpoint URL
        :type url: str
        :return: dict object representing result value.
            In case of error, returns None
        :rtype: dict, optional
        """

        log.info('Sending SWAPI request ...')
        try:
            r = requests.get(url, timeout=self.REQUEST_TIMEOUT)
        except requests.ConnectionError as e:
            log.error('Connection error: %s', e)
            return
        except requests.Timeout:
            log.error('Request timeout')
            return
        except Exception as e:
            log.error('%s', e)
            return

        log.info('URL = %s', r.url)
        if r.status_code != 200:
            log.error('[%s] Error %s', r.status_code,
                      ' : %s' % r.text if r.text else '')
            return
        log.info('[200] %s', r.text)
        if not r.text:
            log.info('Incorrect API response')
            return
        try:
            result_dict = r.json()
            return result_dict
        except Exception as e:
            log.error('Error parsing response: %s', e)
            return



import unittest
import requests
from os import environ
from os.path import dirname, join
from time import sleep
from googleprint.client import (
    delete_job,
    get_job,
    list_jobs,
    list_printers,
    get_printer,
    submit_job,
)
from googleprint.auth import OAuth2


PRINTER_ID = environ.get('CP_PRINTER_ID', '__google__docs')
PDF = join(dirname(__file__), 'test.pdf')

auth = OAuth2(
    client_id=environ['CP_CLIENT_ID'],
    client_secret=environ['CP_CLIENT_SECRET'],
    refresh_token=environ['CP_REFRESH_TOKEN']
)


class UnitTests(unittest.TestCase):
    def test_oauth2_requires_argument_sets(self):
        OAuth2(access_token='foo', token_type='bar')
        OAuth2(client_id='foo', client_secret='bar', refresh_token='baz')

    def test_listing_printers(self):
        printers = list_printers(auth=auth)['printers']
        self.assertIsInstance(printers, list)

    def test_get_printer(self):
        printer = get_printer(printer_id=PRINTER_ID, auth=auth)
        self.assertIsInstance(printer, dict)

    def test_print_pdf(self):
        job = submit_job(PRINTER_ID, PDF, auth=auth)['job']
        self.assertIsInstance(job, dict)

        timeout = 30
        delay = 5
        attempts = range(int(timeout / delay) + 1)

        try:
            latest = None
            for i in attempts:
                if i > 0:
                    sleep(delay)
                latest = get_job(job_id=job['id'], auth=auth)
                if latest['status'] == 'DONE':
                    break
            else:
                self.fail("Job got stuck on '{0}'".format(latest['status']))
        finally:
            self.assertTrue(delete_job(job['id'], auth=auth)['success'])

    def test_response_is_returned_on_remote_failures(self):
        with self.assertRaises(requests.RequestException):
            _ = submit_job('bogus', PDF)

        with self.assertRaises(requests.RequestException):
            _ = delete_job('bogus')

        with self.assertRaises(requests.RequestException):
            _ = list_jobs()


def main():
    unittest.main()


if __name__ == '__main__':
    main()

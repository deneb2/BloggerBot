import mock
import json
import unittest
import requests

import utils
from exceptions import MetadataException

class DataResponse():
    def __init__(self, content, status):
        self.content = content
        self.status_code = status


class MockResponse():
    def __init__(self, c, s):
        self.dr = DataResponse(c, s)

    def get(self, url):
        return self.dr


class TestFetcher(unittest.TestCase):
    def setUp(self):
        self.input_data = []
        with open('test/data/metadata.json') as data:
            for line in data:
                if (line.startswith('#') 
                    or not len(line.strip())):
                    continue
                self.input_data.append(json.loads(line.strip()))

    @mock.patch("utils.requests.get")
    def test_fetcher(self, session):
        for test_data in self.input_data:
            mr = MockResponse(test_data.get('html'), test_data.get('status'))
            session.return_value = mr.get(test_data.get('url'))
            test_metadata = test_data.get('metadata')
            metadata = utils.Metadata({})
            try:
                metadata.get_metadata(test_data.get('url'))
            except MetadataException:
                self.assertEqual(metadata.url, test_metadata.get('url', ''))
                self.assertEqual(metadata.title, test_metadata.get('title', ''))
                continue

            self.assertEqual(metadata.url, test_metadata.get('url', ''))
            self.assertEqual(metadata.title, test_metadata.get('title', ''))
            self.assertEqual(metadata.keywords, test_metadata.get('keywords', ''))
            self.assertEqual(metadata.top_image, test_metadata.get('top_image', ''))
            self.assertEqual(metadata.description, test_metadata.get('description', ''))
            # testing to json function
            json_obj = json.loads(metadata.to_json())
            self.assertEqual(json_obj.get('url'), test_metadata.get('url', ''))
            self.assertEqual(json_obj.get('title'), test_metadata.get('title', ''))
            self.assertEqual(json_obj.get('keywords'), test_metadata.get('keywords', ''))
            self.assertEqual(json_obj.get('top_image'), test_metadata.get('top_image', ''))
            self.assertEqual(json_obj.get('description'), test_metadata.get('description', ''))

    def test_extract_url(self):
        inputs = [
            '',
            'this is a message',
            'message with url http://ciao.it',
            'https://thiisaurl.it/ops',
            'and some param https://ciao.it/log?ppo=4&somthing=4 and some text',
        ]
        outputs = [
            None,
            None,
            'http://ciao.it',
            'https://thiisaurl.it/ops',
            'https://ciao.it/log?ppo=4&somthing=4',
        ]
        for index, inp in enumerate(inputs):
            self.assertEqual(utils.extract_url(inp), outputs[index])

if __name__ == '__main__':
    unittest.main()

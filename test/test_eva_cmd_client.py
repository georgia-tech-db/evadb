
import unittest
import mock
import sys


class CMDClientTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @mock.patch('eva.eva_cmd_client.eva_client')
    def test_main(self, mock_client):
        from eva.eva_cmd_client import main
        with mock.patch.object(sys, 'argv', ['test']):
            main()
        mock_client.called_once_with('0.0.0.0', 5432)

    def test_parse_args(self):
        from eva.eva_cmd_client import parse_args
        args = parse_args(['-P', '2345', '-H', 'test'])
        self.assertEqual(args.host, 'test')
        self.assertEqual(args.port, 2345)

    @mock.patch('eva.server.interpreter.start_cmd_client')
    def test_eva_client(self, mock_client):
        from eva.eva_cmd_client import eva_client
        eva_client()
        mock_client.assert_called_once()

import os
import subprocess
import unittest
from pathlib import Path
from test.util import get_evadb_for_testing, shutdown_ray


class URLSummaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()
        os.environ["ray"] = str(cls.evadb.config.get_value("experimental", "ray"))

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self) -> None:
        shutdown_ray()

    def test_should_run_url_summary_app(self):
        app_path = Path("apps", "url_summary", "url_summary.py")
        input1 = "\n\n"  # Summarize the default url.
        # Assuming that OPENAI_KEY is already set as an environment variable
        inputs = input1
        command = ["python", app_path]

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate(inputs.encode())

        decoded_stdout = stdout.decode()
        assert "Passkeys" or "AliExpress" or "Rate limit" in decoded_stdout
        print(decoded_stdout)
        print(stderr.decode())
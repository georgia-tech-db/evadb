from pathlib import Path
import tempfile
import unittest

from eva.configuration.bootstrap_environment import bootstrap_environment
from eva.configuration.dictionary import EVA_CONFIG_FILE, EVA_INSTALLATION_DIR


class BootstrapEnvironmentTests(unittest.TestCase):
    def test_bootstrap_environment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            bootstrap_environment(temp_dir_path, EVA_INSTALLATION_DIR)

            config_path = temp_dir_path / EVA_CONFIG_FILE
            assert config_path.exists()

            udfs_dir = temp_dir_path / "udfs"
            assert udfs_dir.exists()

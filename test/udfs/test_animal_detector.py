import unittest


class TestAnimalDetector(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    @unittest.skip("disable test due to model downloading time")
    def test_setup(self):
        import os
        from eva.udfs.camera_trap_animal_detector import AnimalDetector
        from eva.configuration.constants import EVA_DEFAULT_DIR

        model = AnimalDetector()
        output_directory = os.path.join(EVA_DEFAULT_DIR, "udfs", "models")
        base_module_arc_path = os.path.join(output_directory, "base_module_arc_blank")
        base_module_ckt_path = os.path.join(output_directory, "base_module_blank.pt")
        classifier_ckt_path = os.path.join(output_directory, "classifier_blank.pt")
        base_module_arc_downloaded = os.path.exists(base_module_arc_path)
        base_module_ckt_downloaded = os.path.exists(base_module_ckt_path)
        classifier_ckt_downloaded = os.path.exists(classifier_ckt_path)
        self.assertEqual(base_module_arc_downloaded, True)
        self.assertEqual(base_module_ckt_downloaded, True)
        self.assertEqual(classifier_ckt_downloaded, True)
    
    @unittest.skip("no need to test this for eva")
    def test_can_download_udf_code(self):
        import os
        import subprocess
        import eva
        from pathlib import Path
        # test for workflow in ipynb, which has nothing to do with eva project itself
        subprocess.run(["wget", "-nc", "https://raw.githubusercontent.com/sashiko-345/eva/master/eva/udfs/camera_trap_animal_detector.py"])
        path = os.getcwd()
        path += "/camera_trap_animal_detector.py"
        self.assertTrue(os.path.exists(path))

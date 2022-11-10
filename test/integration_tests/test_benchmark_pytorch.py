import pytest
import sys

import mock
import pytest

from eva.server.command_handler import execute_query_fetch_all


@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False,
    warmup_iterations=1,
    min_rounds=1,
)
def test_should_run_pytorch_and_fastrcnn(benchmark, setup_pytorch_tests):
    select_query = """SELECT FastRCNNObjectDetector(data) FROM MyVideo
                    WHERE id < 5;"""            
    actual_batch = benchmark(execute_query_fetch_all, select_query)
    assert(len(actual_batch)==5)


@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False,
    warmup_iterations=1,
    min_rounds=1,
)
def test_should_run_pytorch_and_ssd(benchmark, setup_pytorch_tests):
    create_udf_query = """CREATE UDF IF NOT EXISTS SSDObjectDetector
                INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                OUTPUT (label NDARRAY STR(10))
                TYPE  Classification
                IMPL  'eva/udfs/ssd_object_detector.py';
    """
    execute_query_fetch_all(create_udf_query)

    select_query = """SELECT SSDObjectDetector(data) FROM MyVideo
                    WHERE id < 5;"""
    actual_batch = benchmark(execute_query_fetch_all, select_query)
    assert(len(actual_batch)==5)
    # non-trivial test case
    res = actual_batch.frames
    for idx in res.index:
        assert("car" in res["ssdobjectdetector.label"][idx])


@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False,
    warmup_iterations=1,
    min_rounds=1,
)
def test_should_run_pytorch_and_facenet(benchmark, setup_pytorch_tests):
    create_udf_query = """CREATE UDF IF NOT EXISTS FaceDetector
                INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                        scores NDARRAY FLOAT32(ANYDIM))
                TYPE  FaceDetection
                IMPL  'eva/udfs/face_detector.py';
    """
    execute_query_fetch_all(create_udf_query)

    select_query = """SELECT FaceDetector(data) FROM MyVideo
                    WHERE id < 5;"""
    actual_batch = benchmark(execute_query_fetch_all, select_query)
    assert(len(actual_batch)==5)




@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False,
    warmup_iterations=1,
    min_rounds=1,
)
def test_should_run_pytorch_and_ocr(benchmark, setup_pytorch_tests):
    create_udf_query = """CREATE UDF IF NOT EXISTS OCRExtractor
                INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                OUTPUT (labels NDARRAY STR(10),
                        bboxes NDARRAY FLOAT32(ANYDIM, 4),
                        scores NDARRAY FLOAT32(ANYDIM))
                TYPE  OCRExtraction
                IMPL  'eva/udfs/ocr_extractor.py';
    """
    execute_query_fetch_all(create_udf_query)

    select_query = """SELECT OCRExtractor(data) FROM MNIST
                    WHERE id >= 150 AND id < 155;"""
    actual_batch = benchmark(execute_query_fetch_all, select_query)
    assert(len(actual_batch)==5)

    # non-trivial test case for MNIST
    res = actual_batch.frames
    assert(res["ocrextractor.labels"][0][0] == "4")
    assert(res["ocrextractor.scores"][2][0] > 0.9)

@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False,
    warmup_iterations=1,
    min_rounds=1,
)
def test_should_run_pytorch_and_resnet50(benchmark, setup_pytorch_tests):
    create_udf_query = """CREATE UDF IF NOT EXISTS FeatureExtractor
                INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                OUTPUT (features NDARRAY FLOAT32(ANYDIM))
                TYPE  Classification
                IMPL  'eva/udfs/feature_extractor.py';
    """
    execute_query_fetch_all(create_udf_query)

    select_query = """SELECT FeatureExtractor(data) FROM MyVideo
                    WHERE id < 5;"""
    actual_batch = benchmark(execute_query_fetch_all, select_query)
    assert(len(actual_batch)==5)

    # non-trivial test case for Resnet50
    res = actual_batch.frames
    assert(res["featureextractor.features"][0].shape==(1, 2048))
    assert(res["featureextractor.features"][0][0][0] > 0.3)

@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False,
    warmup_iterations=1,
    min_rounds=1,
)
def test_should_raise_import_error_with_missing_torch(benchmark, setup_pytorch_tests):
    with pytest.raises(ImportError):
        with mock.patch.dict(sys.modules, {"torch": None}):
            from eva.udfs.ssd_object_detector import SSDObjectDetector  # noqa: F401

            pass

@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False,
    warmup_iterations=1,
    min_rounds=1,
)
def test_should_raise_import_error_with_missing_torchvision(benchmark, setup_pytorch_tests):
    with pytest.raises(ImportError):
        with mock.patch.dict(sys.modules, {"torchvision.transforms": None}):
            from eva.udfs.ssd_object_detector import SSDObjectDetector  # noqa: F401

            pass
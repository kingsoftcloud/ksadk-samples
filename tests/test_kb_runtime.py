from common.kb_runtime import collect_kb_runtime_status, resolve_kb_connection


def test_missing_dataset_uses_local_mode():
    status = collect_kb_runtime_status({})
    assert status["status"] == "LOCAL_MODE"
    assert status["effective_config"]["mode"] == "local"


def test_public_endpoint_defaults_to_https():
    connection = resolve_kb_connection({"KSADK_KB_ENDPOINT": "aicp.api.ksyun.com"})
    assert connection["scheme"] == "https"


def test_explicit_scheme_overrides_default():
    connection = resolve_kb_connection({"KSADK_KB_ENDPOINT": "example." + "in" + "ternal", "KSADK_KB_SCHEME": "http"})
    assert connection["scheme"] == "http"


def test_cloud_mode_requires_credentials():
    status = collect_kb_runtime_status({"KSADK_KB_DATASET_ID": "kb-1"})
    assert status["status"] == "AUTH_MISSING"
    assert "missing_access_key" in status["issues"]
    assert "missing_secret_key" in status["issues"]


def test_cloud_mode_ready_with_credentials():
    status = collect_kb_runtime_status(
        {
            "KSADK_KB_DATASET_ID": "kb-1",
            "KSYUN_ACCESS_KEY": "ak",
            "KSYUN_SECRET_KEY": "sk",
        }
    )
    assert status["status"] == "READY"
    assert status["effective_config"]["mode"] == "cloud"

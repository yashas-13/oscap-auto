from pathlib import Path

import yaml


REGISTRY = Path(__file__).parents[1] / "registry" / "benchmarks.yaml"


def test_registry_loads():
    data = yaml.safe_load(REGISTRY.read_text())
    assert data["schema_version"] == 1
    assert data["benchmarks"]


def test_benchmarks_have_required_metadata():
    data = yaml.safe_load(REGISTRY.read_text())
    required = {"id", "vendor", "product", "version", "content_type", "source"}
    for benchmark in data["benchmarks"]:
        assert required <= benchmark.keys(), benchmark.get("id")
        assert benchmark["version"]
        assert benchmark["source"] == "official"


def test_core_linux_versions_are_registered():
    data = yaml.safe_load(REGISTRY.read_text())
    ids = {item["id"] for item in data["benchmarks"]}
    expected = {
        "cis-ubuntu-2404",
        "cis-ubuntu-2204",
        "cis-debian-13",
        "cis-debian-12",
        "cis-rhel-10",
        "cis-rocky-10",
    }
    assert expected <= ids

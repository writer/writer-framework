def pytest_collection_modifyitems(config, items):
    if not config.getoption("--full-run"):
        deselected = []
        selected = []
        for item in items:
            if "explicit" in item.keywords:
                deselected.append(item)
            else:
                selected.append(item)
        items[:] = selected
        config.hook.pytest_deselected(items=deselected)


def pytest_addoption(parser):
    parser.addoption(
        "--full-run", action="store_true", default=False, help="Include explicit-marked tests in the run (those are exluded from regular runs)"
    )

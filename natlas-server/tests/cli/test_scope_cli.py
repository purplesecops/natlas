import json

from app.cli.scope import import_items
from app.models import ScopeItem

DEFAULT_SCOPE_ITEMS = ["10.0.0.0/8", "192.168.1.0/24", "192.168.5.0/28"]


def mock_scope_file(scope_items: list = DEFAULT_SCOPE_ITEMS) -> str:
    with open("scope.txt", "w") as f:
        f.write("\n".join(scope_items))
    return "scope.txt"


def test_import_items_no_flags(runner):
    with runner.isolated_filesystem():
        scope_file = mock_scope_file()
        result = runner.invoke(import_items, [scope_file])
        assert result.exit_code == 0
        imported_scope = [item.target for item in ScopeItem.getScope()]
        assert DEFAULT_SCOPE_ITEMS == imported_scope
        result_dict = json.loads(result.output)
        assert len(result_dict["scope"]) == len(DEFAULT_SCOPE_ITEMS)


def test_import_items_scope_flag(runner):
    with runner.isolated_filesystem():
        scope_file = mock_scope_file()
        result = runner.invoke(import_items, ["--scope", scope_file])
        assert result.exit_code == 0
        imported_scope = [item.target for item in ScopeItem.getScope()]
        assert DEFAULT_SCOPE_ITEMS == imported_scope
        result_dict = json.loads(result.output)
        assert len(result_dict["scope"]) == len(DEFAULT_SCOPE_ITEMS)


def test_import_items_blacklist_flag(runner):
    with runner.isolated_filesystem():
        scope_file = mock_scope_file()
        result = runner.invoke(import_items, ["--blacklist", scope_file])
        assert result.exit_code == 0
        imported_blacklist = [item.target for item in ScopeItem.getBlacklist()]
        assert DEFAULT_SCOPE_ITEMS == imported_blacklist
        result_dict = json.loads(result.output)
        assert len(result_dict["blacklist"]) == len(DEFAULT_SCOPE_ITEMS)


def test_import_items_verbose(runner):
    with runner.isolated_filesystem():
        scope_file = mock_scope_file()
        result = runner.invoke(import_items, ["--verbose", scope_file])
        assert result.exit_code == 0
        result_dict = json.loads(result.output)
        assert len(result_dict["scope"]) == len(DEFAULT_SCOPE_ITEMS)
        assert result_dict["summary"]["scope"]["successful"] == len(DEFAULT_SCOPE_ITEMS)
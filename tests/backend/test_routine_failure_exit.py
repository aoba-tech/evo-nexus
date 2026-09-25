import importlib.util
import ast
from pathlib import Path


def test_summary_propagates_failed_step_to_scheduler():
    spec = importlib.util.spec_from_file_location("routine_runner_audit", Path(__file__).resolve().parents[2] / "ADWs/runner.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    assert runner.summary([{"success": False, "duration": 0}], "test") == 1
    assert runner.summary([{"success": True, "duration": 0}], "test") == 0


def test_routines_pass_summary_result_to_process_exit():
    root = Path(__file__).resolve().parents[2]
    routines = ["backup.py", "end_of_day.py", "good_morning.py", "memory_lint.py", "memory_sync.py", "weekly_review.py"]
    for name in routines:
        tree = ast.parse((root / "ADWs" / "routines" / name).read_text())
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "summary"]
        assert calls, f"{name} has no summary() call"
        exits = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and isinstance(n.func.value, ast.Name) and n.func.value.id == "sys" and n.func.attr == "exit"]
        for call in calls:
            assert any(call in list(ast.walk(arg)) for ex in exits for arg in ex.args), f"{name} discards the failure count"

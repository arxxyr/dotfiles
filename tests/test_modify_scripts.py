"""modify_ 脚本回归：Windows 上的目标名与 Codex 多行数组，只用临时目录，不碰真实配置。"""

import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CODEX = tomllib.loads((REPO / ".chezmoidata.toml").read_text(encoding="utf-8"))["codex"]
TARGETS = {
    ".agents/.skill-lock.json",
    ".claude/settings.json",
    ".codex/config.toml",
    ".kimi-code/config.toml",
}


def render(relative_path, data=None):
    command = ["chezmoi", "--source", str(REPO)]
    if data:
        command += ["--override-data", json.dumps(data)]
    command += ["execute-template", "--file", str(REPO / relative_path)]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


class ModifyTargetNameTests(unittest.TestCase):
    """Windows 靠 interpreters 按扩展名选解释器，而 chezmoi 会把命中的扩展名从 modify_ 目标名里
    剥掉：脚本必须以 .py 结尾，剥掉的才是 .py 而不是目标自己的 .json/.toml。"""

    def test_scripts_end_with_py(self):
        scripts = [path for path in REPO.rglob("modify_*") if ".git" not in path.parts]
        self.assertTrue(scripts)
        for path in scripts:
            with self.subTest(path=str(path.relative_to(REPO))):
                self.assertTrue(path.name.removesuffix(".tmpl").endswith(".py"))

    def test_windows_config_only_maps_py(self):
        config = tomllib.loads(render(".chezmoi.toml.tmpl", {"chezmoi": {"os": "windows"}}))
        self.assertEqual(set(config["interpreters"]), {"py"})

    def test_targets_keep_extensions(self):
        # 现行配置只钉 py；没重新 init 的机器还留着旧的 json/toml 两条，两种都得算对
        variants = {
            "current": '[interpreters.py]\ncommand = "python3"\n',
            "legacy": (
                '[interpreters.json]\ncommand = "python3"\n'
                '[interpreters.toml]\ncommand = "python3"\n'
            ),
        }
        stripped = {target.rsplit(".", 1)[0] for target in TARGETS}
        for name, config in variants.items():
            with self.subTest(config=name), tempfile.TemporaryDirectory() as temp:
                temp = Path(temp)
                (temp / "chezmoi.toml").write_text(config, encoding="utf-8")
                managed = subprocess.run(
                    [
                        "chezmoi",
                        "--source", str(REPO),
                        "--destination", str(temp / "home"),
                        "--config", str(temp / "chezmoi.toml"),
                        "--persistent-state", str(temp / "state.boltdb"),
                        "managed", "--include=files",
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.splitlines()
                self.assertLessEqual(TARGETS, set(managed))
                self.assertFalse(stripped & set(managed))


class CodexConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # homeDir 指向不存在的目录：受信项目只播种本机真实存在的路径，输出不随本机目录变化
        cls.script = render(
            "dot_codex/modify_private_config.toml.py.tmpl",
            {"chezmoi": {"homeDir": "/nonexistent-home-for-tests"}},
        )

    def modify(self, content):
        result = subprocess.run(
            [sys.executable, "-c", self.script],
            input=content,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_multiline_array_replaced_whole(self):
        # Windows 上 Codex 自己把 status_line 写成了多行，旧逻辑只换首行，留下续行把 TOML 写坏
        current = (
            'model = "old-model"\n'
            "notify = [\n"
            '    "python3",\n'
            '    "C:/hooks/notify.py",\n'
            "]\n"
            "\n"
            "[tui]\n"
            "status_line = [\n"
            '    "model-with-reasoning",\n'
            '    "odd]#name",  # 引号里的 ] 与 #、注释里的 ] 都不能算括号\n'
            "]\n"
            "\n"
            "[tui.model_availability_nux]\n"
            '"gpt-5.5" = 2\n'
        )
        result = self.modify(current)
        config = tomllib.loads(result)
        self.assertEqual(config["model"], CODEX["model"])
        self.assertEqual(config["tui"]["status_line"], CODEX["status_line"])
        self.assertEqual(config["notify"], ["python3", "C:/hooks/notify.py"])
        self.assertEqual(config["tui"]["model_availability_nux"], {"gpt-5.5": 2})
        self.assertEqual(self.modify(result), result)


if __name__ == "__main__":
    unittest.main()

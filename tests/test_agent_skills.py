"""验证技能源归属、锁文件迁移及精确清理，不修改真实用户目录。"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = tomllib.loads((REPO / ".chezmoidata.toml").read_text(encoding="utf-8"))[
    "agent_skills"
]
MANAGED = set(DATA["managed"])
RETIRED = set(DATA["retired"])
CLIENT_SOURCES = {
    "claude": "dot_claude",
    "codex": "dot_codex",
    "openclaw": "private_dot_openclaw",
}


def render(relative_path, operating_system=None):
    command = ["chezmoi", "--source", str(REPO)]
    if operating_system:
        command += [
            "--override-data",
            json.dumps({"chezmoi": {"os": operating_system}}),
        ]
    command += ["execute-template", "--file", str(REPO / relative_path)]
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


class SkillSourceTests(unittest.TestCase):
    def test_single_source_and_links(self):
        self.assertFalse(MANAGED & RETIRED)
        self.assertEqual(len(MANAGED), len(DATA["managed"]))
        self.assertEqual(len(RETIRED), len(DATA["retired"]))
        actual = {
            path.parent.name for path in (REPO / "dot_agents/skills").glob("*/SKILL.md")
        }
        self.assertEqual(actual, MANAGED)
        for name in MANAGED:
            for client in CLIENT_SOURCES.values():
                link = REPO / client / "skills" / f"symlink_{name}"
                self.assertEqual(
                    link.read_text(encoding="utf-8").strip(),
                    f"../../.agents/skills/{name}",
                )
        for name in RETIRED:
            self.assertFalse((REPO / "dot_agents/skills" / name / "SKILL.md").exists())
            for client in CLIENT_SOURCES.values():
                self.assertFalse(
                    (REPO / client / "skills" / f"symlink_{name}").exists()
                )

    def test_removal_targets_are_exact_and_platform_safe(self):
        expected = {
            f".{client}/skills/{name}"
            for client in ("agents", *CLIENT_SOURCES)
            for name in RETIRED
        }
        for operating_system in ("linux", "darwin", "windows"):
            lines = {
                line.strip()
                for line in render(".chezmoiremove", operating_system).splitlines()
                if line.strip() and not line.startswith("#")
            }
            wanted = expected | (
                {".agents/skills/south-asia-translator/skill.md"}
                if operating_system == "linux"
                else set()
            )
            self.assertEqual(lines, wanted)


class SkillLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = render("dot_agents/modify_dot_skill-lock.json.tmpl")

    def modify(self, content):
        return subprocess.run(
            [sys.executable, "-c", self.script],
            input=content,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_retains_unrelated_data_and_is_idempotent(self):
        state = {
            "version": 3,
            "skills": {name: {"source": "原登记"} for name in MANAGED | RETIRED},
            "dismissed": {"提示": True},
            "lastSelectedAgents": ["codex"],
            "future": {"opaque": [1, 2, 3]},
        }
        state["skills"]["future-user-skill"] = {"source": "用户独立安装", "hash": "abc"}
        result = self.modify(json.dumps(state))
        self.assertEqual(result.returncode, 0, result.stderr)
        state["skills"] = {"future-user-skill": state["skills"]["future-user-skill"]}
        self.assertEqual(json.loads(result.stdout), state)
        self.assertEqual(self.modify(result.stdout).stdout, result.stdout)

    def test_empty_lock(self):
        for content in ("", " \n"):
            result = self.modify(content)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"version": 3, "skills": {}})

    def test_noop_preserves_exact_input(self):
        for content in ('{"version": 4, "skills": {}}', '{"future": true}\n'):
            self.assertEqual(self.modify(content).stdout, content)

    def test_invalid_input_fails_without_replacement(self):
        for content in ("broken", "[]", "null", '{"skills": null}', '{"skills": []}'):
            result = self.modify(content)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")


@unittest.skipIf(os.name == "nt", "隔离目录迁移测试需要无需提权创建符号链接")
class MigrationTests(unittest.TestCase):
    def test_apply_removes_only_retired_skills(self):
        with tempfile.TemporaryDirectory(prefix="chezmoi-skills-test-") as directory:
            temporary = Path(directory)
            source, destination = temporary / "source", temporary / "home"
            source.mkdir()
            destination.mkdir()
            config = temporary / "config.toml"
            config.write_text("", encoding="utf-8")
            for filename in (".chezmoidata.toml", ".chezmoiremove"):
                shutil.copyfile(REPO / filename, source / filename)
            for name in MANAGED:
                skill = source / "dot_agents/skills" / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
                for client_source in CLIENT_SOURCES.values():
                    links = source / client_source / "skills"
                    links.mkdir(parents=True, exist_ok=True)
                    (links / f"symlink_{name}").write_text(
                        f"../../.agents/skills/{name}\n", encoding="utf-8"
                    )
            shutil.copyfile(
                REPO / "dot_agents/modify_dot_skill-lock.json.tmpl",
                source / "dot_agents/modify_dot_skill-lock.json.tmpl",
            )
            for name in RETIRED:
                old = destination / ".agents/skills" / name / "references"
                old.mkdir(parents=True)
                (old / "original.md").write_text("旧技能内容\n", encoding="utf-8")
                for client in CLIENT_SOURCES:
                    links = destination / f".{client}/skills"
                    links.mkdir(parents=True, exist_ok=True)
                    (links / name).symlink_to(f"../../.agents/skills/{name}")
            sentinels = [
                ".codex/skills/.system/skill-creator/SKILL.md",
                ".codex/plugins/cache/untouched/SKILL.md",
                ".agents/skills/future-user-skill/SKILL.md",
                ".claude/skills/learned/notes.md",
                ".openclaw/skills/future-openclaw-skill/SKILL.md",
            ]
            for relative in sentinels:
                sentinel = destination / relative
                sentinel.parent.mkdir(parents=True, exist_ok=True)
                sentinel.write_text("不可删除\n", encoding="utf-8")
            old_entry = destination / ".agents/skills/south-asia-translator/skill.md"
            old_entry.parent.mkdir(parents=True, exist_ok=True)
            old_entry.write_text("小写入口\n", encoding="utf-8")
            lock = destination / ".agents/.skill-lock.json"
            lock.write_text(
                json.dumps(
                    {
                        "version": 3,
                        "skills": {"diagnose": {}, "future-user-skill": {"x": 1}},
                    }
                ),
                encoding="utf-8",
            )
            command = [
                "chezmoi",
                "--source",
                str(source),
                "--destination",
                str(destination),
                "--config",
                str(config),
                "--persistent-state",
                str(temporary / "state.boltdb"),
                "--cache",
                str(temporary / "cache"),
                "--force",
                "apply",
                "--exclude",
                "scripts",
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)
            for name in RETIRED:
                for client in ("agents", *CLIENT_SOURCES):
                    self.assertFalse(
                        os.path.lexists(destination / f".{client}/skills" / name)
                    )
            for name in MANAGED:
                for client in ("agents", *CLIENT_SOURCES):
                    self.assertTrue(
                        (
                            destination / f".{client}/skills" / name / "SKILL.md"
                        ).is_file()
                    )
            for relative in sentinels:
                self.assertEqual(
                    (destination / relative).read_text(encoding="utf-8"), "不可删除\n"
                )
            if sys.platform.startswith("linux"):
                self.assertFalse(old_entry.exists())
            self.assertEqual(
                json.loads(lock.read_text(encoding="utf-8"))["skills"],
                {"future-user-skill": {"x": 1}},
            )
            subprocess.run(command, check=True, capture_output=True, text=True)
            for relative in sentinels:
                self.assertTrue((destination / relative).is_file())


if __name__ == "__main__":
    unittest.main()

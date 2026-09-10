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
    def test_full_source_restores_to_empty_destination(self):
        with tempfile.TemporaryDirectory(prefix="chezmoi-skills-restore-") as directory:
            temporary = Path(directory)
            destination = temporary / "home"
            destination.mkdir()
            config = temporary / "config.toml"
            config.write_text("", encoding="utf-8")
            command = [
                "chezmoi",
                "--source",
                str(REPO),
                "--destination",
                str(destination),
                "--config",
                str(config),
                "--persistent-state",
                str(temporary / "state.boltdb"),
                "--cache",
                str(temporary / "cache"),
                "--force",
                "--use-builtin-diff",
            ]
            targets = [
                str(destination / relative)
                for relative in (
                    ".agents/skills",
                    ".claude/skills",
                    ".codex/skills",
                    ".openclaw/skills",
                    ".agents/.skill-lock.json",
                    ".claude/CLAUDE.md",
                    ".agents/AGENTS.md",
                    ".codex/AGENTS.md",
                )
            ]
            preview = command + [
                "diff",
                "--recursive",
                "--parent-dirs",
                "--exclude",
                "scripts",
                *targets,
            ]
            subprocess.run(preview, check=True, capture_output=True, text=True)
            self.assertEqual(list(destination.iterdir()), [])
            apply_command = command + [
                "apply",
                "--parent-dirs",
                "--exclude",
                "scripts",
                *targets,
            ]
            subprocess.run(apply_command, check=True, capture_output=True, text=True)

            expected_paths = set()
            source_skills = REPO / "dot_agents/skills"
            # 用 chezmoi 的路径映射处理 literal_ 等源属性，再逐字节核对完整资源。
            source_files = sorted(
                path for path in source_skills.rglob("*") if path.is_file()
            )
            mapped = subprocess.run(
                command + ["target-path", *(str(path) for path in source_files)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
            self.assertEqual(len(mapped), len(source_files))
            for source_file, target_path in zip(source_files, mapped, strict=True):
                target_file = Path(target_path)
                relative = target_file.relative_to(destination)
                self.assertEqual(target_file.read_bytes(), source_file.read_bytes())
                expected_paths.add(relative.as_posix())
            for name in MANAGED:
                for client in CLIENT_SOURCES:
                    relative = f".{client}/skills/{name}"
                    target_link = destination / relative
                    self.assertTrue(target_link.is_symlink())
                    self.assertEqual(
                        target_link.readlink().as_posix(),
                        f"../../.agents/skills/{name}",
                    )
                    self.assertEqual(
                        target_link.resolve(), destination / ".agents/skills" / name
                    )
                    expected_paths.add(relative)
            instructions = destination / ".claude/CLAUDE.md"
            self.assertEqual(
                instructions.read_bytes(), (REPO / "dot_claude/CLAUDE.md").read_bytes()
            )
            expected_paths.add(".claude/CLAUDE.md")
            for client in ("agents", "codex"):
                relative = f".{client}/AGENTS.md"
                link = destination / relative
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), instructions)
                expected_paths.add(relative)
            lock_relative = ".agents/.skill-lock.json"
            self.assertEqual(
                json.loads((destination / lock_relative).read_text(encoding="utf-8")),
                {"version": 3, "skills": {}},
            )
            expected_paths.add(lock_relative)
            actual_paths = {
                path.relative_to(destination).as_posix()
                for path in destination.rglob("*")
                if path.is_file() or path.is_symlink()
            }
            self.assertEqual(actual_paths, expected_paths)
            subprocess.run(apply_command, check=True, capture_output=True, text=True)
            result = subprocess.run(preview, check=True, capture_output=True, text=True)
            self.assertEqual(result.stdout, "")

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
                ".unrelated",
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
            (source / "dot_unrelated").write_text("本次不得应用\n", encoding="utf-8")
            old_entry = destination / ".agents/skills/south-asia-translator/skill.md"
            old_entry.parent.mkdir(parents=True, exist_ok=True)
            old_entry.write_text("小写入口\n", encoding="utf-8")
            lock = destination / ".agents/.skill-lock.json"
            lock.write_text(
                json.dumps(
                    {
                        "version": 3,
                        "skills": {
                            **{name: {} for name in RETIRED},
                            "future-user-skill": {"x": 1},
                        },
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
            retired_targets = [
                str(destination / f".{client}/skills" / name)
                for client in ("agents", *CLIENT_SOURCES)
                for name in sorted(RETIRED)
            ]
            subprocess.run(
                command + retired_targets, check=True, capture_output=True, text=True
            )
            for target in retired_targets:
                self.assertFalse(os.path.lexists(target))
            # 精确退役目标之外的旧入口、锁记录与其他配置不应被顺带应用。
            self.assertTrue(old_entry.exists())
            self.assertTrue(
                RETIRED <= json.loads(lock.read_text(encoding="utf-8"))["skills"].keys()
            )
            for relative in sentinels:
                self.assertEqual(
                    (destination / relative).read_text(encoding="utf-8"), "不可删除\n"
                )
            targets = [
                str(destination / f".{client}/skills")
                for client in ("agents", *CLIENT_SOURCES)
            ] + [str(lock)]
            subprocess.run(
                command + targets, check=True, capture_output=True, text=True
            )
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
            subprocess.run(
                command + targets, check=True, capture_output=True, text=True
            )
            for relative in sentinels:
                self.assertTrue((destination / relative).is_file())


if __name__ == "__main__":
    unittest.main()

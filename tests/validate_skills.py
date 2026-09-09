# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0.3",
# ]
# ///
"""复用系统技能验证器，并单独验证共享技能的 Claude 扩展字段。"""

import importlib.util
import os
import sys
import tempfile
from pathlib import Path

import yaml


def main():
    # 仅读取系统验证器，不在由 Codex 管理的目录中生成字节码缓存。
    sys.dont_write_bytecode = True
    repository = Path(__file__).resolve().parents[1]
    codex_directory = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    validator_path = (
        codex_directory / "skills/.system/skill-creator/scripts/quick_validate.py"
    )
    if not validator_path.is_file():
        sys.exit(f"找不到系统技能验证器：{validator_path}")
    spec = importlib.util.spec_from_file_location(
        "system_skill_validator", validator_path
    )
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    failures = []
    entries = sorted((repository / "dot_agents/skills").glob("*/SKILL.md"))
    for entry in entries:
        if entry.parent.name != "team-swe":
            valid, message = validator.validate_skill(entry.parent)
        else:
            # 原验证器不识别 Claude 扩展；只允许这一项且必须是显式调用禁令。
            content = entry.read_text(encoding="utf-8")
            _, frontmatter, body = content.split("---", 2)
            metadata = yaml.safe_load(frontmatter)
            policy = yaml.safe_load(
                (entry.parent / "agents/openai.yaml").read_text(encoding="utf-8")
            )
            if metadata.pop("disable-model-invocation", None) is not True:
                failures.append("team-swe: Claude 显式调用策略缺失或类型错误")
            if policy.get("policy", {}).get("allow_implicit_invocation") is not False:
                failures.append("team-swe: Codex 显式调用策略缺失或类型错误")
            with tempfile.TemporaryDirectory(prefix="skill-validator-") as temporary:
                normalized = Path(temporary)
                (normalized / "SKILL.md").write_text(
                    "---\n"
                    + yaml.safe_dump(metadata, allow_unicode=True)
                    + "---"
                    + body,
                    encoding="utf-8",
                )
                valid, message = validator.validate_skill(normalized)
            message += "（Claude 扩展字段与 Codex 调用策略已单独检查）"
        print(f"{entry.parent.name}: {message}")
        if not valid:
            failures.append(f"{entry.parent.name}: {message}")
    if failures:
        sys.exit("\n".join(failures))
    print(f"已验证 {len(entries)} 个个人技能；系统/插件技能未修改。")


if __name__ == "__main__":
    main()

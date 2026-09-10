# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0.3",
# ]
# ///
"""只读复用系统技能验证器，检查源仓库中的个人技能。"""

import importlib.util
import os
import sys
from pathlib import Path


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
        valid, message = validator.validate_skill(entry.parent)
        print(f"{entry.parent.name}: {message}")
        if not valid:
            failures.append(f"{entry.parent.name}: {message}")
    if failures:
        sys.exit("\n".join(failures))
    print(f"已验证 {len(entries)} 个个人技能；系统/插件技能未修改。")


if __name__ == "__main__":
    main()

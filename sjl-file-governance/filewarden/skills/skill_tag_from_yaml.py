"""
Skill: Tag From YAML (alias/re-export)
Thin alias for skill_yaml_tag_extract to preserve the skills/__init__.py import.
"""
from filewarden.skills.skill_yaml_tag_extract import extract_yaml_tags as tag_from_yaml  # noqa: F401

"""
FileWarden v2 — Skill Library
SJL Sovereign Cloud | 07100_FILEWARDEN

Converted from Hazel automation use cases.
Import all skills to register them with the pipeline decorator.
"""

from filewarden.skills import (
    skill_subfolder_traverse,
    skill_screenshot_sort,
    skill_merge_backup,
    skill_pdf_ocr_detect,
    skill_yaml_tag_extract,
    skill_image_gps_tag,
    skill_video_sort,
    skill_video_convert,
    skill_content_classify,
    skill_date_archive,
    skill_dmg_extract,
    skill_pdf_size_reduce,
    skill_new_files_only,
    skill_stabilize_timing,
    skill_move_parent_folder,
    skill_notes_publish,
    skill_mp4_gather,
    skill_audio_convert,
    skill_tag_from_yaml,
)

__all__ = [
    "skill_subfolder_traverse",
    "skill_screenshot_sort",
    "skill_merge_backup",
    "skill_pdf_ocr_detect",
    "skill_yaml_tag_extract",
    "skill_image_gps_tag",
    "skill_video_sort",
    "skill_video_convert",
    "skill_content_classify",
    "skill_date_archive",
    "skill_dmg_extract",
    "skill_pdf_size_reduce",
    "skill_new_files_only",
    "skill_stabilize_timing",
    "skill_move_parent_folder",
    "skill_notes_publish",
    "skill_mp4_gather",
    "skill_audio_convert",
    "skill_tag_from_yaml",
]

from pathlib import Path
import sys
import zipfile


sys.path.insert(0, str(Path(__file__).parent))
from prepare_course_data import display_name, normalize_archive  # noqa: E402


def test_display_name_repairs_cp437_view_of_gbk_name():
    info = zipfile.ZipInfo("╜╠▓─┐╬╝■╖╓╒┬╜┌pdf░µ/1.1 x.pdf")
    assert display_name(info) == "教材课件分章节pdf版/1.1 x.pdf"


def test_normalize_archive_writes_manifest_and_stable_files(tmp_path):
    archive = tmp_path / "materials.zip"
    with zipfile.ZipFile(archive, "w") as source:
        info = zipfile.ZipInfo("╜╠▓─┐╬╝■╖╓╒┬╜┌pdf░µ/1.1 x.pdf")
        source.writestr(info, b"%PDF-test")
    output = tmp_path / "normalized"
    manifest = normalize_archive(archive, output)
    assert len(manifest) == 1
    assert manifest[0]["source_file"] == "1.1 x.pdf"
    assert manifest[0]["chapter_id"] == 1
    assert list(output.glob("*.pdf"))
    assert '"pdf_count": 1' in (output / "manifest.json").read_text(encoding="utf-8")

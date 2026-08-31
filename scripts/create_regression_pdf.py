#!/usr/bin/env python3
"""Create a small, deterministic PDF used only for functional regression."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "codex-functional-regression-courseware-20260820.pdf"
FONT = "STSong-Light"
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def draw_header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(18 * mm, height - 16 * mm, width - 18 * mm, height - 16 * mm)
    canvas.setFont(FONT, 8.5)
    canvas.setFillColor(colors.HexColor("#52606D"))
    canvas.drawString(18 * mm, height - 12 * mm, "EnergyGraph - Codex functional regression fixture")
    canvas.drawRightString(width - 18 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build() -> Path:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(f"embedded test font not found: {FONT_PATH}")
    # Embed a TrueType font so the fixture renders in both browser PDF viewers
    # and the bundled Poppler runtime used by the acceptance checks.
    pdfmetrics.registerFont(TTFont(FONT, str(FONT_PATH)))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "FixtureTitle",
        parent=styles["Title"],
        fontName=FONT,
        fontSize=26,
        leading=34,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0B4F6C"),
        spaceAfter=14,
    )
    subtitle = ParagraphStyle(
        "FixtureSubtitle",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=12,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#52606D"),
        spaceAfter=18,
    )
    h1 = ParagraphStyle(
        "FixtureHeading",
        parent=styles["Heading1"],
        fontName=FONT,
        fontSize=18,
        leading=26,
        textColor=colors.HexColor("#0B4F6C"),
        spaceBefore=4,
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "FixtureSubheading",
        parent=styles["Heading2"],
        fontName=FONT,
        fontSize=13,
        leading=20,
        textColor=colors.HexColor("#243B53"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "FixtureBody",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=10.5,
        leading=18,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#243B53"),
        spaceAfter=8,
    )
    small = ParagraphStyle(
        "FixtureSmall",
        parent=body,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#52606D"),
    )
    marker = ParagraphStyle(
        "FixtureMarker",
        parent=body,
        fontSize=12,
        leading=20,
        textColor=colors.HexColor("#0B4F6C"),
        backColor=colors.HexColor("#E6F6F8"),
        borderColor=colors.HexColor("#9AD7DE"),
        borderWidth=0.7,
        borderPadding=9,
        spaceBefore=8,
        spaceAfter=12,
    )

    story = [
        Spacer(1, 34 * mm),
        paragraph("Codex 功能回归测试课件", title),
        paragraph("EnergyGraph / PDF upload and retrieval fixture", subtitle),
        paragraph(
            "本文件是自动化测试数据，不是正式课程材料。用于验证 PDF 生成、文本抽取、上传校验、知识库版本、来源定位和回滚流程。",
            body,
        ),
        Spacer(1, 8 * mm),
        paragraph("测试标识", h2),
        paragraph("CODEx-PDF-REGRESSION-20260820", marker),
        paragraph("预期页数：3 页；预期关键字：储能变流器、并网控制、PDF_UPLOAD_MARKER_20260820。", body),
        Spacer(1, 10 * mm),
        paragraph("验收边界", h2),
        ListFlowable(
            [
                ListItem(paragraph("只允许安全文件名和真实 PDF 魔数。", body)),
                ListItem(paragraph("上传内容必须可被 PDF 解析器重新打开。", body)),
                ListItem(paragraph("知识库文件记录必须保留 SHA256 和版本关联。", body)),
                ListItem(paragraph("测试版本不得覆盖当前正式发布版本。", body)),
            ],
            bulletType="bullet",
            leftIndent=18,
        ),
        PageBreak(),
        paragraph("第 1 章 - PDF 上传与文本抽取", h1),
        paragraph(
            "本页用于检查中文文本、英文标识、数字和换行在生成、上传、下载、抽取后的稳定性。测试流程应能识别以下内容，并保持原始文件的 SHA256 不变。",
            body,
        ),
        paragraph("PDF_UPLOAD_MARKER_20260820", marker),
        paragraph(
            "储能变流器是电池储能系统与电网之间的接口。在并网控制测试中，系统需要关注双向能量交换、充放电管理、功率指令跟踪、运行状态反馈和安全边界。该段文字仅为回归样本。",
            body,
        ),
        paragraph("验收数据表", h2),
        Table(
            [
                [paragraph("字段", body), paragraph("预期值", body), paragraph("用途", body)],
                [paragraph("fixture_id", body), paragraph("pdf-regression-20260820", body), paragraph("幂等键和留档关联", body)],
                [paragraph("page_count", body), paragraph("3", body), paragraph("页数校验", body)],
                [paragraph("topic", body), paragraph("储能变流器并网控制", body), paragraph("搜索与问答样本", body)],
                [paragraph("marker", body), paragraph("PDF_UPLOAD_MARKER_20260820", body), paragraph("防止误用正式课件", body)],
            ],
            colWidths=[35 * mm, 66 * mm, 65 * mm],
            repeatRows=1,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2EC")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BCCCDC")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        ),
        Spacer(1, 8 * mm),
        paragraph("预期解析结果", h2),
        paragraph("解析器应能提取 fixture_id、page_count、topic 和 marker；上传接口应拒绝同内容但伪造扩展名的文件。", small),
        PageBreak(),
        paragraph("第 2 章 - 来源定位与回滚验证", h1),
        paragraph(
            "这一页提供足够长的连续文本，用于检查多页 PDF 的页码边界、来源显示和资源回跳。测试实现不应把本文件作为正式课程知识库的默认来源。",
            body,
        ),
        paragraph("来源样本", h2),
        paragraph("[来源文件：codex-functional-regression-courseware-20260820.pdf；章节：第2章 PDF回归；页码：3]", marker),
        paragraph(
            "当测试版本完成上传后，教师应能看到版本状态和文件清单；学生不应看到教师知识库管理接口。执行回滚后，正式版本仍应保持 published，测试版本应进入 archived 或由状态机标记为已回滚。重复上传同一个幂等键只能得到同一个记录，不能生成重复文件。",
            body,
        ),
        paragraph("完成条件", h2),
        ListFlowable(
            [
                ListItem(paragraph("PDF 可重新打开，页数为 3，关键字全部可抽取。", body)),
                ListItem(paragraph("测试版本文件数为 1，SHA256 与本地一致。", body)),
                ListItem(paragraph("非法文件、路径穿越、超限文件和越权上传均被拒绝。", body)),
                ListItem(paragraph("测试结束后不改变正式发布版本和线上 Agent 对话来源。", body)),
            ],
            bulletType="bullet",
            leftIndent=18,
        ),
        Spacer(1, 12 * mm),
        paragraph("END_OF_CODEX_PDF_FIXTURE_20260820", marker),
        paragraph("生成工具：scripts/create_regression_pdf.py；本文件只用于本轮功能回归。", small),
    ]
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=24 * mm,
        bottomMargin=20 * mm,
        title="Codex Functional Regression Courseware",
        author="Codex",
    )
    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    return OUTPUT


if __name__ == "__main__":
    print(build())

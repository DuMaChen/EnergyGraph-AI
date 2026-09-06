#!/usr/bin/env python3
"""Generate a structured, standard 4-page PDF courseware for a new course: 人工智能导论与大模型应用."""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PDF = ROOT / "output" / "pdf" / "1.1-人工智能与大模型核心原理.pdf"
FONT_NAME = "CustomFont"
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")


def draw_header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.setLineWidth(0.8)
    canvas.line(18 * mm, height - 16 * mm, width - 18 * mm, height - 16 * mm)
    canvas.setFont(FONT_NAME, 8.5)
    canvas.setFillColor(colors.HexColor("#475569"))
    canvas.drawString(18 * mm, height - 12 * mm, "《人工智能导论与大模型应用》· 课件教材")
    canvas.drawRightString(width - 18 * mm, 12 * mm, f"第 {doc.page} 页 / 共 4 页")
    canvas.line(18 * mm, 16 * mm, width - 18 * mm, 16 * mm)
    canvas.restoreState()


def build_pdf() -> Path:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(f"Font not found: {FONT_PATH}")
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CourseTitle",
        parent=styles["Title"],
        fontName=FONT_NAME,
        fontSize=22,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=10,
    )
    subtitle_style = ParagraphStyle(
        "CourseSubtitle",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=12,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15,
    )
    h1_style = ParagraphStyle(
        "CourseH1",
        parent=styles["Heading1"],
        fontName=FONT_NAME,
        fontSize=16,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=10,
        spaceAfter=8,
    )
    h2_style = ParagraphStyle(
        "CourseH2",
        parent=styles["Heading2"],
        fontName=FONT_NAME,
        fontSize=12,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "CourseBody",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6,
    )
    box_style = ParagraphStyle(
        "BoxText",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=9.5,
        leading=15,
        textColor=colors.HexColor("#1E3A8A"),
    )

    story = []

    # ================= PAGE 1 =================
    story.append(Paragraph("《人工智能导论与大模型应用》", title_style))
    story.append(Paragraph("第 1 章：人工智能与大语言模型核心原理（主讲课件）", subtitle_style))

    overview_table = Table(
        [[
            Paragraph(
                "<b>【本章学习目标】</b><br/>"
                "1. 理解人工智能三大核心学派演进及其在现代深度学习中的统一；<br/>"
                "2. 掌握 Transformer 自注意力机制与大模型预训练微调范式；<br/>"
                "3. 掌握 RAG 检索增强生成原理及在领域专业知识库中的防幻觉实践；<br/>"
                "4. 掌握自主智能体 (Agent) 的感知、规划、工具调用与协作体系。",
                box_style,
            )
        ]],
        colWidths=[174 * mm],
    )
    overview_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(overview_table)
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph("1.1 人工智能发展历程与三大核心学派", h1_style))
    story.append(
        Paragraph(
            "人工智能（Artificial Intelligence, AI）自 1956 年达特茅斯会议诞生以来，经历了数次繁荣与寒冬。"
            "在其发展历程中，形成了三大经典学派：",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>1. 符号主义（Symbolism / 逻辑主义）：</b>认为智能的本质是符号操作与逻辑推理，代表技术包括知识图谱、专家系统及产生式规则。其优点是可解释性极强，但在处理非结构化数据和模糊认知时存在瓶颈。",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>2. 连接主义（Connectionism / 仿生学派）：</b>主张智能源自神经元之间的连接与突触权重调节，代表技术为人工神经网络、深度学习及大语言模型（LLM）。其擅长从海量数据中提取隐式特征与通用表示。",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>3. 行为主义（Actionism / 进化控制）：</b>强调智能是在与环境的持续交互、试错与适应中涌现的，代表技术包括强化学习（RL）与具身智能（Embodied AI）。",
            body_style,
        )
    )

    story.append(PageBreak())

    # ================= PAGE 2 =================
    story.append(Paragraph("1.2 Transformer 架构与注意力机制", h1_style))
    story.append(
        Paragraph(
            "2017 年提出的 Transformer 架构彻底重塑了自然语言处理与通用大模型的基础格局。"
            "其摒弃了传统 RNN 的时序递归依赖，采用完全基于自注意力（Self-Attention）的并行计算模式。",
            body_style,
        )
    )

    story.append(Paragraph("1.2.1 缩放点积自注意力（Scaled Dot-Product Attention）", h2_style))
    story.append(
        Paragraph(
            "对于输入特征序列，通过线性投影生成查询矩阵 Q、键矩阵 K 和值矩阵 V。注意力的计算公式如下：",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Attention(Q, K, V) = softmax( (Q · K^T) / sqrt(d_k) ) · V</b>",
            ParagraphStyle("Formula", parent=body_style, alignment=TA_CENTER, textColor=colors.HexColor("#DC2626"), fontSize=11),
        )
    )
    story.append(
        Paragraph(
            "其中，除以 sqrt(d_k) 缩放因子的核心目的是防止点积结果在维度较大时数值过大，从而避免 Softmax 进入梯度饱和区导致梯度消失。",
            body_style,
        )
    )

    story.append(Paragraph("1.2.2 多头注意力（Multi-Head Attention）与残差连接", h2_style))
    story.append(
        Paragraph(
            "多头注意力机制允许模型在不同的表示子空间（Subspaces）中联合关注不同位置的上下文信息。"
            "每个注意力头独立计算后进行 Concat 拼接，并通过全连接层输出。网络中引入了 Layer Normalization 与残差连接（Residual Connection），"
            "有效解决了深层网络中的梯度流动与训练退化难题。",
            body_style,
        )
    )

    story.append(PageBreak())

    # ================= PAGE 3 =================
    story.append(Paragraph("1.3 检索增强生成（RAG）知识库架构", h1_style))
    story.append(
        Paragraph(
            "尽管通用大模型拥有强大的语言理解与生成能力，但在面对垂直专业领域（如高精尖工程、医疗、法律）时，仍存在知识时效性不足和“幻觉”（Hallucination）问题。"
            "检索增强生成（RAG, Retrieval-Augmented Generation）技术是解决该问题的核心手段。",
            body_style,
        )
    )

    story.append(Paragraph("1.3.1 RAG 标准三阶段流水线", h2_style))
    rag_steps_table = Table(
        [
            [Paragraph("<b>阶段</b>", box_style), Paragraph("<b>核心流程与关键技术</b>", box_style)],
            [Paragraph("1. 数据预处理与向量化", body_style), Paragraph("PDF/文档解析、自适应分块（Chunking）、语义嵌入（Embedding 模型生成稠密向量）。", body_style)],
            [Paragraph("2. 混合检索与精排", body_style), Paragraph("向量稠密检索（Dense Retrieval）结合 BM25 关键词稀疏检索，通过重排模型（Reranker）获取 Top-K 精确切片。", body_style)],
            [Paragraph("3. 提示词增强与溯源生成", body_style), Paragraph("将检索到的教材段落与用户提问组合，注入 Prompt 并约束大模型严格按资料回答并标记精确来源页码。", body_style)],
        ],
        colWidths=[45 * mm, 129 * mm],
    )
    rag_steps_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(rag_steps_table)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("1.3.2 来源可信度与防幻觉设计", h2_style))
    story.append(
        Paragraph(
            "教学平台中的 RAG 系统必须具备**严格的可核验性**。当检索命中率不足或置信度低于阈值时，系统应明确提示“资料不足或未提及”，"
            "而不是由大模型凭借参数权重随意猜测。每一个知识点答案均应携带原始课件的文件名、章节名和精准页码定位。",
            body_style,
        )
    )

    story.append(PageBreak())

    # ================= PAGE 4 =================
    story.append(Paragraph("1.4 大模型智能体（Agent）体系与教学应用", h1_style))
    story.append(
        Paragraph(
            "AI 智能体（Agent）是大模型从“被动回答”走向“主动任务解决”的关键跃迁。"
            "一个完整的智能体通常由四大核心模块构成：",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>1. 感知与提示工程（Perception）：</b>接收来自用户、环境或传感器的多模态输入，构建上下文提示空间。<br/>"
            "<b>2. 规划能力（Planning）：</b>基于 ReAct（Reasoning + Acting）、Plan-and-Solve 等范式将复杂任务分解为可执行步骤。<br/>"
            "<b>3. 记忆系统（Memory）：</b>分为短期会话记忆（Context Window）与长期持久记忆（向量存储 / 数据库）。<br/>"
            "<b>4. 工具调用（Tool Use / MCP）：</b>通过 Function Calling 调用外部 API、执行代码、操作数据库或驱动教学工作流。",
            body_style,
        )
    )

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("1.5 本章思考与研讨题", h1_style))
    questions_table = Table(
        [[
            Paragraph(
                "<b>思考题 1：</b>为什么在 Transformer 注意力计算中必须除以 sqrt(d_k) 缩放因子？若不缩放会产生什么训练后果？<br/><br/>"
                "<b>思考题 2：</b>对比微调（Fine-Tuning）与 RAG 技术，在专业课教学场景下各自的优缺点是什么？<br/><br/>"
                "<b>思考题 3：</b>设计一个面向高校课程的 AI 助教 Agent，请列出其应具备的工具列表（Tool Definitions）。",
                box_style,
            )
        ]],
        colWidths=[174 * mm],
    )
    questions_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FCD34D")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )
    story.append(questions_table)

    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    print(f"PDF generated successfully at: {OUTPUT_PDF}")
    return OUTPUT_PDF


if __name__ == "__main__":
    build_pdf()

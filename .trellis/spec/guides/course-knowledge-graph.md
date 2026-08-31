# Course Knowledge Graph & Data Baseline Guide

> Domain ontology, knowledge graph nodes, relationships, and courseware normalization.

---

## 1. Domain Ontology & Structure

The knowledge graph models the curriculum of *电力系统储能技术* across 6 chapters:

```text
第1章 概述 (Overview)
  ├── 储能技术分类 (Classification)
  └── 储能技术发展现状 (State of Art)
第2章 电力系统与储能技术的应用 (Power System Applications)
  ├── 发电侧储能 (Generation Side)
  ├── 电网侧储能 (Grid Side)
  └── 用户侧储能 (User Side)
第3章 电力储能系统的组成及工作原理 (System Composition & Principles)
  ├── 抽水蓄能 (Pumped Storage)
  ├── 压缩空气储能 (Compressed Air)
  ├── 飞轮储能 (Flywheel)
  ├── 电化学储能 (Electrochemical - Lithium, Flow Battery)
  └── 超级电容器 (Supercapacitor)
第4章 电力储能系统的规划配置 (Planning & Sizing)
  ├── 容量配置模型 (Capacity Modeling)
  └── 选址定容算法 (Siting & Sizing)
第5章 电力储能系统的接入与运行控制 (Grid Integration & Control)
  ├── 变流器控制 (PCS Control)
  └── 调峰调频协同控制 (Peak Shaving & Frequency Regulation)
第6章 电力储能系统的性能检测与评估 (Testing & Evaluation)
  ├── 循环寿命与效率 (Cycle Life & Efficiency)
  └── 安全与经济性评估 (Safety & Techno-economic Analysis)
```

---

## 2. Knowledge Graph Baseline Metrics

- **Total PDF Documents**: 20 normalized documents (`course-data/normalized/manifest.json`).
- **Total Courseware Pages**: 439 pages.
- **Knowledge Nodes**: 20 key concepts.
- **Relationship Edges**: 17 directed dependency and inclusion edges (`prerequisite_of`, `part_of`, `applies_to`).
- **Baseline Verification**: Run `python3 scripts/verify_course_data.py course-data/normalized` to check ontology consistency.

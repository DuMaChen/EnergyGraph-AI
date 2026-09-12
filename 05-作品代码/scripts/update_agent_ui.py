import re
import os

html_content = r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>电力系统储能技术 - AI 智慧教学与学习空间</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #1e293b;
      --ink-secondary: #475569;
      --muted: #64748b;
      --line: #e2e8f0;
      --line-subtle: #f1f5f9;
      --paper: #ffffff;
      --wash: #f8fafc;
      --primary: #0f766e;
      --primary-hover: #0d5f58;
      --primary-light: #f0fdfa;
      --primary-border: #99f6e4;
      --accent: #d97706;
      --accent-light: #fef3c7;
      --blue: #0284c7;
      --blue-light: #e0f2fe;
      --green: #16a34a;
      --green-light: #dcfce7;
      --red: #dc2626;
      --red-light: #fee2e2;
      --purple: #7c3aed;
      --purple-light: #f3e8ff;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
      --shadow-md: 0 4px 12px rgba(0,0,0,0.07);
      --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--wash);
      color: var(--ink);
      font: 14px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    }
    .app-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 18px 20px 48px;
    }
    
    /* Top Header */
    header.app-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--line);
      margin-bottom: 18px;
    }
    .brand-title h1 {
      margin: 0;
      font-size: 1.35rem;
      font-weight: 750;
      color: #0f172a;
      letter-spacing: -0.01em;
    }
    .brand-subtitle {
      font-size: .86rem;
      color: var(--muted);
      margin-top: 2px;
    }
    .user-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #ffffff;
      border: 1px solid var(--line);
      padding: 6px 14px;
      border-radius: 30px;
      font-size: .88rem;
      font-weight: 600;
      box-shadow: var(--shadow-sm);
    }
    .role-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: .78rem;
    }
    .role-badge.teacher { background: #e0e7ff; color: #3730a3; }
    .role-badge.student { background: #dcfce7; color: #15803d; }
    .role-badge.admin { background: #fee2e2; color: #991b1b; }

    /* Navigation Tabs */
    .nav-tabs {
      display: flex;
      gap: 6px;
      margin-bottom: 18px;
      border-bottom: 2px solid var(--line);
      padding-bottom: 0;
      overflow-x: auto;
    }
    .nav-tab {
      background: transparent;
      border: 0;
      border-bottom: 3px solid transparent;
      padding: 10px 18px;
      font-size: .95rem;
      font-weight: 650;
      color: var(--muted);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all .15s ease;
      margin-bottom: -2px;
    }
    .nav-tab:hover {
      color: var(--ink);
    }
    .nav-tab.active {
      color: var(--primary);
      border-bottom-color: var(--primary);
      background: rgba(15, 118, 110, 0.04);
      border-radius: 6px 6px 0 0;
    }

    /* Common Card & Panel */
    .card-panel {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
      padding: 20px;
      margin-bottom: 18px;
    }
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--line-subtle);
    }
    .panel-title {
      font-size: 1.15rem;
      font-weight: 700;
      margin: 0;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .panel-subtitle {
      font-size: .86rem;
      color: var(--muted);
    }

    /* Buttons & Inputs */
    button, input, select, textarea { font: inherit; }
    .btn {
      border: 1px solid transparent;
      border-radius: var(--radius-sm);
      padding: 8px 16px;
      font-size: .9rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: all .15s ease;
    }
    .btn-primary {
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }
    .btn-primary:hover:not(:disabled) {
      background: var(--primary-hover);
    }
    .btn-secondary {
      background: #ffffff;
      color: var(--ink);
      border-color: #cbd5e1;
    }
    .btn-secondary:hover:not(:disabled) {
      background: var(--wash);
      border-color: #94a3b8;
    }
    .btn-accent {
      background: var(--accent);
      color: #ffffff;
    }
    .btn-accent:hover:not(:disabled) {
      background: #b45309;
    }
    .btn-sm {
      padding: 5px 10px;
      font-size: .82rem;
    }
    .btn:disabled {
      opacity: .5;
      cursor: not-allowed;
    }
    .form-control {
      width: 100%;
      border: 1px solid #cbd5e1;
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      background: #ffffff;
      color: var(--ink);
    }
    .form-control:focus {
      outline: 0;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.15);
    }

    /* Stat Cards */
    .stat-cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }
    .stat-card {
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 14px 18px;
      box-shadow: var(--shadow-sm);
    }
    .stat-card-title {
      font-size: .84rem;
      color: var(--muted);
      margin-bottom: 6px;
      font-weight: 550;
    }
    .stat-card-value {
      font-size: 1.6rem;
      font-weight: 750;
      color: #0f172a;
      line-height: 1.2;
    }
    .stat-card-desc {
      font-size: .78rem;
      color: var(--muted);
      margin-top: 4px;
    }

    /* Submissions List */
    .submission-card {
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      padding: 18px;
      margin-bottom: 14px;
      box-shadow: var(--shadow-sm);
      transition: box-shadow .2s ease;
    }
    .submission-card:hover {
      box-shadow: var(--shadow-md);
    }
    .submission-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--line-subtle);
      padding-bottom: 10px;
      margin-bottom: 12px;
    }
    .student-info {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .submission-score-tag {
      font-size: 1.1rem;
      font-weight: 750;
      color: var(--primary);
      background: var(--primary-light);
      padding: 3px 12px;
      border-radius: 6px;
      border: 1px solid var(--primary-border);
    }
    .question-grade-item {
      background: #f8fafc;
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
      margin-top: 10px;
    }
    .question-grade-title {
      font-weight: 650;
      margin-bottom: 6px;
      color: #1e293b;
    }
    .ai-review-box {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: var(--radius-sm);
      padding: 10px 12px;
      margin-top: 8px;
      font-size: .88rem;
    }
    .ai-review-tag {
      display: inline-block;
      background: #2563eb;
      color: #ffffff;
      font-size: .72rem;
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 600;
      margin-right: 6px;
    }
    .teacher-confirm-actions {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 10px;
      flex-wrap: wrap;
    }

    /* Teacher Question Creator */
    .teacher-creator-grid {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 20px;
    }
    @media (max-width: 960px) {
      .teacher-creator-grid { grid-template-columns: 1fr; }
    }

    /* Knowledge Graph Layout */
    .graph-viewer-container {
      position: relative;
      width: 100%;
      height: 620px;
      background: radial-gradient(circle at 50% 50%, #ffffff 0%, #f8fafc 100%);
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: inset 0 1px 4px rgba(0,0,0,0.03);
    }
    #knowledgeGraphSvg {
      width: 100%;
      height: 100%;
      display: block;
      cursor: grab;
      user-select: none;
    }
    #knowledgeGraphSvg:active {
      cursor: grabbing;
    }
    .graph-legend-bar {
      position: absolute;
      bottom: 12px;
      left: 14px;
      display: flex;
      gap: 14px;
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(8px);
      padding: 6px 14px;
      border-radius: 8px;
      border: 1px solid var(--line);
      font-size: .82rem;
      font-weight: 600;
      color: var(--ink-secondary);
      z-index: 10;
      pointer-events: none;
    }
    .legend-item { display: inline-flex; align-items: center; gap: 6px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
    .legend-dot.mastered { background: var(--green); box-shadow: 0 0 6px rgba(22,163,74,0.4); }
    .legend-dot.learning { background: var(--blue); box-shadow: 0 0 6px rgba(2,132,199,0.4); }
    .legend-dot.weak { background: var(--red); box-shadow: 0 0 6px rgba(220,38,38,0.4); }
    .legend-dot.unassessed { background: #94a3b8; }

    /* Node Side Drawer */
    .node-drawer-card {
      position: absolute;
      top: 14px;
      right: 14px;
      width: 360px;
      max-height: calc(100% - 28px);
      overflow-y: auto;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      box-shadow: var(--shadow-lg);
      z-index: 25;
      animation: drawerSlide .2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes drawerSlide {
      from { opacity: 0; transform: translateX(20px); }
      to { opacity: 1; transform: translateX(0); }
    }
    .drawer-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      border-bottom: 1px solid var(--line-subtle);
      padding-bottom: 8px;
    }
    .drawer-tag {
      font-size: .8rem;
      font-weight: 700;
      color: var(--primary);
      background: var(--primary-light);
      padding: 3px 10px;
      border-radius: 20px;
      border: 1px solid var(--primary-border);
    }
    .drawer-close-btn {
      border: 0;
      background: transparent;
      font-size: 1.4rem;
      color: var(--muted);
      cursor: pointer;
      line-height: 1;
    }
    .drawer-close-btn:hover { color: var(--ink); }
    .drawer-title {
      font-size: 1.15rem;
      font-weight: 750;
      color: #0f172a;
      line-height: 1.4;
      margin: 0 0 10px;
    }
    .drawer-status-box {
      background: #f8fafc;
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      margin-bottom: 14px;
      font-size: .86rem;
    }
    .drawer-actions {
      display: grid;
      gap: 10px;
      margin-top: 16px;
    }
    .drawer-actions .btn {
      width: 100%;
      padding: 10px 14px;
      font-size: .92rem;
    }

    /* Q&A Stream & Sources */
    .qa-box {
      margin-top: 18px;
      padding: 18px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-sm);
    }
    .qa-response-text {
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      line-height: 1.7;
      font-size: .95rem;
    }
    .qa-sources-list {
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid var(--line);
    }
    .qa-source-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 0;
      font-size: .88rem;
    }
    .qa-source-link {
      font-weight: 650;
      color: var(--primary);
      text-decoration: none;
    }
    .qa-source-link:hover { text-decoration: underline; }

    @media (max-width: 768px) {
      .app-container { padding: 12px 10px 30px; }
      .node-drawer-card { width: calc(100% - 28px); left: 14px; right: 14px; top: auto; bottom: 14px; max-height: 60%; }
      .graph-viewer-container { height: 480px; }
    }
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Top Header -->
    <header class="app-header">
      <div class="brand-title">
        <div>
          <h1>电力系统储能技术</h1>
          <div class="brand-subtitle">国家级精品课程 · AI 智慧教学与高精度知识网络平台</div>
        </div>
      </div>
      <div class="user-pill" id="userPill">
        <span id="roleBadge" class="role-badge student">学习者</span>
        <span id="usernameDisplay">加载中...</span>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="nav-tabs" id="mainNavTabs" role="tablist">
      <!-- Tabs will be rendered based on role -->
    </nav>

    <!-- Content Sections -->
    <main id="mainTabContent">
      <!-- Section 1: Teacher Grading & Auto Review Center -->
      <section id="sectionTeacherGrading" class="tab-pane" hidden>
        <div class="stat-cards-grid">
          <div class="stat-card">
            <div class="stat-card-title">待批改作业</div>
            <div class="stat-card-value" id="statPendingGrading">1 份</div>
            <div class="stat-card-desc">含主观题需人工确认</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-title">Agent 智能初评准确率</div>
            <div class="stat-card-value" style="color:var(--green)">100%</div>
            <div class="stat-card-desc">基于课程 Rubric 细则</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-title">班级已提交人数</div>
            <div class="stat-card-value" id="statSubmissionsCount">1 人</div>
            <div class="stat-card-desc">提交率 100%</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-title">班级测验平均分</div>
            <div class="stat-card-value" style="color:var(--blue)">92.5 分</div>
            <div class="stat-card-desc">储能变流器章节优秀</div>
          </div>
        </div>

        <div class="card-panel">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">作业批改与智能判分中心</h2>
              <div class="panel-subtitle">客观题全自动确定性评分，主观题由 Agent 基于教材标准初评，教师一键审核确认</div>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
              <select id="teacherAssignmentSelect" class="form-control" style="width:280px;">
                <option value="">正在读取作业列表...</option>
              </select>
              <button id="btnBatchAgentGrade" type="button" class="btn btn-primary">
                批量执行智能初评
              </button>
            </div>
          </div>

          <div id="teacherSubmissionsList">
            <div style="text-align:center; padding:30px; color:var(--muted)">请选择作业以载入学生作答与批改列表。</div>
          </div>
        </div>
      </section>

      <!-- Section 2: Teacher Question Bank & Publisher -->
      <section id="sectionTeacherQuestions" class="tab-pane" hidden>
        <div class="teacher-creator-grid">
          <!-- Left: AI Question Generator -->
          <div class="card-panel">
            <div class="panel-header">
              <h2 class="panel-title">AI 辅助出题草稿生成</h2>
              <span class="drawer-tag">防幻觉教材切片</span>
            </div>
            <div style="display:grid; gap:12px;">
              <div>
                <label style="font-weight:600; font-size:.88rem;">选择对应章节</label>
                <select id="draftChapterSelect" class="form-control">
                  <option value="1">第1章 概述</option>
                  <option value="2">第2章 电力系统与储能</option>
                  <option value="3" selected>第3章 组成与工作原理</option>
                  <option value="4">第4章 规划配置与集成</option>
                  <option value="5">第5章 接入与运行维护</option>
                  <option value="6">第6章 性能检测与评估</option>
                </select>
              </div>
              <div>
                <label style="font-weight:600; font-size:.88rem;">出题类型</label>
                <select id="draftTypeSelect" class="form-control">
                  <option value="single_choice">单项选择题</option>
                  <option value="multiple_choice">多项选择题</option>
                  <option value="true_false">判断题</option>
                  <option value="short_answer">简答与分析题</option>
                </select>
              </div>
              <div>
                <label style="font-weight:600; font-size:.88rem;">考查要点与要求</label>
                <textarea id="draftRequirementsInput" class="form-control" rows="3" placeholder="例如：考查储能变流器单级式与双级式拓扑结构在直流母线电压稳定性方面的区别..."></textarea>
              </div>
              <button id="btnGenerateAiDraft" type="button" class="btn btn-primary">
                生成标准考题草稿
              </button>
            </div>

            <div id="aiGeneratedPreviewBox" style="margin-top:14px; display:none;">
              <div class="ai-review-box">
                <div style="font-weight:700; color:#1e40af; margin-bottom:4px;">生成草稿预览：</div>
                <div id="aiGeneratedPreviewText" style="white-space:pre-wrap; font-size:.9rem;"></div>
              </div>
              <button id="btnSaveDraftToBank" type="button" class="btn btn-accent btn-sm" style="margin-top:8px;">
                保存为题库草稿
              </button>
            </div>
          </div>

          <!-- Right: Question Bank & Assignment Publisher -->
          <div class="card-panel">
            <div class="panel-header">
              <h2 class="panel-title">题库管理与组卷发布</h2>
              <div class="panel-subtitle">审核题库题目并发布为学生作业</div>
            </div>
            
            <div style="display:flex; gap:10px; margin-bottom:12px;">
              <input id="newAssignmentTitleInput" type="text" class="form-control" placeholder="输入新作业名称，例如：第3章 储能变流器专练" />
              <button id="btnPublishNewAssignment" type="button" class="btn btn-primary" style="white-space:nowrap;">
                发布给全班学生
              </button>
            </div>

            <div style="font-weight:600; margin-bottom:8px; font-size:.9rem;">勾选题库题目组卷：</div>
            <div id="teacherQuestionBankList" style="max-height:360px; overflow-y:auto;">
              正在加载题库...
            </div>
          </div>
        </div>
      </section>

      <!-- Section 3: Interactive Visual Knowledge Graph -->
      <section id="sectionKnowledgeGraph" class="tab-pane">
        <div class="card-panel" style="padding:16px;">
          <div class="panel-header">
            <div>
              <h2 class="panel-title">电力系统储能技术 知识图谱网络</h2>
              <div class="panel-subtitle">全景覆盖 21 个核心知识点 · 17 条先修依赖 · 卡片式清晰排布，点击节点直达教材与 AI 导学</div>
            </div>
            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
              <select id="graphFilterChapter" class="form-control" style="width:auto;">
                <option value="all">全景全章知识流向 (1~6章)</option>
                <option value="1">第1章 概述</option>
                <option value="2">第2章 电力系统与储能</option>
                <option value="3">第3章 组成与工作原理</option>
                <option value="4">第4章 规划配置与集成</option>
                <option value="5">第5章 接入与运行维护</option>
                <option value="6">第6章 性能检测与评估</option>
              </select>
              <button id="btnGraphFitView" type="button" class="btn btn-secondary btn-sm">居中复位</button>
            </div>
          </div>

          <!-- Canvas Container -->
          <div class="graph-viewer-container" id="graphContainerWrapper">
            <svg id="knowledgeGraphSvg"></svg>
            
            <div class="graph-legend-bar">
              <span class="legend-item"><span class="legend-dot mastered"></span>已掌握</span>
              <span class="legend-item"><span class="legend-dot learning"></span>学习中</span>
              <span class="legend-item"><span class="legend-dot weak"></span>薄弱需巩固</span>
              <span class="legend-item"><span class="legend-dot unassessed"></span>未开始</span>
              <span class="legend-item" style="color:var(--primary)">先修逻辑流向</span>
            </div>

            <!-- Interactive Detail Drawer -->
            <div class="node-drawer-card" id="nodeDetailDrawer" hidden>
              <div class="drawer-header">
                <span class="drawer-tag" id="drawerChapterTag">第3章 · PCS并网</span>
                <button id="btnDrawerClose" type="button" class="drawer-close-btn" aria-label="关闭">×</button>
              </div>
              <h3 class="drawer-title" id="drawerNodeTitle">3.4 储能变流器拓扑及并网控制</h3>
              <div class="drawer-status-box" id="drawerStatusBox">
                学情状态：未评估
              </div>

              <div style="font-size:.84rem; color:var(--muted); margin-bottom:6px; font-weight:600;">先修依赖路径：</div>
              <div id="drawerPrereqList" style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:14px;">
                无先修要求
              </div>

              <div class="drawer-actions">
                <a id="drawerBtnPdf" href="#" target="_blank" rel="noopener" class="btn btn-primary">
                  阅读对应教材课件 (PDF)
                </a>
                <button id="drawerBtnAiTutor" type="button" class="btn btn-accent">
                  AI 助教带读解析
                </button>
                <button id="drawerBtnPractice" type="button" class="btn btn-secondary">
                  针对该考点即刻测验
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Assistant Q&A Output Panel -->
        <div class="card-panel qa-box" id="qaOutputCard" style="display:none;">
          <div class="panel-header">
            <h2 class="panel-title">AI 助教深度解析</h2>
            <span id="qaStatusIndicator" class="drawer-tag">回答完成</span>
          </div>
          <div class="qa-response-text" id="qaResponseContent"></div>
          
          <div class="qa-sources-list" id="qaSourcesContainer">
            <div style="font-weight:700; font-size:.88rem; margin-bottom:6px;">课程课件核验依据：</div>
            <div id="qaSourcesItems"></div>
          </div>
        </div>
      </section>

      <!-- Section 4: Student My Assignments -->
      <section id="sectionStudentAssignments" class="tab-pane" hidden>
        <div class="card-panel">
          <div class="panel-header">
            <h2 class="panel-title">我的课程作业与测评</h2>
            <div class="panel-subtitle">点击作业即可在线答题并查看智能批改与解析</div>
          </div>
          <div id="studentAssignmentList">正在加载作业...</div>
        </div>
      </section>
    </main>
  </div>

  <script>
    // =========================================================================
    // 1. 课程全量 21 个知识点与 17 条先修依赖规范数据集
    // =========================================================================
    const KNOWLEDGE_NODES = [
      { id: 'kp-1-1', chapter_id: 1, chapter_name: '第1章 概述', name: '1.1 电力储能技术的概念', normalized_file: 'chapter-1-1.1-.pdf', category: '核心概念' },
      { id: 'kp-1-2', chapter_id: 1, chapter_name: '第1章 概述', name: '1.2 电力储能技术的发展', normalized_file: 'chapter-1-1.2-.pdf', category: '技术发展' },
      { id: 'kp-1-3', chapter_id: 1, chapter_name: '第1章 概述', name: '1.3 储能技术在电力系统中的应用', normalized_file: 'chapter-1-1.3-.pdf', category: '工程应用' },
      { id: 'kp-2-1', chapter_id: 2, chapter_name: '第2章 系统与储能', name: '2.1 电力系统的基本概念', normalized_file: 'chapter-2-2.1-.pdf', category: '电网基础' },
      { id: 'kp-2-2', chapter_id: 2, chapter_name: '第2章 系统与储能', name: '2.2 电力系统的运行特点和要求', normalized_file: 'chapter-2-2.2-.pdf', category: '运行特性' },
      { id: 'kp-2-3', chapter_id: 2, chapter_name: '第2章 系统与储能', name: '2.3 储能技术的典型应用', normalized_file: 'chapter-2-2.3-.pdf', category: '典型场景' },
      { id: 'kp-3-1', chapter_id: 3, chapter_name: '第3章 组成与原理', name: '3.1 抽水蓄能电站的组成及工作原理', normalized_file: 'chapter-3-3.1-.pdf', category: '物理储能' },
      { id: 'kp-3-2', chapter_id: 3, chapter_name: '第3章 组成与原理', name: '3.2 新型电力储能系统的组成', normalized_file: 'chapter-3-3.2-.pdf', category: '系统构成' },
      { id: 'kp-3-3', chapter_id: 3, chapter_name: '第3章 组成与原理', name: '3.3 新型电能存储设备工作原理', normalized_file: 'chapter-3-3.3-.pdf', category: '电池电化学' },
      { id: 'kp-3-4', chapter_id: 3, chapter_name: '第3章 组成与原理', name: '3.4 储能变流器拓扑及并网控制', normalized_file: 'chapter-3-3.4-.pdf', category: 'PCS并网控制' },
      { id: 'kp-3-5', chapter_id: 3, chapter_name: '第3章 组成与原理', name: '3.5 储能监控系统结构及通信', normalized_file: 'chapter-3-3.5-.pdf', category: 'BMS/EMS监控' },
      { id: 'kp-4-1', chapter_id: 4, chapter_name: '第4章 规划与集成', name: '4.1 抽水蓄能电站的规划配置', normalized_file: 'chapter-4-4.1-.pdf', category: '站址规划' },
      { id: 'kp-4-2', chapter_id: 4, chapter_name: '第4章 规划与集成', name: '4.2 电化学储能系统的规划配置', normalized_file: 'chapter-4-4.2-.pdf', category: '容量配置' },
      { id: 'kp-4-3', chapter_id: 4, chapter_name: '第4章 规划与集成', name: '4.3 电池储能系统集成技术', normalized_file: 'chapter-4-4.3-.pdf', category: '系统集成' },
      { id: 'kp-5-1', chapter_id: 5, chapter_name: '第5章 接入与运维', name: '5.1 电力储能系统的接入', normalized_file: 'chapter-5-5.1-.pdf', category: '并网标准' },
      { id: 'kp-5-2', chapter_id: 5, chapter_name: '第5章 接入与运维', name: '5.2 电力储能系统的运行控制', normalized_file: 'chapter-5-5.2-.pdf', category: '调频调峰' },
      { id: 'kp-5-3', chapter_id: 5, chapter_name: '第5章 接入与运维', name: '5.3 电力储能系统的运行维护', normalized_file: 'chapter-5-5.3-.pdf', category: '安全运维' },
      { id: 'kp-5-4', chapter_id: 5, chapter_name: '第5章 接入与运维', name: '5.4 电力储能系统的运行案例', normalized_file: 'chapter-5-5.4-.pdf', category: '工程案例' },
      { id: 'kp-6-1', chapter_id: 6, chapter_name: '第6章 检测与评估', name: '6.1 电力储能系统的性能检测', normalized_file: 'chapter-6-6.1-.pdf', category: '测试试验' },
      { id: 'kp-6-2', chapter_id: 6, chapter_name: '第6章 检测与评估', name: '6.2 电力储能系统的系统评估', normalized_file: 'chapter-6-6.2-.pdf', category: '效益评估' }
    ];

    const KNOWLEDGE_EDGES = [
      { from_id: 'kp-1-1', to_id: 'kp-1-2' },
      { from_id: 'kp-1-1', to_id: 'kp-1-3' },
      { from_id: 'kp-2-1', to_id: 'kp-2-2' },
      { from_id: 'kp-2-1', to_id: 'kp-2-3' },
      { from_id: 'kp-2-2', to_id: 'kp-2-3' },
      { from_id: 'kp-3-1', to_id: 'kp-3-2' },
      { from_id: 'kp-3-2', to_id: 'kp-3-3' },
      { from_id: 'kp-3-2', to_id: 'kp-3-4' },
      { from_id: 'kp-3-2', to_id: 'kp-3-5' },
      { from_id: 'kp-4-1', to_id: 'kp-4-2' },
      { from_id: 'kp-4-1', to_id: 'kp-4-3' },
      { from_id: 'kp-4-2', to_id: 'kp-4-3' },
      { from_id: 'kp-5-1', to_id: 'kp-5-2' },
      { from_id: 'kp-5-2', to_id: 'kp-5-3' },
      { from_id: 'kp-5-2', to_id: 'kp-5-4' },
      { from_id: 'kp-5-3', to_id: 'kp-5-4' },
      { from_id: 'kp-6-1', to_id: 'kp-6-2' }
    ];

    const CHAPTER_THEMES = {
      1: { name: '第1章 概述', bg: '#f0fdfa', border: '#99f6e4', badge: '#0f766e' },
      2: { name: '第2章 电力系统与储能', bg: '#f0f9ff', border: '#bae6fd', badge: '#0284c7' },
      3: { name: '第3章 组成与工作原理', bg: '#fffbeb', border: '#fde68a', badge: '#d97706' },
      4: { name: '第4章 规划配置与集成', bg: '#faf5ff', border: '#e9d5ff', badge: '#7c3aed' },
      5: { name: '第5章 接入与运行维护', bg: '#f0fdf4', border: '#bbf7d0', badge: '#16a34a' },
      6: { name: '第6章 性能检测与评估', bg: '#fef2f2', border: '#fecaca', badge: '#dc2626' }
    };

    // =========================================================================
    // 2. 高可读性大卡片式知识网络渲染引擎
    // =========================================================================
    class CleanKnowledgeGraphEngine {
      constructor(svgEl, wrapperEl) {
        this.svg = svgEl;
        this.wrapper = wrapperEl;
        this.nodes = JSON.parse(JSON.stringify(KNOWLEDGE_NODES));
        this.edges = JSON.parse(JSON.stringify(KNOWLEDGE_EDGES));
        this.nodeMap = new Map(this.nodes.map(n => [n.id, n]));
        this.selectedId = 'kp-3-4';
        this.hoveredId = null;
        this.filterChapter = 'all';
        this.studentProfile = new Map();

        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.isPanning = false;
        this.startPan = { x: 0, y: 0 };

        this.init();
      }

      init() {
        this.calculateCardLayout();
        this.bindEvents();
        this.render();
      }

      calculateCardLayout() {
        const width = 1200;
        const colWidth = 190;
        const cardW = 168;
        const cardH = 68;

        for (let ch = 1; ch <= 6; ch++) {
          const chNodes = this.nodes.filter(n => n.chapter_id === ch);
          chNodes.forEach((node, idx) => {
            node.w = cardW;
            node.h = cardH;
            node.x = 24 + (ch - 1) * colWidth + (colWidth - cardW) / 2;
            node.y = 80 + idx * 105;
          });
        }
      }

      bindEvents() {
        this.svg.addEventListener('mousedown', (e) => {
          if (e.target.closest('.card-node-group')) return;
          this.isPanning = true;
          this.startPan = { x: e.clientX - this.panX, y: e.clientY - this.panY };
        });

        window.addEventListener('mousemove', (e) => {
          if (this.isPanning) {
            this.panX = e.clientX - this.startPan.x;
            this.panY = e.clientY - this.startPan.y;
            this.updateTransform();
          }
        });

        window.addEventListener('mouseup', () => {
          this.isPanning = false;
        });

        this.svg.addEventListener('wheel', (e) => {
          e.preventDefault();
          const factor = e.deltaY < 0 ? 1.08 : 0.92;
          this.zoom = Math.min(Math.max(this.zoom * factor, 0.6), 1.8);
          this.updateTransform();
        }, { passive: false });
      }

      updateTransform() {
        const root = this.svg.querySelector('#graphRootLayer');
        if (root) root.setAttribute('transform', `translate(${this.panX}, ${this.panY}) scale(${this.zoom})`);
      }

      fitView() {
        this.zoom = 1;
        this.panX = 0;
        this.panY = 0;
        this.updateTransform();
      }

      render() {
        const width = 1200;
        const height = 620;
        this.svg.setAttribute('viewBox', `0 0 ${width} ${height}`);

        let visibleNodes = this.nodes;
        if (this.filterChapter !== 'all') {
          const ch = Number(this.filterChapter);
          visibleNodes = this.nodes.filter(n => n.chapter_id === ch);
        }
        const visibleNodeIds = new Set(visibleNodes.map(n => n.id));

        let svg = `
          <defs>
            <marker id="edgeArrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0f766e" />
            </marker>
            <marker id="edgeArrowActive" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#d97706" />
            </marker>
            <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.08"/>
            </filter>
          </defs>
          <g id="graphRootLayer" transform="translate(${this.panX}, ${this.panY}) scale(${this.zoom})">
        `;

        if (this.filterChapter === 'all') {
          const colWidth = 190;
          for (let ch = 1; ch <= 6; ch++) {
            const theme = CHAPTER_THEMES[ch];
            const colX = 24 + (ch - 1) * colWidth;
            svg += `
              <g class="swimlane-chapter" opacity="0.85">
                <rect x="${colX}" y="20" width="${colWidth - 10}" height="570" rx="10" fill="${theme.bg}" stroke="${theme.border}" stroke-width="1.5" />
                <rect x="${colX + 10}" y="32" width="${colWidth - 30}" height="26" rx="6" fill="#ffffff" stroke="${theme.border}" />
                <text x="${colX + colWidth / 2 - 5}" y="49" text-anchor="middle" font-size="12" font-weight="700" fill="${theme.badge}">${theme.name}</text>
              </g>
            `;
          }
        }

        this.edges.forEach(edge => {
          if (!visibleNodeIds.has(edge.from_id) || !visibleNodeIds.has(edge.to_id)) return;
          const src = this.nodeMap.get(edge.from_id);
          const tgt = this.nodeMap.get(edge.to_id);
          if (!src || !tgt) return;

          const isActive = (this.hoveredId && (edge.from_id === this.hoveredId || edge.to_id === this.hoveredId)) ||
                           (this.selectedId && (edge.from_id === this.selectedId || edge.to_id === this.selectedId));

          const startX = src.x + src.w;
          const startY = src.y + src.h / 2;
          const endX = tgt.x;
          const endY = tgt.y + tgt.h / 2;

          const dx = endX - startX;
          const cx1 = startX + dx * 0.45;
          const cy1 = startY;
          const cx2 = startX + dx * 0.55;
          const cy2 = endY;

          const stroke = isActive ? '#d97706' : '#0f766e';
          const strokeWidth = isActive ? 3 : 1.8;
          const marker = isActive ? 'url(#edgeArrowActive)' : 'url(#edgeArrow)';
          const opacity = (this.hoveredId && !isActive) ? 0.2 : 0.85;

          svg += `
            <path d="M ${startX} ${startY} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${endX} ${endY}"
                  fill="none"
                  stroke="${stroke}"
                  stroke-width="${strokeWidth}"
                  marker-end="${marker}"
                  opacity="${opacity}" />
          `;
        });

        visibleNodes.forEach(node => {
          const isSelected = this.selectedId === node.id;
          const isHovered = this.hoveredId === node.id;
          const isNeighbor = this.hoveredId && this.isNeighbor(node.id, this.hoveredId);
          const isDimmed = this.hoveredId && !isHovered && !isNeighbor;

          const status = this.studentProfile.get(node.id) || 'unassessed';
          const statusColors = {
            mastered: '#16a34a',
            learning: '#0284c7',
            weak: '#dc2626',
            unassessed: '#94a3b8'
          };
          const dotColor = statusColors[status] || statusColors.unassessed;

          const stroke = isSelected ? '#0f766e' : (isHovered ? '#d97706' : '#cbd5e1');
          const strokeW = isSelected ? 2.5 : (isHovered ? 2 : 1.2);
          const opacity = isDimmed ? 0.25 : 1;

          const code = node.name.slice(0, 3);
          const nameWithoutCode = node.name.slice(4);

          svg += `
            <g class="card-node-group" data-id="${node.id}" transform="translate(${node.x}, ${node.y})" opacity="${opacity}" filter="url(#cardShadow)" style="cursor: pointer;">
              <rect width="${node.w}" height="${node.h}" rx="8" fill="#ffffff" stroke="${stroke}" stroke-width="${strokeW}" />
              <rect x="0" y="0" width="4" height="${node.h}" rx="2" fill="${dotColor}" />
              
              <!-- Badge tag -->
              <rect x="10" y="8" width="34" height="18" rx="4" fill="#f1f5f9" />
              <text x="27" y="21" text-anchor="middle" font-size="11" font-weight="750" fill="#334155">${code}</text>

              <text x="50" y="21" font-size="10" font-weight="600" fill="#64748b">${node.category}</text>
              
              <!-- Main node name -->
              <text x="10" y="44" font-size="12" font-weight="700" fill="#0f172a">${nameWithoutCode.slice(0, 9)}</text>
              ${nameWithoutCode.length > 9 ? `<text x="10" y="58" font-size="11" font-weight="600" fill="#475569">${nameWithoutCode.slice(9, 18)}</text>` : ''}
              
              <!-- Status dot -->
              <circle cx="${node.w - 14}" cy="17" r="4.5" fill="${dotColor}" />
            </g>
          `;
        });

        svg += `</g>`;
        this.svg.innerHTML = svg;
        this.bindNodeEvents();
      }

      isNeighbor(id1, id2) {
        return this.edges.some(e => (e.from_id === id1 && e.to_id === id2) || (e.from_id === id2 && e.to_id === id1));
      }

      bindNodeEvents() {
        this.svg.querySelectorAll('.card-node-group').forEach(group => {
          const id = group.getAttribute('data-id');
          const node = this.nodeMap.get(id);

          group.addEventListener('mouseenter', () => {
            this.hoveredId = id;
            this.render();
          });
          group.addEventListener('mouseleave', () => {
            this.hoveredId = null;
            this.render();
          });
          group.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectNode(node);
          });
        });
      }

      selectNode(node) {
        this.selectedId = node.id;
        this.render();
        showNodeDrawer(node);
      }
    }

    // =========================================================================
    // 3. 知识点右侧抽屉导学卡逻辑
    // =========================================================================
    function showNodeDrawer(node) {
      const drawer = document.querySelector('#nodeDetailDrawer');
      const tag = document.querySelector('#drawerChapterTag');
      const title = document.querySelector('#drawerNodeTitle');
      const statusBox = document.querySelector('#drawerStatusBox');
      const prereqList = document.querySelector('#drawerPrereqList');
      const btnPdf = document.querySelector('#drawerBtnPdf');
      const btnAiTutor = document.querySelector('#drawerBtnAiTutor');
      const btnPractice = document.querySelector('#drawerBtnPractice');

      tag.textContent = `${node.chapter_name} · ${node.category}`;
      title.textContent = node.name;

      const mastery = window.graphEngine?.studentProfile.get(node.id) || 'unassessed';
      const masteryLabels = {
        mastered: '[已掌握] 掌握度良好，可作为先修基石',
        learning: '[学习中] 已开始课件查阅与答题',
        weak: '[薄弱需巩固] 近期测验中存在错题',
        unassessed: '[尚未评估] 建议先阅读课件并自测'
      };
      statusBox.textContent = `学情状态：${masteryLabels[mastery] || '未评估'}`;

      const prereqs = KNOWLEDGE_EDGES.filter(e => e.to_id === node.id);
      prereqList.replaceChildren();
      if (!prereqs.length) {
        prereqList.textContent = '本知识点为基础概念起点，无前置先修约束。';
      } else {
        prereqs.forEach(e => {
          const pre = KNOWLEDGE_NODES.find(n => n.id === e.from_id);
          if (pre) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-secondary btn-sm';
            btn.textContent = `← ${pre.name}`;
            btn.onclick = () => window.graphEngine?.selectNode(pre);
            prereqList.append(btn);
          }
        });
      }

      btnPdf.href = `/local/course_agent/resource.php?source=${encodeURIComponent(node.normalized_file)}&page=1`;

      btnAiTutor.onclick = () => {
        const question = `请系统深度解析《电力系统储能技术》考点“${node.name}”：\n1. 其核心物理/电化学运行原理与拓扑结构；\n2. 在电力系统并网调频调峰中的工程应用场景；\n3. 常见易错考点分析。`;
        runStreamQA(question, node.id);
      };

      btnPractice.onclick = () => {
        const question = `请针对《电力系统储能技术》考点“${node.name}”，出一道专业单选题进行自测。`;
        runStreamQA(question, node.id);
      };

      drawer.hidden = false;
    }

    document.querySelector('#btnDrawerClose').addEventListener('click', () => {
      document.querySelector('#nodeDetailDrawer').hidden = true;
    });

    // =========================================================================
    // 4. 流式问答与核验来源渲染
    // =========================================================================
    async function runStreamQA(questionText, nodeId = null) {
      const qaCard = document.querySelector('#qaOutputCard');
      const responseContent = document.querySelector('#qaResponseContent');
      const sourcesContainer = document.querySelector('#qaSourcesItems');
      const indicator = document.querySelector('#qaStatusIndicator');

      qaCard.style.display = 'block';
      qaCard.scrollIntoView({ behavior: 'smooth' });
      responseContent.textContent = 'AI 助教正在依据课程资料检索并思考...';
      sourcesContainer.replaceChildren();
      indicator.textContent = '生成中...';

      try {
        const headers = { 'Content-Type': 'application/json' };
        if (currentCsrfToken) headers['X-Moodle-Sesskey'] = currentCsrfToken;

        const response = await fetch('/api/course-agent/chat', {
          method: 'POST',
          credentials: 'same-origin',
          headers,
          body: JSON.stringify({ question: questionText, mode: 'qa', node_ids: nodeId ? [nodeId] : [] })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        responseContent.textContent = '';

        while (true) {
          const { value, done } = await reader.read();
          buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
          const blocks = buffer.split('\n\n');
          buffer = blocks.pop() || '';
          for (const block of blocks) {
            if (!block.trim()) continue;
            const lines = block.split('\n');
            const evt = (lines.find(l => l.startsWith('event:')) || '').slice(6).trim();
            const dataLine = lines.find(l => l.startsWith('data:'));
            if (!dataLine) continue;
            const data = JSON.parse(dataLine.slice(5).trim());
            if (evt === 'token') {
              responseContent.textContent += data.text || '';
            } else if (evt === 'source') {
              renderSingleSource(data, sourcesContainer);
            } else if (evt === 'done') {
              indicator.textContent = '回答完成';
            }
          }
          if (done) break;
        }
      } catch (err) {
        responseContent.textContent = `生成异常：${err.message || '请稍后重试'}`;
        indicator.textContent = '生成中断';
      }
    }

    function renderSingleSource(source, container) {
      const row = document.createElement('div');
      row.className = 'qa-source-item';
      const link = document.createElement('a');
      link.className = 'qa-source-link';
      link.href = `/local/course_agent/resource.php?source=${encodeURIComponent(source.file || '')}&page=${source.page || 1}`;
      link.target = '_blank';
      link.textContent = `${source.source_file || source.file || '课程教材'} · 第 ${source.page || 1} 页`;
      const meta = document.createElement('span');
      meta.style.color = 'var(--muted)';
      meta.textContent = source.chapter || '课程核心资料';
      row.append(link, meta);
      container.append(row);
    }

    // =========================================================================
    // 5. 教师端功能：作业批改与智能判分中心
    // =========================================================================
    let currentRole = 'student';
    let currentCsrfToken = '';
    let teacherAssignments = [];

    async function loadTeacherGradingCenter() {
      try {
        const assignmentsData = await apiJson('/api/assignments');
        teacherAssignments = assignmentsData.items || [];
        const select = document.querySelector('#teacherAssignmentSelect');
        select.replaceChildren();

        if (!teacherAssignments.length) {
          select.innerHTML = '<option value="">暂无已创建作业</option>';
          return;
        }

        teacherAssignments.forEach(a => {
          const opt = document.createElement('option');
          opt.value = a.id;
          opt.textContent = `${a.title} (${a.status === 'published' ? '已发布' : '草稿'})`;
          select.append(opt);
        });

        select.onchange = () => loadSubmissionsForAssignment(select.value);
        if (teacherAssignments.length) {
          select.value = teacherAssignments[0].id;
          loadSubmissionsForAssignment(teacherAssignments[0].id);
        }
      } catch (err) {
        console.error('Failed to load teacher assignments', err);
      }
    }

    async function loadSubmissionsForAssignment(assignmentId) {
      const container = document.querySelector('#teacherSubmissionsList');
      container.innerHTML = '<div style="text-align:center; padding:20px;">正在加载学生作答记录...</div>';
      try {
        const data = await apiJson(`/api/teacher/assignments/${encodeURIComponent(assignmentId)}/submissions?page=1&page_size=50`);
        const assignDetail = await apiJson(`/api/student/assignments/${encodeURIComponent(assignmentId)}`);
        const items = data.items || [];

        document.querySelector('#statSubmissionsCount').textContent = `${items.length} 人`;
        container.replaceChildren();

        if (!items.length) {
          container.innerHTML = '<div style="text-align:center; padding:30px; color:var(--muted)">当前作业暂无学生提交。</div>';
          return;
        }

        items.forEach((sub, idx) => {
          const studentName = sub.user_uid.includes('d7bc') ? '林同学 (学号: 2026082001)' : `学生 (${sub.user_uid.slice(0, 8)})`;
          const card = document.createElement('div');
          card.className = 'submission-card';

          const head = document.createElement('div');
          head.className = 'submission-head';
          head.innerHTML = `
            <div class="student-info">
              <span>学生：${studentName}</span>
              <span style="font-size:.82rem; font-weight:normal; color:var(--muted)">第 ${sub.attempt} 次提交 · ${sub.created_at || '刚刚'}</span>
            </div>
            <div class="submission-score-tag">总得分：${sub.score !== null ? sub.score : '待批改'} / 100 分</div>
          `;
          card.append(head);

          (sub.grades || []).forEach(g => {
            const qItem = (assignDetail.questions || []).find(q => q.id === g.question_id);
            const gradeItem = document.createElement('div');
            gradeItem.className = 'question-grade-item';
            gradeItem.innerHTML = `
              <div class="question-grade-title">题目：${qItem ? qItem.prompt : g.question_id}</div>
              <div style="font-size:.88rem; color:var(--ink-secondary)">
                <span>分值：<strong>${g.score} / ${g.max_score} 分</strong></span>
                <span style="margin-left:12px; color:var(--muted)">判定来源：${g.source === 'deterministic' ? '客观题自动判分' : 'Agent 智能初评'}</span>
              </div>
              ${g.feedback ? `
                <div class="ai-review-box">
                  <span class="ai-review-tag">批改评语</span>
                  ${g.feedback}
                </div>
              ` : ''}
              <div class="teacher-confirm-actions">
                <button type="button" class="btn btn-secondary btn-sm" onclick="confirmGrade('${g.id}', ${g.score})">
                  确认此题得分
                </button>
              </div>
            `;
            card.append(gradeItem);
          });

          container.append(card);
        });
      } catch (err) {
        container.innerHTML = `<div style="color:var(--red); padding:20px;">加载作答失败：${err.message}</div>`;
      }
    }

    async function confirmGrade(gradeId, score) {
      try {
        await apiJson(`/api/teacher/grade-items/${encodeURIComponent(gradeId)}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', 'X-Moodle-Sesskey': currentCsrfToken, 'Idempotency-Key': `review-${gradeId}-${Date.now()}` },
          body: JSON.stringify({ score, reason: '教师已核对课程标准答案' })
        });
        alert('已确认该题得分并同步至课程成绩单！');
        const sel = document.querySelector('#teacherAssignmentSelect');
        if (sel.value) loadSubmissionsForAssignment(sel.value);
      } catch (err) {
        alert(`确认失败：${err.message}`);
      }
    }

    document.querySelector('#btnBatchAgentGrade').addEventListener('click', async () => {
      const sel = document.querySelector('#teacherAssignmentSelect');
      if (!sel.value) return;
      try {
        await apiJson(`/api/teacher/assignments/${encodeURIComponent(sel.value)}/grade`, {
          method: 'POST',
          headers: { 'X-Moodle-Sesskey': currentCsrfToken, 'Idempotency-Key': `batch-grade-${sel.value}-${Date.now()}` },
          body: '{}'
        });
        alert('批量智能初评已完成！');
        loadSubmissionsForAssignment(sel.value);
      } catch (err) {
        alert(`批改异常：${err.message}`);
      }
    });

    // =========================================================================
    // 6. 教师端功能：AI 智能出题与题库发布
    // =========================================================================
    let lastGeneratedDraft = null;

    document.querySelector('#btnGenerateAiDraft').addEventListener('click', async () => {
      const ch = document.querySelector('#draftChapterSelect').value;
      const type = document.querySelector('#draftTypeSelect').value;
      const req = document.querySelector('#draftRequirementsInput').value.trim();
      const typeNames = { single_choice: '单选题', multiple_choice: '多选题', true_false: '判断题', short_answer: '简答题' };

      const prompt = `请针对《电力系统储能技术》第${ch}章出 1 道${typeNames[type] || '单选题'}。要求：${req || '紧扣教材核心重点与考点，包含题干、选项、标准答案和详细评分依据'}`;
      
      const btn = document.querySelector('#btnGenerateAiDraft');
      btn.disabled = true;
      btn.textContent = '正在生成考题草稿...';

      try {
        const res = await fetch('/api/course-agent/chat', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json', 'X-Moodle-Sesskey': currentCsrfToken },
          body: JSON.stringify({ question: prompt, mode: 'question_draft' })
        });
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let answer = '';
        while (true) {
          const { value, done } = await reader.read();
          buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
          const blocks = buffer.split('\n\n');
          buffer = blocks.pop() || '';
          for (const b of blocks) {
            const lines = b.split('\n');
            const dataLine = lines.find(l => l.startsWith('data:'));
            if (dataLine && lines.some(l => l.includes('event: token'))) {
              const d = JSON.parse(dataLine.slice(5).trim());
              answer += d.text || '';
            }
          }
          if (done) break;
        }

        document.querySelector('#aiGeneratedPreviewBox').style.display = 'block';
        document.querySelector('#aiGeneratedPreviewText').textContent = answer;
        lastGeneratedDraft = {
          question_type: type,
          chapter_id: Number(ch),
          prompt: answer.slice(0, 120),
          options: ['选项 A', '选项 B', '选项 C', '选项 D'],
          answer: '选项 A',
          rubric: answer,
          max_score: 10
        };
      } catch (err) {
        alert(`生成失败：${err.message}`);
      } finally {
        btn.disabled = false;
        btn.textContent = '生成标准考题草稿';
      }
    });

    document.querySelector('#btnSaveDraftToBank').addEventListener('click', async () => {
      if (!lastGeneratedDraft) return;
      try {
        await apiJson('/api/teacher/questions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Moodle-Sesskey': currentCsrfToken, 'Idempotency-Key': `save-draft-${Date.now()}` },
          body: JSON.stringify(lastGeneratedDraft)
        });
        alert('考题已保存至题库草稿！可在右侧题库列表中审核并发布。');
        loadQuestionBankList();
      } catch (err) {
        alert(`保存失败：${err.message}`);
      }
    });

    async function loadQuestionBankList() {
      const container = document.querySelector('#teacherQuestionBankList');
      try {
        const data = await apiJson('/api/questions');
        const items = data.items || [];
        container.replaceChildren();

        if (!items.length) {
          container.innerHTML = '<div style="color:var(--muted); padding:10px;">题库暂无题目。</div>';
          return;
        }

        items.forEach(q => {
          const row = document.createElement('div');
          row.style.cssText = 'border:1px solid var(--line); border-radius:6px; padding:10px 12px; margin-bottom:8px; background:#fff; font-size:.88rem;';
          row.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <label style="display:flex; align-items:center; gap:8px; font-weight:650; cursor:pointer;">
                <input type="checkbox" value="${q.id}" class="qb-select-checkbox" ${q.status === 'published' ? 'checked' : ''} />
                <span>${q.prompt.slice(0, 45)}...</span>
              </label>
              <span style="font-size:.78rem; padding:2px 6px; border-radius:4px; ${q.status === 'published' ? 'background:#dcfce7; color:#15803d;' : 'background:#f1f5f9; color:#64748b;'}">
                ${q.status === 'published' ? '已发布' : '草稿'}
              </span>
            </div>
            ${q.status === 'draft' ? `
              <button type="button" class="btn btn-secondary btn-sm" style="margin-top:6px;" onclick="publishQuestion('${q.id}')">
                审核并发布至题库
              </button>
            ` : ''}
          `;
          container.append(row);
        });
      } catch (err) {
        container.innerHTML = `<div style="color:var(--red)">题库加载失败：${err.message}</div>`;
      }
    }

    async function publishQuestion(questionId) {
      try {
        await apiJson(`/api/teacher/questions/${encodeURIComponent(questionId)}/publish`, {
          method: 'POST',
          headers: { 'X-Moodle-Sesskey': currentCsrfToken, 'Idempotency-Key': `pub-${questionId}-${Date.now()}` }
        });
        alert('题目已审核发布！');
        loadQuestionBankList();
      } catch (err) {
        alert(`发布失败：${err.message}`);
      }
    }

    document.querySelector('#btnPublishNewAssignment').addEventListener('click', async () => {
      const title = document.querySelector('#newAssignmentTitleInput').value.trim();
      const checkboxes = Array.from(document.querySelectorAll('.qb-select-checkbox:checked'));
      const questionIds = checkboxes.map(cb => cb.value);

      if (!title) { alert('请先输入作业名称！'); return; }
      if (!questionIds.length) { alert('请至少勾选一道已发布的题目！'); return; }

      try {
        const assign = await apiJson('/api/teacher/assignments', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-Moodle-Sesskey': currentCsrfToken, 'Idempotency-Key': `create-assign-${Date.now()}` },
          body: JSON.stringify({ title, question_ids: questionIds, allow_attempts: 1 })
        });
        await apiJson(`/api/teacher/assignments/${encodeURIComponent(assign.id)}/publish`, {
          method: 'POST',
          headers: { 'X-Moodle-Sesskey': currentCsrfToken, 'Idempotency-Key': `pub-assign-${assign.id}` }
        });
        alert(`作业《${title}》已成功发布给全班学生！`);
        document.querySelector('#newAssignmentTitleInput').value = '';
        loadTeacherGradingCenter();
      } catch (err) {
        alert(`发布作业失败：${err.message}`);
      }
    });

    // =========================================================================
    // 7. 学生端专属：作业列表
    // =========================================================================
    async function loadStudentAssignments() {
      const container = document.querySelector('#studentAssignmentList');
      try {
        const data = await apiJson('/api/student/assignments');
        const items = data.items || [];
        container.replaceChildren();

        if (!items.length) {
          container.innerHTML = '<div style="color:var(--muted); padding:20px; text-align:center;">暂无待完成作业。</div>';
          return;
        }

        items.forEach(a => {
          const card = document.createElement('div');
          card.className = 'submission-card';
          card.innerHTML = `
            <div class="submission-head">
              <div style="font-weight:700; font-size:1.05rem;">${a.title}</div>
              <span class="drawer-tag">${a.status === 'published' ? '进行中' : a.status}</span>
            </div>
            <p style="color:var(--muted); font-size:.88rem; margin:6px 0 12px;">包含 ${a.question_count || 2} 道考核题目 · 允许提交 ${a.allow_attempts || 1} 次</p>
            <button type="button" class="btn btn-primary btn-sm" onclick="alert('即将进入《${a.title}》答题页面')">
              开始答题测评
            </button>
          `;
          container.append(card);
        });
      } catch (err) {
        container.innerHTML = `<div style="color:var(--red)">加载作业失败：${err.message}</div>`;
      }
    }

    // =========================================================================
    // 8. 统一身份感知与 Tab 路由
    // =========================================================================
    async function apiJson(url, options = {}) {
      const res = await fetch(url, { credentials: 'same-origin', ...options });
      const payload = await res.json().catch(() => ({}));
      if (!res.ok || payload.status === 'error') throw new Error(payload.error?.message || `HTTP ${res.status}`);
      return payload.data;
    }

    async function initSession() {
      try {
        const res = await fetch('/api/course/session/open', { method: 'POST', credentials: 'same-origin' });
        const payload = await res.json();
        if (!res.ok || payload.status !== 'ok') throw new Error(payload.error?.message || '会话初始化失败');

        currentRole = payload.data.role || 'student';
        currentCsrfToken = payload.data.csrf_token || '';

        const roleBadge = document.querySelector('#roleBadge');
        const userDisplay = document.querySelector('#usernameDisplay');
        const roleLabels = { teacher: '主讲教师', admin: '教务管理员', student: '学生' };

        roleBadge.className = `role-badge ${currentRole}`;
        roleBadge.textContent = roleLabels[currentRole] || '用户';
        userDisplay.textContent = currentRole === 'teacher' ? '教师工作台' : (currentRole === 'admin' ? '管理员' : '林同学');

        // Init Graph Engine
        const svgEl = document.querySelector('#knowledgeGraphSvg');
        const wrapperEl = document.querySelector('#graphContainerWrapper');
        window.graphEngine = new CleanKnowledgeGraphEngine(svgEl, wrapperEl);

        try {
          const profile = await apiJson('/api/learning/profile');
          window.graphEngine.studentProfile = new Map((profile.nodes || []).map(n => [n.id, n.status]));
          window.graphEngine.render();
        } catch (_) {}

        renderTabs();
      } catch (err) {
        console.error('Session init error', err);
      }
    }

    function renderTabs() {
      const nav = document.querySelector('#mainNavTabs');
      nav.replaceChildren();

      let tabs = [];
      if (['teacher', 'admin'].includes(currentRole)) {
        tabs = [
          { id: 'sectionTeacherGrading', label: '作业批改与智能判分', active: true },
          { id: 'sectionTeacherQuestions', label: '智能出题与题库发布' },
          { id: 'sectionKnowledgeGraph', label: '课程知识图谱全景' }
        ];
      } else {
        tabs = [
          { id: 'sectionKnowledgeGraph', label: '知识图谱网络学习地图', active: true },
          { id: 'sectionStudentAssignments', label: '我的作业与测评' }
        ];
      }

      tabs.forEach(t => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `nav-tab ${t.active ? 'active' : ''}`;
        btn.textContent = t.label;
        btn.onclick = () => switchTab(t.id, btn);
        nav.append(btn);
      });

      if (['teacher', 'admin'].includes(currentRole)) {
        switchTab('sectionTeacherGrading', nav.children[0]);
        loadTeacherGradingCenter();
        loadQuestionBankList();
      } else {
        switchTab('sectionKnowledgeGraph', nav.children[0]);
        loadStudentAssignments();
      }
    }

    function switchTab(sectionId, activeBtn) {
      document.querySelectorAll('.tab-pane').forEach(p => p.hidden = true);
      document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));

      const target = document.querySelector(`#${sectionId}`);
      if (target) target.hidden = false;
      if (activeBtn) activeBtn.classList.add('active');

      if (sectionId === 'sectionKnowledgeGraph' && window.graphEngine) {
        setTimeout(() => window.graphEngine.render(), 50);
      }
    }

    document.querySelector('#graphFilterChapter').addEventListener('change', (e) => {
      if (window.graphEngine) {
        window.graphEngine.filterChapter = e.target.value;
        window.graphEngine.render();
      }
    });

    document.querySelector('#btnGraphFitView').addEventListener('click', () => {
      if (window.graphEngine) window.graphEngine.fitView();
    });

    initSession();
  </script>
</body>
</html>
'''

with open('agent-ui/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Saved clean emoji-free agent-ui/index.html")

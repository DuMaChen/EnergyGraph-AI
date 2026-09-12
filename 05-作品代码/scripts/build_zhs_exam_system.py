import re

with open('agent-ui/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Exam CSS Styles
exam_css = r'''
    /* -------------------------------------------------------------------------
       智慧树 (Zhihuishu) 风格 在线作业与考试系统 UI
       ------------------------------------------------------------------------- */
    .zhs-exam-modal, .zhs-exam-result-modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: #f8fafc;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .exam-top-bar {
      height: 60px;
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      flex-shrink: 0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .exam-top-left {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .exam-back-btn {
      display: inline-flex;
      align-items: center;
      padding: 6px 12px;
      background: #f1f5f9;
      color: #334155;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }
    .exam-back-btn:hover {
      background: #e2e8f0;
      color: #0f172a;
    }
    .exam-title-badge {
      font-size: 0.78rem;
      font-weight: 700;
      padding: 3px 8px;
      background: #f0fdfa;
      color: #0f766e;
      border: 1px solid #99f6e4;
      border-radius: 4px;
    }
    .exam-title-text {
      font-size: 1.05rem;
      font-weight: 700;
      color: #0f172a;
      margin: 0;
    }
    .exam-top-right {
      display: flex;
      align-items: center;
      gap: 18px;
    }
    .exam-progress-box, .exam-score-info {
      font-size: 0.88rem;
      color: #475569;
    }
    
    .exam-main-container {
      flex: 1;
      display: flex;
      overflow: hidden;
    }
    .exam-stage {
      flex: 1;
      overflow-y: auto;
      padding: 24px 32px 80px;
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
    }
    .exam-question-card {
      width: 100%;
      max-width: 860px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 28px 32px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.03);
      margin-bottom: 24px;
    }
    .exam-q-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #f1f5f9;
    }
    .exam-q-num {
      font-size: 1.12rem;
      font-weight: 750;
      color: #0f172a;
    }
    .exam-q-type-badge {
      font-size: 0.82rem;
      font-weight: 600;
      padding: 3px 10px;
      background: #e0f2fe;
      color: #0369a1;
      border-radius: 20px;
    }
    .exam-q-prompt {
      font-size: 1.02rem;
      line-height: 1.75;
      color: #1e293b;
      margin-bottom: 20px;
    }
    .exam-options-list {
      display: grid;
      gap: 12px;
      margin-top: 16px;
    }
    .exam-option-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 14px 18px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .exam-option-item:hover {
      background: #f1f5f9;
      border-color: #cbd5e1;
    }
    .exam-option-item.selected {
      background: #f0fdfa;
      border-color: #0f766e;
      box-shadow: 0 0 0 1px #0f766e;
    }
    .option-radio {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      border: 2px solid #94a3b8;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      background: #ffffff;
    }
    .exam-option-item.selected .option-radio {
      border-color: #0f766e;
      background: #0f766e;
    }
    .exam-option-item.selected .option-radio::after {
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ffffff;
    }
    .option-label {
      font-weight: 700;
      color: #334155;
      font-size: 0.95rem;
    }
    .exam-option-item.selected .option-label {
      color: #0f766e;
    }
    .option-text {
      font-size: 0.96rem;
      color: #1e293b;
      line-height: 1.5;
    }
    .exam-textarea {
      width: 100%;
      min-height: 160px;
      padding: 14px 16px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-family: inherit;
      font-size: 0.96rem;
      line-height: 1.7;
      resize: vertical;
      color: #1e293b;
      background: #ffffff;
      box-sizing: border-box;
    }
    .exam-textarea:focus {
      outline: none;
      border-color: #0f766e;
      box-shadow: 0 0 0 3px rgba(15,118,110,0.15);
    }
    
    .exam-bottom-actions {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 280px;
      height: 64px;
      background: #ffffff;
      border-top: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 32px;
      z-index: 10;
    }
    
    /* Right Sheet Sidebar */
    .exam-sheet-sidebar {
      width: 280px;
      background: #ffffff;
      border-left: 1px solid #e2e8f0;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .sheet-header {
      padding: 18px 20px;
      border-bottom: 1px solid #f1f5f9;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .sheet-header h3 {
      font-size: 1rem;
      font-weight: 750;
      color: #0f172a;
      margin: 0;
    }
    .sheet-legend {
      padding: 10px 20px;
      background: #f8fafc;
      border-bottom: 1px solid #f1f5f9;
      display: flex;
      gap: 16px;
      font-size: 0.82rem;
      color: #64748b;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .legend-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    .legend-dot.answered { background: #0f766e; }
    .legend-dot.unanswered { background: #ffffff; border: 1px solid #cbd5e1; }
    .sheet-grid {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      align-content: start;
    }
    .sheet-num-btn {
      width: 44px;
      height: 44px;
      border-radius: 8px;
      border: 1px solid #cbd5e1;
      background: #ffffff;
      color: #334155;
      font-size: 0.95rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.15s;
    }
    .sheet-num-btn:hover {
      border-color: #0f766e;
      color: #0f766e;
    }
    .sheet-num-btn.active {
      border: 2px solid #0f766e;
      color: #0f766e;
      font-weight: 750;
    }
    .sheet-num-btn.answered {
      background: #0f766e;
      border-color: #0f766e;
      color: #ffffff;
    }
    .sheet-submit-area {
      padding: 16px 20px;
      border-top: 1px solid #e2e8f0;
      background: #ffffff;
    }
    
    /* Result Modal Layout */
    .result-modal-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .result-modal-header {
      padding: 16px 24px;
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .result-score-banner {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .score-main {
      font-size: 1.05rem;
      color: #334155;
    }
    .score-main strong {
      font-size: 1.6rem;
      color: #0f766e;
      margin-left: 4px;
    }
    .result-status-tag {
      padding: 4px 10px;
      background: #fef3c7;
      color: #b45309;
      font-size: 0.82rem;
      font-weight: 600;
      border-radius: 20px;
    }
    .result-status-tag.completed {
      background: #dcfce7;
      color: #15803d;
    }
    .result-questions-list {
      flex: 1;
      overflow-y: auto;
      padding: 24px 32px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 20px;
    }
    .result-q-card {
      width: 100%;
      max-width: 860px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 24px 28px;
    }
    .result-answer-box {
      margin-top: 14px;
      padding: 12px 16px;
      background: #f8fafc;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
      font-size: 0.92rem;
      line-height: 1.6;
    }
    .result-ai-analysis {
      margin-top: 14px;
      padding: 14px 18px;
      background: #f0fdfa;
      border-left: 4px solid #0f766e;
      border-radius: 0 6px 6px 0;
    }
'''

html = html.replace('    /* -------------------------------------------------------------------------', exam_css + '\n    /* -------------------------------------------------------------------------', 1)

print("CSS injected successfully")
with open('agent-ui/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

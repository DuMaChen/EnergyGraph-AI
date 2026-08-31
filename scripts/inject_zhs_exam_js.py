import re

with open('agent-ui/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject HTML modals before </body>
modals_html = r'''
  <!-- ----------------------------------------------------------------- -->
  <!-- 智慧树 (Zhihuishu) 风格 在线作业测评系统 Fullscreen Modal -->
  <!-- ----------------------------------------------------------------- -->
  <div id="zhsExamModal" class="zhs-exam-modal" style="display:none;">
    <div class="exam-top-bar">
      <div class="exam-top-left">
        <button id="btnExitExam" type="button" class="exam-back-btn">
          <span>&lt; 退出作业 (自动暂存)</span>
        </button>
        <span class="exam-title-badge">章节在线测评</span>
        <h2 id="examModalTitle" class="exam-title-text">《电力系统储能技术》作业</h2>
      </div>
      <div class="exam-top-right">
        <div class="exam-progress-box">
          <span>作答进度:</span>
          <strong id="examAnsweredProgress" style="color:#0f766e; margin-left:4px;">0 / 0 已作答</strong>
        </div>
        <div class="exam-score-info">
          <span id="examTotalScoreText">总分: <strong>20 分</strong></span>
        </div>
        <button id="btnSubmitExam" type="button" class="btn btn-green">
          提交作业
        </button>
      </div>
    </div>

    <div class="exam-main-container">
      <!-- Left Question Stage -->
      <div class="exam-stage">
        <div id="examQuestionCard" class="exam-question-card">
          <!-- Injected by JS -->
        </div>

        <div class="exam-bottom-actions">
          <button id="btnPrevQuestion" type="button" class="btn btn-secondary">
            ◀ 上一题
          </button>
          <div style="display:flex; gap:10px;">
            <button id="btnSaveDraftAnswer" type="button" class="btn btn-secondary">
              暂存草稿
            </button>
            <button id="btnNextQuestion" type="button" class="btn btn-primary">
              下一题 ▶
            </button>
          </div>
        </div>
      </div>

      <!-- Right Answer Sheet 答题卡 -->
      <div class="exam-sheet-sidebar">
        <div class="sheet-header">
          <h3>答题卡</h3>
          <span id="sheetQuestionCountTag" style="font-size:0.82rem; color:#64748b;">共 0 题</span>
        </div>
        <div class="sheet-legend">
          <span class="legend-item"><i class="legend-dot answered"></i> 已作答</span>
          <span class="legend-item"><i class="legend-dot unanswered"></i> 未作答</span>
        </div>
        <div id="examSheetGrid" class="sheet-grid">
          <!-- Question number circles: 1, 2, 3... -->
        </div>
        <div class="sheet-submit-area">
          <button id="btnSubmitExamSide" type="button" class="btn btn-green" style="width:100%; padding:12px;">
            确认并提交试卷
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- ----------------------------------------------------------------- -->
  <!-- 智慧树 (Zhihuishu) 风格 作答报告与解析 Modal -->
  <!-- ----------------------------------------------------------------- -->
  <div id="zhsExamResultModal" class="zhs-exam-result-modal" style="display:none;">
    <div class="result-modal-content">
      <div class="result-modal-header">
        <div style="display:flex; align-items:center; gap:14px;">
          <button id="btnCloseResultModal" type="button" class="exam-back-btn">
            <span>&lt; 返回作业列表</span>
          </button>
          <h2 id="resultModalTitle" style="font-size:1.15rem; font-weight:750; color:#0f172a; margin:0;">
            作答报告与智能解析
          </h2>
        </div>
        <div id="resultScoreBanner" class="result-score-banner">
          <div class="score-main">
            <span>综合得分:</span>
            <strong id="resultScoreNumber">--</strong>
            <span style="font-size:0.9rem; color:#64748b;">/ 100 分</span>
          </div>
          <span id="resultStatusTag" class="result-status-tag">待教师复核</span>
        </div>
      </div>
      <div id="resultQuestionsList" class="result-questions-list">
        <!-- Injected by JS -->
      </div>
    </div>
  </div>
'''

if 'id="zhsExamModal"' not in html:
    html = html.replace('  <!-- ----------------------------------------------------------------- -->\n  <!-- 智慧树 (Zhihuishu) 风格全屏资料阅读器 Modal -->', modals_html + '\n  <!-- ----------------------------------------------------------------- -->\n  <!-- 智慧树 (Zhihuishu) 风格全屏资料阅读器 Modal -->')

# 2. Update Student & Teacher JS logic
js_exam_engine = r'''
    // =========================================================================
    // 6. 智慧树 (Zhihuishu) 风格 在线作业答题与解析引擎
    // =========================================================================
    let currentExamAssignment = null;
    let currentExamQuestions = [];
    let currentExamIndex = 0;
    let currentExamAnswers = {};

    async function openZhsExam(assignmentId) {
      try {
        const assign = await apiJson(`/api/student/assignments/${encodeURIComponent(assignmentId)}`);
        currentExamAssignment = assign;
        currentExamQuestions = assign.questions || [];
        currentExamIndex = 0;
        currentExamAnswers = {};

        // Load existing draft/answers if any
        if (assign.my_submissions && assign.my_submissions.length) {
          const lastSub = assign.my_submissions[assign.my_submissions.length - 1];
          // If already submitted and no more attempts
          if (assign.allow_attempts <= assign.my_submissions.length) {
            openZhsExamResult(assignmentId);
            return;
          }
        }

        document.querySelector('#examModalTitle').textContent = assign.title;
        const totalPoints = currentExamQuestions.reduce((sum, q) => sum + (Number(q.max_score) || 10), 0);
        document.querySelector('#examTotalScoreText').innerHTML = `总分: <strong>${totalPoints} 分</strong>`;
        document.querySelector('#sheetQuestionCountTag').textContent = `共 ${currentExamQuestions.length} 题`;

        document.querySelector('#zhsExamModal').style.display = 'flex';
        renderExamQuestion(0);
        renderExamSheetGrid();
      } catch (err) {
        alert(`打开作业失败：${err.message}`);
      }
    }

    function closeZhsExam() {
      document.querySelector('#zhsExamModal').style.display = 'none';
      loadStudentAssignments();
    }

    function renderExamQuestion(index) {
      if (index < 0 || index >= currentExamQuestions.length) return;
      currentExamIndex = index;
      const q = currentExamQuestions[index];
      const card = document.querySelector('#examQuestionCard');
      const typeNames = {
        single_choice: '单选题',
        multiple_choice: '多选题',
        true_false: '判断题',
        short_answer: '简答题'
      };

      const qType = q.question_type || 'single_choice';
      const maxScore = q.max_score || 10;
      const userAns = currentExamAnswers[q.id];

      let optionsHtml = '';
      if (qType === 'single_choice' || qType === 'multiple_choice') {
        const opts = q.options || ['选项 A', '选项 B', '选项 C', '选项 D'];
        optionsHtml = `
          <div class="exam-options-list">
            ${opts.map((opt, i) => {
              const label = String.fromCharCode(65 + i);
              const isSelected = qType === 'single_choice' 
                ? userAns === opt || userAns === label
                : (Array.isArray(userAns) && (userAns.includes(opt) || userAns.includes(label)));
              return `
                <div class="exam-option-item ${isSelected ? 'selected' : ''}" onclick="selectExamOption('${q.id}', '${escapeHtml(opt)}', '${qType}')">
                  <div class="option-radio"></div>
                  <span class="option-label">${label}.</span>
                  <span class="option-text">${escapeHtml(opt)}</span>
                </div>
              `;
            }).join('')}
          </div>
        `;
      } else if (qType === 'true_false') {
        const tfOptions = ['正确', '错误'];
        optionsHtml = `
          <div class="exam-options-list">
            ${tfOptions.map((opt) => {
              const isSelected = userAns === opt || (opt === '正确' && userAns === true) || (opt === '错误' && userAns === false);
              return `
                <div class="exam-option-item ${isSelected ? 'selected' : ''}" onclick="selectExamOption('${q.id}', '${opt}', 'true_false')">
                  <div class="option-radio"></div>
                  <span class="option-label">${opt}</span>
                </div>
              `;
            }).join('')}
          </div>
        `;
      } else {
        // short_answer / subjective
        optionsHtml = `
          <div style="margin-top:16px;">
            <textarea class="exam-textarea" placeholder="请在此输入您的专业解答过程与核心要点..." oninput="setExamSubjectiveAnswer('${q.id}', this.value)">${escapeHtml(userAns || '')}</textarea>
            <div style="font-size:0.82rem; color:#94a3b8; text-align:right; margin-top:6px;">支持输入标准工程分析与推导</div>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="exam-q-header">
          <div class="exam-q-num">第 ${index + 1} 题 <span style="font-size:0.88rem; font-weight:normal; color:#64748b;">(本题 ${maxScore} 分)</span></div>
          <span class="exam-q-type-badge">${typeNames[qType] || '问答题'}</span>
        </div>
        <div class="exam-q-prompt markdown-rendered">
          ${renderMarkdownToHtml(q.prompt)}
        </div>
        ${optionsHtml}
      `;

      // Update Nav Buttons
      document.querySelector('#btnPrevQuestion').disabled = index === 0;
      document.querySelector('#btnNextQuestion').disabled = index === currentExamQuestions.length - 1;
      updateExamProgress();
      renderExamSheetGrid();
    }

    function selectExamOption(qId, val, type) {
      if (type === 'single_choice' || type === 'true_false') {
        currentExamAnswers[qId] = val;
      } else if (type === 'multiple_choice') {
        let arr = Array.isArray(currentExamAnswers[qId]) ? [...currentExamAnswers[qId]] : [];
        if (arr.includes(val)) {
          arr = arr.filter(x => x !== val);
        } else {
          arr.push(val);
        }
        currentExamAnswers[qId] = arr;
      }
      renderExamQuestion(currentExamIndex);
    }

    function setExamSubjectiveAnswer(qId, val) {
      currentExamAnswers[qId] = val;
      updateExamProgress();
      renderExamSheetGrid();
    }

    function updateExamProgress() {
      const answeredCount = Object.keys(currentExamAnswers).filter(k => {
        const v = currentExamAnswers[k];
        return v && (typeof v === 'string' ? v.trim().length > 0 : true);
      }).length;
      document.querySelector('#examAnsweredProgress').textContent = `${answeredCount} / ${currentExamQuestions.length} 已作答`;
    }

    function renderExamSheetGrid() {
      const grid = document.querySelector('#examSheetGrid');
      grid.replaceChildren();
      currentExamQuestions.forEach((q, i) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'sheet-num-btn';
        btn.textContent = i + 1;
        if (i === currentExamIndex) btn.classList.add('active');
        const v = currentExamAnswers[q.id];
        if (v && (typeof v === 'string' ? v.trim().length > 0 : true)) {
          btn.classList.add('answered');
        }
        btn.onclick = () => renderExamQuestion(i);
        grid.append(btn);
      });
    }

    async function submitExam() {
      if (!currentExamAssignment) return;
      const totalQ = currentExamQuestions.length;
      const answeredCount = Object.keys(currentExamAnswers).filter(k => {
        const v = currentExamAnswers[k];
        return v && (typeof v === 'string' ? v.trim().length > 0 : true);
      }).length;

      let msg = `确定提交当前作业吗？\n共 ${totalQ} 道题目，已完成 ${answeredCount} 道。`;
      if (answeredCount < totalQ) {
        msg = `提示：您还有 ${totalQ - answeredCount} 道题目未作答！\n确定现在提交吗？`;
      }

      if (!confirm(msg)) return;

      const btn = document.querySelector('#btnSubmitExam');
      const btnSide = document.querySelector('#btnSubmitExamSide');
      btn.disabled = true;
      btnSide.disabled = true;
      btn.textContent = '正在提交并智能判分...';

      try {
        const payload = {
          answers: currentExamAnswers,
          attempt: (currentExamAssignment.my_submissions?.length || 0) + 1
        };

        const res = await apiJson(`/api/student/assignments/${encodeURIComponent(currentExamAssignment.id)}/submit`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Moodle-Sesskey': currentCsrfToken,
            'Idempotency-Key': `exam-submit-${currentExamAssignment.id}-${Date.now()}`
          },
          body: JSON.stringify(payload)
        });

        alert('作业提交成功！系统已自动完成客观题评分并提交 Agent 智能初评。');
        document.querySelector('#zhsExamModal').style.display = 'none';
        openZhsExamResult(currentExamAssignment.id);
      } catch (err) {
        alert(`提交作业失败：${err.message}`);
      } finally {
        btn.disabled = false;
        btnSide.disabled = false;
        btn.textContent = '提交作业';
      }
    }

    async function openZhsExamResult(assignmentId) {
      try {
        const assign = await apiJson(`/api/student/assignments/${encodeURIComponent(assignmentId)}`);
        const subs = assign.my_submissions || [];
        const lastSub = subs[subs.length - 1];

        document.querySelector('#resultModalTitle').textContent = `《${assign.title}》- 作答报告与智能解析`;
        const scoreBox = document.querySelector('#resultScoreNumber');
        const statusTag = document.querySelector('#resultStatusTag');
        const list = document.querySelector('#resultQuestionsList');
        list.replaceChildren();

        if (lastSub) {
          scoreBox.textContent = lastSub.score !== null ? lastSub.score : '--';
          if (lastSub.grades && lastSub.grades.length) {
            statusTag.textContent = '智能评定完成';
            statusTag.className = 'result-status-tag completed';
          } else {
            statusTag.textContent = '待教师审核';
            statusTag.className = 'result-status-tag';
          }

          (assign.questions || []).forEach((q, idx) => {
            const gradeItem = (lastSub.grades || []).find(g => g.question_id === q.id);
            const card = document.createElement('div');
            card.className = 'result-q-card';

            const score = gradeItem ? gradeItem.score : 0;
            const maxScore = q.max_score || 10;
            const isFull = score >= maxScore;

            card.innerHTML = `
              <div class="exam-q-header">
                <div class="exam-q-num">第 ${idx + 1} 题 <span style="font-size:0.88rem; font-weight:normal; color:#64748b;">(满分 ${maxScore} 分)</span></div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="exam-q-type-badge">${q.question_type || '题目'}</span>
                  <span style="font-weight:750; font-size:1.05rem; color:${isFull ? '#0f766e' : '#b45309'};">得分: ${score} 分</span>
                </div>
              </div>
              <div class="markdown-rendered" style="font-size:1rem; margin-bottom:14px;">
                ${renderMarkdownToHtml(q.prompt)}
              </div>
              ${gradeItem && gradeItem.feedback ? `
                <div class="result-ai-analysis">
                  <div style="font-weight:700; color:#0f766e; margin-bottom:6px; font-size:0.92rem;">AI 智能判分与解析依据</div>
                  <div class="markdown-rendered">${renderMarkdownToHtml(gradeItem.feedback)}</div>
                </div>
              ` : ''}
            `;
            list.append(card);
          });
        } else {
          scoreBox.textContent = '0';
          statusTag.textContent = '未提交';
        }

        document.querySelector('#zhsExamResultModal').style.display = 'flex';
      } catch (err) {
        alert(`加载作业解析失败：${err.message}`);
      }
    }

    document.querySelector('#btnExitExam').onclick = closeZhsExam;
    document.querySelector('#btnSubmitExam').onclick = submitExam;
    document.querySelector('#btnSubmitExamSide').onclick = submitExam;
    document.querySelector('#btnPrevQuestion').onclick = () => renderExamQuestion(currentExamIndex - 1);
    document.querySelector('#btnNextQuestion').onclick = () => renderExamQuestion(currentExamIndex + 1);
    document.querySelector('#btnSaveDraftAnswer').onclick = () => alert('作答草稿已保存在本地，可随时继续作答。');
    document.querySelector('#btnCloseResultModal').onclick = () => {
      document.querySelector('#zhsExamResultModal').style.display = 'none';
      loadStudentAssignments();
    };
'''

# 3. Replace student assignment list loader to use openZhsExam & openZhsExamResult
old_load_student_assign = r'''    async function loadStudentAssignments() {
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
    }'''

new_load_student_assign = js_exam_engine + r'''
    async function loadStudentAssignments() {
      const container = document.querySelector('#studentAssignmentList');
      try {
        const data = await apiJson('/api/student/assignments');
        const items = data.items || [];
        container.replaceChildren();

        if (!items.length) {
          container.innerHTML = '<div style="color:var(--muted); padding:24px; text-align:center;">暂无待完成作业。</div>';
          return;
        }

        for (const a of items) {
          // Fetch full detail for attempt info
          let detail = null;
          try {
            detail = await apiJson(`/api/student/assignments/${encodeURIComponent(a.id)}`);
          } catch (_) {}

          const subs = (detail && detail.my_submissions) || [];
          const hasSubmitted = subs.length > 0;
          const lastSub = subs[subs.length - 1];

          let statusBadge = '<span class="drawer-tag" style="background:#f1f5f9; color:#475569;">未开始</span>';
          let actionBtn = `<button type="button" class="btn btn-primary btn-sm" onclick="openZhsExam('${a.id}')">开始答题测评</button>`;

          if (hasSubmitted) {
            if (lastSub.score !== null) {
              statusBadge = `<span class="drawer-tag" style="background:#dcfce7; color:#15803d; font-weight:700;">已完成 (得分: ${lastSub.score}分)</span>`;
              actionBtn = `<button type="button" class="btn btn-secondary btn-sm" onclick="openZhsExamResult('${a.id}')">查看作答与解析</button>`;
            } else {
              statusBadge = '<span class="drawer-tag" style="background:#fef3c7; color:#b45309;">已提交待批改</span>';
              actionBtn = `<button type="button" class="btn btn-secondary btn-sm" onclick="openZhsExamResult('${a.id}')">查看作答详情</button>`;
            }
          }

          const card = document.createElement('div');
          card.className = 'submission-card';
          card.style.marginBottom = '16px';
          card.innerHTML = `
            <div class="submission-head" style="align-items:center;">
              <div style="font-weight:750; font-size:1.05rem; color:#0f172a;">${escapeHtml(a.title)}</div>
              ${statusBadge}
            </div>
            <p style="color:var(--muted); font-size:.88rem; margin:8px 0 14px;">
              包含 ${a.question_count || 2} 道专业考核题目 · 允许提交 ${a.allow_attempts || 1} 次 · 支持 AI 智能初评与标准答案解析
            </p>
            <div style="display:flex; gap:10px;">
              ${actionBtn}
            </div>
          `;
          container.append(card);
        }
      } catch (err) {
        container.innerHTML = `<div style="color:var(--red); padding:16px;">加载作业失败：${escapeHtml(err.message)}</div>`;
      }
    }'''

if old_load_student_assign in html:
    html = html.replace(old_load_student_assign, new_load_student_assign)
    print("loadStudentAssignments updated with Zhihuishu interactive engine")
else:
    print("WARNING: old_load_student_assign not found")

with open('agent-ui/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

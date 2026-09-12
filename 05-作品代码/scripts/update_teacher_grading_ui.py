with open('agent-ui/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace loadSubmissionsForAssignment and confirmGrade
old_block = r'''    async function loadSubmissionsForAssignment(assignmentId) {
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
              <div style="margin-top:8px;">
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
    }'''

new_block = r'''    async function loadSubmissionsForAssignment(assignmentId) {
      const container = document.querySelector('#teacherSubmissionsList');
      container.innerHTML = '<div style="text-align:center; padding:24px; color:#64748b;">正在加载学生作答记录...</div>';
      try {
        const data = await apiJson(`/api/teacher/assignments/${encodeURIComponent(assignmentId)}/submissions?page=1&page_size=50`);
        const assignDetail = await apiJson(`/api/student/assignments/${encodeURIComponent(assignmentId)}`);
        const items = data.items || [];

        document.querySelector('#statSubmissionsCount').textContent = `${items.length} 份`;
        container.replaceChildren();

        if (!items.length) {
          container.innerHTML = '<div style="text-align:center; padding:32px; color:var(--muted)">当前作业暂无学生提交。</div>';
          return;
        }

        items.forEach((sub, idx) => {
          const studentName = sub.user_uid.includes('d7bc') ? '林同学 (学号: 2026082001)' : `学生 (${sub.user_uid.slice(0, 8)})`;
          const answers = sub.answers || {};
          const card = document.createElement('div');
          card.className = 'submission-card';
          card.style.marginBottom = '20px';

          const head = document.createElement('div');
          head.className = 'submission-head';
          head.innerHTML = `
            <div class="student-info">
              <span style="font-weight:750; font-size:1.05rem; color:#0f172a;">学生：${studentName}</span>
              <span style="font-size:.84rem; font-weight:normal; color:var(--muted); margin-left:10px;">第 ${sub.attempt} 次提交 · ${sub.created_at ? sub.created_at.replace('T', ' ').slice(0, 19) : '刚刚'}</span>
            </div>
            <div class="submission-score-tag" style="background:#f0fdfa; color:#0f766e; font-weight:750; border:1px solid #99f6e4;">
              当前总分：${sub.score !== null ? sub.score : '待批改'} / 100 分
            </div>
          `;
          card.append(head);

          (sub.grades || []).forEach((g, qIdx) => {
            const qItem = (assignDetail.questions || []).find(q => q.id === g.question_id);
            const studentAns = answers[g.question_id] || '未作答';
            const gradeItem = document.createElement('div');
            gradeItem.className = 'question-grade-item';
            gradeItem.style.cssText = 'background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-top:12px;';
            gradeItem.innerHTML = `
              <div class="question-grade-title" style="font-weight:700; color:#0f172a; margin-bottom:8px;">
                第 ${qIdx + 1} 题：${qItem ? escapeHtml(qItem.prompt) : g.question_id}
              </div>
              <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:10px 14px; margin-bottom:10px; font-size:.92rem;">
                <span style="color:#64748b; font-weight:600;">学生作答：</span>
                <span style="color:#0f172a; font-weight:650;">${typeof studentAns === 'object' ? JSON.stringify(studentAns) : escapeHtml(String(studentAns))}</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:8px;">
                <div style="font-size:.88rem; color:var(--ink-secondary)">
                  <span>满分：<strong>${g.max_score} 分</strong></span>
                  <span style="margin-left:14px; color:var(--muted);">判分来源：<strong>${g.source === 'deterministic' ? '客观题自动评分' : 'Agent 智能初评'}</strong></span>
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <label style="font-size:.88rem; font-weight:600; color:#334155;">评定得分：</label>
                  <input type="number" id="input-grade-score-${g.id}" min="0" max="${g.max_score}" value="${g.score}" style="width:70px; padding:5px 8px; border:1px solid #cbd5e1; border-radius:4px; font-weight:750; color:#0f766e; text-align:center;" />
                  <button type="button" class="btn btn-primary btn-sm" onclick="confirmGrade('${g.id}', ${g.score})">
                    确认此题得分
                  </button>
                </div>
              </div>
              ${g.feedback ? `
                <div class="ai-review-box" style="margin-top:10px; background:#f0fdfa; border-left:4px solid #0f766e; padding:10px 14px; border-radius:0 6px 6px 0;">
                  <div style="font-size:.82rem; font-weight:700; color:#0f766e; margin-bottom:4px;">Agent 智能评语与扣分依据</div>
                  <div class="markdown-rendered" style="font-size:.9rem; color:#1e293b;">${renderMarkdownToHtml(g.feedback)}</div>
                </div>
              ` : ''}
            `;
            card.append(gradeItem);
          });

          container.append(card);
        });
      } catch (err) {
        container.innerHTML = `<div style="color:var(--red); padding:20px;">加载作答失败：${escapeHtml(err.message)}</div>`;
      }
    }

    async function confirmGrade(gradeId, fallbackScore) {
      const inputEl = document.querySelector(`#input-grade-score-${gradeId}`);
      const scoreVal = inputEl ? Number(inputEl.value) : Number(fallbackScore);
      try {
        await apiJson(`/api/teacher/grade-items/${encodeURIComponent(gradeId)}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json', 'X-Moodle-Sesskey': currentCsrfToken, 'Idempotency-Key': `review-${gradeId}-${Date.now()}` },
          body: JSON.stringify({ score: scoreVal, reason: '教师已核对课程标准答案' })
        });
        alert('已确认该题得分并同步至 Moodle 成绩单！');
        const sel = document.querySelector('#teacherAssignmentSelect');
        if (sel.value) loadSubmissionsForAssignment(sel.value);
      } catch (err) {
        alert(`确认失败：${err.message}`);
      }
    }'''

if old_block in html:
    html = html.replace(old_block, new_block)
    print("Teacher grading center updated with Zhihuishu score input and review")
else:
    print("WARNING: old_block not found")

with open('agent-ui/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

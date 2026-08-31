import re

with open('agent-ui/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

modal_html = r'''
  <!-- ----------------------------------------------------------------- -->
  <!-- 登录提示引导 Modal (未登录用户友好引导) -->
  <!-- ----------------------------------------------------------------- -->
  <div id="loginPromptModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(15,23,42,0.65); z-index:99999; justify-content:center; align-items:center; backdrop-filter:blur(4px);">
    <div style="background:#ffffff; border-radius:14px; padding:28px 32px; max-width:480px; width:90%; box-shadow:0 20px 40px rgba(0,0,0,0.25); text-align:center;">
      <h3 style="margin:0 0 10px; font-size:1.35rem; color:#0f172a; font-weight:800;">欢迎访问课程空间</h3>
      <p style="color:#64748b; font-size:.92rem; line-height:1.6; margin-bottom:20px;">
        您当前尚未登录，登录 Moodle 平台账号后即可使用 AI 助教答疑、智慧树沉浸式课件阅读与作业智能判分功能。
      </p>
      <a href="/login/index.php?wantsurl=/agent/" class="btn btn-primary" style="display:block; width:100%; padding:12px; font-size:1rem; text-decoration:none; box-sizing:border-box; margin-bottom:14px; border-radius:8px;">
        立即登录 Moodle 平台
      </a>
      <div style="font-size:.85rem; color:#64748b; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px; text-align:left; margin-bottom:16px;">
        <div style="font-weight:700; margin-bottom:6px; color:#1e293b;">演示测试账号：</div>
        <div style="line-height:1.6;">教师端：账号 <code>codex_teacher_20260820</code> 密码 <code>CodexTeacher-2026!Aa</code></div>
        <div style="line-height:1.6;">学生端：账号 <code>codex_student_20260820</code> 密码 <code>CodexStudent-2026!Aa</code></div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:.88rem;">
        <a href="/login/signup.php" style="color:var(--primary); text-decoration:none; font-weight:600;">注册新账号</a>
        <button type="button" onclick="document.querySelector('#loginPromptModal').style.display='none'" style="background:transparent; border:0; color:#64748b; cursor:pointer; font-weight:600;">
          先以访客模式浏览
        </button>
      </div>
    </div>
  </div>
'''

# Insert modal before </body>
content = content.replace('</body>', modal_html + '\n</body>')

# Update initSession
old_init_session = r'''    async function initSession() {
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

        // Show/Hide Teacher Upload Card
        const teacherUploadCard = document.querySelector('#teacherUploadCard');
        if (['teacher', 'admin'].includes(currentRole)) {
          teacherUploadCard.style.display = 'block';
        } else {
          teacherUploadCard.style.display = 'none';
        }

        const svgEl = document.querySelector('#knowledgeGraphSvg');
        const wrapperEl = document.querySelector('#graphContainerWrapper');
        window.graphEngine = new CleanKnowledgeGraphEngine(svgEl, wrapperEl);

        try {
          const profile = await apiJson('/api/learning/profile');
          window.graphEngine.studentProfile = new Map((profile.nodes || []).map(n => [n.id, n.status]));
          window.graphEngine.render();
        } catch (_) {}

        renderTabs();
        renderStudyResourcePackages();
      } catch (err) {
        console.error('Session init error', err);
      }
    }'''

new_init_session = r'''    async function initSession() {
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

        // Show/Hide Teacher Upload Card
        const teacherUploadCard = document.querySelector('#teacherUploadCard');
        if (['teacher', 'admin'].includes(currentRole)) {
          teacherUploadCard.style.display = 'block';
        } else {
          teacherUploadCard.style.display = 'none';
        }

        const svgEl = document.querySelector('#knowledgeGraphSvg');
        const wrapperEl = document.querySelector('#graphContainerWrapper');
        window.graphEngine = new CleanKnowledgeGraphEngine(svgEl, wrapperEl);

        try {
          const profile = await apiJson('/api/learning/profile');
          window.graphEngine.studentProfile = new Map((profile.nodes || []).map(n => [n.id, n.status]));
          window.graphEngine.render();
        } catch (_) {}

        renderTabs();
        renderStudyResourcePackages();
      } catch (err) {
        console.warn('Session unauthenticated or expired', err);
        const roleBadge = document.querySelector('#roleBadge');
        const userDisplay = document.querySelector('#usernameDisplay');
        roleBadge.className = 'role-badge student';
        roleBadge.textContent = '未登录';
        userDisplay.innerHTML = '<a href="/login/index.php?wantsurl=/agent/" style="color:var(--primary); text-decoration:none; font-weight:700;">点击登录平台</a>';

        currentRole = 'student';
        const svgEl = document.querySelector('#knowledgeGraphSvg');
        const wrapperEl = document.querySelector('#graphContainerWrapper');
        window.graphEngine = new CleanKnowledgeGraphEngine(svgEl, wrapperEl);
        renderTabs();
        renderStudyResourcePackages();

        const modal = document.querySelector('#loginPromptModal');
        if (modal) modal.style.display = 'flex';
      }
    }'''

content = content.replace(old_init_session, new_init_session)

with open('agent-ui/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated agent-ui/index.html with login prompt modal')

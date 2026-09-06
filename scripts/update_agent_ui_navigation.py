import re

with open('agent-ui/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Header to add "返回 Moodle 课程主页" and headerActionBtn
old_header = r'''    <!-- Top Header -->
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
    </header>'''

new_header = r'''    <!-- Top Header -->
    <header class="app-header">
      <div class="brand-title" style="display:flex; align-items:center; gap:16px;">
        <a href="/course/view.php?id=2" class="btn btn-secondary" style="display:inline-flex; align-items:center; gap:6px; padding:7px 14px; font-size:.88rem; font-weight:600; text-decoration:none; border-radius:6px; border:1px solid #cbd5e1; color:#334155; background:#ffffff;">
          ‹ 返回 Moodle 课程主页
        </a>
        <div>
          <h1>电力系统储能技术</h1>
          <div class="brand-subtitle">国家级精品课程 · AI 智慧教学与高精度知识网络平台</div>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:12px;">
        <div class="user-pill" id="userPill">
          <span id="roleBadge" class="role-badge student">学习者</span>
          <span id="usernameDisplay">加载中...</span>
        </div>
        <a id="headerActionBtn" href="/login/index.php?wantsurl=/agent/" class="btn btn-primary btn-sm" style="display:none; text-decoration:none;">
          立即登录
        </a>
        <button id="btnHeaderLogout" type="button" class="btn btn-secondary btn-sm" style="display:none;" onclick="handleUserLogout()">
          退出
        </button>
      </div>
    </header>'''

if old_header in content:
    content = content.replace(old_header, new_header)
    print("Header replaced successfully")
else:
    print("WARNING: old_header not found")

# 2. Update Login Prompt Modal to add "已在原页面登录？点击重新检测" button
old_modal_btns = r'''      <a href="/login/index.php?wantsurl=/agent/" class="btn btn-primary" style="display:block; width:100%; padding:12px; font-size:1rem; text-decoration:none; box-sizing:border-box; margin-bottom:14px; border-radius:8px;">
        立即登录 Moodle 平台
      </a>'''

new_modal_btns = r'''      <a href="/login/index.php?wantsurl=/agent/" class="btn btn-primary" style="display:block; width:100%; padding:12px; font-size:1rem; text-decoration:none; box-sizing:border-box; margin-bottom:10px; border-radius:8px;">
        前往 Moodle 登录页面
      </a>
      <button type="button" class="btn btn-secondary" onclick="checkAndRefreshSession(true)" style="display:block; width:100%; padding:10px; font-size:.92rem; box-sizing:border-box; margin-bottom:14px; border-radius:8px;">
        已在其他页面登录？点击即刻同步
      </button>'''

if old_modal_btns in content:
    content = content.replace(old_modal_btns, new_modal_btns)
    print("Modal buttons replaced successfully")
else:
    print("WARNING: old_modal_btns not found")

# 3. Update initSession and add logout and auto-sync functions
old_init_session_block = r'''    async function initSession() {
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

new_init_session_block = r'''    function handleUserLogout() {
      if (currentCsrfToken) {
        window.location.href = `/login/logout.php?sesskey=${encodeURIComponent(currentCsrfToken)}`;
      } else {
        window.location.href = `/login/logout.php`;
      }
    }

    async function checkAndRefreshSession(showAlertIfUnauth = false) {
      await initSession();
      if (showAlertIfUnauth && !currentCsrfToken) {
        alert('尚未检测到有效登录状态，请先在 Moodle 平台完成登录后再试。');
      }
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
        const headerActionBtn = document.querySelector('#headerActionBtn');
        const btnHeaderLogout = document.querySelector('#btnHeaderLogout');
        const roleLabels = { teacher: '主讲教师', admin: '教务管理员', student: '学生' };

        roleBadge.className = `role-badge ${currentRole}`;
        roleBadge.textContent = roleLabels[currentRole] || '用户';
        userDisplay.textContent = currentRole === 'teacher' ? '教师工作台' : (currentRole === 'admin' ? '管理员' : '林同学');

        if (headerActionBtn) headerActionBtn.style.display = 'none';
        if (btnHeaderLogout) btnHeaderLogout.style.display = 'inline-block';

        // Hide Login modal if open
        const modal = document.querySelector('#loginPromptModal');
        if (modal) modal.style.display = 'none';

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
        currentCsrfToken = '';
        currentRole = 'student';

        const roleBadge = document.querySelector('#roleBadge');
        const userDisplay = document.querySelector('#usernameDisplay');
        const headerActionBtn = document.querySelector('#headerActionBtn');
        const btnHeaderLogout = document.querySelector('#btnHeaderLogout');

        roleBadge.className = 'role-badge student';
        roleBadge.textContent = '未登录';
        userDisplay.innerHTML = '<span style="color:#64748b;">访客模式</span>';

        if (headerActionBtn) headerActionBtn.style.display = 'inline-block';
        if (btnHeaderLogout) btnHeaderLogout.style.display = 'none';

        const svgEl = document.querySelector('#knowledgeGraphSvg');
        const wrapperEl = document.querySelector('#graphContainerWrapper');
        window.graphEngine = new CleanKnowledgeGraphEngine(svgEl, wrapperEl);
        renderTabs();
        renderStudyResourcePackages();

        const modal = document.querySelector('#loginPromptModal');
        if (modal) modal.style.display = 'flex';
      }
    }

    // Auto-sync session when user returns to this tab
    let autoSyncDebounce = null;
    function syncOnTabFocus() {
      if (!currentCsrfToken) {
        clearTimeout(autoSyncDebounce);
        autoSyncDebounce = setTimeout(() => {
          initSession();
        }, 400);
      }
    }
    window.addEventListener('focus', syncOnTabFocus);
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') {
        syncOnTabFocus();
      }
    });'''

if old_init_session_block in content:
    content = content.replace(old_init_session_block, new_init_session_block)
    print("initSession block updated successfully")
else:
    print("WARNING: old_init_session_block not found")

with open('agent-ui/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved updated agent-ui/index.html")

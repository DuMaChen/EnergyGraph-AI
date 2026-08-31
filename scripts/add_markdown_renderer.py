import re

with open('agent-ui/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add marked.min.js in <head>
if 'marked.min.js' not in content:
    content = content.replace('</head>', '  <script src="/agent/marked.min.js"></script>\n</head>')

# 2. Add rich Markdown CSS styles
md_css = r'''
    /* -------------------------------------------------------------------------
       专业学术 Markdown 渲染排版规范 (无表情符号，高对比度，清晰层级)
       ------------------------------------------------------------------------- */
    .markdown-rendered, .qa-response-text, .ai-markdown-box {
      line-height: 1.85;
      font-size: 0.96rem;
      color: #1e293b;
      word-break: break-word;
    }
    .markdown-rendered h1, .markdown-rendered h2, .markdown-rendered h3, .markdown-rendered h4,
    .qa-response-text h1, .qa-response-text h2, .qa-response-text h3, .qa-response-text h4,
    .ai-markdown-box h1, .ai-markdown-box h2, .ai-markdown-box h3, .ai-markdown-box h4 {
      color: #0f172a;
      font-weight: 750;
      margin-top: 1.35rem;
      margin-bottom: 0.55rem;
      line-height: 1.4;
    }
    .markdown-rendered h1, .qa-response-text h1, .ai-markdown-box h1 { font-size: 1.32rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }
    .markdown-rendered h2, .qa-response-text h2, .ai-markdown-box h2 { font-size: 1.18rem; border-bottom: 1px solid #f1f5f9; padding-bottom: 4px; color: #0f766e; }
    .markdown-rendered h3, .qa-response-text h3, .ai-markdown-box h3 { font-size: 1.06rem; color: #1e293b; }
    .markdown-rendered h4, .qa-response-text h4, .ai-markdown-box h4 { font-size: 0.98rem; color: #334155; }
    
    .markdown-rendered p, .qa-response-text p, .ai-markdown-box p {
      margin: 0.7rem 0;
      line-height: 1.8;
    }
    
    .markdown-rendered ul, .markdown-rendered ol,
    .qa-response-text ul, .qa-response-text ol,
    .ai-markdown-box ul, .ai-markdown-box ol {
      padding-left: 1.6rem;
      margin: 0.7rem 0;
    }
    .markdown-rendered li, .qa-response-text li, .ai-markdown-box li {
      margin: 0.35rem 0;
      line-height: 1.75;
    }
    .markdown-rendered li::marker, .qa-response-text li::marker, .ai-markdown-box li::marker {
      color: #0f766e;
      font-weight: 700;
    }
    
    .markdown-rendered strong, .qa-response-text strong, .ai-markdown-box strong {
      font-weight: 750;
      color: #0f172a;
    }
    .markdown-rendered em, .qa-response-text em, .ai-markdown-box em {
      font-style: italic;
      color: #334155;
    }
    
    .markdown-rendered code, .qa-response-text code, .ai-markdown-box code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.88em;
      background: #f1f5f9;
      color: #0f766e;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 2px 6px;
    }
    
    .markdown-rendered pre, .qa-response-text pre, .ai-markdown-box pre {
      background: #0f172a;
      color: #f8fafc;
      padding: 14px 18px;
      border-radius: 8px;
      overflow-x: auto;
      margin: 1rem 0;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.88rem;
      line-height: 1.6;
      border: 1px solid #334155;
    }
    .markdown-rendered pre code, .qa-response-text pre code, .ai-markdown-box pre code {
      background: transparent;
      color: inherit;
      border: none;
      padding: 0;
      font-size: inherit;
    }
    
    .markdown-rendered blockquote, .qa-response-text blockquote, .ai-markdown-box blockquote {
      margin: 0.9rem 0;
      padding: 10px 18px;
      background: #f0fdfa;
      border-left: 4px solid #0f766e;
      border-radius: 0 8px 8px 0;
      color: #1e293b;
      font-size: 0.94rem;
    }
    .markdown-rendered blockquote p, .qa-response-text blockquote p, .ai-markdown-box blockquote p {
      margin: 0.35rem 0;
    }
    
    .markdown-rendered table, .qa-response-text table, .ai-markdown-box table {
      width: 100%;
      border-collapse: collapse;
      margin: 1.1rem 0;
      font-size: 0.92rem;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      overflow: hidden;
    }
    .markdown-rendered th, .qa-response-text th, .ai-markdown-box th {
      background: #f8fafc;
      color: #0f172a;
      font-weight: 700;
      text-align: left;
      padding: 10px 14px;
      border: 1px solid #cbd5e1;
      border-bottom: 2px solid #94a3b8;
    }
    .markdown-rendered td, .qa-response-text td, .ai-markdown-box td {
      padding: 8px 14px;
      border: 1px solid #e2e8f0;
      color: #334155;
    }
    .markdown-rendered tr:nth-child(even), .qa-response-text tr:nth-child(even), .ai-markdown-box tr:nth-child(even) {
      background: #f8fafc;
    }
    
    .markdown-rendered hr, .qa-response-text hr, .ai-markdown-box hr {
      border: none;
      border-top: 1px solid #e2e8f0;
      margin: 1.3rem 0;
    }
    
    /* Math / Formula styling */
    .math-inline {
      font-family: "Cambria Math", "Latin Modern Math", "STIX Two Math", "Times New Roman", serif;
      font-style: italic;
      color: #0369a1;
      padding: 0 3px;
      font-size: 1.05em;
    }
    .math-block {
      text-align: center;
      margin: 1rem 0;
      padding: 10px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      font-family: "Cambria Math", "Latin Modern Math", "STIX Two Math", "Times New Roman", serif;
      color: #0369a1;
      font-size: 1.1em;
      overflow-x: auto;
    }
'''

content = content.replace('    /* Q&A Stream */', md_css + '\n    /* Q&A Stream */')

# 3. Add renderMarkdownToHtml function
helper_js = r'''
    function escapeHtml(str) {
      return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function renderMarkdownToHtml(markdownText) {
      if (!markdownText) return '';
      let raw = String(markdownText);

      // Handle math syntax $...$ and $$...$$
      raw = raw.replace(/\$\$([^$]+)\$\$/g, '<div class="math-block">$1</div>');
      raw = raw.replace(/\$([^$\n]+)\$/g, '<span class="math-inline">$1</span>');

      if (window.marked && typeof window.marked.parse === 'function') {
        try {
          return window.marked.parse(raw, { gfm: true, breaks: true });
        } catch (e) {
          console.warn('marked parse error', e);
        }
      }

      // Robust built-in markdown parser fallback
      let html = raw
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/gim, '<em>$1</em>')
        .replace(/`([^`]+)`/gim, '<code>$1</code>')
        .replace(/^\> (.*$)/gim, '<blockquote><p>$1</p></blockquote>')
        .replace(/\n\n/gim, '</p><p>')
        .replace(/\n/gim, '<br />');
      return `<p>${html}</p>`;
    }
'''

# 4. Update runStreamQA to use renderMarkdownToHtml
old_run_qa = r'''    async function runStreamQA(questionText, nodeId = null) {
      const qaCard = document.querySelector('#qaOutputCard');
      const responseContent = document.querySelector('#qaResponseContent');
      const indicator = document.querySelector('#qaStatusIndicator');

      qaCard.style.display = 'block';
      qaCard.scrollIntoView({ behavior: 'smooth' });
      responseContent.textContent = 'AI 助教正在依据课程资料检索并思考...';
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
    }'''

new_run_qa = helper_js + r'''
    async function runStreamQA(questionText, nodeId = null) {
      const qaCard = document.querySelector('#qaOutputCard');
      const responseContent = document.querySelector('#qaResponseContent');
      const indicator = document.querySelector('#qaStatusIndicator');

      qaCard.style.display = 'block';
      qaCard.scrollIntoView({ behavior: 'smooth' });
      responseContent.className = 'qa-response-text markdown-rendered';
      responseContent.innerHTML = '<div style="color:var(--muted); font-style:italic;">AI 助教正在依据课程资料与讯飞知识库检索并思考...</div>';
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
        let fullText = '';

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
              fullText += data.text || '';
              responseContent.innerHTML = renderMarkdownToHtml(fullText);
            } else if (evt === 'done') {
              indicator.textContent = '回答完成';
              responseContent.innerHTML = renderMarkdownToHtml(fullText);
            }
          }
          if (done) break;
        }
      } catch (err) {
        responseContent.innerHTML = `<div style="color:#b91c1c; background:#fef2f2; padding:12px 16px; border-radius:6px; border:1px solid #fca5a5;">生成异常：${escapeHtml(err.message || '请稍后重试')}</div>`;
        indicator.textContent = '生成中断';
      }
    }'''

if old_run_qa in content:
    content = content.replace(old_run_qa, new_run_qa)
    print("runStreamQA updated with Markdown renderer")
else:
    print("WARNING: old_run_qa not found")

# 5. Also update teacher AI question draft preview to use renderMarkdownToHtml
old_draft_render = "document.querySelector('#aiGeneratedPreviewText').textContent = answer;"
new_draft_render = "const prevBox = document.querySelector('#aiGeneratedPreviewText'); prevBox.className = 'ai-markdown-box markdown-rendered'; prevBox.innerHTML = renderMarkdownToHtml(answer);"

if old_draft_render in content:
    content = content.replace(old_draft_render, new_draft_render)
    print("aiGeneratedPreviewText updated with Markdown renderer")
else:
    print("WARNING: old_draft_render not found")

with open('agent-ui/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved updated agent-ui/index.html")

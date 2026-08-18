const fallbackWorkItems = [
  {
    id: 'executive-value-memo',
    title: 'Executive value memo',
    project: 'Kojie voice-over career',
    summary: 'Drafting the client-facing value narrative for the Kojie voice-over project.',
    status: 'in_progress',
    stage: 'Drafting',
    time: '2 min ago',
    model: 'Gemma via LM Studio',
    tags: ['Research', 'Needs approval'],
    artifactSummary: 'A concise business-facing assessment explaining how AgencyOS Teams creates value through portfolio visibility, better outreach workflows, clearer handoffs, and stronger governance.',
    nextAction: 'Approve'
  }
];

let workItems = [];

const columns = [
  { key: 'in_progress', label: 'In progress' },
  { key: 'waiting', label: 'Waiting' },
  { key: 'ready', label: 'Ready' },
  { key: 'completed', label: 'Completed' }
];

const statusConfig = {
  in_progress: { className: 'amber', label: 'Drafting' },
  waiting: { className: '', label: 'Approval' },
  ready: { className: 'green', label: 'Ready' },
  completed: { className: 'green', label: 'Closed' }
};

const state = {
  selectedId: null,
  currentView: 'workboard',
  lastMarkdownOutput: '',
  lastMarkdownUrl: '',
  chatMessages: [
    {
      role: 'assistant',
      content: 'AgencyOS is ready. Send a project brief to the LM Studio endpoint and I will return a structured response.'
    }
  ],
  // Controls whether the preview panel is visible. Start visible by default; user can close it with the X.
  previewVisible: true
};

function formatTagClasses(tag) {
  if (tag === 'Ready' || tag === 'Closed') return 'tag green';
  if (tag === 'Drafting' || tag === 'Reviewing' || tag === 'Approval') return 'tag amber';
  return 'tag slate';
}

function safeText(value) {
  return String(value ?? '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderNavigation() {
  document.querySelectorAll('.nav-item[data-view]').forEach(item => {
    const isActive = item.dataset.view === state.currentView;
    item.classList.toggle('active', isActive);
    item.onclick = () => {
      state.currentView = item.dataset.view;
      renderNavigation();
      renderWorkspaceViews();
      if (state.currentView === 'new-project') {
        hydrateNewProjectForm();
      }
    };
  });
}

function renderWorkspaceViews() {
  const boardView = document.getElementById('workboardView');
  const projectView = document.getElementById('newProjectView');

  if (!boardView || !projectView) return;
  boardView.classList.toggle('hidden', state.currentView === 'new-project');
  projectView.classList.toggle('hidden', state.currentView !== 'new-project');
}

function renderStats() {
  const statsContainer = document.getElementById('stats');
  const counts = {
    in_progress: workItems.filter(item => item.status === 'in_progress').length,
    waiting: workItems.filter(item => item.status === 'waiting').length,
    ready: workItems.filter(item => item.status === 'ready').length,
    completed: workItems.filter(item => item.status === 'completed').length
  };

  statsContainer.innerHTML = [
    { label: 'In progress', value: counts.in_progress },
    { label: 'Waiting', value: counts.waiting },
    { label: 'Ready', value: counts.ready },
    { label: 'Completed', value: counts.completed }
  ].map(item => `
    <div class="stat-card">
      <div class="label">${item.label}</div>
      <div class="value">${item.value}</div>
    </div>
  `).join('');
}

function renderBoard() {
  const board = document.getElementById('board');

  board.innerHTML = columns.map(column => {
    const items = workItems.filter(item => item.status === column.key);

    return `
      <div class="column">
        <div class="column-header">
          <h3>${column.label}</h3>
          <span class="chip">${items.length}</span>
        </div>
        ${items.map(item => `
          <article class="task-card" data-id="${safeText(item.id)}">
            <h4>${safeText(item.title)}</h4>
            <p>${safeText(item.summary)}</p>
            <div class="meta">
              <span class="${formatTagClasses(item.stage)}">${safeText(item.stage)}</span>
              <span class="time">${safeText(item.time)}</span>
            </div>
          </article>
        `).join('') || '<div style="padding: 8px 6px; color: var(--muted); font-size: 0.8rem;">No items</div>'}
      </div>
    `;
  }).join('');

  document.querySelectorAll('.task-card').forEach(card => {
    card.addEventListener('click', () => {
      state.selectedId = card.dataset.id;
      // Ensure the preview becomes visible when a project is explicitly selected
      state.previewVisible = true;
      renderPreview();
      document.querySelectorAll('.task-card').forEach(item => item.style.borderColor = 'var(--line)');
      card.style.borderColor = '#b78045';
    });
  });

  const selectedCard = document.querySelector(`.task-card[data-id="${state.selectedId}"]`);
  if (selectedCard) {
    selectedCard.style.borderColor = '#b78045';
  }
}

async function loadAvailableModels() {
  const modelInput = document.getElementById('lmModelInput');
  const endpointInput = document.getElementById('lmEndpointInput');
  if (!modelInput || !endpointInput) return;

  const endpoint = (endpointInput.value || 'http://localhost:1234/v1').replace(/\/$/, '');

  try {
    const response = await fetch(`${endpoint}/models`);
    if (!response.ok) throw new Error('Models endpoint unavailable');
    const data = await response.json();
    const modelOptions = Array.isArray(data?.data) ? data.data.map(item => item.id || item.name || item.model).filter(Boolean) : [];

    if (modelOptions.length) {
      modelInput.innerHTML = modelOptions.map(model => `<option value="${safeText(model)}">${safeText(model)}</option>`).join('');
      if (!modelInput.value) {
        modelInput.value = modelOptions[0];
      }
      return;
    }

    modelInput.innerHTML = '<option value="">Select a model</option>';
    modelInput.value = '';
  } catch (error) {
    modelInput.innerHTML = '<option value="">Select a model</option>';
    modelInput.value = '';
  }
}

function hydrateNewProjectForm() {
  const item = workItems.find(entry => entry.id === state.selectedId) || workItems[0];
  const projectInput = document.getElementById('projectNameInput');
  const clientInput = document.getElementById('clientNameInput');
  const requestTypeInput = document.getElementById('requestTypeInput');
  const endpointInput = document.getElementById('lmEndpointInput');
  const briefInput = document.getElementById('requestBriefInput');
  const modelInput = document.getElementById('lmModelInput');

  if (!projectInput || !clientInput || !requestTypeInput || !endpointInput || !briefInput) return;

  projectInput.value = item?.project || '';
  clientInput.value = item?.project ? 'Client' : '';
  requestTypeInput.value = 'Opportunity review';
  endpointInput.value = 'http://localhost:1234/v1';
  briefInput.value = item?.artifactSummary || 'Review this opportunity and propose the highest-value AgencyOS intervention.';

  if (modelInput) {
    modelInput.value = modelInput.value || '';
  }

  if (requestTypeInput && !Array.from(requestTypeInput.options).some(option => option.value === requestTypeInput.value)) {
    requestTypeInput.value = 'Opportunity review';
  }

  state.chatMessages = [
    {
      role: 'assistant',
      content: 'AgencyOS is ready. Send a project brief to the LM Studio endpoint and I will return a structured response.'
    }
  ];
  state.lastMarkdownOutput = '';
  renderMarkdownDownloadLink();

  renderChatMessages();
  updateRequestJsonPreview();
  bindFormEvents();
  loadAvailableModels();
}

function buildRequestPayload() {
  const item = workItems.find(entry => entry.id === state.selectedId) || workItems[0];
  const projectName = document.getElementById('projectNameInput')?.value || item?.project || 'AgencyOS project';
  const clientName = document.getElementById('clientNameInput')?.value || 'Client';
  const requestType = document.getElementById('requestTypeInput')?.value || 'Opportunity review';
  const brief = document.getElementById('requestBriefInput')?.value || item?.artifactSummary || 'Review this project and identify the operational opportunity.';

  return {
    request_id: `req-${Date.now()}`,
    project_name: projectName,
    client_name: clientName,
    request_type: requestType,
    source_item: item?.id || null,
    brief,
    status: 'new',
    created_at: new Date().toISOString(),
    model: document.getElementById('lmModelInput')?.value || 'Select a model'
  };
}

function updateRequestJsonPreview() {
  const preview = document.getElementById('requestJsonPreview');
  if (!preview) return;
  const payload = buildRequestPayload();
  preview.textContent = JSON.stringify(payload, null, 2);
}

function renderChatMessages() {
  const container = document.getElementById('chatHistory');
  if (!container) return;

  container.innerHTML = state.chatMessages.map(message => `
    <div class="chat-message ${message.role}">
      ${safeText(message.content)}
    </div>
  `).join('');

  container.scrollTop = container.scrollHeight;
}

function resetChatForm() {
  hydrateNewProjectForm();
}

function renderMarkdownDownloadLink() {
  const link = document.getElementById('markdownDownloadLink');
  if (!link) return;

  const markdown = state.lastMarkdownOutput.trim();
  if (!markdown) {
    link.style.display = 'none';
    link.removeAttribute('href');
    link.removeAttribute('download');
    return;
  }

  if (state.lastMarkdownUrl) {
    URL.revokeObjectURL(state.lastMarkdownUrl);
  }

  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  state.lastMarkdownUrl = url;

  link.href = url;
  link.download = `${(document.getElementById('projectNameInput')?.value || 'agencyos-project').replace(/[^a-z0-9-_]+/gi, '-').toLowerCase()}.md`;
  link.style.display = 'inline-flex';
  link.textContent = 'Download .md';
}

function appendChatMessage(role, content) {
  state.chatMessages.push({ role, content });
  renderChatMessages();

  if (role === 'assistant') {
    state.lastMarkdownOutput = content;
    renderMarkdownDownloadLink();
  }
}

async function sendRequestToLMStudio() {
  const requestInput = document.getElementById('requestBriefInput');
  const endpointInput = document.getElementById('lmEndpointInput');
  const modelInput = document.getElementById('lmModelInput');

  const userBrief = requestInput?.value?.trim();
  if (!userBrief) {
    appendChatMessage('assistant', 'Please enter a request before sending it to LM Studio.');
    return;
  }

  const model = modelInput?.value?.trim();
  if (!model) {
    appendChatMessage('assistant', 'Choose a valid model from LM Studio before sending the request.');
    return;
  }

  const payload = buildRequestPayload();
  const endpoint = (endpointInput?.value || 'http://localhost:1234/v1').replace(/\/$/, '');

  appendChatMessage('user', `Request submitted for ${payload.project_name}: ${userBrief}`);

  const submitButton = document.getElementById('sendRequestButton');
  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = 'Sending...';
  }

  try {
    const response = await fetch('http://localhost:8001/api/new-project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...payload,
        endpoint,
        model,
        brief: userBrief
      })
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.error || 'Agent intake failed');
    }

    const reply = data.output || 'No response received from the model.';
    appendChatMessage('assistant', reply);

    if (data.files && data.files.length) {
      appendChatMessage('assistant', `Saved markdown deliverables to: ${data.folder}`);
    }
  } catch (error) {
    appendChatMessage('assistant', `Unable to reach the local AgencyOS intake service. Check that the backend server is running. Details: ${safeText(error.message)}`);
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.textContent = 'Send request';
    }
  }
}

function bindFormEvents() {
  const requestBriefInput = document.getElementById('requestBriefInput');
  const requestTypeInput = document.getElementById('requestTypeInput');
  const projectNameInput = document.getElementById('projectNameInput');
  const clientNameInput = document.getElementById('clientNameInput');
  const lmEndpointInput = document.getElementById('lmEndpointInput');
  const lmModelInput = document.getElementById('lmModelInput');
  const sendButton = document.getElementById('sendRequestButton');
  const resetButton = document.getElementById('resetChatButton');
  const markdownLink = document.getElementById('markdownDownloadLink');

  [requestBriefInput, requestTypeInput, projectNameInput, clientNameInput, lmEndpointInput, lmModelInput].forEach(element => {
    if (element) {
      element.oninput = updateRequestJsonPreview;
      element.onchange = updateRequestJsonPreview;
    }
  });

  if (lmEndpointInput) {
    lmEndpointInput.onchange = () => {
      loadAvailableModels();
    };
  }

  if (sendButton) {
    sendButton.onclick = sendRequestToLMStudio;
  }

  if (resetButton) {
    resetButton.onclick = resetChatForm;
  }
}

function renderPreview() {
  const preview = document.getElementById('preview');
  const item = workItems.find(entry => entry.id === state.selectedId) || workItems[0];

  // If preview has been explicitly closed, render nothing
  if (!state.previewVisible) {
    preview.innerHTML = '';
    preview.style.display = 'none';
    return;
  }

  if (!item) {
    preview.innerHTML = '<div class="preview-panel"><h3 class="preview-title">Selected artifact</h3><p class="preview-sub">No work available.</p></div>';
    preview.style.display = 'block';
    return;
  }

  preview.innerHTML = `
    <div class="preview-panel">
      <button id="previewCloseButton" class="preview-close" title="Close">✕</button>
      <h3 class="preview-title">Selected artifact</h3>
      <p class="preview-sub">${safeText(item.title)} — ${safeText(item.project)}</p>

      <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
        <span class="summary-pill">${safeText(item.stage)}</span>
        <span style="color: var(--muted); font-size: 0.75rem;">Updated ${safeText(item.time)}</span>
      </div>

      <div class="artifact">
        <h5>Artifact summary</h5>
        <p>${safeText(item.artifactSummary)}</p>
      </div>

      <div class="footer-mini">
        ${item.tags.map(tag => `<span class="mini-badge">${safeText(tag)}</span>`).join('')}
        <span class="mini-badge">${safeText(item.model)}</span>
      </div>

      <div class="actions">
        <button class="button primary">Open</button>
        <button class="button secondary">${safeText(item.nextAction)}</button>
        <button class="button secondary">Export</button>
      </div>
    </div>
  `;

  // Ensure preview is visible
  preview.style.display = 'block';

  // Wire the close button to hide the preview and persist that state until next selection
  const closeBtn = document.getElementById('previewCloseButton');
  if (closeBtn) {
    closeBtn.onclick = () => {
      state.previewVisible = false;
      preview.innerHTML = '';
      preview.style.display = 'none';
    };
  }

  // Wire action buttons so they are clickable and provide immediate feedback.
  const openBtn = preview.querySelector('.actions .button.primary');
  const secondaryBtns = preview.querySelectorAll('.actions .button.secondary');

  if (openBtn) {
    openBtn.onclick = (e) => {
      e.stopPropagation();
      appendChatMessage('assistant', `Opening artifact: ${item.title}`);
      // Highlight the card visually (non-persistent)
      const card = document.querySelector(`.task-card[data-id="${item.id}"]`);
      if (card) {
        card.style.boxShadow = '0 12px 28px rgba(31,31,31,0.08)';
        setTimeout(() => card.style.boxShadow = '', 1200);
      }
    };
  }

  if (secondaryBtns && secondaryBtns.length) {
    // First secondary button is the item-specific next action (e.g., Approve, Review)
    if (secondaryBtns[0]) {
      secondaryBtns[0].onclick = (e) => {
        e.stopPropagation();
        appendChatMessage('assistant', `${item.nextAction} clicked for ${item.title}`);
      };
    }

    // Second secondary button is Export
    if (secondaryBtns[1]) {
      secondaryBtns[1].onclick = (e) => {
        e.stopPropagation();
        appendChatMessage('assistant', `Exporting ${item.title}...`);
        // Create a simple markdown export from the artifact summary
        try {
          const md = `# ${item.title}\n\nProject: ${item.project}\n\n${item.artifactSummary || ''}`;
          const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = `${(item.id || item.title).replace(/[^a-z0-9-_]+/gi, '-').toLowerCase()}.md`;
          document.body.appendChild(a);
          a.click();
          a.remove();
          setTimeout(() => URL.revokeObjectURL(url), 1500);
        } catch (err) {
          appendChatMessage('assistant', `Failed to export: ${err.message}`);
        }
      };
    }
  }
}

async function loadWorkItems() {
  try {
    const response = await fetch('./workboard-data.json');
    if (!response.ok) throw new Error('No data file');
    const payload = await response.json();
    workItems = Array.isArray(payload.items) ? payload.items : payload;
  } catch (error) {
    workItems = fallbackWorkItems;
  }

  if (!workItems.length) {
    workItems = fallbackWorkItems;
  }

  state.selectedId = workItems[0].id;
  renderStats();
  renderBoard();
  renderPreview();
  renderNavigation();
  renderWorkspaceViews();
  hydrateNewProjectForm();
}

loadWorkItems();

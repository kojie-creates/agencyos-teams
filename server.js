const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8001;
const ROOT_DIR = __dirname;
const PROJECTS_DIR = path.join(ROOT_DIR, 'projects');

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function sanitizeSlug(value) {
  return String(value || 'agencyos-project')
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'agencyos-project';
}

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  });
  res.end(body);
}

function ensureProjectFiles(projectName, briefText) {
  const slug = sanitizeSlug(projectName);
  const projectDir = path.join(PROJECTS_DIR, slug);
  const deliverablesDir = path.join(projectDir, 'deliverables');
  const requestsDir = path.join(projectDir, 'requests');
  const researchDir = path.join(projectDir, 'research');
  const opsDir = path.join(projectDir, 'ops');
  const launchDir = path.join(projectDir, 'launch');
  const approvalsDir = path.join(projectDir, 'approvals');
  const snapshotsDir = path.join(projectDir, 'snapshots');

  // create directories
  [deliverablesDir, requestsDir, researchDir, opsDir, launchDir, approvalsDir, snapshotsDir].forEach(d => ensureDir(d));

  const createdAt = new Date().toISOString();
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  const requestJson = {
    project_name: projectName,
    created_at: createdAt,
    brief: briefText
  };

  const files = {
    'brief.md': `# ${projectName}\n\n${briefText}\n`,
    'updates.md': `# Updates\n\n- Project created: ${createdAt}\n- Intake captured and submitted to LM Studio for synthesis.\n`,
    'plan.md': `# Plan\n\n1. Confirm project goals and operating context.\n2. Review opportunities, risks, and requirements.\n3. Draft output and next actions.\n4. Publish to the project brief and update logs.\n`,
    'assigned-beings.md': `# Assigned Beings\n\n- Project owner: ${projectName}\n- Operations lead: AgencyOS Operator\n- Research support: AgencyOS Research Agency\n- Risk validation: AgencyOS Risk & Proof Agency\n`
  };

  // write deliverable files
  Object.entries(files).forEach(([fileName, content]) => {
    const dest = path.join(deliverablesDir, fileName);
    fs.writeFileSync(dest, content, 'utf8');

    // create a timestamped snapshot copy
    const snapName = `${timestamp}-${fileName}`;
    fs.writeFileSync(path.join(snapshotsDir, snapName), content, 'utf8');
  });

  // write the intake/request
  fs.writeFileSync(path.join(requestsDir, 'intake-request.json'), JSON.stringify(requestJson, null, 2), 'utf8');

  // generate project index (README) with metadata and links
  const indexContent = [`# ${projectName}`, ``, `**Created:** ${createdAt}`, `**Client:** ${requestJson.client_name || ''}`, ``, `## Summary`, ``, briefText, ``, `## Deliverables`, ``];

  Object.keys(files).forEach(fn => {
    indexContent.push(`- [${fn}](./deliverables/${fn})`);
  });

  indexContent.push(``, `## Snapshots`, ``);
  const snapshotFiles = fs.readdirSync(snapshotsDir).filter(f => f.endsWith('.md'));
  snapshotFiles.forEach(sf => indexContent.push(`- [${sf}](./snapshots/${sf})`));

  indexContent.push(``, `## Requests`, ``);
  indexContent.push(`- [intake-request.json](./requests/intake-request.json)`);

  const indexPath = path.join(projectDir, 'INDEX.md');
  fs.writeFileSync(indexPath, indexContent.join('\n'), 'utf8');

  // return relative paths for API response
  const relative = p => path.join('projects', slug, path.relative(ROOT_DIR, p)).replace(/\\/g, '/');

  return {
    slug,
    projectDir,
    deliverablesDir,
    researchDir,
    opsDir,
    launchDir,
    approvalsDir,
    snapshotsDir,
    files: Object.keys(files).map(fileName => path.join('projects', slug, 'deliverables', fileName)),
    snapshots: snapshotFiles.map(f => path.join('projects', slug, 'snapshots', f)),
    index: path.join('projects', slug, 'INDEX.md')
  };
}

async function callLmStudio(endpoint, model, payload) {
  const lmEndpoint = (endpoint || 'http://localhost:1234/v1').replace(/\/$/, '');
  const response = await fetch(`${lmEndpoint}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model,
      messages: [
        {
          role: 'system',
          content: 'You are AgencyOS, a strategic operations assistant. Produce a comprehensive markdown brief with headings, bullet points, and concise analysis. Do not stop mid-section; keep going until the response is complete and polished.'
        },
        {
          role: 'user',
          content: JSON.stringify(payload, null, 2)
        }
      ],
      temperature: 0.3,
      max_tokens: 2500,
      stream: false
    })
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`LM Studio request failed (${response.status}): ${message.slice(0, 200)}`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content || 'No response received from the model.';
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }

  if (req.method === 'GET' && url.pathname === '/health') {
    sendJson(res, 200, { ok: true, status: 'ready' });
    return;
  }

  if (req.method === 'POST' && url.pathname === '/api/new-project') {
    try {
      const chunks = [];
      for await (const chunk of req) {
        chunks.push(chunk);
      }
      const body = Buffer.concat(chunks).length ? JSON.parse(Buffer.concat(chunks).toString()) : {};

      const projectName = body.project_name || body.projectName || 'AgencyOS project';
      const clientName = body.client_name || body.clientName || 'Client';
      const requestType = body.request_type || body.requestType || 'Opportunity review';
      const brief = body.brief || 'Review this opportunity and propose the highest-value AgencyOS intervention.';
      const endpoint = body.endpoint || 'http://localhost:1234/v1';
      const model = body.model || 'google/gemma-4-e4b';

      const payload = {
        request_id: `req-${Date.now()}`,
        project_name: projectName,
        client_name: clientName,
        request_type: requestType,
        brief,
        created_at: new Date().toISOString(),
        model
      };

      const generated = await callLmStudio(endpoint, model, payload);
      const created = ensureProjectFiles(projectName, generated);

      sendJson(res, 200, {
        success: true,
        project_name: projectName,
        output: generated,
        project_dir: path.join('projects', created.slug).replace(/\\/g, '/'),
        files: created.files,
        folder: path.join('projects', created.slug).replace(/\\/g, '/')
      });
      return;
    } catch (error) {
      sendJson(res, 500, {
        success: false,
        error: error.message || 'Unable to process request'
      });
      return;
    }
  }

  sendJson(res, 404, { success: false, error: 'Not found' });
});

server.listen(PORT, () => {
  console.log(`AgencyOS intake server running on http://localhost:${PORT}`);
});

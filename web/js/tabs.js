/* Tab content renderers — uses I18n.t(), G.*, shared helpers */
var Tabs = {};
const t = (k, p) => I18n.t(k, p);

/* ── Viewer ─────────────────────────────────────────── */
Tabs.viewer = {
  title: true,
  render() {
    const speeds = ['0.25x','0.5x','1.0x','1.5x','2.0x','4.0x'];
    const speedOpts = speeds.map(s => `<option${s==='1.0x'?' selected':''}>${s}</option>`).join('');
    return `
      <div style="display:flex;gap:0.75rem;height:100%;">
        <!-- Left: file browser -->
        <div style="width:220px;display:flex;flex-direction:column;gap:0.75rem;overflow-y:auto;flex-shrink:0;">
          <div class="card-flat" style="padding:0.75rem;">
            <div class="text-label" style="margin-bottom:0.5rem;">${t('settings.model')}</div>
            <div style="display:flex;gap:0.25rem;margin-bottom:0.5rem;">
              <button class="btn btn-secondary btn-sm" style="flex:1;" onclick="Tabs.viewer.browseModel()">${t('browse')}</button>
              <button class="btn btn-ghost btn-sm" onclick="Tabs.viewer.refreshModels()" title="Refresh">↻</button>
            </div>
            <div id="v-model-list" style="max-height:140px;overflow-y:auto;font-size:12px;" class="text-secondary">Loading...</div>
          </div>
          <div class="card-flat" style="padding:0.75rem;">
            <div class="text-label" style="margin-bottom:0.5rem;">Video / Image</div>
            <div style="display:flex;gap:0.25rem;margin-bottom:0.5rem;">
              <button class="btn btn-secondary btn-sm" style="flex:1;" onclick="Tabs.viewer.browseVideo()">${t('browse')}</button>
              <button class="btn btn-ghost btn-sm" onclick="Tabs.viewer.refreshVideos()" title="Refresh">↻</button>
            </div>
            <div id="v-video-list" style="max-height:200px;overflow-y:auto;font-size:12px;" class="text-secondary">Loading...</div>
          </div>
        </div>
        <!-- Center: canvas + controls -->
        <div style="flex:1;display:flex;flex-direction:column;gap:0.5rem;min-width:0;">
          <div class="card" style="flex:1;display:flex;align-items:center;justify-content:center;min-height:360px;overflow:hidden;">
            <div id="viewer-canvas" style="color:var(--text-02);text-align:center;">${t('viewer.open_hint')}</div>
          </div>
          <!-- Seek slider -->
          <input type="range" id="v-seek" min="0" max="0" value="0" style="width:100%;accent-color:var(--action-link-05);margin:0;" disabled>
          <!-- Control bar -->
          <div style="display:flex;gap:0.35rem;align-items:center;flex-wrap:wrap;">
            <button class="btn btn-secondary btn-sm" id="btn-prev" onclick="Tabs.viewer.stepBack()" disabled title="◀ 1 frame">◀</button>
            <button class="btn btn-primary btn-sm" id="btn-play" onclick="Tabs.viewer.play()" disabled>▶ ${t('viewer.play')}</button>
            <button class="btn btn-secondary btn-sm" id="btn-pause" onclick="Tabs.viewer.pause()" disabled>⏸</button>
            <button class="btn btn-secondary btn-sm" id="btn-next" onclick="Tabs.viewer.stepFwd()" disabled title="▶ 1 frame">▶</button>
            <button class="btn btn-secondary btn-sm" id="btn-stop" onclick="Tabs.viewer.stop()" disabled>⏹</button>
            <span style="width:1px;height:20px;background:var(--border-default);margin:0 0.25rem;"></span>
            <button class="btn btn-secondary btn-sm" id="btn-snapshot" onclick="Tabs.viewer.snapshot()" disabled>📷</button>
            <span style="width:1px;height:20px;background:var(--border-default);margin:0 0.25rem;"></span>
            <label class="text-secondary" style="font-size:12px;">${t('viewer.speed')}:</label>
            <select class="form-input" id="v-speed" style="width:70px;height:28px;font-size:12px;" onchange="Tabs.viewer.setSpeed(this.value)">${speedOpts}</select>
            <div style="flex:1;"></div>
            <span class="text-secondary" style="font-size:12px;" id="v-fps">FPS: —</span>
            <span class="text-secondary" style="font-size:12px;margin-left:0.5rem;" id="v-frame-counter">0 / 0</span>
          </div>
        </div>
        <!-- Right: info panels -->
        <div style="width:210px;display:flex;flex-direction:column;gap:0.5rem;overflow-y:auto;flex-shrink:0;font-size:11px;">
          <div class="card-flat" style="padding:0.6rem;">
            <div class="text-label" style="margin-bottom:0.35rem;font-size:11px;">${t('viewer.model_info')}</div>
            <div id="v-model-info" class="text-secondary">—</div>
          </div>
          <div class="card-flat" style="padding:0.6rem;">
            <div class="text-label" style="margin-bottom:0.35rem;font-size:11px;">${t('viewer.video_info')}</div>
            <div id="v-video-info" class="text-secondary">—</div>
          </div>
          <div class="card-flat" style="padding:0.6rem;">
            <div class="text-label" style="margin-bottom:0.35rem;font-size:11px;">${t('viewer.infer_stats')}</div>
            <div id="v-infer-stats" class="text-secondary">—</div>
          </div>
          <div class="card-flat" style="padding:0.6rem;">
            <div class="text-label" style="margin-bottom:0.35rem;font-size:11px;">${t('viewer.det_results')}</div>
            <div id="viewer-results" class="text-secondary">—</div>
          </div>
          <div class="card-flat" style="padding:0.6rem;">
            <div class="text-label" style="margin-bottom:0.35rem;font-size:11px;">${t('viewer.hw_stats')}</div>
            <div id="v-hw-stats" class="text-secondary">—</div>
          </div>
          <div class="card-flat" style="padding:0.6rem;">
            <div class="text-label" style="margin-bottom:0.35rem;font-size:11px;">${t('viewer.sys_info')}</div>
            <div id="v-sys-info" class="text-secondary">—</div>
          </div>
        </div>
      </div>`;
  },
  async init() {
    this.refreshModels();
    this.refreshVideos();
    // System info
    try {
      const info = await API.sysInfo();
      const el = document.getElementById('v-sys-info');
      if (el) el.innerHTML = `OS: ${info.os||'—'}<br>Python: ${info.python||'—'}<br>ORT: ${info.ort||'—'}<br>Torch: ${info.torch||'—'}<br>CUDA: ${info.cuda||'—'}<br>GPU: ${info.gpu_name||'—'}`;
    } catch(e) {}
    if (G.model) this._showModelInfo(G.model);
    // Seek slider
    const seek = document.getElementById('v-seek');
    if (seek) seek.oninput = () => this._onSeek(+seek.value);
    // Start HW polling
    this._hwInterval = setInterval(() => this._pollHW(), 2000);
    this._pollHW();
    // Keyboard shortcuts
    this._keyHandler = (e) => this._onKey(e);
    document.addEventListener('keydown', this._keyHandler);
  },
  _hwInterval: null,
  async _pollHW() {
    try {
      const h = await API.hwStats();
      const el = document.getElementById('v-hw-stats');
      if (el) el.innerHTML = `CPU: ${h.cpu}%<br>RAM: ${h.ram_mb} MB<br>GPU: ${h.gpu_util||0}%<br>VRAM: ${h.gpu_mem_used||0}/${h.gpu_mem_total||0} MB<br>Temp: ${h.gpu_temp||'—'}°C`;
    } catch(e) {}
  },
  _onKey(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') return;
    if (e.key === ' ') { e.preventDefault(); this._streamSessionId ? (this._paused ? this.play() : this.pause()) : this.play(); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); this.stepBack(); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); this.stepFwd(); }
    else if (e.key === 's' || e.key === 'S') this.snapshot();
    else if (e.key === '+' || e.key === '=') this._changeSpeed(1);
    else if (e.key === '-') this._changeSpeed(-1);
  },
  _changeSpeed(dir) {
    const speeds = [0.25,0.5,1.0,1.5,2.0,4.0];
    const sel = document.getElementById('v-speed');
    const cur = parseFloat(sel.value);
    const idx = speeds.indexOf(cur);
    const next = speeds[Math.max(0, Math.min(speeds.length-1, idx+dir))];
    sel.value = next+'x';
    this.setSpeed(next+'x');
  },
  async refreshModels() {
    try {
      const r = await API.listDir({ path: 'Models', exts: ['.onnx','.pt'] });
      const el = document.getElementById('v-model-list');
      if (!r.files || !r.files.length) { el.textContent = 'No models in Models/'; return; }
      el.innerHTML = r.files.map(f =>
        `<div class="nav-item" style="padding:0.25rem 0.5rem;cursor:pointer;font-size:12px;border-radius:4px;" onclick="Tabs.viewer.selectModel('${f.path.replace(/\\/g,'\\\\').replace(/'/g,"\\'")}')" title="${f.path}">${f.name}</div>`
      ).join('');
    } catch(e) { document.getElementById('v-model-list').textContent = 'Models/ not found'; }
  },
  async refreshVideos() {
    try {
      const r = await API.listDir({ path: 'Videos', exts: ['.mp4','.avi','.mov','.mkv','.jpg','.jpeg','.png','.bmp'] });
      const el = document.getElementById('v-video-list');
      if (!r.files || !r.files.length) { el.textContent = 'No files in Videos/'; return; }
      el.innerHTML = r.files.map(f =>
        `<div class="nav-item" style="padding:0.25rem 0.5rem;cursor:pointer;font-size:12px;border-radius:4px;" onclick="Tabs.viewer.selectVideo('${f.path.replace(/\\/g,'\\\\').replace(/'/g,"\\'")}')" title="${f.path}">${f.name}</div>`
      ).join('');
    } catch(e) { document.getElementById('v-video-list').textContent = 'Videos/ not found'; }
  },
  async selectModel(path) {
    setModel(path);
    this._showModelInfo(path);
  },
  async _showModelInfo(path) {
    try {
      const info = await API.post('/api/model/load', { path });
      const el = document.getElementById('v-model-info');
      if (el && info && !info.error) {
        el.innerHTML = `File: ${info.name||'—'}<br>Input: ${info.input_shape||'—'}<br>Output: ${info.output_shape||'—'}<br>Layout: ${(info.layout||'—').toUpperCase()}<br>Task: ${info.task||'—'}<br>Classes: ${info.num_classes||0}`;
      }
      document.getElementById('btn-play').disabled = !G.model;
    } catch(e) { document.getElementById('v-model-info').textContent = `Error: ${e.message}`; }
  },
  async selectVideo(path) {
    G.videoPath = path;
    const name = path.split(/[\\/]/).pop();
    App.setStatus(`Video: ${name}`);
    document.getElementById('btn-play').disabled = !G.model;
    // Fetch video info
    try {
      const vi = await API.videoInfo(path);
      const el = document.getElementById('v-video-info');
      if (el && !vi.error) {
        el.innerHTML = `File: ${name}<br>Resolution: ${vi.width} × ${vi.height}<br>FPS: ${vi.fps}<br>Frames: ${vi.total_frames?.toLocaleString()}<br>Duration: ${vi.duration}`;
        const seek = document.getElementById('v-seek');
        if (seek) { seek.max = vi.total_frames - 1; seek.disabled = false; }
      }
    } catch(e) { document.getElementById('v-video-info').innerHTML = `File: ${name}`; }
  },
  async browseModel() {
    try {
      const r = await API.selectFile({ filters: 'Models (*.onnx *.pt)' });
      if (r.path) this.selectModel(r.path);
    } catch(e) {}
  },
  async browseVideo() {
    try {
      const r = await API.selectFile({ filters: 'Media (*.mp4 *.avi *.mov *.mkv *.jpg *.jpeg *.png *.bmp)' });
      if (r.path) this.selectVideo(r.path);
    } catch(e) {}
  },
  play() {
    if (!G.model) { App.setStatus('Select a model first'); return; }
    if (!G.videoPath) { App.setStatus('Select a video/image first'); return; }
    // If paused, resume
    if (this._streamSessionId && this._paused) {
      this._togglePause(); return;
    }
    App.setStatus('Starting inference...');
    const ext = G.videoPath.split('.').pop().toLowerCase();
    if (['jpg','jpeg','png','bmp'].includes(ext)) this._inferImage();
    else this._startStream();
  },
  async _inferImage() {
    try {
      const r = await API.post('/api/infer/image', {
        model_path: G.model, image_path: G.videoPath, conf: 0.25
      });
      if (r.error) { App.setStatus('Error: ' + r.error); return; }
      document.getElementById('viewer-canvas').innerHTML = `<img src="data:image/jpeg;base64,${r.image}" style="max-width:100%;max-height:100%;">`;
      document.getElementById('viewer-results').textContent = `${r.detections} detections`;
      document.getElementById('v-infer-stats').innerHTML = `Infer: ${r.infer_ms} ms`;
      App.setStatus(`Inference done: ${r.detections} detections, ${r.infer_ms}ms`);
    } catch(e) { App.setStatus('Error: ' + e.message); }
  },
  _streamSessionId: null,
  _paused: false,
  async _startStream() {
    try {
      const r = await API.post('/api/viewer/start', {
        model_path: G.model, video_path: G.videoPath, conf: 0.25
      });
      if (r.error) { App.setStatus('Error: ' + r.error); return; }
      this._streamSessionId = r.session_id;
      this._paused = false;
      document.getElementById('viewer-canvas').innerHTML = `<img src="/api/viewer/stream/${r.session_id}" style="max-width:100%;max-height:100%;">`;
      this._setControls(true);
      App.setStatus(`Playing: ${r.total_frames} frames @ ${r.fps?.toFixed(1)} FPS`);
      this._pollStatus();
    } catch(e) { App.setStatus('Error: ' + e.message); }
  },
  _setControls(playing) {
    document.getElementById('btn-play').disabled = playing;
    document.getElementById('btn-pause').disabled = !playing;
    document.getElementById('btn-stop').disabled = !this._streamSessionId;
    document.getElementById('btn-prev').disabled = !this._streamSessionId;
    document.getElementById('btn-next').disabled = !this._streamSessionId;
    document.getElementById('btn-snapshot').disabled = !this._streamSessionId;
  },
  async _pollStatus() {
    if (!this._streamSessionId) return;
    try {
      const s = await API.get('/api/viewer/status/' + this._streamSessionId);
      document.getElementById('viewer-results').textContent = `${s.detections} detections`;
      document.getElementById('v-infer-stats').innerHTML = `Infer: ${s.infer_ms} ms`;
      document.getElementById('v-frame-counter').textContent = `${s.frame_idx} / ${s.total}`;
      const seek = document.getElementById('v-seek');
      if (seek && !seek.matches(':active')) seek.value = s.frame_idx;
      if (s.playing && !s.paused) setTimeout(() => this._pollStatus(), 300);
      else if (!s.playing) { App.setStatus('Playback finished'); this._resetAll(); }
    } catch(e) {}
  },
  _resetAll() {
    this._streamSessionId = null;
    this._paused = false;
    document.getElementById('btn-play').disabled = !G.model || !G.videoPath;
    document.getElementById('btn-pause').disabled = true;
    document.getElementById('btn-stop').disabled = true;
    document.getElementById('btn-prev').disabled = true;
    document.getElementById('btn-next').disabled = true;
    document.getElementById('btn-snapshot').disabled = true;
  },
  async _togglePause() {
    if (!this._streamSessionId) return;
    const r = await API.post('/api/viewer/pause/' + this._streamSessionId, {});
    this._paused = r.paused;
    document.getElementById('btn-play').disabled = !this._paused;
    document.getElementById('btn-pause').disabled = this._paused;
    App.setStatus(this._paused ? 'Paused' : 'Playing');
    if (!this._paused) this._pollStatus();
  },
  pause() { this._togglePause(); },
  async stop() {
    if (!this._streamSessionId) return;
    await API.post('/api/viewer/stop/' + this._streamSessionId, {});
    document.getElementById('viewer-canvas').innerHTML = t('viewer.open_hint');
    this._resetAll();
    App.setStatus(t('ready'));
  },
  async stepFwd() {
    if (!this._streamSessionId) return;
    await API.post('/api/viewer/step/' + this._streamSessionId, { delta: 1 });
  },
  async stepBack() {
    if (!this._streamSessionId) return;
    await API.post('/api/viewer/step/' + this._streamSessionId, { delta: -1 });
  },
  async _onSeek(frame) {
    if (!this._streamSessionId) return;
    await API.post('/api/viewer/seek/' + this._streamSessionId, { frame });
  },
  async setSpeed(val) {
    const speed = parseFloat(val);
    if (!this._streamSessionId) return;
    await API.post('/api/viewer/speed/' + this._streamSessionId, { speed });
  },
  async snapshot() {
    if (!this._streamSessionId) return;
    const r = await API.post('/api/viewer/snapshot/' + this._streamSessionId, {});
    if (r.ok) App.setStatus(`Snapshot saved: ${r.path}`);
    else App.setStatus('Snapshot failed: ' + (r.error||''));
  },
};

/* ── Settings ───────────────────────────────────────── */
Tabs.settings = {
  title: true,
  render() {
    return `
      <div style="display:flex;gap:1.5rem;align-items:flex-start;">
        <div style="max-width:480px;flex:1;display:flex;flex-direction:column;gap:1.5rem;">
          <div class="card" style="padding:1.5rem;">
            <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('settings.model')}</h3>
            ${modelInput('set-model')}
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
              <div class="form-group">
                <label class="form-label">${t('settings.model_type')}</label>
                <select class="form-input input-normal" id="model-type">
                  <option value="yolo">YOLO (v5/v7/v8/v9/v11)</option>
                  <option value="darknet">CenterNet</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">${t('settings.batch_size')}</label>
                <input type="number" class="form-input input-normal" value="1" min="1" max="16" id="batch-size">
              </div>
            </div>
            <div class="form-group" style="margin-top:1rem;">
              <label class="form-label">${t('settings.conf')}</label>
              <div style="display:flex;align-items:center;gap:0.75rem;">
                <input type="range" min="1" max="99" step="1" value="25" id="conf-slider" style="flex:1;accent-color:var(--action-link-05);">
                <span class="form-hint" id="conf-value" style="min-width:36px;text-align:right;">0.25</span>
              </div>
            </div>
          </div>
          <div class="card" style="padding:1.5rem;">
            <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('settings.display')}</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
              <div class="form-group"><label class="form-label">${t('settings.box_thick')}</label><input type="number" class="form-input input-normal" value="2" min="1" max="10" id="box-thickness"></div>
              <div class="form-group"><label class="form-label">${t('settings.label_size')}</label><input type="number" class="form-input input-normal" value="0.55" min="0.1" max="2.0" step="0.05" id="label-size"></div>
            </div>
            <div style="display:flex;gap:1.5rem;margin-top:0.75rem;">
              <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;color:var(--text-04);"><input type="checkbox" checked id="show-labels"> ${t('settings.show_labels')}</label>
              <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;color:var(--text-04);"><input type="checkbox" checked id="show-conf"> ${t('settings.show_conf')}</label>
            </div>
          </div>
          <div style="display:flex;gap:0.5rem;">
            <button class="btn btn-primary" onclick="Tabs.settings.save()">${t('save')}</button>
            <button class="btn btn-secondary" onclick="Tabs.settings.loadConfig()">${t('reset')}</button>
          </div>
        </div>
        <div style="flex:1;max-width:480px;">
          <div class="card" style="padding:1.5rem;">
            <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('settings.class_table')}</h3>
            <div id="class-table-container" class="text-secondary" style="font-size:12px;">Load a model to see class settings</div>
          </div>
        </div>
      </div>`;
  },
  async init() {
    const s = document.getElementById('conf-slider'), l = document.getElementById('conf-value');
    if (s) s.oninput = () => { l.textContent = (s.value / 100).toFixed(2); };
    this.loadConfig();
  },
  async loadConfig() {
    try {
      const c = await API.config();
      if (c.error) return;
      document.getElementById('model-type').value = c.model_type || 'yolo';
      document.getElementById('batch-size').value = c.batch_size || 1;
      const s = document.getElementById('conf-slider');
      s.value = Math.round((c.conf_threshold || 0.25) * 100);
      document.getElementById('conf-value').textContent = (c.conf_threshold || 0.25).toFixed(2);
      document.getElementById('box-thickness').value = c.box_thickness || 2;
      document.getElementById('label-size').value = c.label_size || 0.55;
      document.getElementById('show-labels').checked = c.show_labels !== false;
      document.getElementById('show-conf').checked = c.show_confidence !== false;
    } catch(e) {}
    // Load class table if model is loaded
    try {
      const mi = await API.modelInfo();
      if (mi.loaded && mi.info && mi.info.names) this._buildClassTable(mi.info.names);
    } catch(e) {}
  },
  _buildClassTable(names) {
    const container = document.getElementById('class-table-container');
    if (!names || !Object.keys(names).length) { container.textContent = 'No classes'; return; }
    let rows = '';
    for (const [id, name] of Object.entries(names)) {
      rows += `<tr>
        <td style="padding:4px 6px;">${id}: ${name}</td>
        <td style="padding:4px 6px;text-align:center;"><input type="checkbox" checked data-cls="${id}" class="cls-enabled"></td>
        <td style="padding:4px 6px;text-align:center;"><input type="color" value="#00ff00" data-cls="${id}" class="cls-color" style="width:32px;height:22px;border:none;cursor:pointer;"></td>
        <td style="padding:4px 6px;"><input type="number" value="0" min="0" max="10" data-cls="${id}" class="cls-thick" style="width:50px;font-size:11px;" title="0=default"></td>
      </tr>`;
    }
    container.innerHTML = `<div style="max-height:400px;overflow-y:auto;">
      <table style="width:100%;font-size:12px;"><thead><tr>
        <th style="text-align:left;padding:4px 6px;">Class</th>
        <th style="padding:4px 6px;">${t('settings.enabled')}</th>
        <th style="padding:4px 6px;">${t('settings.color')}</th>
        <th style="padding:4px 6px;">${t('settings.thickness')}</th>
      </tr></thead><tbody>${rows}</tbody></table></div>`;
  },
  async save() {
    try {
      await API.post('/api/config', {
        model_type: document.getElementById('model-type').value,
        batch_size: +document.getElementById('batch-size').value,
        conf_threshold: +document.getElementById('conf-slider').value / 100,
        box_thickness: +document.getElementById('box-thickness').value,
        label_size: +document.getElementById('label-size').value,
        show_labels: document.getElementById('show-labels').checked,
        show_confidence: document.getElementById('show-conf').checked,
      });
      App.setStatus(t('settings.saved'));
    } catch(e) { App.setStatus(`Error: ${e.message}`); }
  }
};

/* ── Benchmark ──────────────────────────────────────── */
Tabs.benchmark = {
  title: true,
  render() {
    return `
      <div style="display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          ${multiModelSlots('bench-slots','bench-list')}
        </div>
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('bench.config')}</h3>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;">
            <div class="form-group"><label class="form-label">${t('bench.iters')}</label><input type="number" class="form-input input-normal" value="500" min="10" max="5000" step="100" id="bench-iters"></div>
            <div class="form-group"><label class="form-label">${t('bench.input_size')}</label><select class="form-input input-normal" id="bench-size"><option>640</option><option>320</option><option>1280</option></select></div>
            <div class="form-group"><label class="form-label">${t('bench.warmup')}</label><span class="form-input" style="background:var(--background-neutral-02);color:var(--text-03);">${t('bench.fixed')}</span></div>
          </div>
          <div style="display:flex;gap:0.5rem;margin-top:1rem;">
            <button class="btn btn-primary" id="bench-run" onclick="Tabs.benchmark.run()">${t('bench.run')}</button>
            <button class="btn btn-danger btn-sm" id="bench-stop" disabled onclick="Tabs.benchmark.stop()">${t('stop')}</button>
          </div>
          <div style="margin-top:0.75rem;">
            <div class="progress-track"><div class="progress-fill" id="bench-progress" style="width:0%"></div></div>
            <span class="text-secondary" id="bench-status" style="margin-top:0.25rem;display:block;">${t('ready')}</span>
          </div>
        </div>
        <div class="card" style="padding:1.5rem;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
            <h3 class="text-heading-h3">${t('bench.results')}</h3>
            <div style="display:flex;gap:0.5rem;">
              <button class="btn btn-secondary btn-sm" onclick="Tabs.benchmark.exportResults()">${t('export')}</button>
              <button class="btn btn-ghost btn-sm" onclick="document.getElementById('bench-results').innerHTML='<tr><td colspan=7 class=text-secondary style=text-align:center;padding:2rem>${t('bench.run_hint')}</td></tr>'">${t('reset')}</button>
            </div>
          </div>
          <div class="table-container"><table><thead><tr><th>Model</th><th>Provider</th><th>FPS</th><th>Avg(ms)</th><th>P50</th><th>P95</th><th>P99</th></tr></thead>
          <tbody id="bench-results"><tr><td colspan="7" class="text-secondary" style="text-align:center;padding:2rem;">${t('bench.run_hint')}</td></tr></tbody></table></div>
        </div>
      </div>`;
  },
  async run() {
    const models = getSlotModels('bench-slots');
    if (!models.length) { App.setStatus(t('bench.no_models')); return; }
    document.getElementById('bench-run').disabled = true;
    document.getElementById('bench-stop').disabled = false;
    document.getElementById('bench-status').textContent = t('bench.running');
    document.getElementById('bench-progress').style.width = '0%';
    App.setStatus(t('bench.running'));
    try {
      const r = await API.post('/api/benchmark/run', {
        models, iterations: +document.getElementById('bench-iters').value,
        input_size: +document.getElementById('bench-size').value
      });
      if (r.error) { App.setStatus('Error: ' + r.error); return; }
      // Poll for results
      this._polling = true;
      this._poll();
    } catch(e) { App.setStatus(`Error: ${e.message}`); document.getElementById('bench-run').disabled = false; }
  },
  _polling: false,
  async _poll() {
    if (!this._polling) return;
    try {
      const s = await API.get('/api/benchmark/status');
      const pct = s.total > 0 ? Math.round(s.progress / s.total * 100) : 0;
      document.getElementById('bench-progress').style.width = pct + '%';
      document.getElementById('bench-status').textContent = s.msg || '';
      if (s.results && s.results.length) {
        const tb = document.getElementById('bench-results');
        tb.innerHTML = s.results.map((x, i) => {
          if (x.error) return `<tr><td colspan="7" style="color:var(--action-danger-05);">${x.error}</td></tr>`;
          const hl = i === 0 ? ' style="background:var(--status-success-01);font-weight:600;"' : '';
          return `<tr${hl}><td>${x.name||'—'}</td><td>${x.provider||'—'}</td><td>${x.fps||'—'}</td><td>${x.avg||'—'}</td><td>${x.p50||'—'}</td><td>${x.p95||'—'}</td><td>${x.p99||'—'}</td></tr>`;
        }).join('');
      }
      if (s.running) {
        setTimeout(() => this._poll(), 500);
      } else {
        this._polling = false;
        document.getElementById('bench-run').disabled = false;
        document.getElementById('bench-stop').disabled = true;
        document.getElementById('bench-progress').style.width = '100%';
        App.setStatus(t('bench.complete'));
      }
    } catch(e) { setTimeout(() => this._poll(), 1000); }
  },
  stop() {
    this._polling = false;
    App.setStatus('Stopped');
    document.getElementById('bench-run').disabled = false;
    document.getElementById('bench-stop').disabled = true;
  },
  exportResults() { App.setStatus('Export not yet implemented'); },
};

/* ── Evaluation ─────────────────────────────────────── */
Tabs.evaluation = {
  title: true,
  render() {
    return `
      <div style="display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('eval.setup')}</h3>
          ${multiModelSlots('eval-slots','eval-list')}
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
            ${imgDirInput('eval-img')}
            ${lblDirInput('eval-lbl')}
          </div>
          <div style="display:flex;gap:0.5rem;margin-top:1rem;">
            <button class="btn btn-primary" onclick="Tabs.evaluation.run()">${t('eval.run')}</button>
            <button class="btn btn-danger btn-sm" disabled>${t('stop')}</button>
          </div>
          <div style="margin-top:0.5rem;"><div class="progress-track"><div class="progress-fill" id="eval-prog" style="width:0%"></div></div></div>
        </div>
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('eval.results')}</h3>
          <div class="table-container"><table><thead><tr><th>Model</th><th>mAP@50</th><th>mAP@50:95</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead>
          <tbody id="eval-results"><tr><td colspan="6" class="text-secondary" style="text-align:center;padding:2rem;">${t('eval.run_hint')}</td></tr></tbody></table></div>
        </div>
      </div>`;
  },
  async run() {
    const models = getSlotModels('eval-slots');
    const imgDir = document.getElementById('eval-img').value || G.imgDir;
    const lblDir = document.getElementById('eval-lbl').value || G.lblDir;
    if (!models.length) { App.setStatus('Add at least one model'); return; }
    if (!imgDir) { App.setStatus('Select images directory'); return; }
    App.setStatus('Running evaluation...');
    try {
      const r = await API.post('/api/evaluation/run', { models, img_dir: imgDir, label_dir: lblDir });
      const tb = document.getElementById('eval-results');
      if (Array.isArray(r) && r.length) {
        tb.innerHTML = r.map(x => `<tr><td>${x.name||'—'}</td><td>${(x.map50*100)?.toFixed(1)||'—'}%</td><td>${(x.map5095*100)?.toFixed(1)||'—'}%</td><td>${(x.precision*100)?.toFixed(1)||'—'}%</td><td>${(x.recall*100)?.toFixed(1)||'—'}%</td><td>${(x.f1*100)?.toFixed(1)||'—'}%</td></tr>`).join('');
      }
      App.setStatus('Evaluation complete');
    } catch(e) { App.setStatus(`Error: ${e.message}`); }
  }
};

/* ── Analysis ───────────────────────────────────────── */
Tabs.analysis = {
  title: true,
  render() {
    return `
      <div style="display:flex;gap:1rem;height:100%;">
        <div style="flex:1;display:flex;flex-direction:column;gap:1rem;">
          <div class="card" style="padding:1rem;">
            ${modelInput('ana-model')}
            ${imgDirInput('ana-img')}
          </div>
          <div class="card" style="flex:1;padding:1.5rem;display:flex;align-items:center;justify-content:center;min-height:300px;">
            <span class="text-muted">${t('viewer.open_hint')}</span>
          </div>
        </div>
        <div style="width:260px;display:flex;flex-direction:column;gap:0.75rem;">
          <div class="card-flat" style="padding:1rem;"><div class="text-label" style="margin-bottom:0.5rem;">Insights</div><div class="text-secondary">—</div></div>
        </div>
      </div>`;
  }
};

/* ── Explorer ───────────────────────────────────────── */
Tabs.explorer = {
  title: true,
  render() {
    return `
      <div style="display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <div style="display:grid;grid-template-columns:1fr 1fr auto;gap:1rem;align-items:end;">
            ${imgDirInput('exp-img')}
            ${lblDirInput('exp-lbl')}
            <button class="btn btn-primary" style="height:36px;" onclick="Tabs.explorer.load()">${t('explorer.load')}</button>
          </div>
        </div>
        <div style="display:flex;gap:1rem;">
          <div style="width:200px;">
            <div class="card-flat" style="padding:1rem;">
              <div class="text-label" style="margin-bottom:0.5rem;">${t('explorer.filter')}</div>
              <div class="form-group" style="margin-bottom:0.5rem;">
                <label class="form-label">Class</label>
                <select class="form-input input-normal" id="exp-class-filter"><option value="">All</option></select>
              </div>
              <div class="form-group">
                <label class="form-label">Min boxes</label>
                <input type="number" class="form-input input-normal" value="0" min="0" id="exp-min-boxes">
              </div>
            </div>
            <div class="card-flat" style="padding:1rem;margin-top:0.75rem;">
              <div class="text-label" style="margin-bottom:0.5rem;">${t('explorer.stats')}</div>
              <div id="exp-stats" class="text-secondary">—</div>
            </div>
          </div>
          <div style="flex:1;">
            <div id="exp-gallery" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:0.5rem;">
              <div class="text-secondary" style="grid-column:1/-1;text-align:center;padding:3rem;">${t('explorer.load_hint')}</div>
            </div>
          </div>
        </div>
      </div>`;
  },
  async load() { App.setStatus('Loading dataset...'); }
};

/* ── Splitter ───────────────────────────────────────── */
Tabs.splitter = {
  title: true,
  render() {
    return `
      <div style="max-width:640px;display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('splitter.input')}</h3>
          ${imgDirInput('split-img')}
          ${lblDirInput('split-lbl')}
          ${outDirInput('split-out')}
        </div>
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">${t('splitter.ratio')}</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
            <div class="form-group"><label class="form-label">${t('splitter.train')}</label><input type="number" class="form-input input-normal" value="0.7" min="0" max="1" step="0.05"></div>
            <div class="form-group"><label class="form-label">${t('splitter.val')}</label><input type="number" class="form-input input-normal" value="0.2" min="0" max="1" step="0.05"></div>
            <div class="form-group"><label class="form-label">${t('splitter.test')}</label><input type="number" class="form-input input-normal" value="0.1" min="0" max="1" step="0.05"></div>
          </div>
          <label style="display:flex;align-items:center;gap:0.5rem;margin-top:0.75rem;cursor:pointer;color:var(--text-04);"><input type="checkbox" checked> ${t('splitter.stratified')}</label>
        </div>
        <button class="btn btn-primary" onclick="App.setStatus('Splitting...')">${t('splitter.run')}</button>
      </div>`;
  }
};

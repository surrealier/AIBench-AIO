/* tabs-extra.js — Remaining tab renderers using shared helpers */

/* ── Generic functional tab builder ─────────────────── */
function makeTab(opts) {
  return {
    title: true,
    render() {
      let html = '<div style="display:flex;flex-direction:column;gap:1.5rem;">';
      html += `<div class="card" style="padding:1.5rem;">
        <h3 class="text-heading-h3" style="margin-bottom:1rem;">${opts.heading}</h3>`;
      if (opts.needsModel) html += modelInput(opts.id+'-model');
      if (opts.needsImgDir) html += imgDirInput(opts.id+'-img');
      if (opts.needsLblDir) html += lblDirInput(opts.id+'-lbl');
      if (opts.needsOutDir) html += outDirInput(opts.id+'-out');
      if (opts.multiModel) html += multiModelSlots(opts.id+'-slots', opts.id+'-list');
      if (opts.extraHtml) html += opts.extraHtml;
      if (opts.fields) {
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-top:0.75rem;">';
        opts.fields.forEach(([label, type, id, val, extra]) => {
          html += `<div class="form-group"><label class="form-label">${label}</label>`;
          if (type === 'select') html += `<select class="form-input input-normal" id="${id}">${val}</select>`;
          else if (type === 'number') html += `<input type="number" class="form-input input-normal" id="${id}" value="${val}" ${extra||''}>`;
          else html += `<input type="text" class="form-input input-normal" id="${id}" value="${val||''}" ${extra||''}>`;
          html += '</div>';
        });
        html += '</div>';
      }
      if (opts.checks) {
        html += '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:0.75rem;">';
        opts.checks.forEach(([label, checked]) => {
          html += `<label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;color:var(--text-04);"><input type="checkbox" ${checked?'checked':''}> ${label}</label>`;
        });
        html += '</div>';
      }
      const action = opts.action || t('run');
      const onclick = opts.onclick ? ` onclick="${opts.onclick}"` : ` onclick="App.setStatus('Running...')"`;
      html += `<button class="btn btn-primary" style="margin-top:1rem;"${onclick}>${action}</button></div>`;
      if (opts.progress) {
        html += `<div><div class="progress-track"><div class="progress-fill" id="${opts.id}-prog" style="width:0%"></div></div>
          <span class="text-secondary" style="margin-top:0.25rem;display:block;">${t('ready')}</span></div>`;
      }
      if (opts.resultCols) {
        html += `<div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">${opts.resultTitle || t('bench.results')}</h3>
          <div class="table-container"><table><thead><tr>${opts.resultCols.map(c=>`<th>${c}</th>`).join('')}</tr></thead>
          <tbody id="${opts.id}-results"><tr><td colspan="${opts.resultCols.length}" class="text-secondary" style="text-align:center;padding:2rem;">${opts.resultHint||'—'}</td></tr></tbody></table></div>
        </div>`;
      }
      html += '</div>';
      return html;
    }
  };
}

/* ── Model Compare ──────────────────────────────────── */
Tabs['model-compare'] = {
  title: true,
  render() {
    return `
      <div style="display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">Setup</h3>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
            <div class="form-group">
              <label class="form-label">Model A</label>
              <div style="display:flex;gap:0.5rem;">
                <input type="text" class="form-input input-normal" style="flex:1;" readonly id="cmp-a" value="${G.model}">
                <button class="btn btn-secondary btn-sm" onclick="pickModel('cmp-a')">${t('browse')}</button>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Model B</label>
              <div style="display:flex;gap:0.5rem;">
                <input type="text" class="form-input input-normal" style="flex:1;" readonly id="cmp-b">
                <button class="btn btn-secondary btn-sm" onclick="pickModel('cmp-b')">${t('browse')}</button>
              </div>
            </div>
          </div>
          ${imgDirInput('cmp-img')}
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="App.setStatus('Comparing...')">${t('run')}</button>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
          <div class="card" style="padding:1rem;min-height:300px;display:flex;align-items:center;justify-content:center;"><span class="text-muted">Model A</span></div>
          <div class="card" style="padding:1rem;min-height:300px;display:flex;align-items:center;justify-content:center;"><span class="text-muted">Model B</span></div>
        </div>
      </div>`;
  }
};

/* ── Error Analyzer ─────────────────────────────────── */
Tabs['error-analyzer'] = makeTab({
  id: 'ea', heading: 'FP/FN Analysis',
  needsModel: true, needsImgDir: true, needsLblDir: true,
  fields: [['IoU Threshold','number','ea-iou','0.5','min="0.1" max="0.9" step="0.05"']],
  resultCols: ['Type','Count','Small','Medium','Large','Top','Center','Bottom'],
  resultHint: 'Run analysis to see FP/FN breakdown', progress: true,
});

/* ── Conf Optimizer ─────────────────────────────────── */
Tabs['conf-optimizer'] = makeTab({
  id: 'co', heading: 'Confidence Threshold Optimizer',
  needsModel: true, needsImgDir: true, needsLblDir: true,
  fields: [['Step','number','co-step','0.05','min="0.01" max="0.1" step="0.01"']],
  resultCols: ['Class','Best Threshold','F1','Precision','Recall'],
  resultHint: 'Run optimizer to find best thresholds', progress: true,
});

/* ── Embedding Viewer ───────────────────────────────── */
Tabs['embedding-viewer'] = {
  title: true,
  render() {
    return `
      <div style="display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">Embedding Visualization</h3>
          ${modelInput('ev-model')}
          ${imgDirInput('ev-img')}
          <div class="form-group" style="margin-top:0.75rem;">
            <label class="form-label">Method</label>
            <select class="form-input input-normal" style="width:auto;"><option>t-SNE</option><option>UMAP</option><option>PCA</option></select>
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="App.setStatus('Computing embeddings...')">${t('run')}</button>
        </div>
        <div class="card" style="padding:1.5rem;min-height:400px;display:flex;align-items:center;justify-content:center;">
          <span class="text-muted">2D scatter plot will appear here</span>
        </div>
      </div>`;
  }
};

/* ── Segmentation ───────────────────────────────────── */
Tabs.segmentation = makeTab({
  id: 'seg', heading: 'Segmentation Evaluation',
  needsModel: true, needsImgDir: true, needsLblDir: true,
  resultCols: ['Class','IoU','Dice','Images'],
  resultHint: 'Run evaluation to see mIoU/Dice', progress: true,
});

/* ── CLIP ───────────────────────────────────────────── */
Tabs.clip = {
  title: true,
  render() {
    return `
      <div style="max-width:640px;display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">CLIP Zero-Shot</h3>
          <div class="form-group">
            <label class="form-label">Image Encoder</label>
            <div style="display:flex;gap:0.5rem;">
              <input type="text" class="form-input input-normal" style="flex:1;" readonly id="clip-img-enc">
              <button class="btn btn-secondary btn-sm" onclick="pickFile('clip-img-enc','ONNX (*.onnx)')">${t('browse')}</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Text Encoder</label>
            <div style="display:flex;gap:0.5rem;">
              <input type="text" class="form-input input-normal" style="flex:1;" readonly id="clip-txt-enc">
              <button class="btn btn-secondary btn-sm" onclick="pickFile('clip-txt-enc','ONNX (*.onnx)')">${t('browse')}</button>
            </div>
          </div>
          ${imgDirInput('clip-img')}
          <div class="form-group" style="margin-top:0.75rem;">
            <label class="form-label">Class Labels (comma-separated)</label>
            <input type="text" class="form-input input-normal" placeholder="cat, dog, bird, car..." id="clip-labels">
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="App.setStatus('Running CLIP...')">${t('run')}</button>
        </div>
      </div>`;
  }
};

/* ── Embedder Eval ──────────────────────────────────── */
Tabs.embedder = makeTab({
  id: 'emb', heading: 'Embedder Evaluation',
  needsModel: true, needsImgDir: true,
  fields: [['Top-K','number','emb-k','5','min="1" max="100"']],
  resultCols: ['Class','Retrieval@1','Retrieval@K','Avg Cosine'],
  progress: true,
});

/* ── Converter ──────────────────────────────────────── */
Tabs.converter = {
  title: true,
  render() {
    return `
      <div style="max-width:640px;display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">Format Converter</h3>
          ${lblDirInput('conv-in')}
          ${outDirInput('conv-out')}
          <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:0.5rem;align-items:center;margin-top:1rem;">
            <select class="form-input input-normal"><option>YOLO</option><option>COCO JSON</option><option>Pascal VOC</option></select>
            <span style="font-size:20px;color:var(--text-02);">→</span>
            <select class="form-input input-normal"><option>COCO JSON</option><option>YOLO</option><option>Pascal VOC</option></select>
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="App.setStatus('Converting...')">${t('run')}</button>
          <div style="margin-top:0.5rem;"><div class="progress-track"><div class="progress-fill" style="width:0%"></div></div></div>
        </div>
      </div>`;
  }
};

/* ── Remapper ───────────────────────────────────────── */
Tabs.remapper = makeTab({
  id: 'remap', heading: 'Class Remapper',
  needsLblDir: true, needsOutDir: true,
  checks: [['Auto-reindex', true]],
  resultCols: ['Original ID','Original Name','→','New ID','New Name'],
  resultHint: 'Load labels to see class mapping', action: 'Apply Remap',
});

/* ── Merger ──────────────────────────────────────────── */
Tabs.merger = {
  title: true, _n: 1,
  render() {
    return `
      <div style="max-width:640px;display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">Dataset Merger</h3>
          <div id="merger-datasets" style="display:flex;flex-direction:column;gap:0.5rem;">
            ${imgDirInput('merge-d1')}
          </div>
          <button class="btn btn-secondary btn-sm" style="margin-top:0.5rem;" onclick="Tabs.merger.addDataset()">+ Add Dataset</button>
          ${outDirInput('merge-out')}
          <div class="form-group" style="margin-top:0.75rem;">
            <label class="form-label">dHash Threshold</label>
            <input type="number" class="form-input input-normal" value="10" min="0" max="64">
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="App.setStatus('Merging...')">Merge</button>
        </div>
      </div>`;
  },
  addDataset() {
    this._n++;
    const c = document.getElementById('merger-datasets');
    const d = document.createElement('div');
    d.innerHTML = imgDirInput(`merge-d${this._n}`);
    c.appendChild(d.firstElementChild || d);
  }
};

/* ── Smart Sampler ──────────────────────────────────── */
Tabs.sampler = makeTab({
  id: 'samp', heading: 'Smart Sampler',
  needsImgDir: true, needsLblDir: true, needsOutDir: true,
  fields: [
    ['Strategy','select','samp-strat','<option>Random</option><option>Balanced</option><option>Stratified</option>'],
    ['Target Count','number','samp-n','500','min="1"'],
    ['Seed','number','samp-seed','42','min="0"'],
  ],
  checks: [['Include labels', true]], progress: true,
});

/* ── Label Anomaly ──────────────────────────────────── */
Tabs.anomaly = makeTab({
  id: 'anom', heading: 'Label Anomaly Detector',
  needsImgDir: true, needsLblDir: true,
  checks: [['Out-of-bounds', true],['Size outliers', true],['High overlap', true]],
  resultCols: ['File','Type','Details','Severity'],
  resultHint: 'Run detector to find anomalies', progress: true,
});

/* ── Image Quality ──────────────────────────────────── */
Tabs.quality = makeTab({
  id: 'qual', heading: 'Image Quality Checker',
  needsImgDir: true,
  checks: [['Blur', true],['Brightness', true],['Overexposure', true],['Entropy', true],['Aspect ratio', true]],
  resultCols: ['File','Blur','Brightness','Entropy','Aspect','Issues'],
  progress: true,
});

/* ── Near Duplicates ────────────────────────────────── */
Tabs.duplicate = makeTab({
  id: 'dup', heading: 'Near-Duplicate Detector',
  needsImgDir: true,
  fields: [['Hamming Threshold','number','dup-thr','10','min="0" max="64"']],
  resultCols: ['Group','Image A','Image B','Distance'],
  progress: true,
});

/* ── Leaky Split ────────────────────────────────────── */
Tabs.leaky = {
  title: true,
  render() {
    const dirInput = (id, label) => `<div class="form-group">
      <label class="form-label">${label}</label>
      <div style="display:flex;gap:0.5rem;">
        <input type="text" class="form-input input-normal" style="flex:1;" readonly id="${id}">
        <button class="btn btn-secondary btn-sm" onclick="pickDir('${id}')">${t('browse')}</button>
      </div></div>`;
    return `
      <div style="max-width:640px;display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">Leaky Split Detector</h3>
          ${dirInput('leak-train', t('splitter.train'))}
          ${dirInput('leak-val', t('splitter.val'))}
          ${dirInput('leak-test', t('splitter.test'))}
          <div class="form-group" style="margin-top:0.75rem;">
            <label class="form-label">Hamming Threshold</label>
            <input type="number" class="form-input input-normal" value="10" min="0" max="64">
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="App.setStatus('Detecting leaks...')">${t('run')}</button>
          <div style="margin-top:0.5rem;"><div class="progress-track"><div class="progress-fill" style="width:0%"></div></div></div>
        </div>
        <div class="card" style="padding:1.5rem;">
          <div class="table-container"><table><thead><tr><th>Split Pair</th><th>Duplicates</th><th>Files</th></tr></thead>
          <tbody><tr><td colspan="3" class="text-secondary" style="text-align:center;padding:2rem;">Run detector to find cross-split duplicates</td></tr></tbody></table></div>
        </div>
      </div>`;
  }
};

/* ── Similarity Search ──────────────────────────────── */
Tabs.similarity = makeTab({
  id: 'sim', heading: 'Similarity Search',
  needsImgDir: true,
  fields: [['Top-K','number','sim-k','10','min="1" max="100"']],
  action: 'Build Index', resultCols: ['Rank','Image','Cosine Similarity'],
  progress: true,
});

/* ── Batch Inference ────────────────────────────────── */
Tabs.batch = makeTab({
  id: 'bat', heading: 'Batch Inference',
  needsModel: true, needsImgDir: true, needsOutDir: true,
  fields: [['Output Format','select','bat-fmt','<option>YOLO txt</option><option>JSON</option><option>CSV</option>']],
  checks: [['Save visualizations', false]],
  progress: true, action: 'Run Batch',
});

/* ── Augmentation ───────────────────────────────────── */
Tabs.augmentation = {
  title: true,
  render() {
    return `
      <div style="display:flex;flex-direction:column;gap:1.5rem;">
        <div class="card" style="padding:1.5rem;">
          <h3 class="text-heading-h3" style="margin-bottom:1rem;">Augmentation Preview</h3>
          ${imgDirInput('aug-img')}
          ${lblDirInput('aug-lbl')}
          <div class="form-group" style="margin-top:0.75rem;">
            <label class="form-label">Augmentation Type</label>
            <select class="form-input input-normal">
              <option>Mosaic 2×2</option><option>Flip</option><option>Rotate</option>
              <option>Brightness</option><option>Albumentations</option>
            </select>
          </div>
          <button class="btn btn-primary" style="margin-top:1rem;" onclick="App.setStatus('Previewing...')">Preview</button>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
          <div class="card" style="padding:1rem;min-height:250px;display:flex;align-items:center;justify-content:center;"><span class="text-muted">Original</span></div>
          <div class="card" style="padding:1rem;min-height:250px;display:flex;align-items:center;justify-content:center;"><span class="text-muted">Augmented</span></div>
        </div>
      </div>`;
  }
};

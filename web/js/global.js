/* Global state & shared UI helpers */
const G = {
  model: '',      // current model path
  imgDir: '',     // current images/video directory
  lblDir: '',     // current labels directory (auto-set from imgDir)
  models: [],     // list of loaded model paths (for multi-model tabs)
};

/* Auto-set lblDir when imgDir changes */
function setImgDir(dir) {
  G.imgDir = dir;
  if (!G.lblDir || G.lblDir === G.imgDir) G.lblDir = dir;
  // Update all visible imgDir inputs
  document.querySelectorAll('[data-bind="imgDir"]').forEach(el => el.value = dir);
  document.querySelectorAll('[data-bind="lblDir"]').forEach(el => { if (!el.dataset.manual) el.value = dir; });
}
function setLblDir(dir) {
  G.lblDir = dir;
  document.querySelectorAll('[data-bind="lblDir"]').forEach(el => { el.value = dir; el.dataset.manual = '1'; });
}
function setModel(path) {
  G.model = path;
  if (path && !G.models.includes(path)) G.models.push(path);
  document.querySelectorAll('[data-bind="model"]').forEach(el => el.value = path);
  App.setStatus(`Model: ${path.split(/[\\/]/).pop()}`);
}

/* Reusable UI components */
function modelInput(id) {
  return `<div class="form-group">
    <label class="form-label">${t('settings.model')}</label>
    <div style="display:flex;gap:0.5rem;">
      <input type="text" class="form-input input-normal" style="flex:1;" readonly id="${id}" data-bind="model" value="${G.model}">
      <button class="btn btn-secondary btn-sm" onclick="pickModel('${id}')">
        ${t('browse')}
      </button>
    </div>
  </div>`;
}
function imgDirInput(id) {
  return `<div class="form-group">
    <label class="form-label">${t('explorer.img_dir')}</label>
    <div style="display:flex;gap:0.5rem;">
      <input type="text" class="form-input input-normal" style="flex:1;" readonly id="${id}" data-bind="imgDir" value="${G.imgDir}">
      <button class="btn btn-secondary btn-sm" onclick="pickImgDir('${id}')">
        ${t('browse')}
      </button>
    </div>
  </div>`;
}
function lblDirInput(id) {
  return `<div class="form-group">
    <label class="form-label">${t('explorer.lbl_dir')}</label>
    <div style="display:flex;gap:0.5rem;">
      <input type="text" class="form-input input-normal" style="flex:1;" readonly id="${id}" data-bind="lblDir" value="${G.lblDir}">
      <button class="btn btn-secondary btn-sm" onclick="pickLblDir('${id}')">
        ${t('browse')}
      </button>
    </div>
  </div>`;
}
function outDirInput(id) {
  return `<div class="form-group">
    <label class="form-label">${t('splitter.output')}</label>
    <div style="display:flex;gap:0.5rem;">
      <input type="text" class="form-input input-normal" style="flex:1;" readonly id="${id}">
      <button class="btn btn-secondary btn-sm" onclick="pickDir('${id}')">
        ${t('browse')}
      </button>
    </div>
  </div>`;
}

/* Multi-model selector: file dialog allows multiple, auto-creates slots */
function multiModelSlots(containerId, listId) {
  return `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.75rem;">
    <h3 class="text-heading-h3">${t('bench.models')}</h3>
    <div style="display:flex;gap:0.5rem;">
      <button class="btn btn-secondary btn-sm" onclick="addModelSlot('${containerId}','${listId}')">${t('add_model')}</button>
    </div>
  </div>
  <div id="${containerId}" style="display:flex;flex-direction:column;gap:0.5rem;">
    <div class="text-secondary" style="padding:1rem;text-align:center;" id="${listId}-hint">${t('bench.add_hint')}</div>
  </div>`;
}

/* Picker functions */
async function pickModel(inputId) {
  try {
    const r = await API.selectFile({ filters: 'ONNX (*.onnx);;PyTorch (*.pt)' });
    if (r.path) { setModel(r.path); document.getElementById(inputId).value = r.path; }
  } catch(e) {}
}
async function pickImgDir(inputId) {
  try {
    const r = await API.selectDir();
    if (r.path) { setImgDir(r.path); document.getElementById(inputId).value = r.path; }
  } catch(e) {}
}
async function pickLblDir(inputId) {
  try {
    const r = await API.selectDir();
    if (r.path) { setLblDir(r.path); document.getElementById(inputId).value = r.path; }
  } catch(e) {}
}
async function pickDir(inputId) {
  try {
    const r = await API.selectDir();
    if (r.path) document.getElementById(inputId).value = r.path;
  } catch(e) {}
}
async function pickFile(inputId, filters) {
  try {
    const r = await API.selectFile({ filters: filters || '' });
    if (r.path) document.getElementById(inputId).value = r.path;
  } catch(e) {}
}

/* Add model slot to multi-model container */
let _slotN = 0;
async function addModelSlot(containerId, listId) {
  try {
    const r = await API.post('/api/fs/select-multi', { filters: 'ONNX (*.onnx)' });
    if (!r.paths || !r.paths.length) return;
    for (const path of r.paths) {
      _addOneSlot(containerId, listId, path);
    }
  } catch(e) {}
}
function _addOneSlot(containerId, listId, path) {
  const c = document.getElementById(containerId);
  const hint = document.getElementById(listId + '-hint');
  if (hint) hint.remove();
  const id = ++_slotN;
  const name = path.split(/[\\/]/).pop();
  const d = document.createElement('div');
  d.className = 'card-flat'; d.id = `ms-${id}`;
  d.style.cssText = 'padding:0.5rem 0.75rem;display:flex;align-items:center;gap:0.5rem;';
  d.innerHTML = `<span class="text-mono" style="flex:1;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${path}">${name}</span>
    <input type="hidden" class="model-slot-path" value="${path}">
    <button class="btn btn-ghost btn-sm" onclick="document.getElementById('ms-${id}').remove()" style="color:var(--action-danger-05);padding:0 0.25rem;">✕</button>`;
  c.appendChild(d);
  if (!G.models.includes(path)) G.models.push(path);
}

/* Collect all model paths from slots */
function getSlotModels(containerId) {
  return [...document.querySelectorAll(`#${containerId} .model-slot-path`)].map(e => e.value);
}

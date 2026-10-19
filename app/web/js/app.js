/* CYVEX - frontend controller */
(() => {
  "use strict";

  const t = (k, v) => window.I18N.t(k, v);

  /* ----------------------------- icons ------------------------------ */
  const I = {
    dashboard: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>',
    scan: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    quarantine: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4.5 6v5.5c0 4.2 3 7.8 7.5 9 4.5-1.2 7.5-4.8 7.5-9V6L12 3Z"/><rect x="9.5" y="10" width="5" height="5" rx="1"/></svg>',
    history: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    protection: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4.5 6v5.5c0 4.2 3 7.8 7.5 9 4.5-1.2 7.5-4.8 7.5-9V6L12 3Z"/><path d="m9 12 2 2 4-4"/></svg>',
    settings: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1.2l2-1.6-2-3.4-2.4 1a7 7 0 0 0-2-1.2L14 3h-4l-.4 2.6a7 7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.6A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.6 2 3.4 2.4-1c.6.5 1.3.9 2 1.2L10 21h4l.4-2.6c.7-.3 1.4-.7 2-1.2l2.4 1 2-3.4-2-1.6c.1-.4.1-.8.1-1.2Z"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-10"/></svg>',
    alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5 2.5 20h19L12 3.5Z"/><path d="M12 9.5v4.5M12 17.2v.1"/></svg>',
    shieldCheck: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4.5 6v5.5c0 4.2 3 7.8 7.5 9 4.5-1.2 7.5-4.8 7.5-9V6L12 3Z"/><path d="m8.8 12 2.4 2.4 4-4.6"/></svg>',
    shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4.5 6v5.5c0 4.2 3 7.8 7.5 9 4.5-1.2 7.5-4.8 7.5-9V6L12 3Z"/></svg>',
    trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M9 7V5h6v2M6 7l1 13h10l1-13"/></svg>',
    restore: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12a8 8 0 1 0 2.3-5.6L4 8"/><path d="M4 4v4h4"/></svg>',
    folder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"/></svg>',
    plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
    refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 1 0-2.3 5.6"/><path d="M20 4v4h-4"/></svg>',
    cloud: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 18a4.5 4.5 0 0 1 0-9 6 6 0 0 1 11.5 1.5A3.8 3.8 0 0 1 17.5 18h-11Z"/></svg>',
    usb: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m9 6 3-3 3 3"/><circle cx="12" cy="18" r="3"/><path d="M6 12h3M15 12h3"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 8v4l2.5 1.8"/></svg>',
    activity: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12h3l3-7 4 14 3-7h5"/></svg>',
    file: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/></svg>',
    drive: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8" cy="15" r="1.4"/><path d="M13 15h5"/></svg>',
    sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
    moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
    pause: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 5v14M15 5v14"/></svg>',
    play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>',
    stop: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>',
    bell: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>',
    menu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
    download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m7 11 5 5 5-5"/><path d="M5 21h14"/></svg>',
    external: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 5h5v5"/><path d="M19 5l-8 8"/><path d="M19 14v4a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h4"/></svg>',
    copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg>',
    spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/><circle cx="12" cy="12" r="3.2"/></svg>',
    lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/></svg>',
    db: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6v6c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V6"/><path d="M5 12v6c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6v-6"/></svg>',
    palette: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a9 9 0 1 0 0 18c1.2 0 2-.9 2-2 0-.5-.2-.9-.5-1.2-.3-.3-.5-.7-.5-1.1 0-.8.7-1.5 1.5-1.5H16a5 5 0 0 0 5-5c0-3.9-4-7.2-9-7.2Z"/><circle cx="7.5" cy="10.5" r="1"/><circle cx="12" cy="7.5" r="1"/><circle cx="16.5" cy="10.5" r="1"/></svg>'
  };

  /* ---------------------------- helpers ----------------------------- */
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function fmtBytes(n) {
    if (!n) return "0 B";
    const u = ["B", "KB", "MB", "GB", "TB"];
    let i = 0, v = n;
    while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
    return `${v.toFixed(v >= 10 || i === 0 ? 0 : 1)} ${u[i]}`;
  }
  function fmtDate(iso) {
    if (!iso) return "—";
    const d = new Date(iso);
    if (isNaN(d)) return iso;
    return d.toLocaleString(window.I18N.lang === "ar" ? "ar-EG" : "en-GB",
      { year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
  }
  function fmtDuration(sec) {
    if (sec == null) return "—";
    sec = Math.round(sec);
    if (sec < 60) return `${sec}s`;
    const m = Math.floor(sec / 60), s = sec % 60;
    return `${m}m ${s}s`;
  }
  const severityClass = (s) => ({ critical: "danger", high: "danger", medium: "warning", low: "low" }[s] || "info");

  const ACCENTS = ["navy", "royal", "azure", "ice"];
  function applyAppearance(s) {
    const root = document.documentElement;
    root.dataset.accent = ACCENTS.includes(s.accent) ? s.accent : "navy";
    root.dataset.contrast = s.high_contrast ? "high" : "normal";
    root.dataset.motion = s.reduce_motion ? "reduce" : "full";
  }
  function copyText(text) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(text); return true; }
    } catch (e) { /* ignore */ }
    try {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select(); document.execCommand("copy"); ta.remove();
      return true;
    } catch (e) { return false; }
  }
  function countUp(el, target) {
    if (!el) return;
    const reduce = document.documentElement.dataset.motion === "reduce";
    const end = Number(target) || 0;
    if (reduce || end === 0) { el.textContent = end; return; }
    const start = performance.now(), dur = 700;
    function tick(now) {
      const t = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(end * eased);
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function tableState(name) {
    if (!state.tables[name]) state.tables[name] = { q: "", sortKey: null, sortDir: -1, page: 1, pageSize: 8, selected: {} };
    return state.tables[name];
  }
  function sortRows(rows, key, dir) {
    if (!key) return rows;
    return rows.slice().sort((a, b) => {
      let x = a[key], y = b[key];
      if (typeof x === "number" && typeof y === "number") return (x - y) * dir;
      x = String(x == null ? "" : x); y = String(y == null ? "" : y);
      return x.localeCompare(y, undefined, { numeric: true }) * dir;
    });
  }
  function filterRows(rows, q, fields) {
    if (!q) return rows;
    const needle = q.toLowerCase();
    return rows.filter((r) => fields.some((f) => String(r[f] == null ? "" : r[f]).toLowerCase().includes(needle)));
  }
  function paged(rows, ts) {
    const total = rows.length;
    const pages = Math.max(1, Math.ceil(total / ts.pageSize));
    ts.page = Math.min(Math.max(1, ts.page), pages);
    const startIdx = (ts.page - 1) * ts.pageSize;
    return { slice: rows.slice(startIdx, startIdx + ts.pageSize), total, pages };
  }
  function sortArrow(ts, key) {
    if (ts.sortKey !== key) return '<span class="arw">⇅</span>';
    return `<span class="arw on">${ts.sortDir === 1 ? "▲" : "▼"}</span>`;
  }
  function tableToolbar(name, total, bulkHtml) {
    const ts = tableState(name);
    const selCount = Object.keys(ts.selected).length;
    const bulk = (selCount && bulkHtml) ? `<div class="bulkbar"><span>${esc(t("table.selected", { n: selCount }))}</span><span class="grow"></span>${bulkHtml}</div>` : "";
    return `<div class="table-toolbar">
        <div class="search-box">${I.search}<input class="input" type="text" data-tsearch="${name}" placeholder="${esc(t("table.search"))}" value="${esc(ts.q)}"></div>
        <span class="grow"></span>
        <span class="small muted">${esc(t("table.rows", { n: total }))}</span>
      </div>${bulk}`;
  }
  function tablePager(name, total, pages) {
    const ts = tableState(name);
    if (pages <= 1) return "";
    return `<div class="pager">
        <button class="btn sm" data-tpage="prev" data-tname="${name}" ${ts.page <= 1 ? "disabled" : ""}>${esc(t("table.prev"))}</button>
        <span>${esc(t("table.page", { n: ts.page, m: pages }))}</span>
        <button class="btn sm" data-tpage="next" data-tname="${name}" ${ts.page >= pages ? "disabled" : ""}>${esc(t("table.next"))}</button>
      </div>`;
  }

  /* ------------------------------ API ------------------------------- */
  function ready() {
    return new Promise((resolve) => {
      if (window.pywebview && window.pywebview.api) return resolve();
      window.addEventListener("pywebviewready", () => resolve(), { once: true });
    });
  }
  async function call(method, ...args) {
    await ready();
    return window.pywebview.api[method](...args);
  }

  /* ----------------------------- toasts ----------------------------- */
  function toast(type, title, sub) {
    const root = $("#toasts");
    const node = document.createElement("div");
    node.className = `toast ${type || ""}`;
    const icon = type === "danger" ? I.alert : type === "warning" ? I.alert : type === "success" ? I.check : I.shield;
    node.innerHTML = `<span class="ti">${icon}</span><div><div class="tt">${esc(title)}</div>${sub ? `<div class="ts">${esc(sub)}</div>` : ""}</div>`;
    root.appendChild(node);
    setTimeout(() => { node.style.opacity = "0"; node.style.transform = "translateY(-6px)"; }, 4200);
    setTimeout(() => node.remove(), 4700);
  }

  function confirmDialog(title, message) {
    return new Promise((resolve) => {
      const root = $("#modal-root");
      root.innerHTML = `<div class="modal-backdrop"><div class="modal"><h3>${esc(title)}</h3><p>${esc(message)}</p>
        <div class="modal-actions"><button class="btn" data-x>${t("common.cancel")}</button><button class="btn danger" data-ok>${t("common.confirm")}</button></div></div></div>`;
      const close = (val) => { root.innerHTML = ""; resolve(val); };
      $("[data-x]", root).onclick = () => close(false);
      $("[data-ok]", root).onclick = () => close(true);
    });
  }

  function infoDialog(title, htmlBody) {
    const root = $("#modal-root");
    root.innerHTML = `<div class="modal-backdrop"><div class="modal"><h3>${esc(title)}</h3><div class="selectable" style="max-height:55vh;overflow:auto">${htmlBody}</div>
      <div class="modal-actions" style="margin-top:16px"><button class="btn primary" data-x>${t("common.close")}</button></div></div></div>`;
    $("[data-x]", root).onclick = () => { root.innerHTML = ""; };
    root.querySelector(".modal-backdrop").onclick = (e) => { if (e.target.classList.contains("modal-backdrop")) root.innerHTML = ""; };
  }

  function closeModal() { const r = $("#modal-root"); if (r) r.innerHTML = ""; }
  function customModal(inner) {
    const root = $("#modal-root");
    root.innerHTML = `<div class="modal-backdrop"><div class="modal">${inner}</div></div>`;
    const backdrop = root.querySelector(".modal-backdrop");
    backdrop.onclick = (e) => { if (e.target === backdrop || e.target.closest("[data-x]")) closeModal(); };
    return root;
  }

  function showThreatDetail(d) {
    d = d || {};
    const hash = d.sha256 && /^[a-f0-9]{64}$/i.test(d.sha256) ? d.sha256 : "";
    const dir = String(d.path || "").replace(/[\\/][^\\/]*$/, "");
    const root = customModal(`
      <div class="threat-head">
        <div class="lead danger">${I.alert}</div>
        <div><h3>${esc(d.name || t("threat.title"))}</h3>
          <div class="row" style="gap:8px;margin-top:6px;flex-wrap:wrap">
            <span class="badge ${severityClass(d.severity)}">${esc(t("common." + d.severity) || d.severity || "—")}</span>
            <span class="badge info">${esc(t("engine." + d.engine) || d.engine || "—")}</span>
            ${d.action ? `<span class="badge">${esc(d.action)}</span>` : ""}
          </div>
        </div>
      </div>
      <div class="field" style="margin-top:16px"><label>${t("common.path")}</label><div class="mono selectable break">${esc(d.path || "—")}</div></div>
      ${hash ? `<div class="field"><label>${t("threat.sha")}</label><div class="mono selectable break">${esc(hash)}</div></div>` : ""}
      ${d.created ? `<div class="field"><label>${t("threat.detected")}</label><div>${esc(fmtDate(d.created))}</div></div>` : ""}
      <div class="modal-actions" style="margin-top:16px;justify-content:space-between;flex-wrap:wrap;gap:8px">
        ${dir ? `<button class="btn" data-open-loc="${esc(dir)}">${I.external}${t("threat.openLocation")}</button>` : "<span></span>"}
        <div class="row" style="gap:8px">
          ${hash ? `<button class="btn" data-copy-hash="${esc(hash)}">${I.copy}${t("threat.copyHash")}</button>
          <button class="btn" data-vt-hash="${esc(hash)}">${I.cloud}${t("threat.vt")}</button>` : ""}
          <button class="btn primary" data-x>${t("common.close")}</button>
        </div>
      </div>`);
    $$("[data-copy-hash]", root).forEach((b) => b.onclick = () => { copyText(b.dataset.copyHash); toast("success", t("threat.copied")); });
    $$("[data-open-loc]", root).forEach((b) => b.onclick = () => call("open_path", b.dataset.openLoc));
    $$("[data-vt-hash]", root).forEach((b) => b.onclick = () => vtLookup(b.dataset.vtHash));
  }

  async function vtLookup(hash) {
    if (!state.settings.virustotal_enabled || !state.settings.virustotal_api_key) { toast("warning", t("threat.vt"), t("threat.vtNeedKey")); return; }
    toast("info", t("threat.vt"), t("threat.vtChecking"));
    const res = await call("vt_check", hash);
    if (!res.ok) { toast("warning", t("threat.vt"), res.error || t("toast.failed")); return; }
    const engines = res.engines || {};
    const rows = Object.keys(engines).slice(0, 16).map((name) => `<div class="between" style="padding:6px 0;border-bottom:1px solid var(--border-soft)"><span>${esc(name)}</span><span class="badge danger">${esc(engines[name])}</span></div>`).join("");
    customModal(`<h3>${t("threat.vt")}</h3>
      <div class="row" style="gap:14px;margin:14px 0">
        <div class="stat danger"><div class="k">${t("set.vtPositive")}</div><div class="v">${res.positives}</div></div>
        <div class="stat"><div class="k">${t("set.vtTotal")}</div><div class="v">${res.total}</div></div>
      </div>
      <div class="mono small break">${esc(hash)}</div>
      <div style="margin-top:10px">${rows || `<div class="empty">${I.check}<div class="t">${t("threat.vtNone")}</div></div>`}</div>
      <div class="modal-actions" style="margin-top:16px"><button class="btn primary" data-x>${t("common.close")}</button></div>`);
  }

  /* ------------------------- notifications -------------------------- */
  const seenKey = "novu_notif_seen";
  function seenId() { return Number(localStorage.getItem(seenKey) || 0); }
  function notifUnread() { return (state.notifications || []).filter((n) => Number(n.id || 0) > seenId()).length; }
  function updateBell() {
    const dot = $("#bell-dot");
    if (!dot) return;
    const n = notifUnread();
    dot.textContent = n > 9 ? "9+" : String(n);
    dot.hidden = n === 0;
  }
  function renderNotifPanel() {
    const panel = $("#notif-panel");
    if (!panel) return;
    const items = state.notifications || [];
    const seen = seenId();
    const sevCls = (n) => (n.severity === "critical" || n.severity === "error") ? "danger" : n.severity === "warning" ? "warning" : n.severity === "success" ? "success" : "";
    const body = items.length ? items.slice(0, 40).map((n) => `<div class="notif-item ${Number(n.id || 0) > seen ? "unread" : ""}">
        <div class="nd ${sevCls(n)}">${(n.kind === "detection" || n.severity === "critical" || n.severity === "error") ? I.alert : I.bell}</div>
        <div style="min-width:0"><div class="nt">${esc(n.message)}</div><div class="ns">${esc(fmtDate(n.created))}</div></div>
      </div>`).join("") : `<div class="empty">${I.check}<div class="t">${t("notif.empty")}</div></div>`;
    panel.innerHTML = `<div class="notif-head"><span>${t("notif.title")}</span><button class="btn sm ghost" data-notif-clear>${t("notif.clear")}</button></div>${body}`;
    const clear = $("[data-notif-clear]", panel);
    if (clear) clear.onclick = () => {
      const top = items.length ? Number(items[0].id || 0) : seenId();
      localStorage.setItem(seenKey, String(top));
      updateBell(); renderNotifPanel();
    };
  }
  function toggleBell() {
    const panel = $("#notif-panel");
    if (!panel) return;
    const open = panel.hasAttribute("hidden");
    if (open) {
      panel.removeAttribute("hidden");
      panel.classList.add("open");
      renderNotifPanel();
      const top = (state.notifications[0] || {}).id;
      if (top) localStorage.setItem(seenKey, String(top));
      updateBell();
    } else {
      panel.setAttribute("hidden", "");
      panel.classList.remove("open");
    }
  }

  /* --------------------------- tables ------------------------------- */
  function bindTable(name, view) {
    const ts = tableState(name);
    const input = $(`[data-tsearch="${name}"]`, view);
    if (input) input.oninput = () => {
      ts.q = input.value; ts.page = 1;
      state._focus = name; state._caret = input.selectionStart;
      render();
    };
    $$(`[data-tsort="${name}"]`, view).forEach((th) => th.onclick = () => {
      const key = th.dataset.tkey;
      if (ts.sortKey === key) ts.sortDir = -ts.sortDir; else { ts.sortKey = key; ts.sortDir = 1; }
      render();
    });
    $$(`[data-tpage]`, view).forEach((b) => b.onclick = () => {
      if (b.disabled) return;
      ts.page += b.dataset.tpage === "next" ? 1 : -1; render();
    });
    const all = $(`[data-rowsel-all="${name}"]`, view);
    if (all) all.onchange = () => {
      $$(`[data-rowsel="${name}"]`, view).forEach((cb) => {
        if (all.checked) ts.selected[cb.dataset.rowid] = true; else delete ts.selected[cb.dataset.rowid];
      });
      render();
    };
    $$(`[data-rowsel="${name}"]`, view).forEach((cb) => cb.onchange = () => {
      if (cb.checked) ts.selected[cb.dataset.rowid] = true; else delete ts.selected[cb.dataset.rowid];
      render();
    });
  }
  async function quarantineBulk(action) {
    const ts = tableState("quarantine");
    const ids = Object.keys(ts.selected).map(Number);
    if (!ids.length) return;
    if (action === "delete" && !(await confirmDialog(t("table.deleteSelected"), t("quar.confirmDelete")))) return;
    for (const id of ids) await call("quarantine_action", id, action);
    ts.selected = {};
    await loadQuarantine(); await refreshAll(); render();
  }

  /* ------------------------------ state ----------------------------- */
  const state = {
    boot: null,
    view: "dashboard",
    dashboard: null,
    scan: { running: false, scan_type: null, percent: 0, files_scanned: 0, total_files: 0, threats_found: 0, current_path: "", phase: "idle", paused: false, status: "idle" },
    scanDetections: [],
    customTargets: [],
    scanFormType: "quick",
    settings: {},
    historyDetections: null,
    stats: null,
    notifications: [],
    notifRead: 0,
    tables: {},
    lastResult: null
  };

  const NAV = [
    { id: "dashboard", icon: "dashboard", label: "nav.dashboard" },
    { id: "scan", icon: "scan", label: "nav.scan" },
    { id: "quarantine", icon: "quarantine", label: "nav.quarantine" },
    { id: "history", icon: "history", label: "nav.history" },
    { id: "protection", icon: "protection", label: "nav.protection" },
    { id: "settings", icon: "settings", label: "nav.settings" }
  ];

  /* --------------------------- navigation --------------------------- */
  function renderNav() {
    const nav = $("#nav");
    nav.innerHTML = NAV.map((n) => `<button class="nav-item ${state.view === n.id ? "active" : ""}" data-nav="${n.id}">${I[n.icon]}<span>${esc(t(n.label))}</span></button>`).join("");
    $$("[data-nav]", nav).forEach((b) => b.onclick = () => setView(b.dataset.nav));
  }
  function setView(view) {
    state.view = view;
    renderNav();
    render();
  }

  /* ---------------------------- top bar ----------------------------- */
  function updateTopbar() {
    const d = state.dashboard;
    const pill = $("#status-pill");
    const risk = d ? d.risk : "safe";
    pill.className = `status-pill ${risk}`;
    pill.innerHTML = `<span class="dot ${risk === "safe" ? "on" : risk === "warning" ? "warn" : "off"}"></span>${esc(t(risk === "safe" ? "status.safe" : risk === "warning" ? "status.warning" : "status.danger"))}`;
    if (d) {
      const rt = d.protection.realtime;
      $("#foot-status").textContent = t(rt ? "status.protecting" : "status.offline");
      $("#status-dot").className = `dot ${rt ? "on" : "off"}`;
    }
  }

  /* --------------------------- view router -------------------------- */
  function render() {
    const titles = { dashboard: "dash.title", scan: "scan.title", quarantine: "quar.title", history: "hist.title", protection: "prot.title", settings: "set.title" };
    $("#view-title").textContent = t(titles[state.view]);
    const view = $("#view");
    let html = "";
    if (state.view === "dashboard") html = viewDashboard();
    else if (state.view === "scan") html = viewScan();
    else if (state.view === "quarantine") html = viewQuarantine();
    else if (state.view === "history") html = viewHistory();
    else if (state.view === "protection") html = viewProtection();
    else if (state.view === "settings") html = viewSettings();
    view.innerHTML = `<div class="view-inner fade-in">${html}</div>`;
    bindView();
    updateTopbar();
    if (state._focus) {
      const inp = $(`[data-tsearch="${state._focus}"]`);
      if (inp) { inp.focus(); try { const c = state._caret || inp.value.length; inp.setSelectionRange(c, c); } catch (e) { /* ignore */ } }
      state._focus = null;
    }
    if (state.view === "dashboard") {
      $$(".countup").forEach((el) => countUp(el, el.dataset.count));
      updateScanUI();
    }
  }

  /* ============================ DASHBOARD =========================== */
  function gauge(pct, risk, label, sub) {
    const C = 2 * Math.PI * 100;
    const off = C * (1 - Math.max(0, Math.min(100, pct)) / 100);
    return `<div class="gauge ${risk}" id="gauge">
      <svg width="230" height="230" viewBox="0 0 230 230">
        <defs>
          <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#60A5FA"/><stop offset="1" stop-color="#2563EB"/>
          </linearGradient>
        </defs>
        <circle class="ring-bg" cx="115" cy="115" r="100" fill="none" stroke-width="12"/>
        <circle class="ring-fg" id="gauge-ring" cx="115" cy="115" r="100" fill="none" stroke-width="12"
          stroke-dasharray="${C.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}"/>
      </svg>
      <div class="gauge-center">
        <span class="gauge-icon" id="gauge-icon" style="color:var(--${risk === "safe" ? "brand" : risk === "warning" ? "warning" : "danger"})">${risk === "safe" ? I.shieldCheck : I.alert}</span>
        <span class="gauge-status" id="gauge-status">${esc(label)}</span>
        <span class="gauge-meta" id="gauge-meta">${esc(sub)}</span>
      </div>
    </div>`;
  }

  function trendChart(tl) {
    if (!tl || !tl.length) return `<div class="empty">${I.activity}<div class="t">${t("dash.noData")}</div></div>`;
    const W = 520, H = 180, padL = 30, padR = 14, padT = 16, padB = 28;
    const n = tl.length;
    const maxV = Math.max(1, ...tl.map((d) => Math.max(d.detections, d.scans)));
    const stepX = (W - padL - padR) / Math.max(1, n - 1);
    const y = (v) => padT + (1 - v / maxV) * (H - padT - padB);
    const pts = (key) => tl.map((d, i) => [padL + i * stepX, y(d[key] || 0)]);
    const path = (p) => p.map((q, i) => (i ? "L" : "M") + q[0].toFixed(1) + " " + q[1].toFixed(1)).join(" ");
    const pd = pts("detections"), ps = pts("scans");
    const area = path(pd) + ` L ${(padL + (n - 1) * stepX).toFixed(1)} ${H - padB} L ${padL} ${H - padB} Z`;
    const grid = [0, 0.5, 1].map((f) => {
      const gy = padT + f * (H - padT - padB);
      return `<line class="trend-grid" x1="${padL}" y1="${gy.toFixed(1)}" x2="${W - padR}" y2="${gy.toFixed(1)}"/>`;
    }).join("");
    const labels = tl.map((d, i) =>
      `<text class="trend-x" x="${(padL + i * stepX).toFixed(1)}" y="${H - 8}" text-anchor="middle">${esc((d.day || "").slice(5))}</text>`).join("");
    const dots = pd.map((q) => `<circle cx="${q[0].toFixed(1)}" cy="${q[1].toFixed(1)}" r="3.2" fill="var(--brand-2)"/>`).join("");
    return `<svg class="trend-svg" viewBox="0 0 ${W} ${H}">
      ${grid}
      <path class="trend-area" d="${area}"/>
      <path class="trend-line" d="${path(pd)}"/>
      <path class="trend-line2" d="${path(ps)}"/>
      ${dots}${labels}
    </svg>`;
  }

  function donutChart(sev) {
    const order = [["critical", "#dc2626"], ["high", "#ef5563"], ["medium", "#f2a93b"], ["low", "#60a5fa"]];
    const total = order.reduce((a, [k]) => a + (sev[k] || 0), 0);
    const R = 58, C = 2 * Math.PI * R;
    let offset = 0;
    const segs = order.map(([k, color]) => {
      const v = sev[k] || 0, frac = total ? v / total : 0;
      const el = `<circle cx="70" cy="70" r="${R}" stroke="${color}" stroke-dasharray="${(frac * C).toFixed(2)} ${(C - frac * C).toFixed(2)}" stroke-dashoffset="${(-offset * C).toFixed(2)}" stroke-linecap="butt"/>`;
      offset += frac;
      return el;
    }).join("");
    const rows = order.map(([k, color]) => {
      const v = sev[k] || 0, pct = total ? Math.round(v / total * 100) : 0;
      return `<div class="sev-row"><span class="lg-dot" style="background:${color}"></span><span style="width:54px">${esc(t("common." + k))}</span><span class="bar"><span style="width:${pct}%;background:${color}"></span></span><span style="width:32px;text-align:end">${v}</span></div>`;
    }).join("");
    return `<div class="donut-wrap">
      <div class="donut-holder">
        <svg class="donut" width="140" height="140" viewBox="0 0 140 140">
          <circle class="track" cx="70" cy="70" r="${R}"/>${total ? segs : ""}
        </svg>
        <div class="donut-center"><div class="n">${total}</div><div class="l">${esc(t("dash.detsLegend"))}</div></div>
      </div>
      <div class="sev-list">${rows}</div>
    </div>`;
  }

  function viewDashboard() {
    const d = state.dashboard || {};
    const s = state.scan;
    const running = s.running;
    const risk = d.risk || "safe";
    const last = d.last_scan;
    const lastText = last ? fmtDate(last.finished || last.started) : t("dash.never");
    const pct = running ? (s.phase === "counting" ? 4 : s.percent) : (risk === "safe" ? 100 : risk === "warning" ? 100 : 100);
    const gaugeLabel = running ? t("dash.scanning") : t(risk === "safe" ? "status.safe" : risk === "warning" ? "status.warning" : "status.danger");
    const gaugeSub = running ? `${s.files_scanned}/${s.total_files || "…"}` : lastText;

    const mod = d.protection || {};
    const modules = [
      { key: "realtime_enabled", label: "prot.realtime", active: mod.realtime },
      { key: "usb_enabled", label: "prot.usb", active: mod.usb },
      { key: "ransomware_enabled", label: "prot.ransomware", active: mod.ransomware },
      { key: "scheduled_enabled", label: "prot.scheduler", active: mod.scheduler }
    ];

    const stats = [
      { cls: "danger", icon: I.alert, k: "dash.threats24", v: (d.totals || {}).threats_24h || 0 },
      { cls: "brand", icon: I.quarantine, k: "dash.quarantine", v: (d.quarantine || {}).count || 0 },
      { cls: "brand", icon: I.file, k: "dash.signatures", v: (d.signatures || {}).count || 0 },
      { cls: "brand", icon: I.activity, k: "dash.scans", v: (d.totals || {}).scans || 0 }
    ];

    const activity = (d.activity || []).map((a) => `<div class="list-item">
        <div class="lead ${a.severity === "critical" || a.severity === "error" ? "danger" : a.severity === "warning" ? "warning" : a.severity === "success" ? "success" : "brand"}">${a.kind === "detection" ? I.alert : I.activity}</div>
        <div class="body"><div class="t">${esc(a.message)}</div><div class="s">${fmtDate(a.created)}</div></div>
      </div>`).join("") || `<div class="empty">${I.check}<div class="t">${t("dash.noActivity")}</div></div>`;

    const drives = ((d.system || {}).drives || []).map((dr) => {
      const usedPct = dr.total ? Math.round(dr.used / dr.total * 100) : 0;
      return `<div class="list-item">
        <div class="lead brand">${I.drive}</div>
        <div class="body">
          <div class="between"><div class="t">${esc(dr.root)} <span class="dim small">${esc(dr.type)}</span></div>
          <div class="s">${fmtBytes(dr.free)} ${t("dash.free")} ${t("dash.of")} ${fmtBytes(dr.total)}</div></div>
          <div class="progress" style="margin-top:7px"><span style="width:${usedPct}%"></span></div>
        </div></div>`;
    }).join("") || `<div class="empty">${t("dash.noActivity")}</div>`;

    return `
      <div class="grid cols-2" style="grid-template-columns: 1.35fr 1fr;">
        <div class="card pad-lg">
          <div class="gauge-wrap">
            ${gauge(pct, risk, gaugeLabel, gaugeSub)}
            <div class="grow">
              <h2 style="font-size:20px;margin-bottom:6px">${esc(t(risk === "safe" ? "status.safe" : "status.warning"))}</h2>
              <div class="muted small" style="margin-bottom:16px">${esc(t("dash.lastScan"))}: ${esc(lastText)}</div>
              ${running
                ? `<div class="row wrap">
                     <button class="btn" data-scan="pause" ${s.paused ? "disabled" : ""}>${I.pause}${t("scan.pause")}</button>
                     <button class="btn" data-scan="resume" ${s.paused ? "" : "disabled"}>${I.play}${t("scan.resume")}</button>
                     <button class="btn danger" data-scan="stop">${I.stop}${t("scan.stop")}</button>
                     <button class="btn primary" data-nav-btn="scan">${t("scan.viewDetections")}</button>
                   </div>`
                : `<button class="btn primary lg" data-quick-scan>${I.search}${t("dash.scanNow")}</button>`}
            </div>
          </div>
        </div>
        <div class="grid cols-2" style="grid-auto-rows:1fr">
          ${stats.map((st) => `<div class="card stat ${st.cls}"><div class="k">${st.icon}${t(st.k)}</div><div class="v countup" data-count="${st.v}">${st.v}</div></div>`).join("")}
        </div>
      </div>

      <div class="charts">
        <div class="card chart-card">
          <div class="card-title">${I.activity}${t("dash.trend")}</div>
          <div style="margin-top:6px">${trendChart((state.stats || {}).timeline || [])}</div>
          <div class="chart-legend">
            <span class="lg-item"><span class="lg-dot" style="background:var(--brand-2)"></span>${t("dash.detsLegend")}</span>
            <span class="lg-item"><span class="lg-dot" style="background:var(--warning)"></span>${t("dash.scansLegend")}</span>
          </div>
        </div>
        <div class="card chart-card">
          <div class="card-title">${I.alert}${t("dash.breakdown")}</div>
          <div style="margin-top:6px">${donutChart((state.stats || {}).severity || {})}</div>
        </div>
      </div>

      <div class="grid cols-2" style="grid-template-columns: 1fr 1fr;">
        <div class="card">
          <div class="card-title">${I.protection}${t("dash.modules")}</div>
          <div class="list" style="margin-top:8px">
            ${modules.map((m) => `<div class="list-item">
              <div class="lead ${m.active ? "success" : "warning"}">${m.active ? I.check : I.alert}</div>
              <div class="body"><div class="t">${esc(t(m.label))}</div><div class="s">${t(m.active ? "common.enabled" : "common.disabled")}</div></div>
              <label class="switch"><input type="checkbox" data-module="${m.key}" ${m.active ? "checked" : ""}><span class="track"></span><span class="thumb"></span></label>
            </div>`).join("")}
          </div>
        </div>
        <div class="card">
          <div class="card-title">${I.activity}${t("dash.activity")}</div>
          <div class="list" style="margin-top:8px;max-height:260px;overflow:auto">${activity}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">${I.drive}${t("dash.drives")}</div>
        <div class="list" style="margin-top:8px">${drives}</div>
      </div>`;
  }

  /* ============================== SCAN ============================== */
  function scanCard(type, label, desc) {
    const active = state.scanFormType === type;
    return `<button class="card" data-ftype="${type}" style="text-align:start;border-color:${active ? "var(--brand)" : "var(--border)"};background:${active ? "var(--brand-soft)" : "var(--surface)"}">
      <div class="card-title" style="color:${active ? "var(--brand)" : "var(--text)"}">${I.scan}${esc(t(label))}</div>
      <div class="card-sub" style="margin-top:6px">${esc(t(desc))}</div>
    </button>`;
  }

  function scanStages(s) {
    let st = ["wait", "wait", "wait", "wait"];
    if (!s.running && s.status === "completed") st = ["done", "done", "done", "done"];
    else if (!s.running && (s.status === "stopped" || s.status === "error")) st = ["done", "stopped", "wait", "wait"];
    else if (s.phase === "counting") st = ["active", "wait", "wait", "wait"];
    else st = ["done", "active", "wait", "wait"];
    return [["scan.stage.prepare", st[0]], ["scan.stage.files", st[1]], ["scan.stage.finish", st[2]], ["scan.stage.done", st[3]]];
  }

  function stageRows(s) {
    const sdot = (state) => state === "done" ? I.check : state === "active" ? '<span class="spin"></span>' : state === "stopped" ? I.alert : "";
    return scanStages(s).map(([label, state]) => `<div class="stage ${state}">
      <div class="sdot">${sdot(state)}</div>
      <div><div class="st">${esc(t(label))}</div><div class="ss">${esc(t(state === "wait" ? "scan.stage.wait" : state === "stopped" ? "scan.stage.stopped" : state === "done" ? "scan.stage.done" : "scan.stage.active"))}</div></div>
    </div>`).join("");
  }

  function liveDetections() {
    if (!state.scanDetections.length) return `<div class="empty">${I.check}<div class="t">${t("hist.noDetections")}</div></div>`;
    return `<div class="list" style="margin-top:8px">${state.scanDetections.map((d, i) => `<div class="list-item" data-det-row="${i}" style="cursor:pointer">
      <div class="lead danger">${I.alert}</div>
      <div class="body"><div class="t">${esc(d.name)} <span class="badge ${severityClass(d.severity)}">${esc(t("common." + d.severity) || d.severity)}</span></div>
      <div class="s truncate" title="${esc(d.path)}">${esc(d.path)}</div></div>
      <span class="badge ${d.action === "quarantined" ? "success" : "warning"}">${esc(t("common." + d.action) || d.action)}</span>
    </div>`).join("")}</div>`;
  }

  function progressBlock() {
    const s = state.scan;
    const pct = s.phase === "counting" ? 3 : s.percent;
    const indet = s.phase === "counting";
    return `
      <div class="card pad-lg">
        <div class="scan-live">
          <div class="radar" id="radar">
            <div class="ring" style="inset:6%"></div>
            <div class="ring" style="inset:26%"></div>
            <div class="ring" style="inset:46%"></div>
            <div class="cross"></div><div class="cross2"></div>
            <div class="sweep"></div>
            <div class="blip" style="top:34%;inset-inline-start:62%"></div>
            <div class="blip" style="top:60%;inset-inline-start:30%;animation-delay:.8s"></div>
            <div class="blip" style="top:24%;inset-inline-start:38%;animation-delay:1.5s"></div>
          </div>
          <div class="stages">
            <div class="card-title" style="margin-bottom:8px">${I.shield}${t("scan.stages")}</div>
            ${stageRows(s)}
          </div>
        </div>
        <div class="between" style="margin-top:18px">
          <div class="card-sub">${esc(String(s.scan_type || ""))} · ${esc(t("scan.running"))}</div>
          <div class="row">
            <button class="btn sm" data-scan="pause" ${s.paused ? "disabled" : ""}>${I.pause}${t("scan.pause")}</button>
            <button class="btn sm" data-scan="resume" ${s.paused ? "" : "disabled"}>${I.play}${t("scan.resume")}</button>
            <button class="btn sm danger" data-scan="stop">${I.stop}${t("scan.stop")}</button>
          </div>
        </div>
        <div class="progress ${indet ? "indeterminate" : ""}" id="scan-progress" style="margin-top:12px"><span id="scan-progress-bar" style="width:${pct}%"></span></div>
        <div class="between small muted" style="margin-top:8px">
          <span id="scan-percent">${Math.round(pct)}%</span>
          <span id="scan-counter">${s.files_scanned} / ${s.total_files || "…"}</span>
        </div>
        <div class="grid cols-3" style="margin-top:16px">
          <div class="stat"><div class="k">${I.file}${t("scan.files")}</div><div class="v" id="scan-files">${s.files_scanned}</div></div>
          <div class="stat danger"><div class="k">${I.alert}${t("scan.threats")}</div><div class="v" id="scan-threats">${s.threats_found}</div></div>
          <div class="stat"><div class="k">${I.clock}${t("scan.currentFile")}</div><div class="v small truncate" id="scan-current" style="font-size:12px" title="${esc(s.current_path)}">${esc(s.current_path || "—")}</div></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">${I.alert}${t("scan.detections")}</div>
        <div id="scan-live">${liveDetections()}</div>
      </div>`;
  }

  function viewScanResult(r) {
    const threats = r.threats_found || 0;
    const safe = threats === 0;
    return `<div class="card pad-lg">
        <div class="result-hero">
          <div class="result-badge ${safe ? "safe" : "danger"}">${safe ? I.shield : I.alert}</div>
          <div class="result-title">${safe ? esc(t("scan.result.safe")) : esc(t("scan.result.threats", { n: threats }))}</div>
          <div class="result-sub">${esc(t(safe ? "scan.result.safeDesc" : "scan.result.threatsDesc"))}</div>
        </div>
        <div class="grid cols-3" style="margin-top:14px">
          <div class="stat"><div class="k">${I.file}${t("scan.result.files")}</div><div class="v">${r.files_scanned || 0}</div></div>
          <div class="stat ${safe ? "brand" : "danger"}"><div class="k">${I.alert}${t("scan.result.threats")}</div><div class="v">${threats}</div></div>
          <div class="stat"><div class="k">${I.clock}${t("scan.result.duration")}</div><div class="v">${fmtDuration(r.duration)}</div></div>
        </div>
        <div class="row wrap" style="justify-content:flex-end;margin-top:18px">
          <button class="btn" data-export-report="${r.scan_id || ""}">${I.download}${t("scan.export")}</button>
          <button class="btn" data-export-pdf="${r.scan_id || ""}">${I.download}${t("scan.exportPdf")}</button>
          ${threats ? `<button class="btn" data-nav-btn="quarantine">${I.quarantine}${t("nav.quarantine")}</button>` : ""}
          <button class="btn primary" data-new-scan>${I.search}${t("scan.newScan")}</button>
        </div>
      </div>`;
  }

  function viewScan() {
    const s = state.scan;
    if (s.running || s.phase === "counting") return progressBlock();
    if (state.lastResult) return viewScanResult(state.lastResult);
    return `
      <div class="grid cols-3">${scanCard("quick", "scan.quick", "scan.quickDesc")}${scanCard("full", "scan.full", "scan.fullDesc")}${scanCard("custom", "scan.custom", "scan.customDesc")}</div>
      <div class="card pad-lg">
        <div class="between wrap">
          <div>
            <div class="card-title">${I.scan}${esc(t("scan." + state.scanFormType))}</div>
            <div class="card-sub" style="max-width:520px;margin-top:6px">${esc(t("scan." + state.scanFormType + "Desc"))}</div>
          </div>
          <div class="row">
            ${state.scanFormType === "custom" ? `<button class="btn" data-pick-folder>${I.folder}${t("scan.chooseFolder")}</button>` : ""}
            <button class="btn primary lg" data-start-scan>${I.search}${t("scan.start")}</button>
          </div>
        </div>
        ${state.scanFormType === "custom" ? `
          <div class="divider" style="margin:16px 0"></div>
          <div class="small muted" style="margin-bottom:8px">${t("scan.selected")}</div>
          <div class="row wrap" id="target-chips">
            ${state.customTargets.length ? state.customTargets.map((p) => `<span class="chip">${I.folder}<span class="path">${esc(p)}</span><button data-rm-target="${esc(p)}" title="remove">${I.x}</button></span>`).join("") : `<span class="hint">${t("scan.noTargets")}</span>`}
          </div>` : ""}
      </div>`;
  }

  /* =========================== QUARANTINE ========================== */
  function viewQuarantine() {
    const items = state.quarantine || [];
    const ts = tableState("quarantine");
    if (!items.length) {
      return `<div class="card"><div class="empty">${I.quarantine}<div class="t">${t("quar.empty")}</div><div class="small">${t("quar.emptyDesc")}</div></div></div>`;
    }
    const filtered = filterRows(items, ts.q, ["name", "original_path", "engine"]);
    const sorted = sortRows(filtered, ts.sortKey, ts.sortDir);
    const { slice, total, pages } = paged(sorted, ts);
    const bulk = `<button class="btn sm" data-q-bulk="restore">${I.restore}${esc(t("table.restoreSelected"))}</button>
      <button class="btn sm danger" data-q-bulk="delete">${I.trash}${esc(t("table.deleteSelected"))}</button>`;
    const th = (key, label) => `<th class="sortable" data-tsort="quarantine" data-tkey="${key}">${esc(label)} ${sortArrow(ts, key)}</th>`;
    const body = total
      ? `<tbody>${slice.map((q) => `<tr>
          <td><input class="rowsel" type="checkbox" data-rowsel="quarantine" data-rowid="${q.id}" ${ts.selected[q.id] ? "checked" : ""}></td>
          <td><span class="badge ${severityClass(q.severity)}">${esc(t("common." + q.severity) || q.severity)}</span> <span style="font-weight:600">${esc(q.name)}</span></td>
          <td class="truncate mono" style="max-width:320px" title="${esc(q.original_path)}">${esc(q.original_path)}</td>
          <td>${esc(t("engine." + q.engine) || q.engine || "—")}</td>
          <td>${fmtBytes(q.size)}</td>
          <td class="small muted">${fmtDate(q.created)}</td>
          <td class="actions"><button class="btn sm" data-q-restore="${q.id}">${I.restore}${t("quar.restore")}</button>
          <button class="btn sm danger" data-q-delete="${q.id}">${I.trash}${t("quar.delete")}</button></td>
        </tr>`).join("")}</tbody>`
      : `<tbody><tr><td colspan="7"><div class="empty">${I.search}<div class="t">${t("table.noResults")}</div></div></td></tr></tbody>`;
    return `<div class="card">
      ${tableToolbar("quarantine", total, bulk)}
      <div style="overflow:auto"><table class="table sortable">
        <thead><tr>
          <th style="width:34px"><input class="rowsel" type="checkbox" data-rowsel-all="quarantine"></th>
          ${th("name", t("quar.col.threat"))}${th("original_path", t("quar.col.original"))}${th("engine", t("quar.col.engine"))}${th("size", t("quar.col.size"))}${th("created", t("quar.col.date"))}<th></th>
        </tr></thead>${body}
      </table></div>
      ${tablePager("quarantine", total, pages)}
      <div class="row" style="justify-content:flex-end;margin-top:12px"><button class="btn danger sm" data-empty-quarantine>${I.trash}${esc(t("quar.emptyAll"))}</button></div>
    </div>`;
  }

  /* ============================= HISTORY =========================== */
  function viewHistory() {
    const items = (state.history || []).map((h) => ({ ...h, date: h.finished || h.started }));
    const ts = tableState("history");
    const filtered = filterRows(items, ts.q, ["scan_type", "status"]);
    const sorted = sortRows(filtered, ts.sortKey, ts.sortDir);
    const { slice, total, pages } = paged(sorted, ts);
    const statusBadge = (s) => `<span class="badge ${s === "completed" ? "success" : s === "stopped" ? "warning" : "danger"}">${esc(s)}</span>`;
    const th = (key, label) => `<th class="sortable" data-tsort="history" data-tkey="${key}">${esc(label)} ${sortArrow(ts, key)}</th>`;
    const body = total
      ? `<tbody>${slice.map((h) => `<tr>
          <td><span class="badge info">${esc(h.scan_type)}</span></td>
          <td class="small muted">${fmtDate(h.date)}</td>
          <td>${fmtDuration(h.duration)}</td>
          <td>${h.files_scanned}</td>
          <td>${h.threats_found ? `<span class="badge danger">${h.threats_found}</span>` : `<span class="dim">0</span>`}</td>
          <td>${statusBadge(h.status)}</td>
          <td class="actions"><button class="btn sm ghost" data-h-detections="${h.id}">${I.file}${t("hist.viewDetections")}</button></td>
        </tr>`).join("")}</tbody>`
      : `<tbody><tr><td colspan="7"><div class="empty">${I.search}<div class="t">${t("table.noResults")}</div></div></td></tr></tbody>`;
    return `<div class="card">
      <div class="between" style="margin-bottom:12px">
        <div class="card-title">${I.history}${t("hist.title")} <span class="badge info">${items.length}</span></div>
        <div class="row">
          <button class="btn sm" data-export-all>${I.download}${t("common.export")}</button>
          <button class="btn sm" data-export-all-pdf>${I.download}${t("scan.exportPdf")}</button>
        </div>
      </div>
      ${tableToolbar("history", total, "")}
      <div style="overflow:auto"><table class="table sortable">
        <thead><tr>${th("scan_type", t("hist.col.type"))}${th("date", t("hist.col.date"))}${th("duration", t("hist.col.duration"))}${th("files_scanned", t("hist.col.files"))}${th("threats_found", t("hist.col.threats"))}${th("status", t("hist.col.status"))}<th></th></tr></thead>
        ${body}
      </table></div>
      ${tablePager("history", total, pages)}
    </div>`;
  }

  /* ============================ PROTECTION ========================= */
  function moduleRow(key, label, desc, active) {
    return `<div class="list-item">
      <div class="lead ${active ? "success" : "warning"}">${active ? I.check : I.alert}</div>
      <div class="body"><div class="t">${esc(t(label))}</div><div class="s">${esc(t(desc))}</div></div>
      <label class="switch"><input type="checkbox" data-module="${key}" ${active ? "checked" : ""}><span class="track"></span><span class="thumb"></span></label>
    </div>`;
  }

  function viewProtection() {
    const p = state.protection || {};
    const folders = p.protected_folders || [];
    const backup = p.backup || {};
    const st = state.settings || {};
    const exclusions = state.exclusions || [];
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const dayNames = window.I18N.lang === "ar"
      ? ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"] : days;

    return `
      <div class="grid cols-2">
        <div class="card">
          <div class="card-title">${I.protection}${t("prot.title")}</div>
          <div class="list" style="margin-top:8px">
            ${moduleRow("realtime_enabled", "prot.realtime", "prot.realtimeDesc", p.realtime)}
            ${moduleRow("usb_enabled", "prot.usb", "prot.usbDesc", p.usb)}
            ${moduleRow("ransomware_enabled", "prot.ransomware", "prot.ransomwareDesc", p.ransomware)}
            ${moduleRow("scheduled_enabled", "prot.scheduler", "prot.schedulerDesc", p.scheduler)}
          </div>
        </div>

        <div class="card">
          <div class="card-title">${I.clock}${t("prot.scheduler")}</div>
          <div class="grid cols-2" style="margin-top:12px">
            <div class="field"><label>${t("prot.frequency")}</label>
              <select class="input" data-sched="schedule_frequency">
                <option value="daily" ${st.schedule_frequency === "daily" ? "selected" : ""}>${t("prot.daily")}</option>
                <option value="weekly" ${st.schedule_frequency === "weekly" ? "selected" : ""}>${t("prot.weekly")}</option>
              </select></div>
            <div class="field"><label>${t("prot.time")}</label>
              <input class="input" type="time" data-sched="schedule_time" value="${esc(st.schedule_time || "12:00")}"></div>
          </div>
          <div class="field"><label>${t("prot.day")}</label>
            <select class="input" data-sched="schedule_day">
              ${dayNames.map((d, i) => `<option value="${i}" ${Number(st.schedule_day) === i ? "selected" : ""}>${esc(d)}</option>`).join("")}
            </select></div>
          <div class="hint">${t("prot.schedulerDesc")}</div>
        </div>
      </div>

      <div class="card">
        <div class="between" style="margin-bottom:12px">
          <div><div class="card-title">${I.shield}${t("prot.ransomware")}</div>
          <div class="card-sub">${t("prot.ransomwareDesc")}</div></div>
          <div class="row">
            <button class="btn" data-shield-backup>${I.shield}${t("prot.backupNow")}</button>
            <button class="btn" data-shield-restore ${backup.exists ? "" : "disabled"}>${I.restore}${t("prot.restore")}</button>
            <button class="btn primary" data-add-folder>${I.plus}${t("prot.addFolder")}</button>
          </div>
        </div>
        <div class="row wrap">
          ${folders.length ? folders.map((f) => `<span class="chip">${I.folder}<span class="path">${esc(f)}</span><button data-rm-folder="${esc(f)}">${I.x}</button></span>`).join("") : `<span class="hint">${t("prot.noFolders")}</span>`}
        </div>
        ${backup.exists ? `<div class="hint" style="margin-top:10px">${t("prot.backupNow")}: ${backup.files} · ${fmtDate(backup.created)}</div>` : ""}
      </div>

      <div class="card">
        <div class="between" style="margin-bottom:12px">
          <div><div class="card-title">${I.x}${t("prot.exclusions")}</div><div class="card-sub">${t("prot.exclusionsDesc")}</div></div>
          <button class="btn" data-add-exclusion>${I.plus}${t("prot.addExclusion")}</button>
        </div>
        <div class="list">
          ${exclusions.length ? exclusions.map((e) => `<div class="list-item"><div class="lead brand">${I.folder}</div>
            <div class="body"><div class="t truncate" title="${esc(e.path)}">${esc(e.path)}</div><div class="s">${fmtDate(e.created)}</div></div>
            <button class="btn sm ghost" data-rm-exclusion="${e.id}">${I.trash}${t("common.remove")}</button></div>`).join("") : `<div class="empty">${I.check}<div class="small">${t("prot.exclusionsDesc")}</div></div>`}
        </div>
      </div>`;
  }

  /* ============================= SETTINGS ========================== */
  function viewSettings() {
    const s = state.settings || {};
    const sig = state.signatures || {};
    return `
      <div class="grid cols-2">
        <div class="card">
          <div class="card-title">${I.palette}${t("set.appearance")}</div>
          <div class="field" style="margin-top:12px"><label>${t("set.accent")}</label>
            <select class="input" data-set="accent">
              ${["navy", "royal", "azure", "ice"].map((a) => `<option value="${a}" ${s.accent === a ? "selected" : ""}>${t("set.accent." + a)}</option>`).join("")}
            </select></div>
          <div class="list">
            ${toggleRow("reduce_motion", "set.reduceMotion", "set.reduceMotionDesc", s.reduce_motion)}
            ${toggleRow("high_contrast", "set.highContrast", "set.highContrastDesc", s.high_contrast)}
            ${toggleRow("frameless_window", "set.frameless", "set.framelessDesc", s.frameless_window)}
          </div>
          <div class="hint" style="margin-top:10px">${t("set.framelessNote")}</div>
        </div>

        <div class="card">
          <div class="card-title">${I.settings}${t("set.general")}</div>
          <div class="field" style="margin-top:12px"><label>${t("set.language")}</label>
            <select class="input" data-set="language">
              <option value="ar" ${s.language === "ar" ? "selected" : ""}>${t("set.arabic")}</option>
              <option value="en" ${s.language === "en" ? "selected" : ""}>${t("set.english")}</option>
            </select></div>
          <div class="field"><label>${t("set.theme")}</label>
            <select class="input" data-set="theme">
              <option value="dark" ${s.theme === "dark" ? "selected" : ""}>${t("set.dark")}</option>
              <option value="light" ${s.theme === "light" ? "selected" : ""}>${t("set.light")}</option>
            </select></div>
        </div>

        <div class="card">
          <div class="card-title">${I.scan}${t("set.scanning")}</div>
          <div class="list" style="margin-top:8px">
            ${toggleRow("scan_archives", "set.scanArchives", "set.scanArchivesDesc", s.scan_archives)}
            ${toggleRow("auto_quarantine", "set.autoQuarantine", "set.autoQuarantineDesc", s.auto_quarantine)}
            ${toggleRow("scan_removable", "set.scanRemovable", null, s.scan_removable)}
          </div>
          <div class="field" style="margin-top:12px"><label>${t("set.maxSize")}</label>
            <input class="input" type="number" min="1" max="4096" data-set="scan_max_size_mb" value="${Number(s.scan_max_size_mb) || 64}">
            <span class="hint">${t("set.maxSizeDesc")}</span></div>
        </div>

        <div class="card">
          <div class="card-title">${I.cloud}${t("set.virustotal")}</div>
          <div class="list" style="margin-top:8px">
            ${toggleRow("virustotal_enabled", "set.vtEnable", "set.vtEnableDesc", s.virustotal_enabled)}
          </div>
          <div class="field" style="margin-top:12px"><label>${t("set.vtKey")}</label>
            <input class="input mono" type="password" data-set="virustotal_api_key" placeholder="${esc(s.virustotal_api_key || "")}" value="">
            <span class="hint">${t("set.vtEnableDesc")}</span></div>
          <button class="btn" data-vt-test>${I.cloud}${t("set.vtTest")}</button>
        </div>

        <div class="card">
          <div class="card-title">${I.quarantine}${t("set.signatures")}</div>
          <div class="grid cols-2" style="margin-top:10px">
            <div class="stat brand"><div class="k">${I.file}${t("set.sigCount")}</div><div class="v">${sig.count || 0}</div></div>
            <div class="stat"><div class="k">${I.clock}${t("set.sigUpdated")}</div><div class="v small" style="font-size:13px">${sig.updated ? fmtDate(sig.updated) : "—"}</div></div>
          </div>
          <div class="row" style="margin-top:14px">
            <button class="btn" data-sig-update>${I.refresh}${t("set.sigUpdate")}</button>
            <button class="btn" data-sig-import>${I.plus}${t("set.sigImport")}</button>
          </div>
        </div>

        <div class="card">
          <div class="card-title">${I.settings}${t("set.system")}</div>
          <div class="list" style="margin-top:8px">
            ${toggleRow("tray_enabled", "set.tray", "set.trayDesc", s.tray_enabled)}
            ${toggleRow("close_to_tray", "set.closeToTray", "set.closeToTrayDesc", s.close_to_tray)}
            ${toggleRow("autostart", "set.autostart", "set.autostartDesc", s.autostart)}
            ${toggleRow("context_menu", "set.contextMenu", "set.contextMenuDesc", s.context_menu)}
            ${toggleRow("signature_auto_update", "set.sigAuto", "set.sigAutoDesc", s.signature_auto_update)}
          </div>
          <div class="field" style="margin-top:12px"><label>${t("set.sigUrl")}</label>
            <input class="input mono" type="text" data-set="signature_update_url" value="${esc(s.signature_update_url || "")}" placeholder="https://…">
            <span class="hint">${t("set.sigUrlDesc")}</span></div>
          <div class="row" style="margin-top:12px">
            <button class="btn" data-open-logs>${I.file}${t("set.logs")}</button>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">${I.shield}${t("set.about")}</div>
        <div class="card-sub" style="margin-top:8px">${esc(t("set.aboutDesc"))}</div>
        <div class="row" style="margin-top:12px">
          <span class="badge info">${esc((state.boot && state.boot.app.name) || "CYVEX")}</span>
          <span class="badge">v${esc((state.boot && state.boot.app.version) || "1.0.0")}</span>
          <span class="badge mono">${esc((state.dashboard && state.dashboard.system && state.dashboard.system.data_dir) || "")}</span>
        </div>
      </div>

      <div class="row" style="justify-content:flex-end">
        <button class="btn primary lg" data-save-settings>${I.check}${t("set.save")}</button>
      </div>`;
  }

  function toggleRow(key, label, desc, active) {
    return `<div class="list-item">
      <div class="body"><div class="t">${esc(t(label))}</div>${desc ? `<div class="s">${esc(t(desc))}</div>` : ""}</div>
      <label class="switch"><input type="checkbox" data-set-toggle="${key}" ${active ? "checked" : ""}><span class="track"></span><span class="thumb"></span></label>
    </div>`;
  }

  /* ============================ bindings =========================== */
  function bindView() {
    const view = $("#view");

    $$("[data-nav-btn]", view).forEach((b) => b.onclick = () => setView(b.dataset.navBtn));
    $$("[data-quick-scan]", view).forEach((b) => b.onclick = () => startScan("quick"));
    $$("[data-scan]", view).forEach((b) => b.onclick = () => scanControl(b.dataset.scan));

    if (state.view === "dashboard") {
      $$("[data-module]", view).forEach((cb) => cb.onchange = () => setModule(cb.dataset.module, cb.checked));
    }

    if (state.view === "scan") {
      $$("[data-ftype]", view).forEach((b) => b.onclick = () => { state.scanFormType = b.dataset.ftype; render(); });
      $$("[data-start-scan]", view).forEach((b) => b.onclick = doStartScan);
      $$("[data-pick-folder]", view).forEach((b) => b.onclick = pickFolder);
      $$("[data-rm-target]", view).forEach((b) => b.onclick = () => {
        state.customTargets = state.customTargets.filter((p) => p !== b.dataset.rmTarget); render();
      });
      $$("[data-det-row]", view).forEach((el) => el.onclick = () => showThreatDetail(state.scanDetections[Number(el.dataset.detRow)]));
      $$("[data-export-report]", view).forEach((b) => b.onclick = () => exportScan(b.dataset.exportReport || null, "csv"));
      $$("[data-export-pdf]", view).forEach((b) => b.onclick = () => exportScan(b.dataset.exportPdf || null, "pdf"));
      $$("[data-new-scan]", view).forEach((b) => b.onclick = () => { state.lastResult = null; render(); });
    }

    if (state.view === "quarantine") {
      bindTable("quarantine", view);
      $$("[data-q-bulk]", view).forEach((b) => b.onclick = () => quarantineBulk(b.dataset.qBulk));
      $$("[data-q-restore]", view).forEach((b) => b.onclick = () => quarantineAction(b.dataset.qRestore, "restore"));
      $$("[data-q-delete]", view).forEach((b) => b.onclick = () => quarantineAction(b.dataset.qDelete, "delete"));
      $$("[data-empty-quarantine]", view).forEach((b) => b.onclick = async () => {
        if (await confirmDialog(t("quar.emptyAll"), t("quar.confirmEmpty"))) {
          await call("empty_quarantine"); await loadQuarantine(); render();
        }
      });
    }

    if (state.view === "history") {
      bindTable("history", view);
      $$("[data-h-detections]", view).forEach((b) => b.onclick = () => showDetections(b.dataset.hDetections));
      $$("[data-export-all]", view).forEach((b) => b.onclick = () => exportScan(null, "csv"));
      $$("[data-export-all-pdf]", view).forEach((b) => b.onclick = () => exportScan(null, "pdf"));
    }

    if (state.view === "protection") {
      $$("[data-module]", view).forEach((cb) => cb.onchange = () => setModule(cb.dataset.module, cb.checked));
      $$("[data-sched]", view).forEach((el) => el.onchange = () => saveSched(el.dataset.sched, el.value));
      $$("[data-add-folder]", view).forEach((b) => b.onclick = addProtectedFolder);
      $$("[data-rm-folder]", view).forEach((b) => b.onclick = () => removeProtectedFolder(b.dataset.rmFolder));
      $$("[data-shield-backup]", view).forEach((b) => b.onclick = shieldBackup);
      $$("[data-shield-restore]", view).forEach((b) => b.onclick = shieldRestore);
      $$("[data-add-exclusion]", view).forEach((b) => b.onclick = addExclusion);
      $$("[data-rm-exclusion]", view).forEach((b) => b.onclick = () => removeExclusion(b.dataset.rmExclusion));
    }

    if (state.view === "settings") {
      $$("[data-set-toggle]", view).forEach((cb) => cb.onchange = () => saveSetting(cb.dataset.setToggle, cb.checked, true));
      $$("[data-set]", view).forEach((el) => el.onchange = () => {
        const key = el.dataset.set;
        if (key === "virustotal_api_key" && !el.value) return;
        const value = key === "scan_max_size_mb" ? Number(el.value) : el.value;
        saveSetting(key, value, true);
      });
      $$("[data-vt-test]", view).forEach((b) => b.onclick = testVirusTotal);
      $$("[data-sig-update]", view).forEach((b) => b.onclick = updateSignatures);
      $$("[data-sig-import]", view).forEach((b) => b.onclick = importSignatures);
      $$("[data-open-logs]", view).forEach((b) => b.onclick = () => { call("open_logs_folder"); });
      $$("[data-save-settings]", view).forEach((b) => b.onclick = async () => {
        await call("save_settings", collectSettings(view));
        await refreshAll();
        toast("success", t("toast.saved"));
        render();
      });
    }
  }

  function collectSettings(view) {
    const out = {};
    $$("[data-set]", view).forEach((el) => {
      const key = el.dataset.set;
      if (key === "virustotal_api_key") { if (el.value) out[key] = el.value; return; }
      out[key] = key === "scan_max_size_mb" ? Number(el.value) : el.value;
    });
    $$("[data-set-toggle]", view).forEach((cb) => out[cb.dataset.setToggle] = cb.checked);
    return out;
  }

  /* ============================ actions ============================ */
  async function startScan(type, targets) {
    const res = await call("start_scan", type, targets || []);
    if (!res.ok) { toast("warning", t("toast.failed"), res.error || ""); return; }
    state.scanDetections = [];
    state.lastResult = null;
    setView("scan");
  }
  function doStartScan() {
    if (state.scanFormType === "custom" && !state.customTargets.length) {
      toast("warning", t("scan.noTargets")); return;
    }
    startScan(state.scanFormType, state.scanFormType === "custom" ? state.customTargets : []);
  }
  async function scanControl(action) { await call("scan_control", action); }
  async function pickFolder() {
    const folder = await call("pick_folder");
    if (folder && !state.customTargets.includes(folder)) { state.customTargets.push(folder); render(); }
  }
  async function setModule(moduleKey, enabled) {
    await call("save_settings", { [moduleKey]: enabled });
    if (moduleKey === "scheduled_enabled") { await loadProtection(); }
    await refreshAll();
    render();
  }
  async function saveSched(key, value) {
    const v = key === "schedule_day" ? Number(value) : value;
    await call("save_settings", { [key]: v });
    await refreshAll();
  }
  async function saveSetting(key, value, silent) {
    await call("save_settings", { [key]: value });
    state.settings[key] = value;
    if (key === "theme") applyTheme(value);
    if (key === "language") { window.I18N.setLang(value); applyLang(); renderNav(); }
    if (key === "accent" || key === "reduce_motion" || key === "high_contrast") applyAppearance(state.settings);
    if (key === "frameless_window") toast("info", t("set.frameless"), t("set.framelessNote"));
    if (!silent) render();
  }
  async function loadQuarantine() {
    state.quarantine = await call("get_quarantine");
    const ts = tableState("quarantine");
    const ids = new Set(state.quarantine.map((q) => String(q.id)));
    Object.keys(ts.selected).forEach((id) => { if (!ids.has(id)) delete ts.selected[id]; });
  }
  async function quarantineAction(id, action) {
    if (action === "delete" && !(await confirmDialog(t("quar.delete"), t("quar.confirmDelete")))) return;
    const res = await call("quarantine_action", Number(id), action);
    if (!res.ok) toast("warning", t("toast.failed"), res.error);
    await loadQuarantine(); await refreshAll(); render();
  }
  async function addProtectedFolder() {
    const folder = await call("pick_folder");
    if (folder) { await call("add_protected_folder", folder); await loadProtection(); render(); }
  }
  async function removeProtectedFolder(folder) { await call("remove_protected_folder", folder); await loadProtection(); render(); }
  async function shieldBackup() {
    const res = await call("shield_backup");
    if (res.ok) toast("success", t("prot.backupNow"), `${res.files} • ${fmtBytes(res.bytes)}`);
    else toast("warning", t("toast.failed"), res.error);
    await loadProtection(); render();
  }
  async function shieldRestore() {
    if (!(await confirmDialog(t("prot.restore"), t("prot.ransomwareDesc")))) return;
    const res = await call("shield_restore");
    if (res.ok) toast("success", t("prot.restore"), `${res.restored}`);
  }
  async function addExclusion() {
    const folder = await call("pick_folder");
    if (folder) { await call("add_exclusion", folder); state.exclusions = await call("get_exclusions"); render(); }
  }
  async function removeExclusion(id) { await call("remove_exclusion", Number(id)); state.exclusions = await call("get_exclusions"); render(); }
  async function testVirusTotal() {
    const key = $("[data-set='virustotal_api_key']") ? $("[data-set='virustotal_api_key']").value : "";
    if (key) await call("save_settings", { virustotal_api_key: key, virustotal_enabled: true });
    const res = await call("vt_check", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    if (res.ok) toast("success", t("set.vtTest"), `${res.positives}/${res.total}`);
    else toast("warning", t("set.vtTest"), res.error);
  }
  async function updateSignatures() {
    const res = await call("update_signatures", null);
    toast(res.ok ? "success" : "warning", t("set.sigUpdate"), res.ok ? `+${res.added}` : res.error);
    await refreshAll(); render();
  }
  async function importSignatures() {
    const res = await call("import_signatures_file");
    toast(res.ok ? "success" : "warning", t("set.sigImport"), res.ok ? `+${res.added}` : res.error);
    await refreshAll(); render();
  }
  async function showDetections(scanId) {
    const dets = await call("get_detections", Number(scanId));
    window.__detCache = dets;
    const rows = dets.length ? `<table class="table"><thead><tr><th>${t("common.name")}</th><th>${t("common.path")}</th><th>${t("common.engine")}</th></tr></thead>
      <tbody>${dets.map((d, i) => `<tr class="clickable" data-det-idx="${i}"><td style="font-weight:600">${esc(d.name)}</td><td class="mono small truncate" style="max-width:340px" title="${esc(d.path)}">${esc(d.path)}</td><td>${esc(t("engine." + d.engine) || d.engine)}</td></tr>`).join("")}</tbody></table>`
      : `<div class="empty">${I.check}<div class="t">${t("hist.noDetections")}</div></div>`;
    const root = customModal(`<h3>${t("hist.viewDetections")}</h3><div class="selectable" style="max-height:55vh;overflow:auto;margin-top:10px">${rows}</div>
      <div class="modal-actions" style="margin-top:16px;justify-content:space-between">
        <div class="row">
          <button class="btn" data-export-scan="${scanId}">${I.download}${t("common.export")}</button>
          <button class="btn" data-export-scan-pdf="${scanId}">${I.download}${t("scan.exportPdf")}</button>
        </div>
        <button class="btn primary" data-x>${t("common.close")}</button></div>`);
    $$("[data-det-idx]", root).forEach((tr) => tr.onclick = () => showThreatDetail(window.__detCache[Number(tr.dataset.detIdx)]));
    const exp = $("[data-export-scan]", root);
    if (exp) exp.onclick = () => exportScan(Number(scanId), "csv");
    const expPdf = $("[data-export-scan-pdf]", root);
    if (expPdf) expPdf.onclick = () => exportScan(Number(scanId), "pdf");
  }

  async function exportScan(scanId, fmt) {
    const res = await call("export_report", scanId ? Number(scanId) : null, fmt || "csv");
    if (res.ok) toast("success", t("toast.exported"), res.path);
    else if (res.error && res.error !== "cancelled") toast("warning", t("toast.failed"), res.error);
  }

  /* ============================ loading ============================ */
  async function loadProtection() {
    state.protection = await call("get_shield_status");
    state.protection.realtime = (await call("get_protection_status")).realtime;
    state.protection.usb = (await call("get_protection_status")).usb;
    state.protection.scheduler = (await call("get_protection_status")).scheduler;
    state.exclusions = await call("get_exclusions");
  }
  async function refreshAll() {
    state.dashboard = await call("get_dashboard");
    state.settings = await call("get_settings");
    state.signatures = await call("get_signatures_info");
    state.quarantine = await call("get_quarantine");
    state.history = await call("get_history", 50);
    state.stats = await call("get_stats");
    await loadProtection();
    updateTopbar();
  }

  /* ============================ events ============================= */
  function updateScanUI() {
    const s = state.scan;
    const ring = $("#gauge-ring");
    if (ring) {
      const C = 2 * Math.PI * 100;
      const pct = s.running ? (s.phase === "counting" ? 4 : s.percent) : 100;
      ring.style.strokeDashoffset = (C * (1 - pct / 100)).toFixed(1);
    }
    const gstatus = $("#gauge-status");
    if (gstatus) {
      if (s.running) gstatus.textContent = t("dash.scanning");
    }
    const gmeta = $("#gauge-meta");
    if (gmeta && s.running) gmeta.textContent = `${s.files_scanned}/${s.total_files || "…"}`;

    const bar = $("#scan-progress-bar");
    if (bar) {
      const prog = $("#scan-progress");
      const pct = s.phase === "counting" ? 4 : s.percent;
      if (prog) prog.classList.toggle("indeterminate", s.phase === "counting");
      bar.style.width = pct + "%";
      const pc = $("#scan-percent"); if (pc) pc.textContent = Math.round(pct) + "%";
      const cnt = $("#scan-counter"); if (cnt) cnt.textContent = `${s.files_scanned} / ${s.total_files || "…"}`;
      const f = $("#scan-files"); if (f) f.textContent = s.files_scanned;
      const th = $("#scan-threats"); if (th) th.textContent = s.threats_found;
      const cur = $("#scan-current"); if (cur) { cur.textContent = s.current_path || "—"; cur.title = s.current_path || ""; }
      const ph = $("#scan-phase-label"); if (ph) ph.textContent = s.phase === "counting" ? t("scan.preparing") : t("scan.scanning");
    }
  }

  function handleEvent(e) {
    if (!e || !e.type) return;
    if (e.type === "scan:started") {
      state.scanDetections = [];
      state.lastResult = null;
      state.scan._progressRendered = false;
      Object.assign(state.scan, { running: true, phase: "counting", percent: 0, files_scanned: 0, threats_found: 0 });
      setView("scan");
    } else if (e.type === "scan:progress") {
      Object.assign(state.scan, e);
      if (state.view === "scan" || state.view === "dashboard") updateScanUI();
    } else if (e.type === "scan:finished") {
      state.scan.running = false;
      state.scan.percent = 100;
      state.lastResult = {
        scan_id: e.scan_id, files_scanned: e.files_scanned,
        threats_found: e.threats_found, duration: e.duration, status: e.status
      };
      if (e.threats_found) toast("warning", t("toast.scanDone"), t("toast.scanDoneBody", { files: e.files_scanned, threats: e.threats_found }));
      else toast("success", t("toast.scanDone"), t("toast.scanDoneBody", { files: e.files_scanned, threats: 0 }));
      setTimeout(async () => { await refreshAll(); if (state.view === "scan" || state.view === "dashboard") render(); }, 400);
    } else if (e.type === "threat") {
      state.scanDetections.unshift(e);
      toast("danger", t("toast.threatTitle"), `${e.name} — ${e.path}`);
      const th = $("#scan-threats"); if (th) th.textContent = state.scan.threats_found;
      const live = $("#scan-live");
      if (live) { live.innerHTML = liveDetections(); $$("[data-det-row]", live).forEach((el) => el.onclick = () => showThreatDetail(state.scanDetections[Number(el.dataset.detRow)])); }
    } else if (e.type === "activity") {
      call("get_notifications", 30).then((n) => { state.notifications = n; updateBell(); });
      if (state.view === "dashboard") { call("get_activity", 15).then((a) => { if (state.dashboard) state.dashboard.activity = a; if (state.view === "dashboard") render(); }); }
    } else if (e.type === "protection") {
      if (state.view === "protection" || state.view === "dashboard") refreshAll().then(render);
    } else if (e.type === "ransomware:alert") {
      toast("danger", t("toast.ransom"), e.message);
    } else if (e.type === "usb:attached") {
      toast("info", t("toast.usb"), e.drive);
    }
  }
  window.NOVU = { receive: handleEvent };

  /* ======================== theme / language ======================= */
  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    const btn = $("#theme-toggle");
    if (btn) btn.innerHTML = theme === "dark" ? I.sun : I.moon;
  }
  function applyLang() {
    const lang = window.I18N.lang;
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    const btn = $("#lang-toggle");
    if (btn) btn.textContent = lang === "ar" ? "EN" : "ع";
    const dt = document.querySelector("#drop-overlay .drop-t");
    if (dt) dt.textContent = t("drop.hint");
  }

  function applySidebar() {
    document.body.classList.toggle("collapsed", !!state.settings.sidebar_collapsed);
  }
  function toggleSidebar() {
    state.settings.sidebar_collapsed = !state.settings.sidebar_collapsed;
    applySidebar();
    saveSetting("sidebar_collapsed", state.settings.sidebar_collapsed, true);
  }

  function wireChrome() {
    const bell = $("#bell");
    if (bell) bell.onclick = (e) => { e.stopPropagation(); toggleBell(); };
    document.addEventListener("click", (e) => {
      const p = $("#notif-panel");
      if (p && !p.hasAttribute("hidden") && !e.target.closest(".bell-wrap")) {
        p.setAttribute("hidden", ""); p.classList.remove("open");
      }
    });
    const sb = $("#sidebar-toggle");
    if (sb) { sb.innerHTML = I.menu; sb.onclick = () => { toggleSidebar(); }; }
    $$("[data-win]").forEach((b) => b.onclick = () => call("window_action", b.dataset.win));
  }

  function wireDrop() {
    let overlay = document.getElementById("drop-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "drop-overlay";
      overlay.className = "drop-overlay";
      overlay.hidden = true;
      overlay.innerHTML = `<div class="drop-card"><div class="drop-ic">${I.download}</div><div class="drop-t"></div></div>`;
      document.body.appendChild(overlay);
    }
    overlay.querySelector(".drop-t").textContent = t("drop.hint");
    let depth = 0;
    window.addEventListener("dragenter", (e) => { e.preventDefault(); depth += 1; overlay.hidden = false; });
    window.addEventListener("dragover", (e) => e.preventDefault());
    window.addEventListener("dragleave", (e) => { e.preventDefault(); depth = Math.max(0, depth - 1); if (!depth) overlay.hidden = true; });
    window.addEventListener("drop", () => { depth = 0; overlay.hidden = true; });
  }

  function showWizard() {
    let step = 0;
    const root = $("#modal-root");
    const feats = [["wiz.f1", "wiz.f1d", "shield"], ["wiz.f2", "wiz.f2d", "quarantine"], ["wiz.f3", "wiz.f3d", "lock"], ["wiz.f4", "wiz.f4d", "clock"]];
    const draw = () => {
      let inner;
      if (step === 0) {
        inner = `<div class="wizard-hero"><div class="wiz-hero">${I.shield}</div></div>
          <div class="wizard-step">${esc(t("wiz.step", { n: 1, m: 2 }))}</div>
          <h2>${esc(t("wiz.welcome"))}</h2>
          <div class="lead">${esc(t("wiz.intro"))}</div>
          <div class="wiz-features">${feats.map(([a, b, ic]) => `<div class="wiz-feature"><div class="wf-ic">${I[ic]}</div><div><div class="wf-t">${esc(t(a))}</div><div class="wf-d">${esc(t(b))}</div></div></div>`).join("")}</div>
          <div class="wizard-actions"><button class="btn ghost" data-wiz-skip>${esc(t("wiz.skip"))}</button><button class="btn primary" data-wiz-next>${esc(t("wiz.getStarted"))}</button></div>`;
      } else {
        inner = `<div class="wizard-step">${esc(t("wiz.step", { n: 2, m: 2 }))}</div>
          <h2>${esc(t("wiz.enableRt"))}</h2>
          <div class="lead">${esc(t("wiz.intro"))}</div>
          <div class="list">
            <div class="list-item"><div class="lead success">${I.shield}</div><div class="body"><div class="t">${esc(t("prot.realtime"))}</div><div class="s">${esc(t("wiz.f1d"))}</div></div>
              <label class="switch"><input type="checkbox" id="wiz-rt" ${state.settings.realtime_enabled ? "checked" : ""}><span class="track"></span><span class="thumb"></span></label></div>
          </div>
          <div class="wizard-actions" style="margin-top:22px"><button class="btn ghost" data-wiz-back>${esc(t("common.cancel"))}</button><button class="btn primary" data-wiz-finish>${esc(t("wiz.getStarted"))}</button></div>`;
      }
      root.innerHTML = `<div class="wizard-backdrop"><div class="wizard">${inner}</div></div>`;
      const next = $("[data-wiz-next]", root); if (next) next.onclick = () => { step = 1; draw(); };
      const back = $("[data-wiz-back]", root); if (back) back.onclick = () => { step = 0; draw(); };
      const skip = $("[data-wiz-skip]", root); if (skip) skip.onclick = () => finish();
      const fin = $("[data-wiz-finish]", root); if (fin) fin.onclick = async () => {
        const rt = $("#wiz-rt");
        await saveSetting("realtime_enabled", rt ? rt.checked : true, true);
        finish();
      };
    };
    const finish = async () => {
      closeModal();
      await call("complete_first_run");
      state.settings.first_run = false;
      await refreshAll(); render();
    };
    draw();
  }

  /* ============================= boot ============================== */
  async function boot() {
    window.__bootStage = "start";
    try {
      const data = await call("bootstrap");
      window.__bootStage = "bootstrapped";
      state.boot = data;
      state.settings = data.settings || {};
      window.I18N.setLang(state.settings.language || "ar");
      applyLang();
      applyTheme(state.settings.theme || "dark");
      applyAppearance(state.settings);
      applySidebar();
      state.dashboard = data.dashboard;

      if (state.settings.frameless_window) {
        document.body.classList.add("frameless");
        const tb = $("#titlebar"); if (tb) tb.hidden = false;
      }

      $("#app-version").textContent = "v" + ((data.app && data.app.version) || "1.0.0");
      await refreshAll();
      window.__bootStage = "refreshed";
      state.notifications = await call("get_notifications", 30);
      renderNav();
      render();
      wireChrome();
      wireDrop();
      updateBell();
      window.__bootStage = "rendered";

      $("#theme-toggle").onclick = () => {
        const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
        applyTheme(next); saveSetting("theme", next, true);
      };
      $("#lang-toggle").onclick = () => {
        const next = window.I18N.lang === "ar" ? "en" : "ar";
        window.I18N.setLang(next); applyLang(); saveSetting("language", next, true); renderNav(); render();
      };

      const sp = $("#splash");
      if (sp) { sp.classList.add("hide"); setTimeout(() => sp.remove(), 500); }

      if (state.settings.first_run) setTimeout(showWizard, 350);

      const initial = (data.initial_scan && data.initial_scan.target) || (window.NOVU_INITIAL_SCAN || null);
      if (initial) setTimeout(() => startScan("custom", [initial]), 600);

      setInterval(async () => {
        if (!state.scan.running) return;
        const s = await call("get_scan_status");
        Object.assign(state.scan, s);
        if (state.view === "scan" || state.view === "dashboard") updateScanUI();
        if (s.running && state.view === "scan" && s.phase !== "counting" && !state.scan._progressRendered) {
          state.scan._progressRendered = true; render();
        }
      }, 1500);
    } catch (err) {
      window.__bootStage = "error: " + (err && err.message || err);
      document.body.innerHTML = `<div style="padding:40px;font-family:sans-serif;color:#e5484d">CYVEX failed to start: ${esc(err && err.message || err)}</div>`;
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})();

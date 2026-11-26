// Azure Portal screenshot aid. Read-only visual redaction; it does not click,
// submit, save or provision. Inspect the final capture and keep raw captures private.
(() => {
  const extra = Array.isArray(window.__AZURE_REDACTIONS__)
    ? window.__AZURE_REDACTIONS__ : [];
  const guidLabels = new Map();
  const redact = (value) => {
    let text = value;
    text = text.replace(/\/subscriptions\/[0-9a-f-]{36}/ig, "/subscriptions/<subscription-id>");
    text = text.replace(/\/tenants\/[0-9a-f-]{36}/ig, "/tenants/<tenant-id>");
    text = text.replace(/\/resourceGroups\/[^\/?\s]+/ig, "/resourceGroups/<resource-group>");
    text = text.replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/ig, "<email>");
    text = text.replace(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g, (ip) => {
      if (/^(192\.0\.2\.|198\.51\.100\.|203\.0\.113\.)/.test(ip)) return ip;
      return "<ip-address>";
    });
    text = text.replace(/\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b/ig, (id) => {
      if (!guidLabels.has(id.toLowerCase())) {
        guidLabels.set(id.toLowerCase(), "<azure-id-" + (guidLabels.size + 1) + ">");
      }
      return guidLabels.get(id.toLowerCase());
    });
    for (const [pattern, replacement] of extra) {
      if (pattern instanceof RegExp && typeof replacement === "string") {
        text = text.replace(pattern, replacement);
      }
    }
    return text;
  };
  const visit = (root) => {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (!parent || /^(SCRIPT|STYLE|NOSCRIPT)$/i.test(parent.tagName)) continue;
      const next = redact(node.nodeValue || "");
      if (next !== node.nodeValue) node.nodeValue = next;
    }
    for (const el of root.querySelectorAll ? root.querySelectorAll("*") : []) {
      if (el.shadowRoot) visit(el.shadowRoot);
      if (el.tagName === "IFRAME") {
        try { if (el.contentDocument) visit(el.contentDocument); } catch (_) { /* cross-origin */ }
      }
      if ((el.tagName === "INPUT" || el.tagName === "TEXTAREA") && el.value) {
        el.value = redact(el.value);
      }
    }
  };
  if (window.__azureCaptureObserver) window.__azureCaptureObserver.disconnect();
  visit(document);
  window.__azureCaptureObserver = new MutationObserver(() => visit(document));
  window.__azureCaptureObserver.observe(document.documentElement, {
    subtree: true, childList: true, characterData: true
  });
  document.documentElement.style.zoom = (window.innerWidth / 1400).toFixed(3);
  return "Azure visual redaction installed; verify the rendered capture manually.";
})();

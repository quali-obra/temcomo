/* Mini-DOM honesto: parseia innerHTML, casa seletores simples e despacha eventos de
   verdade. Se um listener não estiver ligado, o clique não faz nada — que é justamente
   o que o teste precisa enxergar. */
function criarDom() {
  function No(tag) {
    this.tagName = String(tag || "div").toUpperCase();
    this.children = []; this.attrs = {}; this.ouvintes = {};
    this.className = ""; this._text = ""; this.value = "";
    this.disabled = false; this.hidden = false; this.style = {}; this.parent = null;
  }
  No.prototype.setAttribute = function (n, v) { this.attrs[n] = String(v); };
  No.prototype.getAttribute = function (n) {
    if (n === "class") return this.className;
    return Object.prototype.hasOwnProperty.call(this.attrs, n) ? this.attrs[n] : null;
  };
  No.prototype.appendChild = function (f) { f.parent = this; this.children.push(f); return f; };
  No.prototype.addEventListener = function (tipo, fn) {
    (this.ouvintes[tipo] = this.ouvintes[tipo] || []).push(fn);
  };
  No.prototype.dispatchEvent = function (ev) {
    var alvo = this;
    ev.target = ev.target || this;
    while (alvo) {
      (alvo.ouvintes[ev.type] || []).forEach(function (fn) { fn.call(alvo, ev); });
      alvo = alvo.parent;
    }
    return true;
  };
  No.prototype.matches = function (sel) { return casa(this, sel); };
  No.prototype.closest = function (sel) {
    var n = this; while (n) { if (casa(n, sel)) return n; n = n.parent; } return null;
  };
  No.prototype.focus = function () { this.focado = true; };
  No.prototype.scrollIntoView = function () {};
  Object.defineProperty(No.prototype, "textContent", {
    get: function () {
      return this._text + this.children.map(function (f) { return f.textContent; }).join("");
    },
    set: function (v) { this._text = String(v); this.children = []; }
  });
  Object.defineProperty(No.prototype, "innerHTML", {
    get: function () { return this._html || ""; },
    set: function (v) { this._html = String(v); this.children = analisar(String(v), this); }
  });
  No.prototype.querySelectorAll = function (sel) {
    var achados = [];
    (function anda(n) {
      n.children.forEach(function (f) { if (casa(f, sel)) achados.push(f); anda(f); });
    })(this);
    return achados;
  };
  No.prototype.querySelector = function (sel) { return this.querySelectorAll(sel)[0] || null; };

  function casa(no, sel) {
    sel = String(sel).trim();
    var m;
    if ((m = sel.match(/^\[([\w-]+)(?:=["']?([^"'\]]*)["']?)?\]$/))) {
      var v = no.getAttribute(m[1]);
      return v !== null && (m[2] === undefined || v === m[2]);
    }
    if (sel[0] === ".") return (" " + no.className + " ").indexOf(" " + sel.slice(1) + " ") !== -1;
    if (sel[0] === "#") return no.attrs.id === sel.slice(1);
    return no.tagName === sel.toUpperCase();
  }

  function analisar(html, pai) {
    var filhos = [], re = /<(\w+)([^>]*)>|<\/(\w+)>|([^<]+)/g, pilha = [], m;
    function ondeEstou() { return pilha.length ? pilha[pilha.length - 1] : null; }
    while ((m = re.exec(html))) {
      if (m[1]) {
        var no = new No(m[1]);
        (m[2] || "").replace(/([\w-]+)\s*=\s*"([^"]*)"/g, function (_, k, v) {
          if (k === "class") no.className = v; else no.setAttribute(k, v); return "";
        });
        var atual = ondeEstou();
        if (atual) atual.appendChild(no); else { no.parent = pai; filhos.push(no); }
        if (!/^(br|img|input|hr|meta|link)$/i.test(m[1])) pilha.push(no);
      } else if (m[3]) {
        pilha.pop();
      } else if (m[4] && m[4].trim()) {
        var dono = ondeEstou();
        if (dono) dono._text += m[4];
      }
    }
    return filhos;
  }

  var doc = new No("body");
  doc.criados = {};
  doc.getElementById = function (id) {
    if (!doc.criados[id]) { var n = new No("div"); n.setAttribute("id", id); doc.criados[id] = n; }
    return doc.criados[id];
  };
  doc.createElement = function (tag) { return new No(tag); };
  doc.body = doc;
  return { doc: doc, No: No, evento: function (tipo) { return { type: tipo, target: null }; } };
}
module.exports = { criarDom: criarDom };

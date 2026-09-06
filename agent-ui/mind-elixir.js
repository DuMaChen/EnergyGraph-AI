var pt = Object.defineProperty;
var gt = (e, t, n) => t in e ? pt(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var X = (e, t, n) => (gt(e, typeof t != "symbol" ? t + "" : t, n), n);
const we = {
  name: "Latte",
  type: "light",
  palette: ["#dd7878", "#ea76cb", "#8839ef", "#e64553", "#fe640b", "#df8e1d", "#40a02b", "#209fb5", "#1e66f5", "#7287fd"],
  cssVar: {
    "--node-gap-x": "30px",
    "--node-gap-y": "10px",
    "--main-gap-x": "65px",
    "--main-gap-y": "45px",
    "--root-radius": "30px",
    "--main-radius": "20px",
    "--root-color": "#ffffff",
    "--root-bgcolor": "#4c4f69",
    "--root-border-color": "rgba(0, 0, 0, 0)",
    "--main-color": "#444446",
    "--main-bgcolor": "#ffffff",
    "--topic-padding": "3px",
    "--color": "#777777",
    "--bgcolor": "#f6f6f6",
    "--selected": "#4dc4ff",
    "--accent-color": "#e64553",
    "--panel-color": "#444446",
    "--panel-bgcolor": "#ffffff",
    "--panel-border-color": "#eaeaea",
    "--map-padding": "50px"
  }
}, xe = {
  name: "Dark",
  type: "dark",
  palette: ["#848FA0", "#748BE9", "#D2F9FE", "#4145A5", "#789AFA", "#706CF4", "#EF987F", "#775DD5", "#FCEECF", "#DA7FBC"],
  cssVar: {
    "--node-gap-x": "30px",
    "--node-gap-y": "10px",
    "--main-gap-x": "65px",
    "--main-gap-y": "45px",
    "--root-radius": "30px",
    "--main-radius": "20px",
    "--root-color": "#ffffff",
    "--root-bgcolor": "#2d3748",
    "--root-border-color": "rgba(255, 255, 255, 0.1)",
    "--main-color": "#ffffff",
    "--main-bgcolor": "#4c4f69",
    "--topic-padding": "3px",
    "--color": "#cccccc",
    "--bgcolor": "#252526",
    "--selected": "#4dc4ff",
    "--accent-color": "#789AFA",
    "--panel-color": "#ffffff",
    "--panel-bgcolor": "#2d3748",
    "--panel-border-color": "#696969",
    "--map-padding": "50px 80px"
  }
};
function pe(e) {
  return e.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}
const ie = function(e, t) {
  if (t.id === e)
    return t;
  if (t.children && t.children.length) {
    for (let n = 0; n < t.children.length; n++) {
      const o = ie(e, t.children[n]);
      if (o)
        return o;
    }
    return null;
  } else
    return null;
}, B = (e, t) => {
  if (e.parent = t, e.children)
    for (let n = 0; n < e.children.length; n++)
      B(e.children[n], e);
}, Y = (e, t, n) => {
  if (e.expanded = t, e.children)
    if (n === void 0 || n > 0) {
      const o = n !== void 0 ? n - 1 : void 0;
      e.children.forEach((s) => {
        Y(s, t, o);
      });
    } else
      e.children.forEach((o) => {
        Y(o, !1);
      });
};
function Ce(e) {
  if (e.id = I(), e.children)
    for (let t = 0; t < e.children.length; t++)
      Ce(e.children[t]);
}
function re(e, t, n, o) {
  const s = o - t, i = e - n;
  let c = Math.atan(Math.abs(s) / Math.abs(i)) / 3.14 * 180;
  if (isNaN(c))
    return;
  i < 0 && s > 0 && (c = 180 - c), i < 0 && s < 0 && (c = 180 + c), i > 0 && s < 0 && (c = 360 - c);
  const r = 12, l = 30, d = c + l, f = c - l;
  return {
    x1: n + Math.cos(Math.PI * d / 180) * r,
    y1: o - Math.sin(Math.PI * d / 180) * r,
    x2: n + Math.cos(Math.PI * f / 180) * r,
    y2: o - Math.sin(Math.PI * f / 180) * r
  };
}
function I() {
  return ((/* @__PURE__ */ new Date()).getTime().toString(16) + Math.random().toString(16).substr(2)).substr(2, 16);
}
const mt = function() {
  const e = I();
  return {
    topic: this.newTopicName,
    id: e
  };
};
function Ee(e) {
  return JSON.parse(
    JSON.stringify(e, (n, o) => {
      if (n !== "parent")
        return o;
    })
  );
}
const O = (e, t) => {
  let n = 0, o = 0;
  for (; t && t !== e; )
    n += t.offsetLeft, o += t.offsetTop, t = t.offsetParent;
  return { offsetLeft: n, offsetTop: o };
}, k = (e, t) => {
  for (const n in t)
    e.setAttribute(n, t[n]);
}, ge = (e) => e ? e.tagName === "ME-TPC" : !1, de = (e) => e.filter((t) => t.nodeObj.parent).filter((t, n, o) => {
  for (let s = 0; s < o.length; s++) {
    if (t === o[s])
      continue;
    const { parent: i } = t.nodeObj;
    if (i === o[s].nodeObj)
      return !1;
  }
  return !0;
}), Xe = (e) => {
  const t = /translate\(([^,]+),\s*([^)]+)\)/, n = e.match(t);
  return n ? { x: parseFloat(n[1]), y: parseFloat(n[2]) } : { x: 0, y: 0 };
}, Se = function(e) {
  for (let t = 0; t < e.length; t++) {
    const { dom: n, evt: o, func: s } = e[t];
    n.addEventListener(o, s);
  }
  return function() {
    for (let n = 0; n < e.length; n++) {
      const { dom: o, evt: s, func: i } = e[n];
      o.removeEventListener(s, i);
    }
  };
}, P = {
  LHS: "lhs",
  RHS: "rhs"
}, vt = (e) => {
  const t = e.map.querySelectorAll(".lhs>me-wrapper>me-parent>me-tpc");
  e.selectNode(t[Math.ceil(t.length / 2) - 1]);
}, bt = (e) => {
  const t = e.map.querySelectorAll(".rhs>me-wrapper>me-parent>me-tpc");
  e.selectNode(t[Math.ceil(t.length / 2) - 1]);
}, yt = (e) => {
  e.selectNode(e.map.querySelector("me-root>me-tpc"));
}, wt = function(e, t) {
  const n = t.parentElement.parentElement.parentElement.previousSibling;
  if (n) {
    const o = n.firstChild;
    e.selectNode(o);
  }
}, xt = function(e, t) {
  const n = t.parentElement.nextSibling;
  if (n && n.firstChild) {
    const o = n.firstChild.firstChild.firstChild;
    e.selectNode(o);
  }
}, Pe = function(e, t) {
  var i, c;
  const n = e.currentNode || ((i = e.currentNodes) == null ? void 0 : i[0]);
  if (!n)
    return;
  const o = n.nodeObj, s = n.offsetParent.offsetParent.parentElement;
  o.parent ? s.className === t ? xt(e, n) : (c = o.parent) != null && c.parent ? wt(e, n) : yt(e) : t === P.LHS ? vt(e) : bt(e);
}, $e = function(e, t) {
  const n = e.currentNode;
  if (!n || !n.nodeObj.parent)
    return;
  const s = t + "Sibling", i = n.parentElement.parentElement[s];
  i ? e.selectNode(i.firstChild.firstChild) : e.selectNode(n);
}, ce = function(e, t, n) {
  const { scaleVal: o, scaleSensitivity: s } = e;
  switch (t) {
    case "in":
      e.scale(o + s, n);
      break;
    case "out":
      e.scale(o - s, n);
  }
};
function Ct(e, t) {
  t = t === !0 ? {} : t;
  const n = () => {
    e.currentArrow ? e.removeArrow() : e.currentSummary ? e.removeSummary(e.currentSummary.summaryObj.id) : e.currentNodes && e.removeNodes(e.currentNodes);
  };
  let o = !1, s = null;
  const i = (r) => {
    const l = e.nodeData;
    if (r.key === "0")
      for (const d of l.children)
        Y(d, !1);
    if (r.key === "=")
      for (const d of l.children)
        Y(d, !0);
    if (["1", "2", "3", "4", "5", "6", "7", "8", "9"].includes(r.key))
      for (const d of l.children)
        Y(d, !0, Number(r.key) - 1);
    e.refresh(), e.toCenter(), o = !1, s && (clearTimeout(s), s = null, e.container.removeEventListener("keydown", i));
  }, c = {
    Enter: (r) => {
      r.shiftKey ? e.insertSibling("before") : r.ctrlKey || r.metaKey ? e.insertParent() : e.insertSibling("after");
    },
    Tab: () => {
      e.addChild();
    },
    F1: () => {
      e.toCenter();
    },
    F2: () => {
      e.currentSummary ? e.editSummary(e.currentSummary) : e.currentArrow ? e.editArrowLabel(e.currentArrow) : e.beginEdit();
    },
    ArrowUp: (r) => {
      if (r.altKey)
        e.moveUpNode();
      else {
        if (r.metaKey || r.ctrlKey)
          return e.initSide();
        $e(e, "previous");
      }
    },
    ArrowDown: (r) => {
      r.altKey ? e.moveDownNode() : $e(e, "next");
    },
    ArrowLeft: (r) => {
      if (r.metaKey || r.ctrlKey)
        return e.initLeft();
      Pe(e, P.LHS);
    },
    ArrowRight: (r) => {
      if (r.metaKey || r.ctrlKey)
        return e.initRight();
      Pe(e, P.RHS);
    },
    PageUp: () => e.moveUpNode(),
    PageDown: () => {
      e.moveDownNode();
    },
    c: (r) => {
      (r.metaKey || r.ctrlKey) && (e.waitCopy = e.currentNodes);
    },
    x: (r) => {
      (r.metaKey || r.ctrlKey) && (e.waitCopy = e.currentNodes, n());
    },
    v: (r) => {
      !e.waitCopy || !e.currentNode || (r.metaKey || r.ctrlKey) && (e.waitCopy.length === 1 ? e.copyNode(e.waitCopy[0], e.currentNode) : e.copyNodes(e.waitCopy, e.currentNode));
    },
    "=": (r) => {
      (r.metaKey || r.ctrlKey) && ce(e, "in");
    },
    "-": (r) => {
      (r.metaKey || r.ctrlKey) && ce(e, "out");
    },
    0: (r) => {
      if (r.metaKey || r.ctrlKey) {
        if (o)
          return;
        e.scale(1);
      }
    },
    k: (r) => {
      (r.metaKey || r.ctrlKey) && (o = !0, s && (clearTimeout(s), e.container.removeEventListener("keydown", i)), s = window.setTimeout(() => {
        o = !1, s = null;
      }, 2e3), e.container.addEventListener("keydown", i));
    },
    Delete: n,
    Backspace: n,
    ...t
  };
  e.container.onkeydown = (r) => {
    if (r.preventDefault(), !e.editable)
      return;
    const l = c[r.key];
    l && l(r);
  };
}
function Et(e) {
  const { dragMoveHelper: t } = e;
  let n = 0;
  e.spacePressed = !1;
  const o = (a) => {
    var C, S;
    if (a.button !== 0)
      return;
    if ((C = e.helper1) != null && C.moved) {
      e.helper1.clear();
      return;
    }
    if ((S = e.helper2) != null && S.moved) {
      e.helper2.clear();
      return;
    }
    if (t.moved) {
      t.clear();
      return;
    }
    const h = a.target;
    if (h.tagName === "ME-EPD")
      a.ctrlKey || a.metaKey ? e.expandNodeAll(h.previousSibling) : e.expandNode(h.previousSibling);
    else if (h.tagName === "ME-TPC" && e.currentNodes.length > 1)
      e.selectNode(h);
    else if (!e.editable)
      return;
    if (h.classList.contains("svg-label")) {
      const y = h.dataset.svgId, x = h.dataset.type, E = document.getElementById(y);
      if (E) {
        if (x === "arrow") {
          e.selectArrow(E);
          return;
        } else if (x === "summary") {
          e.selectSummary(E);
          return;
        }
      }
    }
    if (h.closest(".topiclinks")) {
      const y = h.closest("g");
      if (y) {
        e.selectArrow(y);
        return;
      }
    }
    if (h.closest(".summary")) {
      const y = h.closest("g");
      if (y) {
        e.selectSummary(y);
        return;
      }
    }
  }, s = (a) => {
    if (!e.editable)
      return;
    const h = a.target;
    if (ge(h) && e.beginEdit(h), h.classList.contains("svg-label")) {
      const C = h.dataset.svgId, S = h.dataset.type, y = document.getElementById(C);
      if (y) {
        if (S === "arrow") {
          e.editArrowLabel(y);
          return;
        } else if (S === "summary") {
          e.editSummary(y);
          return;
        }
      }
    }
    if (h.closest(".topiclinks")) {
      const C = h.closest("g");
      if (C) {
        e.editArrowLabel(C);
        return;
      }
    }
    if (h.closest(".summary")) {
      const C = h.closest("g");
      if (C) {
        e.editSummary(C);
        return;
      }
    }
  }, i = (a) => {
    if (a.pointerType === "mouse")
      return;
    const h = (/* @__PURE__ */ new Date()).getTime(), v = h - n;
    v < 300 && v > 0 && s(a), n = h;
  }, c = (a) => {
    a.code === "Space" && (e.spacePressed = !0, e.container.classList.add("space-pressed"), a.preventDefault());
  }, r = (a) => {
    a.code === "Space" && (e.spacePressed = !1, e.container.classList.remove("space-pressed"));
  }, l = (a) => {
    t.moved = !1;
    const h = e.spacePressed && a.button === 0 && a.pointerType === "mouse", v = e.mouseSelectionButton === 0 ? 2 : 0, w = a.button === v && a.pointerType === "mouse";
    if (!h && !w)
      return;
    t.x = a.clientX, t.y = a.clientY;
    const C = a.target;
    (h || C.className !== "circle" && C.contentEditable !== "plaintext-only") && (t.mousedown = !0, C.setPointerCapture(a.pointerId));
  }, d = (a) => {
    if (a.target.contentEditable !== "plaintext-only" || e.spacePressed && t.mousedown) {
      const h = a.clientX - t.x, v = a.clientY - t.y;
      t.onMove(h, v);
    }
    t.x = a.clientX, t.y = a.clientY;
  }, f = (a) => {
    if (!t.mousedown)
      return;
    const h = a.target;
    h.hasPointerCapture && h.hasPointerCapture(a.pointerId) && h.releasePointerCapture(a.pointerId), t.clear();
  }, u = () => {
    t.mousedown && t.clear();
  }, g = (a) => {
    if (a.preventDefault(), a.button !== 2 || !e.editable)
      return;
    const h = a.target;
    ge(h) && !h.classList.contains("selected") && e.selectNode(h), setTimeout(() => {
      e.dragMoveHelper.moved || e.bus.fire("showContextMenu", a);
    }, 200);
  }, b = (a) => {
    a.stopPropagation(), a.preventDefault(), a.ctrlKey || a.metaKey ? a.deltaY < 0 ? ce(e, "in", e.dragMoveHelper) : e.scaleVal - e.scaleSensitivity > 0 && ce(e, "out", e.dragMoveHelper) : a.shiftKey ? e.move(-a.deltaY, 0) : e.move(-a.deltaX, -a.deltaY);
  }, { container: p } = e;
  return Se([
    { dom: p, evt: "pointerdown", func: l },
    { dom: p, evt: "pointermove", func: d },
    { dom: p, evt: "pointerup", func: f },
    { dom: p, evt: "pointerup", func: i },
    { dom: p, evt: "click", func: o },
    { dom: p, evt: "dblclick", func: s },
    { dom: p, evt: "contextmenu", func: g },
    { dom: p, evt: "wheel", func: typeof e.handleWheel == "function" ? e.handleWheel : b },
    { dom: p, evt: "blur", func: u },
    { dom: document, evt: "keydown", func: c },
    { dom: document, evt: "keyup", func: r }
  ]);
}
function St() {
  return {
    handlers: {},
    addListener: function(e, t) {
      this.handlers[e] === void 0 && (this.handlers[e] = []), this.handlers[e].push(t);
    },
    fire: function(e, ...t) {
      if (this.handlers[e] instanceof Array) {
        const n = this.handlers[e];
        for (let o = 0; o < n.length; o++)
          n[o](...t);
      }
    },
    removeListener: function(e, t) {
      if (!this.handlers[e])
        return;
      const n = this.handlers[e];
      if (!t)
        n.length = 0;
      else if (n.length)
        for (let o = 0; o < n.length; o++)
          n[o] === t && this.handlers[e].splice(o, 1);
    }
  };
}
const le = document, Nt = function() {
  this.nodes.innerHTML = "";
  const e = this.createTopic(this.nodeData);
  Ne.call(this, e, this.nodeData), e.draggable = !1;
  const t = le.createElement("me-root");
  t.appendChild(e);
  const n = this.nodeData.children || [];
  if (this.direction === 2) {
    let o = 0, s = 0;
    n.map((i) => {
      i.direction === 0 ? o += 1 : i.direction === 1 ? s += 1 : o <= s ? (i.direction = 0, o += 1) : (i.direction = 1, s += 1);
    });
  }
  kt(this, n, t);
}, kt = function(e, t, n) {
  const o = le.createElement("me-main");
  o.className = P.LHS;
  const s = le.createElement("me-main");
  s.className = P.RHS;
  for (let i = 0; i < t.length; i++) {
    const c = t[i], { grp: r } = e.createWrapper(c);
    e.direction === 2 ? c.direction === 0 ? o.appendChild(r) : s.appendChild(r) : e.direction === 0 ? o.appendChild(r) : s.appendChild(r);
  }
  e.nodes.appendChild(o), e.nodes.appendChild(n), e.nodes.appendChild(s), e.nodes.appendChild(e.lines), e.nodes.appendChild(e.labelContainer);
}, _t = function(e, t) {
  const n = le.createElement("me-children");
  for (let o = 0; o < t.length; o++) {
    const s = t[o], { grp: i } = e.createWrapper(s);
    n.appendChild(i);
  }
  return n;
}, _ = document, Je = function(e, t) {
  const o = (this != null && this.el ? this.el : t || document).querySelector(`[data-nodeid="me${e}"]`);
  if (!o)
    throw new Error(`FindEle: Node ${e} not found, maybe it's collapsed.`);
  return o;
}, Ne = function(e, t) {
  if (e.innerHTML = "", t.style) {
    const n = t.style;
    for (const o in n)
      e.style[o] = n[o];
  }
  if (t.dangerouslySetInnerHTML) {
    e.innerHTML = t.dangerouslySetInnerHTML;
    return;
  }
  if (t.image) {
    const n = t.image;
    if (n.url && n.width && n.height) {
      const o = _.createElement("img");
      o.src = this.imageProxy ? this.imageProxy(n.url) : n.url, o.style.width = n.width + "px", o.style.height = n.height + "px", n.fit && (o.style.objectFit = n.fit), e.appendChild(o), e.image = o;
    }
  } else
    e.image && (e.image = void 0);
  {
    const n = _.createElement("span");
    n.className = "text", this.markdown ? n.innerHTML = this.markdown(t.topic, t) : n.textContent = t.topic, e.appendChild(n), e.text = n;
  }
  if (t.hyperLink) {
    const n = _.createElement("a");
    n.className = "hyper-link", n.target = "_blank", n.innerText = "↗", n.href = t.hyperLink, e.appendChild(n), e.link = n;
  } else
    e.link && (e.link = void 0);
  if (t.icons && t.icons.length) {
    const n = _.createElement("span");
    n.className = "icons", n.innerHTML = t.icons.map((o) => `<span>${pe(o)}</span>`).join(""), e.appendChild(n), e.icons = n;
  } else
    e.icons && (e.icons = void 0);
  if (t.tags && t.tags.length) {
    const n = _.createElement("div");
    n.className = "tags", t.tags.forEach((o) => {
      const s = _.createElement("span");
      typeof o == "string" ? s.textContent = o : (s.textContent = o.text, o.className && (s.className = o.className), o.style && Object.assign(s.style, o.style)), n.appendChild(s);
    }), e.appendChild(n), e.tags = n;
  } else
    e.tags && (e.tags = void 0);
}, Tt = function(e, t) {
  const n = _.createElement("me-wrapper"), { p: o, tpc: s } = this.createParent(e);
  if (n.appendChild(o), !t && e.children && e.children.length > 0) {
    const i = ke(e.expanded);
    if (o.appendChild(i), e.expanded !== !1) {
      const c = _t(this, e.children);
      n.appendChild(c);
    }
  }
  return { grp: n, top: o, tpc: s };
}, Lt = function(e) {
  const t = _.createElement("me-parent"), n = this.createTopic(e);
  return Ne.call(this, n, e), t.appendChild(n), { p: t, tpc: n };
}, At = function(e) {
  const t = _.createElement("me-children");
  return t.append(...e), t;
}, Mt = function(e) {
  const t = _.createElement("me-tpc");
  return t.nodeObj = e, t.dataset.nodeid = "me" + e.id, t.draggable = this.draggable, t;
};
function Ze(e) {
  const t = _.createRange();
  t.selectNodeContents(e);
  const n = window.getSelection();
  n && (n.removeAllRanges(), n.addRange(t));
}
const Dt = function(e) {
  if (!e)
    return;
  const t = _.createElement("div"), n = e.nodeObj, o = n.topic, { offsetLeft: s, offsetTop: i } = O(this.nodes, e);
  this.nodes.appendChild(t), t.id = "input-box", t.textContent = o, t.contentEditable = "plaintext-only", t.spellcheck = !1;
  const c = getComputedStyle(e);
  t.style.cssText = `
  left: ${s}px;
  top: ${i}px;
  min-width:${e.offsetWidth - 8}px;
  color:${c.color};
  padding:${c.padding};
  margin:${c.margin}; 
  background-color:${c.backgroundColor !== "rgba(0, 0, 0, 0)" && c.backgroundColor};
  border: ${c.border};
  border-radius:${c.borderRadius}; `, this.direction === 0 && (t.style.right = "0"), Ze(t), this.bus.fire("operation", {
    name: "beginEdit",
    obj: e.nodeObj
  }), t.addEventListener("keydown", (r) => {
    r.stopPropagation();
    const l = r.key;
    if (l === "Enter" || l === "Tab") {
      if (r.shiftKey)
        return;
      r.preventDefault(), t.blur(), this.container.focus();
    }
  }), t.addEventListener("blur", () => {
    var l;
    if (!t)
      return;
    t.remove();
    const r = ((l = t.textContent) == null ? void 0 : l.trim()) || "";
    r === o || r === "" || (n.topic = r, this.markdown ? e.text.innerHTML = this.markdown(n.topic, n) : e.text.textContent = r, this.linkDiv(), this.bus.fire("operation", {
      name: "finishEdit",
      obj: n,
      origin: o
    }));
  });
}, ke = function(e) {
  const t = _.createElement("me-epd");
  return t.expanded = e !== !1, t.className = e !== !1 ? "minus" : "", t;
}, q = document, D = "http://www.w3.org/2000/svg", he = function(e) {
  const t = e.clientWidth, n = e.clientHeight, o = e.dataset, s = Number(o.x), i = Number(o.y), c = o.anchor;
  let r = s;
  c === "middle" ? r = s - t / 2 : c === "end" && (r = s - t), e.style.left = `${r}px`, e.style.top = `${i - n / 2}px`, e.style.visibility = "visible";
}, me = function(e, t, n, o) {
  const { anchor: s = "middle", color: i, dataType: c, svgId: r } = o, l = document.createElement("div");
  l.className = "svg-label", l.style.color = i || "#666";
  const d = "label-" + r;
  return l.id = d, l.innerHTML = e, l.dataset.type = c, l.dataset.svgId = r, l.dataset.x = t.toString(), l.dataset.y = n.toString(), l.dataset.anchor = s, l;
}, Qe = function(e, t, n) {
  const o = q.createElementNS(D, "path");
  return k(o, {
    d: e,
    stroke: t || "#666",
    fill: "none",
    "stroke-width": n
  }), o;
}, J = function(e) {
  const t = q.createElementNS(D, "svg");
  return t.setAttribute("class", e), t.setAttribute("overflow", "visible"), t;
}, Oe = function() {
  const e = q.createElementNS(D, "line");
  return e.setAttribute("stroke", "#4dc4ff"), e.setAttribute("fill", "none"), e.setAttribute("stroke-width", "2"), e.setAttribute("opacity", "0.45"), e;
}, Pt = function(e, t, n, o) {
  const s = q.createElementNS(D, "g");
  return [
    {
      name: "line",
      d: e
    },
    {
      name: "arrow1",
      d: t
    },
    {
      name: "arrow2",
      d: n
    }
  ].forEach((c, r) => {
    const l = c.d, d = q.createElementNS(D, "path"), f = {
      d: l,
      stroke: (o == null ? void 0 : o.stroke) || "rgb(227, 125, 116)",
      fill: "none",
      "stroke-linecap": (o == null ? void 0 : o.strokeLinecap) || "cap",
      "stroke-width": String((o == null ? void 0 : o.strokeWidth) || "2")
    };
    (o == null ? void 0 : o.opacity) !== void 0 && (f.opacity = String(o.opacity)), k(d, f), r === 0 && d.setAttribute("stroke-dasharray", (o == null ? void 0 : o.strokeDasharray) || "6,4");
    const u = q.createElementNS(D, "path");
    k(u, {
      d: l,
      stroke: "transparent",
      fill: "none",
      "stroke-width": "15"
    }), s.appendChild(u), s.appendChild(d), s[c.name] = d;
  }), s;
}, et = function(e, t, n) {
  if (!t)
    return;
  const o = n.label, s = t.cloneNode(!0);
  e.nodes.appendChild(s), s.id = "input-box", s.textContent = o, s.contentEditable = "plaintext-only", s.spellcheck = !1, s.style.cssText = `
    left:${t.style.left};
    top:${t.style.top}; 
    max-width: 200px;
  `, Ze(s), e.scrollIntoView(s), s.addEventListener("keydown", (i) => {
    i.stopPropagation();
    const c = i.key;
    if (c === "Enter" || c === "Tab") {
      if (i.shiftKey)
        return;
      i.preventDefault(), s.blur(), e.container.focus();
    }
  }), s.addEventListener("blur", () => {
    var c;
    if (!s)
      return;
    const i = ((c = s.textContent) == null ? void 0 : c.trim()) || "";
    i === "" ? n.label = o : n.label = i, s.remove(), i !== o && (t.textContent = n.label, he(t), "parent" in n ? e.bus.fire("operation", {
      name: "finishEditSummary",
      obj: n
    }) : e.bus.fire("operation", {
      name: "finishEditArrowLabel",
      obj: n
    }));
  });
}, $t = function(e) {
  const t = this.map.querySelector("me-root"), n = t.offsetTop, o = t.offsetLeft, s = t.offsetWidth, i = t.offsetHeight, c = this.map.querySelectorAll("me-main > me-wrapper");
  this.lines.innerHTML = "";
  for (let r = 0; r < c.length; r++) {
    const l = c[r], d = l.querySelector("me-tpc"), { offsetLeft: f, offsetTop: u } = O(this.nodes, d), g = d.offsetWidth, b = d.offsetHeight, p = l.parentNode.className, m = this.generateMainBranch({ pT: n, pL: o, pW: s, pH: i, cT: u, cL: f, cW: g, cH: b, direction: p, containerHeight: this.nodes.offsetHeight }), a = this.theme.palette, h = d.nodeObj.branchColor || a[r % a.length];
    if (d.style.borderColor = h, this.lines.appendChild(Qe(m, h, "3")), e && e !== l)
      continue;
    const v = J("subLines"), w = l.lastChild;
    w.tagName === "svg" && w.remove(), l.appendChild(v), tt(this, v, h, l, p, !0);
  }
  this.labelContainer.innerHTML = "", this.renderArrow(), this.renderSummary(), this.bus.fire("linkDiv");
}, tt = function(e, t, n, o, s, i) {
  const c = o.firstChild, r = o.children[1].children;
  if (r.length === 0)
    return;
  const l = c.offsetTop, d = c.offsetLeft, f = c.offsetWidth, u = c.offsetHeight;
  for (let g = 0; g < r.length; g++) {
    const b = r[g], p = b.firstChild, m = p.offsetTop, a = p.offsetLeft, h = p.offsetWidth, v = p.offsetHeight, w = p.firstChild.nodeObj.branchColor || n, C = e.generateSubBranch({ pT: l, pL: d, pW: f, pH: u, cT: m, cL: a, cW: h, cH: v, direction: s, isFirst: i });
    t.appendChild(Qe(C, w, "2"));
    const S = p.children[1];
    if (S) {
      if (!S.expanded)
        continue;
    } else
      continue;
    tt(e, t, w, b, s);
  }
}, je = {
  addChild: "插入子节点",
  addParent: "插入父节点",
  addSibling: "插入同级节点",
  removeNode: "删除节点",
  focus: "专注",
  cancelFocus: "取消专注",
  moveUp: "上移",
  moveDown: "下移",
  link: "连接",
  linkBidirectional: "双向连接",
  clickTips: "请点击目标节点",
  summary: "摘要"
}, He = {
  cn: je,
  zh_CN: je,
  zh_TW: {
    addChild: "插入子節點",
    addParent: "插入父節點",
    addSibling: "插入同級節點",
    removeNode: "刪除節點",
    focus: "專注",
    cancelFocus: "取消專注",
    moveUp: "上移",
    moveDown: "下移",
    link: "連接",
    linkBidirectional: "雙向連接",
    clickTips: "請點擊目標節點",
    summary: "摘要"
  },
  en: {
    addChild: "Add child",
    addParent: "Add parent",
    addSibling: "Add sibling",
    removeNode: "Remove node",
    focus: "Focus Mode",
    cancelFocus: "Cancel Focus Mode",
    moveUp: "Move up",
    moveDown: "Move down",
    link: "Link",
    linkBidirectional: "Bidirectional Link",
    clickTips: "Please click the target node",
    summary: "Summary"
  },
  ru: {
    addChild: "Добавить дочерний элемент",
    addParent: "Добавить родительский элемент",
    addSibling: "Добавить на этом уровне",
    removeNode: "Удалить узел",
    focus: "Режим фокусировки",
    cancelFocus: "Отменить режим фокусировки",
    moveUp: "Поднять выше",
    moveDown: "Опустить ниже",
    link: "Ссылка",
    linkBidirectional: "Двунаправленная ссылка",
    clickTips: "Пожалуйста, нажмите на целевой узел",
    summary: "Описание"
  },
  ja: {
    addChild: "子ノードを追加する",
    addParent: "親ノードを追加します",
    addSibling: "兄弟ノードを追加する",
    removeNode: "ノードを削除",
    focus: "集中",
    cancelFocus: "集中解除",
    moveUp: "上へ移動",
    moveDown: "下へ移動",
    link: "コネクト",
    linkBidirectional: "双方向リンク",
    clickTips: "ターゲットノードをクリックしてください",
    summary: "概要"
  },
  pt: {
    addChild: "Adicionar item filho",
    addParent: "Adicionar item pai",
    addSibling: "Adicionar item irmao",
    removeNode: "Remover item",
    focus: "Modo Foco",
    cancelFocus: "Cancelar Modo Foco",
    moveUp: "Mover para cima",
    moveDown: "Mover para baixo",
    link: "Link",
    linkBidirectional: "Link bidirecional",
    clickTips: "Favor clicar no item alvo",
    summary: "Resumo"
  },
  it: {
    addChild: "Aggiungi figlio",
    addParent: "Aggiungi genitore",
    addSibling: "Aggiungi fratello",
    removeNode: "Rimuovi nodo",
    focus: "Modalità Focus",
    cancelFocus: "Annulla Modalità Focus",
    moveUp: "Sposta su",
    moveDown: "Sposta giù",
    link: "Collega",
    linkBidirectional: "Collegamento bidirezionale",
    clickTips: "Si prega di fare clic sul nodo di destinazione",
    summary: "Unisci nodi"
  },
  es: {
    addChild: "Agregar hijo",
    addParent: "Agregar padre",
    addSibling: "Agregar hermano",
    removeNode: "Eliminar nodo",
    focus: "Modo Enfoque",
    cancelFocus: "Cancelar Modo Enfoque",
    moveUp: "Mover hacia arriba",
    moveDown: "Mover hacia abajo",
    link: "Enlace",
    linkBidirectional: "Enlace bidireccional",
    clickTips: "Por favor haga clic en el nodo de destino",
    summary: "Resumen"
  },
  fr: {
    addChild: "Ajout enfant",
    addParent: "Ajout parent",
    addSibling: "Ajout voisin",
    removeNode: "Supprimer",
    focus: "Cibler",
    cancelFocus: "Retour",
    moveUp: "Monter",
    moveDown: "Descendre",
    link: "Lier",
    linkBidirectional: "Lien bidirectionnel",
    clickTips: "Cliquer sur le noeud cible",
    summary: "Annoter"
  },
  ko: {
    addChild: "자식 추가",
    addParent: "부모 추가",
    addSibling: "형제 추가",
    removeNode: "노드 삭제",
    focus: "포커스 모드",
    cancelFocus: "포커스 모드 취소",
    moveUp: "위로 이동",
    moveDown: "아래로 이동",
    link: "연결",
    linkBidirectional: "양방향 연결",
    clickTips: "대상 노드를 클릭하십시오",
    summary: "요약"
  }
};
function Ot(e, t) {
  t = t === !0 ? {
    focus: !0,
    link: !0
  } : t;
  const n = (y) => {
    const x = document.createElement("div");
    return x.innerText = y, x.className = "tips", x;
  }, o = (y, x, E) => {
    const N = document.createElement("li");
    return N.id = y, N.innerHTML = `<span>${pe(x)}</span><span ${E ? 'class="key"' : ""}>${pe(E)}</span>`, N;
  }, s = He[e.locale] ? e.locale : "en", i = He[s], c = o("cm-add_child", i.addChild, "Tab"), r = o("cm-add_parent", i.addParent, "Ctrl + Enter"), l = o("cm-add_sibling", i.addSibling, "Enter"), d = o("cm-remove_child", i.removeNode, "Delete"), f = o("cm-fucus", i.focus, ""), u = o("cm-unfucus", i.cancelFocus, ""), g = o("cm-up", i.moveUp, "PgUp"), b = o("cm-down", i.moveDown, "Pgdn"), p = o("cm-link", i.link, ""), m = o("cm-link-bidirectional", i.linkBidirectional, ""), a = o("cm-summary", i.summary, ""), h = document.createElement("ul");
  if (h.className = "menu-list", h.appendChild(c), h.appendChild(r), h.appendChild(l), h.appendChild(d), t.focus && (h.appendChild(f), h.appendChild(u)), h.appendChild(g), h.appendChild(b), h.appendChild(a), t.link && (h.appendChild(p), h.appendChild(m)), t && t.extend)
    for (let y = 0; y < t.extend.length; y++) {
      const x = t.extend[y], E = o(x.name, x.name, x.key || "");
      h.appendChild(E), E.onclick = (N) => {
        x.onclick(N);
      };
    }
  const v = document.createElement("div");
  v.className = "context-menu", v.appendChild(h), v.hidden = !0, e.container.append(v);
  let w = !0;
  const C = (y) => {
    const x = y.target;
    if (ge(x)) {
      x.parentElement.tagName === "ME-ROOT" ? w = !0 : w = !1, w ? (f.className = "disabled", g.className = "disabled", b.className = "disabled", r.className = "disabled", l.className = "disabled", d.className = "disabled") : (f.className = "", g.className = "", b.className = "", r.className = "", l.className = "", d.className = ""), v.hidden = !1, h.style.top = "", h.style.bottom = "", h.style.left = "", h.style.right = "";
      const E = h.getBoundingClientRect(), N = h.offsetHeight, L = h.offsetWidth, A = y.clientY - E.top, V = y.clientX - E.left;
      N + A > window.innerHeight ? (h.style.top = "", h.style.bottom = "0px") : (h.style.bottom = "", h.style.top = A + 15 + "px"), L + V > window.innerWidth ? (h.style.left = "", h.style.right = "0px") : (h.style.right = "", h.style.left = V + 10 + "px");
    }
  };
  e.bus.addListener("showContextMenu", C), v.onclick = (y) => {
    y.target === v && (v.hidden = !0);
  }, c.onclick = () => {
    e.addChild(), v.hidden = !0;
  }, r.onclick = () => {
    e.insertParent(), v.hidden = !0;
  }, l.onclick = () => {
    w || (e.insertSibling("after"), v.hidden = !0);
  }, d.onclick = () => {
    w || (e.removeNodes(e.currentNodes || []), v.hidden = !0);
  }, f.onclick = () => {
    w || (e.focusNode(e.currentNode), v.hidden = !0);
  }, u.onclick = () => {
    e.cancelFocus(), v.hidden = !0;
  }, g.onclick = () => {
    w || (e.moveUpNode(), v.hidden = !0);
  }, b.onclick = () => {
    w || (e.moveDownNode(), v.hidden = !0);
  };
  const S = (y) => {
    v.hidden = !0;
    const x = e.currentNode, E = n(i.clickTips);
    e.container.appendChild(E), e.map.addEventListener(
      "click",
      (N) => {
        N.preventDefault(), E.remove();
        const L = N.target;
        (L.parentElement.tagName === "ME-PARENT" || L.parentElement.tagName === "ME-ROOT") && e.createArrow(x, L, y);
      },
      {
        once: !0
      }
    );
  };
  return p.onclick = () => S(), m.onclick = () => S({ bidirectional: !0 }), a.onclick = () => {
    v.hidden = !0, e.createSummary(), e.unselectNodes(e.currentNodes);
  }, () => {
    c.onclick = null, r.onclick = null, l.onclick = null, d.onclick = null, f.onclick = null, u.onclick = null, g.onclick = null, b.onclick = null, p.onclick = null, a.onclick = null, v.onclick = null, e.container.oncontextmenu = null;
  };
}
const ve = document, jt = function(e, t) {
  if (!t)
    return be(e), e;
  let n = e.querySelector(".insert-preview");
  const o = `insert-preview ${t} show`;
  return n || (n = ve.createElement("div"), e.appendChild(n)), n.className = o, e;
}, be = function(e) {
  if (!e)
    return;
  const t = e.querySelectorAll(".insert-preview");
  for (const n of t || [])
    n.remove();
}, Be = function(e, t) {
  for (const n of t) {
    const o = n.parentElement.parentElement.contains(e);
    if (!(e && e.tagName === "ME-TPC" && e !== n && !o && e.nodeObj.parent))
      return !1;
  }
  return !0;
}, Ht = function(e) {
  const t = document.createElement("div");
  return t.className = "mind-elixir-ghost", e.container.appendChild(t), t;
};
class Bt {
  constructor(t) {
    X(this, "mind");
    X(this, "isMoving", !1);
    X(this, "interval", null);
    X(this, "speed", 20);
    this.mind = t;
  }
  move(t, n) {
    this.isMoving || (this.isMoving = !0, this.interval = setInterval(() => {
      this.mind.move(t * this.speed * this.mind.scaleVal, n * this.speed * this.mind.scaleVal);
    }, 100));
  }
  stop() {
    this.isMoving = !1, clearInterval(this.interval);
  }
}
function Rt(e) {
  let t = null, n = null;
  const o = Ht(e), s = new Bt(e), i = (d) => {
    if (e.spacePressed) {
      d.preventDefault();
      return;
    }
    e.selection.cancel();
    const f = d.target;
    if ((f == null ? void 0 : f.tagName) !== "ME-TPC") {
      d.preventDefault();
      return;
    }
    let u = e.currentNodes;
    u != null && u.includes(f) || (e.selectNode(f), u = e.currentNodes), e.dragged = u, u.length > 1 ? o.innerHTML = u.length + "" : o.innerHTML = f.innerHTML;
    for (const g of u)
      g.parentElement.parentElement.style.opacity = "0.5";
    d.dataTransfer.setDragImage(o, 0, 0), d.dataTransfer.dropEffect = "move", e.dragMoveHelper.clear();
  }, c = (d) => {
    const { dragged: f } = e;
    if (!f)
      return;
    s.stop();
    for (const g of f)
      g.parentElement.parentElement.style.opacity = "1";
    const u = d.target;
    u.style.opacity = "", n && (be(n), t === "before" ? e.moveNodeBefore(f, n) : t === "after" ? e.moveNodeAfter(f, n) : t === "in" && e.moveNodeIn(f, n), e.dragged = null, o.innerHTML = "");
  }, r = (d) => {
    d.preventDefault();
    const f = 12 * e.scaleVal, { dragged: u } = e;
    if (!u)
      return;
    const g = e.container.getBoundingClientRect();
    d.clientX < g.x + 50 ? s.move(1, 0) : d.clientX > g.x + g.width - 50 ? s.move(-1, 0) : d.clientY < g.y + 50 ? s.move(0, 1) : d.clientY > g.y + g.height - 50 ? s.move(0, -1) : s.stop(), be(n);
    const b = ve.elementFromPoint(d.clientX, d.clientY - f);
    if (Be(b, u)) {
      n = b;
      const p = b.getBoundingClientRect(), m = p.y;
      d.clientY > m + p.height ? t = "after" : t = "in";
    } else {
      const p = ve.elementFromPoint(d.clientX, d.clientY + f), m = p.getBoundingClientRect();
      if (Be(p, u)) {
        n = p;
        const a = m.y;
        d.clientY < a ? t = "before" : t = "in";
      } else
        t = n = null;
    }
    n && jt(n, t);
  };
  return Se([
    { dom: e.map, evt: "dragstart", func: i },
    { dom: e.map, evt: "dragend", func: c },
    { dom: e.map, evt: "dragover", func: r }
  ]);
}
const Ft = function(e) {
  return ["createSummary", "removeSummary", "finishEditSummary"].includes(e.name) ? {
    type: "summary",
    value: e.obj.id
  } : ["createArrow", "removeArrow", "finishEditArrowLabel"].includes(e.name) ? {
    type: "arrow",
    value: e.obj.id
  } : ["removeNodes", "copyNodes", "moveNodeBefore", "moveNodeAfter", "moveNodeIn"].includes(e.name) ? {
    type: "nodes",
    value: e.objs.map((t) => t.id)
  } : {
    type: "nodes",
    value: [e.obj.id]
  };
};
function It(e) {
  let t = [], n = -1, o = e.getData(), s = [];
  e.undo = function() {
    if (n > -1) {
      const l = t[n];
      o = l.prev, e.refresh(l.prev);
      try {
        l.currentTarget.type === "nodes" && (l.operation === "removeNodes" ? e.selectNodes(l.currentTarget.value.map((d) => this.findEle(d))) : e.selectNodes(l.currentSelected.map((d) => this.findEle(d))));
      } catch {
      } finally {
        n--;
      }
    }
  }, e.redo = function() {
    if (n < t.length - 1) {
      n++;
      const l = t[n];
      o = l.next, e.refresh(l.next);
      try {
        l.currentTarget.type === "nodes" && (l.operation === "removeNodes" ? e.selectNodes(l.currentSelected.map((d) => this.findEle(d))) : e.selectNodes(l.currentTarget.value.map((d) => this.findEle(d))));
      } catch {
      }
    }
  };
  const i = function(l) {
    if (l.name === "beginEdit")
      return;
    t = t.slice(0, n + 1);
    const d = e.getData(), f = {
      prev: o,
      operation: l.name,
      currentSelected: s.map((u) => u.id),
      currentTarget: Ft(l),
      next: d
    };
    t.push(f), o = d, n = t.length - 1;
  }, c = function(l) {
    (l.metaKey || l.ctrlKey) && (l.shiftKey && l.key === "Z" || l.key === "y") ? e.redo() : (l.metaKey || l.ctrlKey) && l.key === "z" && e.undo();
  }, r = function() {
    s = e.currentNodes.map((l) => l.nodeObj);
  };
  return e.bus.addListener("operation", i), e.bus.addListener("selectNodes", r), e.container.addEventListener("keydown", c), () => {
    e.bus.removeListener("operation", i), e.bus.removeListener("selectNodes", r), e.container.removeEventListener("keydown", c);
  };
}
const Wt = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169394918" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2021" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M851.91168 328.45312c-59.97056 0-108.6208 48.47104-108.91264 108.36992l-137.92768 38.4a109.14304 109.14304 0 0 0-63.46752-46.58688l1.39264-137.11872c47.29344-11.86816 82.31936-54.66624 82.31936-105.64096 0-60.15488-48.76288-108.91776-108.91776-108.91776s-108.91776 48.76288-108.91776 108.91776c0 49.18784 32.60928 90.75712 77.38368 104.27392l-1.41312 138.87488a109.19936 109.19936 0 0 0-63.50336 48.55808l-138.93632-39.48544 0.01024-0.72704c0-60.15488-48.76288-108.91776-108.91776-108.91776s-108.91776 48.75776-108.91776 108.91776c0 60.15488 48.76288 108.91264 108.91776 108.91264 39.3984 0 73.91232-20.92032 93.03552-52.2496l139.19232 39.552-0.00512 0.2304c0 25.8304 9.00096 49.5616 24.02816 68.23424l-90.14272 132.63872a108.7488 108.7488 0 0 0-34.2528-5.504c-60.15488 0-108.91776 48.768-108.91776 108.91776 0 60.16 48.76288 108.91776 108.91776 108.91776 60.16 0 108.92288-48.75776 108.92288-108.91776 0-27.14624-9.9328-51.968-26.36288-71.04l89.04704-131.03104a108.544 108.544 0 0 0 37.6832 6.70208 108.672 108.672 0 0 0 36.48512-6.272l93.13792 132.57216a108.48256 108.48256 0 0 0-24.69888 69.0688c0 60.16 48.768 108.92288 108.91776 108.92288 60.16 0 108.91776-48.76288 108.91776-108.92288 0-60.14976-48.75776-108.91776-108.91776-108.91776a108.80512 108.80512 0 0 0-36.69504 6.3488l-93.07136-132.48a108.48768 108.48768 0 0 0 24.79616-72.22784l136.09984-37.888c18.99008 31.93856 53.84192 53.3504 93.69088 53.3504 60.16 0 108.92288-48.75776 108.92288-108.91264-0.00512-60.15488-48.77312-108.92288-108.92288-108.92288z" p-id="2022"></path></svg>', Kt = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169375313" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1775" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M639 463.30000001L639 285.1c0-36.90000001-26.4-68.5-61.3-68.5l-150.2 0c-1.5 0-3 0.1-4.5 0.3-10.2-38.7-45.5-67.3-87.5-67.3-50 0-90.5 40.5-90.5 90.5s40.5 90.5 90.5 90.5c42 0 77.3-28.6 87.5-67.39999999 1.4 0.3 2.9 0.4 4.5 0.39999999L577.7 263.6c6.8 0 14.3 8.9 14.3 21.49999999l0 427.00000001c0 12.7-7.40000001 21.5-14.30000001 21.5l-150.19999999 0c-1.5 0-3 0.2-4.5 0.4-10.2-38.8-45.5-67.3-87.5-67.3-50 0-90.5 40.5-90.5 90.4 0 49.9 40.5 90.6 90.5 90.59999999 42 0 77.3-28.6 87.5-67.39999999 1.4 0.2 2.9 0.4 4.49999999 0.4L577.7 780.7c34.80000001 0 61.3-31.6 61.3-68.50000001L639 510.3l79.1 0c10.4 38.5 45.49999999 67 87.4 67 50 0 90.5-40.5 90.5-90.5s-40.5-90.5-90.5-90.5c-41.79999999 0-77.00000001 28.4-87.4 67L639 463.30000001z" fill="currentColor" p-id="1776"></path></svg>', Gt = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169667709" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3037" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M385 560.69999999L385 738.9c0 36.90000001 26.4 68.5 61.3 68.5l150.2 0c1.5 0 3-0.1 4.5-0.3 10.2 38.7 45.5 67.3 87.5 67.3 50 0 90.5-40.5 90.5-90.5s-40.5-90.5-90.5-90.5c-42 0-77.3 28.6-87.5 67.39999999-1.4-0.3-2.9-0.4-4.5-0.39999999L446.3 760.4c-6.8 0-14.3-8.9-14.3-21.49999999l0-427.00000001c0-12.7 7.40000001-21.5 14.30000001-21.5l150.19999999 0c1.5 0 3-0.2 4.5-0.4 10.2 38.8 45.5 67.3 87.5 67.3 50 0 90.5-40.5 90.5-90.4 0-49.9-40.5-90.6-90.5-90.59999999-42 0-77.3 28.6-87.5 67.39999999-1.4-0.2-2.9-0.4-4.49999999-0.4L446.3 243.3c-34.80000001 0-61.3 31.6-61.3 68.50000001L385 513.7l-79.1 0c-10.4-38.5-45.49999999-67-87.4-67-50 0-90.5 40.5-90.5 90.5s40.5 90.5 90.5 90.5c41.79999999 0 77.00000001-28.4 87.4-67L385 560.69999999z" fill="currentColor" p-id="3038"></path></svg>', Yt = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169402629" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2170" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M639.328 416c8.032 0 16.096-3.008 22.304-9.056l202.624-197.184-0.8 143.808c-0.096 17.696 14.144 32.096 31.808 32.192 0.064 0 0.128 0 0.192 0 17.6 0 31.904-14.208 32-31.808l1.248-222.208c0-0.672-0.352-1.248-0.384-1.92 0.032-0.512 0.288-0.896 0.288-1.408 0.032-17.664-14.272-32-31.968-32.032L671.552 96l-0.032 0c-17.664 0-31.968 14.304-32 31.968C639.488 145.632 653.824 160 671.488 160l151.872 0.224-206.368 200.8c-12.672 12.32-12.928 32.608-0.64 45.248C622.656 412.736 630.976 416 639.328 416z" p-id="2171"></path><path d="M896.032 639.552 896.032 639.552c-17.696 0-32 14.304-32.032 31.968l-0.224 151.872-200.832-206.4c-12.32-12.64-32.576-12.96-45.248-0.64-12.672 12.352-12.928 32.608-0.64 45.248l197.184 202.624-143.808-0.8c-0.064 0-0.128 0-0.192 0-17.6 0-31.904 14.208-32 31.808-0.096 17.696 14.144 32.096 31.808 32.192l222.24 1.248c0.064 0 0.128 0 0.192 0 0.64 0 1.12-0.32 1.76-0.352 0.512 0.032 0.896 0.288 1.408 0.288l0.032 0c17.664 0 31.968-14.304 32-31.968L928 671.584C928.032 653.952 913.728 639.584 896.032 639.552z" p-id="2172"></path><path d="M209.76 159.744l143.808 0.8c0.064 0 0.128 0 0.192 0 17.6 0 31.904-14.208 32-31.808 0.096-17.696-14.144-32.096-31.808-32.192L131.68 95.328c-0.064 0-0.128 0-0.192 0-0.672 0-1.248 0.352-1.888 0.384-0.448 0-0.8-0.256-1.248-0.256 0 0-0.032 0-0.032 0-17.664 0-31.968 14.304-32 31.968L96 352.448c-0.032 17.664 14.272 32 31.968 32.032 0 0 0.032 0 0.032 0 17.664 0 31.968-14.304 32-31.968l0.224-151.936 200.832 206.4c6.272 6.464 14.624 9.696 22.944 9.696 8.032 0 16.096-3.008 22.304-9.056 12.672-12.32 12.96-32.608 0.64-45.248L209.76 159.744z" p-id="2173"></path><path d="M362.368 617.056l-202.624 197.184 0.8-143.808c0.096-17.696-14.144-32.096-31.808-32.192-0.064 0-0.128 0-0.192 0-17.6 0-31.904 14.208-32 31.808l-1.248 222.24c0 0.704 0.352 1.312 0.384 2.016 0 0.448-0.256 0.832-0.256 1.312-0.032 17.664 14.272 32 31.968 32.032L352.448 928c0 0 0.032 0 0.032 0 17.664 0 31.968-14.304 32-31.968s-14.272-32-31.968-32.032l-151.936-0.224 206.4-200.832c12.672-12.352 12.96-32.608 0.64-45.248S375.008 604.704 362.368 617.056z" p-id="2174"></path></svg>', qt = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169573443" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2883" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M514.133333 488.533333m-106.666666 0a106.666667 106.666667 0 1 0 213.333333 0 106.666667 106.666667 0 1 0-213.333333 0Z" fill="currentColor" p-id="2884"></path><path d="M512 64C264.533333 64 64 264.533333 64 512c0 236.8 183.466667 428.8 416 445.866667v-134.4c-53.333333-59.733333-200.533333-230.4-200.533333-334.933334 0-130.133333 104.533333-234.666667 234.666666-234.666666s234.666667 104.533333 234.666667 234.666666c0 61.866667-49.066667 153.6-145.066667 270.933334l-59.733333 68.266666V960C776.533333 942.933333 960 748.8 960 512c0-247.466667-200.533333-448-448-448z" fill="currentColor" p-id="2885"></path></svg>', zt = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169419447" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2480" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M863.328 482.56l-317.344-1.12L545.984 162.816c0-17.664-14.336-32-32-32s-32 14.336-32 32l0 318.4L159.616 480.064c-0.032 0-0.064 0-0.096 0-17.632 0-31.936 14.24-32 31.904C127.424 529.632 141.728 544 159.392 544.064l322.592 1.152 0 319.168c0 17.696 14.336 32 32 32s32-14.304 32-32l0-318.944 317.088 1.12c0.064 0 0.096 0 0.128 0 17.632 0 31.936-14.24 32-31.904C895.264 496.992 880.96 482.624 863.328 482.56z" p-id="2481"></path></svg>', Vt = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"><svg t="1750169426515" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2730" xmlns:xlink="http://www.w3.org/1999/xlink" width="200" height="200"><path d="M863.744 544 163.424 544c-17.664 0-32-14.336-32-32s14.336-32 32-32l700.32 0c17.696 0 32 14.336 32 32S881.44 544 863.744 544z" p-id="2731"></path></svg>';
const Ut = {
  side: Wt,
  left: Kt,
  right: Gt,
  full: Yt,
  living: qt,
  zoomin: zt,
  zoomout: Vt
}, F = (e, t) => {
  const n = document.createElement("span");
  return n.id = e, n.innerHTML = Ut[t], n;
};
function Xt(e) {
  const t = document.createElement("div"), n = F("fullscreen", "full"), o = F("toCenter", "living"), s = F("zoomout", "zoomout"), i = F("zoomin", "zoomin"), c = document.createElement("span");
  return c.innerText = "100%", t.appendChild(n), t.appendChild(o), t.appendChild(s), t.appendChild(i), t.className = "mind-elixir-toolbar rb", n.onclick = () => {
    document.fullscreenElement === e.el ? document.exitFullscreen() : e.el.requestFullscreen();
  }, o.onclick = () => {
    e.toCenter();
  }, s.onclick = () => {
    e.scale(e.scaleVal - e.scaleSensitivity);
  }, i.onclick = () => {
    e.scale(e.scaleVal + e.scaleSensitivity);
  }, t;
}
function Jt(e) {
  const t = document.createElement("div"), n = F("tbltl", "left"), o = F("tbltr", "right"), s = F("tblts", "side");
  return t.appendChild(n), t.appendChild(o), t.appendChild(s), t.className = "mind-elixir-toolbar lt", n.onclick = () => {
    e.initLeft();
  }, o.onclick = () => {
    e.initRight();
  }, s.onclick = () => {
    e.initSide();
  }, t;
}
function Zt(e) {
  e.container.append(Xt(e)), e.container.append(Jt(e));
}
/*! @viselect/vanilla v3.9.0 MIT | https://github.com/Simonwep/selection/tree/master/packages/vanilla */
class Qt {
  constructor() {
    this._listeners = /* @__PURE__ */ new Map(), this.on = this.addEventListener, this.off = this.removeEventListener, this.emit = this.dispatchEvent;
  }
  addEventListener(t, n) {
    const o = this._listeners.get(t) ?? /* @__PURE__ */ new Set();
    return this._listeners.set(t, o), o.add(n), this;
  }
  removeEventListener(t, n) {
    var o;
    return (o = this._listeners.get(t)) == null || o.delete(n), this;
  }
  dispatchEvent(t, ...n) {
    let o = !0;
    for (const s of this._listeners.get(t) ?? [])
      o = s(...n) !== !1 && o;
    return o;
  }
  unbindAllListeners() {
    this._listeners.clear();
  }
}
const Re = (e, t = "px") => typeof e == "number" ? e + t : e, j = ({ style: e }, t, n) => {
  if (typeof t == "object")
    for (const [o, s] of Object.entries(t))
      s !== void 0 && (e[o] = Re(s));
  else
    n !== void 0 && (e[t] = Re(n));
}, Fe = (e = 0, t = 0, n = 0, o = 0) => {
  const s = { x: e, y: t, width: n, height: o, top: t, left: e, right: e + n, bottom: t + o };
  return { ...s, toJSON: () => JSON.stringify(s) };
}, en = (e) => {
  let t, n = -1, o = !1;
  return {
    next: (...s) => {
      t = s, o || (o = !0, n = requestAnimationFrame(() => {
        e(...t), o = !1;
      }));
    },
    cancel: () => {
      cancelAnimationFrame(n), o = !1;
    }
  };
}, Ie = (e, t, n = "touch") => {
  switch (n) {
    case "center": {
      const o = t.left + t.width / 2, s = t.top + t.height / 2;
      return o >= e.left && o <= e.right && s >= e.top && s <= e.bottom;
    }
    case "cover":
      return t.left >= e.left && t.top >= e.top && t.right <= e.right && t.bottom <= e.bottom;
    case "touch":
      return e.right >= t.left && e.left <= t.right && e.bottom >= t.top && e.top <= t.bottom;
  }
}, tn = () => matchMedia("(hover: none), (pointer: coarse)").matches, nn = () => "safari" in window, ye = (e) => Array.isArray(e) ? e : [e], nt = (e) => (t, n, o, s = {}) => {
  (t instanceof HTMLCollection || t instanceof NodeList) && (t = Array.from(t)), n = ye(n), t = ye(t);
  for (const i of t)
    if (i)
      for (const c of n)
        i[e](c, o, { capture: !1, ...s });
}, H = nt("addEventListener"), M = nt("removeEventListener"), te = (e) => {
  var t;
  const { clientX: n, clientY: o, target: s } = ((t = e.touches) == null ? void 0 : t[0]) ?? e;
  return { x: n, y: o, target: s };
}, W = (e, t = document) => ye(e).map(
  (n) => typeof n == "string" ? Array.from(t.querySelectorAll(n)) : n instanceof Element ? n : null
).flat().filter(Boolean), on = (e, t) => t.some((n) => typeof n == "number" ? e.button === n : typeof n == "object" ? n.button !== e.button ? !1 : n.modifiers.every((o) => {
  switch (o) {
    case "alt":
      return e.altKey;
    case "ctrl":
      return e.ctrlKey || e.metaKey;
    case "shift":
      return e.shiftKey;
  }
}) : !1), { abs: R, max: We, min: Ke, ceil: Ge } = Math, Ye = (e = []) => ({
  stored: e,
  selected: [],
  touched: [],
  changed: { added: [], removed: [] }
}), ot = class extends Qt {
  constructor(t) {
    var n, o, s, i, c;
    super(), this._selection = Ye(), this._targetBoundaryScrolled = !0, this._selectables = [], this._areaLocation = { y1: 0, x2: 0, y2: 0, x1: 0 }, this._areaRect = Fe(), this._singleClick = !0, this._scrollAvailable = !0, this._scrollingActive = !1, this._scrollSpeed = { x: 0, y: 0 }, this._scrollDelta = { x: 0, y: 0 }, this._lastMousePosition = { x: 0, y: 0 }, this.enable = this._toggleStartEvents, this.disable = this._toggleStartEvents.bind(this, !1), this._options = {
      selectionAreaClass: "selection-area",
      selectionContainerClass: void 0,
      selectables: [],
      document: window.document,
      startAreas: ["html"],
      boundaries: ["html"],
      container: "body",
      ...t,
      behaviour: {
        overlap: "invert",
        intersect: "touch",
        triggers: [0],
        ...t.behaviour,
        startThreshold: (n = t.behaviour) != null && n.startThreshold ? typeof t.behaviour.startThreshold == "number" ? t.behaviour.startThreshold : { x: 10, y: 10, ...t.behaviour.startThreshold } : { x: 10, y: 10 },
        scrolling: {
          speedDivider: 10,
          manualSpeed: 750,
          ...(o = t.behaviour) == null ? void 0 : o.scrolling,
          startScrollMargins: {
            x: 0,
            y: 0,
            ...(i = (s = t.behaviour) == null ? void 0 : s.scrolling) == null ? void 0 : i.startScrollMargins
          }
        }
      },
      features: {
        range: !0,
        touch: !0,
        deselectOnBlur: !1,
        ...t.features,
        singleTap: {
          allow: !0,
          intersect: "native",
          ...(c = t.features) == null ? void 0 : c.singleTap
        }
      }
    };
    for (const f of Object.getOwnPropertyNames(Object.getPrototypeOf(this)))
      typeof this[f] == "function" && (this[f] = this[f].bind(this));
    const { document: r, selectionAreaClass: l, selectionContainerClass: d } = this._options;
    this._area = r.createElement("div"), this._clippingElement = r.createElement("div"), this._clippingElement.appendChild(this._area), this._area.classList.add(l), d && this._clippingElement.classList.add(d), j(this._area, {
      willChange: "top, left, bottom, right, width, height",
      top: 0,
      left: 0,
      position: "fixed"
    }), j(this._clippingElement, {
      overflow: "hidden",
      position: "fixed",
      transform: "translate3d(0, 0, 0)",
      // https://stackoverflow.com/a/38268846
      pointerEvents: "none",
      zIndex: "1"
    }), this._frame = en((f) => {
      this._recalculateSelectionAreaRect(), this._updateElementSelection(), this._emitEvent("move", f), this._redrawSelectionArea();
    }), this.enable();
  }
  _toggleStartEvents(t = !0) {
    const { document: n, features: o } = this._options, s = t ? H : M;
    s(n, "mousedown", this._onTapStart), o.touch && s(n, "touchstart", this._onTapStart, { passive: !1 });
  }
  _onTapStart(t, n = !1) {
    const { x: o, y: s, target: i } = te(t), { document: c, startAreas: r, boundaries: l, features: d, behaviour: f } = this._options, u = i.getBoundingClientRect();
    if (t instanceof MouseEvent && !on(t, f.triggers))
      return;
    const g = W(r, c), b = W(l, c);
    this._targetElement = b.find(
      (h) => Ie(h.getBoundingClientRect(), u)
    );
    const p = t.composedPath(), m = g.find((h) => p.includes(h));
    if (this._targetBoundary = b.find((h) => p.includes(h)), !this._targetElement || !m || !this._targetBoundary || !n && this._emitEvent("beforestart", t) === !1)
      return;
    this._areaLocation = { x1: o, y1: s, x2: 0, y2: 0 };
    const a = c.scrollingElement ?? c.body;
    this._scrollDelta = { x: a.scrollLeft, y: a.scrollTop }, this._singleClick = !0, this.clearSelection(!1, !0), H(c, ["touchmove", "mousemove"], this._delayedTapMove, { passive: !1 }), H(c, ["mouseup", "touchcancel", "touchend"], this._onTapStop), H(c, "scroll", this._onScroll), d.deselectOnBlur && (this._targetBoundaryScrolled = !1, H(this._targetBoundary, "scroll", this._onStartAreaScroll));
  }
  _onSingleTap(t) {
    const { singleTap: { intersect: n }, range: o } = this._options.features, s = te(t);
    let i;
    if (n === "native")
      i = s.target;
    else if (n === "touch") {
      this.resolveSelectables();
      const { x: r, y: l } = s;
      i = this._selectables.find((d) => {
        const { right: f, left: u, top: g, bottom: b } = d.getBoundingClientRect();
        return r < f && r > u && l < b && l > g;
      });
    }
    if (!i)
      return;
    for (this.resolveSelectables(); !this._selectables.includes(i); )
      if (i.parentElement)
        i = i.parentElement;
      else {
        this._targetBoundaryScrolled || this.clearSelection();
        return;
      }
    const { stored: c } = this._selection;
    if (this._emitEvent("start", t), t.shiftKey && o && this._latestElement) {
      const r = this._latestElement, [l, d] = r.compareDocumentPosition(i) & 4 ? [i, r] : [r, i], f = [...this._selectables.filter(
        (u) => u.compareDocumentPosition(l) & 4 && u.compareDocumentPosition(d) & 2
      ), l, d];
      this.select(f), this._latestElement = r;
    } else
      c.includes(i) && (c.length === 1 || t.ctrlKey || c.every((r) => this._selection.stored.includes(r))) ? this.deselect(i) : (this.select(i), this._latestElement = i);
  }
  _delayedTapMove(t) {
    const { container: n, document: o, behaviour: { startThreshold: s } } = this._options, { x1: i, y1: c } = this._areaLocation, { x: r, y: l } = te(t);
    if (
      // Single number for both coordinates
      typeof s == "number" && R(r + l - (i + c)) >= s || // Different x and y threshold
      typeof s == "object" && R(r - i) >= s.x || R(l - c) >= s.y
    ) {
      if (M(o, ["mousemove", "touchmove"], this._delayedTapMove, { passive: !1 }), this._emitEvent("beforedrag", t) === !1) {
        M(o, ["mouseup", "touchcancel", "touchend"], this._onTapStop);
        return;
      }
      H(o, ["mousemove", "touchmove"], this._onTapMove, { passive: !1 }), j(this._area, "display", "block"), W(n, o)[0].appendChild(this._clippingElement), this.resolveSelectables(), this._singleClick = !1, this._targetRect = this._targetElement.getBoundingClientRect(), this._scrollAvailable = this._targetElement.scrollHeight !== this._targetElement.clientHeight || this._targetElement.scrollWidth !== this._targetElement.clientWidth, this._scrollAvailable && (H(this._targetElement, "wheel", this._wheelScroll, { passive: !1 }), H(this._options.document, "keydown", this._keyboardScroll, { passive: !1 }), this._selectables = this._selectables.filter((d) => this._targetElement.contains(d))), this._setupSelectionArea(), this._emitEvent("start", t), this._onTapMove(t);
    }
    this._handleMoveEvent(t);
  }
  _setupSelectionArea() {
    const { _clippingElement: t, _targetElement: n, _area: o } = this, s = this._targetRect = n.getBoundingClientRect();
    this._scrollAvailable ? (j(t, {
      top: s.top,
      left: s.left,
      width: s.width,
      height: s.height
    }), j(o, {
      marginTop: -s.top,
      marginLeft: -s.left
    })) : (j(t, {
      top: 0,
      left: 0,
      width: "100%",
      height: "100%"
    }), j(o, {
      marginTop: 0,
      marginLeft: 0
    }));
  }
  _onTapMove(t) {
    const { _scrollSpeed: n, _areaLocation: o, _options: s, _frame: i } = this, { speedDivider: c } = s.behaviour.scrolling, r = this._targetElement, { x: l, y: d } = te(t);
    if (o.x2 = l, o.y2 = d, this._lastMousePosition.x = l, this._lastMousePosition.y = d, this._scrollAvailable && !this._scrollingActive && (n.y || n.x)) {
      this._scrollingActive = !0;
      const f = () => {
        if (!n.x && !n.y) {
          this._scrollingActive = !1;
          return;
        }
        const { scrollTop: u, scrollLeft: g } = r;
        n.y && (r.scrollTop += Ge(n.y / c), o.y1 -= r.scrollTop - u), n.x && (r.scrollLeft += Ge(n.x / c), o.x1 -= r.scrollLeft - g), i.next(t), requestAnimationFrame(f);
      };
      requestAnimationFrame(f);
    } else
      i.next(t);
    this._handleMoveEvent(t);
  }
  _handleMoveEvent(t) {
    const { features: n } = this._options;
    (n.touch && tn() || this._scrollAvailable && nn()) && t.preventDefault();
  }
  _onScroll() {
    const { _scrollDelta: t, _options: { document: n } } = this, { scrollTop: o, scrollLeft: s } = n.scrollingElement ?? n.body;
    this._areaLocation.x1 += t.x - s, this._areaLocation.y1 += t.y - o, t.x = s, t.y = o, this._setupSelectionArea(), this._frame.next(null);
  }
  _onStartAreaScroll() {
    this._targetBoundaryScrolled = !0, M(this._targetElement, "scroll", this._onStartAreaScroll);
  }
  _wheelScroll(t) {
    const { manualSpeed: n } = this._options.behaviour.scrolling, o = t.deltaY ? t.deltaY > 0 ? 1 : -1 : 0, s = t.deltaX ? t.deltaX > 0 ? 1 : -1 : 0;
    this._scrollSpeed.y += o * n, this._scrollSpeed.x += s * n, this._onTapMove(t), t.preventDefault();
  }
  _keyboardScroll(t) {
    const { manualSpeed: n } = this._options.behaviour.scrolling, o = t.key === "ArrowLeft" ? -1 : t.key === "ArrowRight" ? 1 : 0, s = t.key === "ArrowUp" ? -1 : t.key === "ArrowDown" ? 1 : 0;
    this._scrollSpeed.x += Math.sign(o) * n, this._scrollSpeed.y += Math.sign(s) * n, t.preventDefault(), this._onTapMove({
      clientX: this._lastMousePosition.x,
      clientY: this._lastMousePosition.y,
      preventDefault: () => {
      }
    });
  }
  _recalculateSelectionAreaRect() {
    const { _scrollSpeed: t, _areaLocation: n, _targetElement: o, _options: s } = this, { scrollTop: i, scrollHeight: c, clientHeight: r, scrollLeft: l, scrollWidth: d, clientWidth: f } = o, u = this._targetRect, { x1: g, y1: b } = n;
    let { x2: p, y2: m } = n;
    const { behaviour: { scrolling: { startScrollMargins: a } } } = s;
    p < u.left + a.x ? (t.x = l ? -R(u.left - p + a.x) : 0, p = p < u.left ? u.left : p) : p > u.right - a.x ? (t.x = d - l - f ? R(u.left + u.width - p - a.x) : 0, p = p > u.right ? u.right : p) : t.x = 0, m < u.top + a.y ? (t.y = i ? -R(u.top - m + a.y) : 0, m = m < u.top ? u.top : m) : m > u.bottom - a.y ? (t.y = c - i - r ? R(u.top + u.height - m - a.y) : 0, m = m > u.bottom ? u.bottom : m) : t.y = 0;
    const h = Ke(g, p), v = Ke(b, m), w = We(g, p), C = We(b, m);
    this._areaRect = Fe(h, v, w - h, C - v);
  }
  _redrawSelectionArea() {
    const { x: t, y: n, width: o, height: s } = this._areaRect, { style: i } = this._area;
    i.left = `${t}px`, i.top = `${n}px`, i.width = `${o}px`, i.height = `${s}px`;
  }
  _onTapStop(t, n) {
    var o;
    const { document: s, features: i } = this._options, { _singleClick: c } = this;
    M(this._targetElement, "scroll", this._onStartAreaScroll), M(s, ["mousemove", "touchmove"], this._delayedTapMove), M(s, ["touchmove", "mousemove"], this._onTapMove), M(s, ["mouseup", "touchcancel", "touchend"], this._onTapStop), M(s, "scroll", this._onScroll), this._keepSelection(), t && c && i.singleTap.allow ? this._onSingleTap(t) : !c && !n && (this._updateElementSelection(), this._emitEvent("stop", t)), this._scrollSpeed.x = 0, this._scrollSpeed.y = 0, M(this._targetElement, "wheel", this._wheelScroll, { passive: !0 }), M(this._options.document, "keydown", this._keyboardScroll, { passive: !0 }), this._clippingElement.remove(), (o = this._frame) == null || o.cancel(), j(this._area, "display", "none");
  }
  _updateElementSelection() {
    const { _selectables: t, _options: n, _selection: o, _areaRect: s } = this, { stored: i, selected: c, touched: r } = o, { intersect: l, overlap: d } = n.behaviour, f = d === "invert", u = [], g = [], b = [];
    for (let m = 0; m < t.length; m++) {
      const a = t[m];
      if (Ie(s, a.getBoundingClientRect(), l)) {
        if (c.includes(a))
          i.includes(a) && !r.includes(a) && r.push(a);
        else if (f && i.includes(a)) {
          b.push(a);
          continue;
        } else
          g.push(a);
        u.push(a);
      }
    }
    f && g.push(...i.filter((m) => !c.includes(m)));
    const p = d === "keep";
    for (let m = 0; m < c.length; m++) {
      const a = c[m];
      !u.includes(a) && !// Check if the user wants to keep previously selected elements, e.g.,
      // not make them part of the current selection as soon as they're touched.
      (p && i.includes(a)) && b.push(a);
    }
    o.selected = u, o.changed = { added: g, removed: b }, this._latestElement = void 0;
  }
  _emitEvent(t, n) {
    return this.emit(t, {
      event: n,
      store: this._selection,
      selection: this
    });
  }
  _keepSelection() {
    const { _options: t, _selection: n } = this, { selected: o, changed: s, touched: i, stored: c } = n, r = o.filter((l) => !c.includes(l));
    switch (t.behaviour.overlap) {
      case "drop": {
        n.stored = [
          ...r,
          ...c.filter((l) => !i.includes(l))
          // Elements not touched
        ];
        break;
      }
      case "invert": {
        n.stored = [
          ...r,
          ...c.filter((l) => !s.removed.includes(l))
          // Elements not removed from selection
        ];
        break;
      }
      case "keep": {
        n.stored = [
          ...c,
          ...o.filter((l) => !c.includes(l))
          // Newly added
        ];
        break;
      }
    }
  }
  /**
   * Manually triggers the start of a selection
   * @param evt A MouseEvent / TouchEvent-like object
   * @param silent If beforestart should be fired
   */
  trigger(t, n = !0) {
    this._onTapStart(t, n);
  }
  /**
   * Can be used if during a selection elements have been added
   * Will update everything that can be selected
   */
  resolveSelectables() {
    this._selectables = W(this._options.selectables, this._options.document);
  }
  /**
   * Same as deselecting, but for all elements currently selected
   * @param includeStored If the store should also get cleared
   * @param quiet If move / stop events should be fired
   */
  clearSelection(t = !0, n = !1) {
    const { selected: o, stored: s, changed: i } = this._selection;
    i.added = [], i.removed.push(
      ...o,
      ...t ? s : []
    ), n || (this._emitEvent("move", null), this._emitEvent("stop", null)), this._selection = Ye(t ? [] : s);
  }
  /**
   * @returns {Array} Selected elements
   */
  getSelection() {
    return this._selection.stored;
  }
  /**
   * @returns {HTMLElement} The selection area element
   */
  getSelectionArea() {
    return this._area;
  }
  /**
   * @returns {Element[]} Available selectable elements for current selection
   */
  getSelectables() {
    return this._selectables;
  }
  /**
   * Set the location of the selection area
   * @param location A partial AreaLocation object
   */
  setAreaLocation(t) {
    Object.assign(this._areaLocation, t), this._redrawSelectionArea();
  }
  /**
   * @returns {AreaLocation} The current location of the selection area
   */
  getAreaLocation() {
    return this._areaLocation;
  }
  /**
   * Cancel the current selection process, pass true to fire a stop event after cancel
   * @param keepEvent If a stop event should be fired
   */
  cancel(t = !1) {
    this._onTapStop(null, !t);
  }
  /**
   * Unbinds all events and removes the area-element.
   */
  destroy() {
    this.cancel(), this.disable(), this._clippingElement.remove(), super.unbindAllListeners();
  }
  /**
   * Adds elements to the selection
   * @param query CSS Query, can be an array of queries
   * @param quiet If this should not trigger the move event
   */
  select(t, n = !1) {
    const { changed: o, selected: s, stored: i } = this._selection, c = W(t, this._options.document).filter(
      (r) => !s.includes(r) && !i.includes(r)
    );
    return i.push(...c), s.push(...c), o.added.push(...c), o.removed = [], this._latestElement = void 0, n || (this._emitEvent("move", null), this._emitEvent("stop", null)), c;
  }
  /**
   * Removes a particular element from the selection
   * @param query CSS Query, can be an array of queries
   * @param quiet If this should not trigger the move event
   */
  deselect(t, n = !1) {
    const { selected: o, stored: s, changed: i } = this._selection, c = W(t, this._options.document).filter(
      (r) => o.includes(r) || s.includes(r)
    );
    this._selection.stored = s.filter((r) => !c.includes(r)), this._selection.selected = o.filter((r) => !c.includes(r)), this._selection.changed.added = [], this._selection.changed.removed.push(
      ...c.filter((r) => !i.removed.includes(r))
    ), this._latestElement = void 0, n || (this._emitEvent("move", null), this._emitEvent("stop", null));
  }
};
ot.version = "3.9.0";
let sn = ot;
function rn(e) {
  const t = e.mouseSelectionButton === 2 ? [2] : [0], n = new sn({
    selectables: [".map-container me-tpc"],
    boundaries: [e.container],
    container: e.selectionContainer,
    features: {
      // deselectOnBlur: true,
      touch: !1
    },
    behaviour: {
      triggers: t,
      // Scroll configuration.
      scrolling: {
        // On scrollable areas the number on px per frame is devided by this amount.
        // Default is 10 to provide a enjoyable scroll experience.
        speedDivider: 10,
        // Browsers handle mouse-wheel events differently, this number will be used as
        // numerator to calculate the mount of px while scrolling manually: manualScrollSpeed / scrollSpeedDivider.
        manualSpeed: 750,
        // This property defines the virtual inset margins from the borders of the container
        // component that, when crossed by the mouse/touch, trigger the scrolling. Useful for
        // fullscreen containers.
        startScrollMargins: { x: 10, y: 10 }
      }
    }
  }).on("beforestart", ({ event: o }) => {
    var c;
    if (e.spacePressed)
      return !1;
    const s = o.target;
    if (s.id === "input-box" || s.className === "circle" || (c = e.container.querySelector(".context-menu")) != null && c.contains(s))
      return !1;
    if (!o.ctrlKey && !o.metaKey) {
      if (s.tagName === "ME-TPC" && s.classList.contains("selected"))
        return !1;
      e.clearSelection();
    }
    const i = n.getSelectionArea();
    return i.style.background = "#4f90f22d", i.style.border = "1px solid #4f90f2", i.parentElement && (i.parentElement.style.zIndex = "9999"), !0;
  }).on(
    "move",
    ({
      store: {
        changed: { added: o, removed: s }
      }
    }) => {
      if (o.length > 0 || s.length > 0, o.length > 0) {
        for (const i of o)
          i.className = "selected";
        e.currentNodes = [...e.currentNodes, ...o], e.bus.fire(
          "selectNodes",
          o.map((i) => i.nodeObj)
        );
      }
      if (s.length > 0) {
        for (const i of s)
          i.classList.remove("selected");
        e.currentNodes = e.currentNodes.filter((i) => !(s != null && s.includes(i))), e.bus.fire(
          "unselectNodes",
          s.map((i) => i.nodeObj)
        );
      }
    }
  );
  e.selection = n;
}
const cn = function(e, t = !0) {
  this.theme = e;
  const o = {
    ...(e.type === "dark" ? xe : we).cssVar,
    ...e.cssVar
  }, s = Object.keys(o);
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    this.container.style.setProperty(c, o[c]);
  }
  t && this.refresh();
}, z = (e) => {
  var o;
  const t = (o = e.parent) == null ? void 0 : o.children, n = (t == null ? void 0 : t.indexOf(e)) ?? 0;
  return { siblings: t, index: n };
};
function ln(e) {
  const { siblings: t, index: n } = z(e);
  if (t === void 0)
    return;
  const o = t[n];
  n === 0 ? (t[n] = t[t.length - 1], t[t.length - 1] = o) : (t[n] = t[n - 1], t[n - 1] = o);
}
function an(e) {
  const { siblings: t, index: n } = z(e);
  if (t === void 0)
    return;
  const o = t[n];
  n === t.length - 1 ? (t[n] = t[0], t[0] = o) : (t[n] = t[n + 1], t[n + 1] = o);
}
function st(e) {
  const { siblings: t, index: n } = z(e);
  return t === void 0 ? 0 : (t.splice(n, 1), t.length);
}
function dn(e, t, n) {
  const { siblings: o, index: s } = z(n);
  o !== void 0 && (t === "before" ? o.splice(s, 0, e) : o.splice(s + 1, 0, e));
}
function hn(e, t) {
  const { siblings: n, index: o } = z(e);
  n !== void 0 && (n[o] = t, t.children = [e]);
}
function it(e, t, n) {
  var o;
  if (st(t), (o = n.parent) != null && o.parent || (t.direction = n.direction), e === "in")
    n.children ? n.children.push(t) : n.children = [t];
  else {
    t.direction !== void 0 && (t.direction = n.direction);
    const { siblings: s, index: i } = z(n);
    if (s === void 0)
      return;
    e === "before" ? s.splice(i, 0, t) : s.splice(i + 1, 0, t);
  }
}
const un = function({ map: e, direction: t }, n) {
  var o, s;
  if (t === 0)
    return 0;
  if (t === 1)
    return 1;
  if (t === 2) {
    const i = ((o = e.querySelector(".lhs")) == null ? void 0 : o.childElementCount) || 0, c = ((s = e.querySelector(".rhs")) == null ? void 0 : s.childElementCount) || 0;
    return i <= c ? (n.direction = 0, 0) : (n.direction = 1, 1);
  }
}, rt = function(e, t, n) {
  var i, c;
  const o = n.children[0].children[0], s = t.parentElement;
  if (s.tagName === "ME-PARENT") {
    if (Z(o), s.children[1])
      s.nextSibling.appendChild(n);
    else {
      const r = e.createChildren([n]);
      s.appendChild(ke(!0)), s.insertAdjacentElement("afterend", r);
    }
    e.linkDiv(n.offsetParent);
  } else
    s.tagName === "ME-ROOT" && (un(e, o.nodeObj) === 0 ? (i = e.container.querySelector(".lhs")) == null || i.appendChild(n) : (c = e.container.querySelector(".rhs")) == null || c.appendChild(n), e.linkDiv());
}, fn = function(e, t) {
  const n = e.parentNode;
  if (t === 0) {
    const o = n.parentNode.parentNode;
    o.tagName !== "ME-MAIN" && (o.previousSibling.children[1].remove(), o.remove());
  }
  n.parentNode.remove();
}, ct = {
  before: "beforebegin",
  after: "afterend"
}, Z = function(e) {
  const n = e.parentElement.parentElement.lastElementChild;
  (n == null ? void 0 : n.tagName) === "svg" && (n == null || n.remove());
}, pn = function(e, t) {
  const n = e.nodeObj, o = Ee(n);
  o.style && t.style && (t.style = Object.assign(o.style, t.style));
  const s = Object.assign(n, t);
  Ne.call(this, e, s), this.linkDiv(), this.bus.fire("operation", {
    name: "reshapeNode",
    obj: s,
    origin: o
  });
}, _e = function(e, t, n) {
  if (!t)
    return null;
  const o = t.nodeObj;
  o.expanded === !1 && (e.expandNode(t, !0), t = e.findEle(o.id));
  const s = n || e.generateNewObj();
  o.children ? o.children.push(s) : o.children = [s], B(e.nodeData);
  const { grp: i, top: c } = e.createWrapper(s);
  return rt(e, t, i), { newTop: c, newNodeObj: s };
}, gn = function(e, t, n) {
  var d, f, u, g;
  const o = t || this.currentNode;
  if (!o)
    return;
  const s = o.nodeObj;
  if (s.parent) {
    if (!((d = s.parent) != null && d.parent) && ((u = (f = s.parent) == null ? void 0 : f.children) == null ? void 0 : u.length) === 1 && this.direction === 2) {
      this.addChild(this.findEle(s.parent.id), n);
      return;
    }
  } else {
    this.addChild();
    return;
  }
  const i = n || this.generateNewObj();
  if (!((g = s.parent) != null && g.parent)) {
    const b = o.closest("me-main").className === P.LHS ? 0 : 1;
    i.direction = b;
  }
  dn(i, e, s), B(this.nodeData);
  const c = o.parentElement, { grp: r, top: l } = this.createWrapper(i);
  c.parentElement.insertAdjacentElement(ct[e], r), this.linkDiv(r.offsetParent), n || this.editTopic(l.firstChild), this.bus.fire("operation", {
    name: "insertSibling",
    type: e,
    obj: i
  }), this.selectNode(l.firstChild, !0);
}, mn = function(e, t) {
  const n = e || this.currentNode;
  if (!n)
    return;
  Z(n);
  const o = n.nodeObj;
  if (!o.parent)
    return;
  const s = t || this.generateNewObj();
  hn(o, s), B(this.nodeData);
  const i = n.parentElement.parentElement, { grp: c, top: r } = this.createWrapper(s, !0);
  r.appendChild(ke(!0)), i.insertAdjacentElement("afterend", c);
  const l = this.createChildren([i]);
  r.insertAdjacentElement("afterend", l), this.linkDiv(), t || this.editTopic(r.firstChild), this.selectNode(r.firstChild, !0), this.bus.fire("operation", {
    name: "insertParent",
    obj: s
  });
}, vn = function(e, t) {
  const n = e || this.currentNode;
  if (!n)
    return;
  const o = _e(this, n, t);
  if (!o)
    return;
  const { newTop: s, newNodeObj: i } = o;
  this.bus.fire("operation", {
    name: "addChild",
    obj: i
  }), t || this.editTopic(s.firstChild), this.selectNode(s.firstChild, !0);
}, bn = function(e, t) {
  const n = Ee(e.nodeObj);
  Ce(n);
  const o = _e(this, t, n);
  if (!o)
    return;
  const { newNodeObj: s } = o;
  this.selectNode(this.findEle(s.id)), this.bus.fire("operation", {
    name: "copyNode",
    obj: s
  });
}, yn = function(e, t) {
  e = de(e);
  const n = [];
  for (let o = 0; o < e.length; o++) {
    const s = e[o], i = Ee(s.nodeObj);
    Ce(i);
    const c = _e(this, t, i);
    if (!c)
      return;
    const { newNodeObj: r } = c;
    n.push(r);
  }
  this.unselectNodes(this.currentNodes), this.selectNodes(n.map((o) => this.findEle(o.id))), this.bus.fire("operation", {
    name: "copyNodes",
    objs: n
  });
}, wn = function(e) {
  const t = e || this.currentNode;
  if (!t)
    return;
  const n = t.nodeObj;
  ln(n);
  const o = t.parentNode.parentNode;
  o.parentNode.insertBefore(o, o.previousSibling), this.linkDiv(), this.bus.fire("operation", {
    name: "moveUpNode",
    obj: n
  });
}, xn = function(e) {
  const t = e || this.currentNode;
  if (!t)
    return;
  const n = t.nodeObj;
  an(n);
  const o = t.parentNode.parentNode;
  o.nextSibling ? o.nextSibling.insertAdjacentElement("afterend", o) : o.parentNode.prepend(o), this.linkDiv(), this.bus.fire("operation", {
    name: "moveDownNode",
    obj: n
  });
}, Cn = function(e) {
  if (!Array.isArray(e)) e = e ? [e] : [];
  if (e.length === 0)
    return;
  e = de(e);
  for (const n of e) {
    const o = n.nodeObj, s = st(o);
    fn(n, s);
  }
  const t = e[e.length - 1];
  this.selectNode(this.findEle(t.nodeObj.parent.id)), this.linkDiv(), this.bus.fire("operation", {
    name: "removeNodes",
    objs: e.map((n) => n.nodeObj)
  });
}, En = function(e, t) {
  e = de(e);
  const n = t.nodeObj;
  n.expanded === !1 && (this.expandNode(t, !0), t = this.findEle(n.id));
  for (const o of e) {
    const s = o.nodeObj;
    it("in", s, n), B(this.nodeData);
    const i = o.parentElement;
    rt(this, t, i.parentElement);
  }
  this.linkDiv(), this.bus.fire("operation", {
    name: "moveNodeIn",
    objs: e.map((o) => o.nodeObj),
    toObj: n
  });
}, lt = (e, t, n, o) => {
  e = de(e), t === "after" && (e = e.reverse());
  const s = n.nodeObj, i = [];
  for (const c of e) {
    const r = c.nodeObj;
    it(t, r, s), B(o.nodeData), Z(c);
    const l = c.parentElement.parentNode;
    i.includes(l.parentElement) || i.push(l.parentElement), n.parentElement.parentNode.insertAdjacentElement(ct[t], l);
  }
  for (const c of i)
    c.childElementCount === 0 && c.tagName !== "ME-MAIN" && (c.previousSibling.children[1].remove(), c.remove());
  o.linkDiv(), o.bus.fire("operation", {
    name: t === "before" ? "moveNodeBefore" : "moveNodeAfter",
    objs: e.map((c) => c.nodeObj),
    toObj: s
  });
}, Sn = function(e, t) {
  lt(e, "before", t, this);
}, Nn = function(e, t) {
  lt(e, "after", t, this);
}, kn = function(e) {
  const t = e || this.currentNode;
  t && (t.nodeObj.dangerouslySetInnerHTML || this.editTopic(t));
}, _n = function(e, t) {
  e.text.textContent = t, e.nodeObj.topic = t, this.linkDiv();
}, at = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  addChild: vn,
  beginEdit: kn,
  copyNode: bn,
  copyNodes: yn,
  insertParent: mn,
  insertSibling: gn,
  moveDownNode: xn,
  moveNodeAfter: Nn,
  moveNodeBefore: Sn,
  moveNodeIn: En,
  moveUpNode: wn,
  removeNode: Cn,
  removeNodes: Cn,
  reshapeNode: pn,
  rmSubline: Z,
  setNodeTopic: _n
}, Symbol.toStringTag, { value: "Module" }));
function Tn(e) {
  return {
    nodeData: e.isFocusMode ? e.nodeDataBackup : e.nodeData,
    arrows: e.arrows,
    summaries: e.summaries,
    direction: e.direction,
    theme: e.theme
  };
}
const Ln = function(e) {
  const t = this.container, n = e.getBoundingClientRect(), o = t.getBoundingClientRect();
  if (n.top > o.bottom || n.bottom < o.top || n.left > o.right || n.right < o.left) {
    const i = n.left + n.width / 2, c = n.top + n.height / 2, r = o.left + o.width / 2, l = o.top + o.height / 2, d = i - r, f = c - l;
    this.move(-d, -f, !0);
  }
}, An = function(e, t, n) {
  this.clearSelection(), this.scrollIntoView(e), this.selection.select(e), t && this.bus.fire("selectNewNode", e.nodeObj);
}, Mn = function(e) {
  this.selection.select(e);
}, Dn = function(e) {
  this.selection.deselect(e);
}, Pn = function() {
  this.unselectNodes(this.currentNodes), this.unselectSummary(), this.unselectArrow();
}, $n = function() {
  const e = Tn(this);
  return JSON.stringify(e, (t, n) => {
    if (!(t === "parent" && typeof n != "string"))
      return n;
  });
}, On = function() {
  return JSON.parse(this.getDataString());
}, jn = function() {
  this.editable = !0;
}, Hn = function() {
  this.editable = !1;
}, Bn = function(e, t = { x: 0, y: 0 }) {
  if (e < this.scaleMin || e > this.scaleMax)
    return;
  const n = this.container.getBoundingClientRect(), o = t.x ? t.x - n.left - n.width / 2 : 0, s = t.y ? t.y - n.top - n.height / 2 : 0, { dx: i, dy: c } = dt(this), r = this.map.style.transform, { x: l, y: d } = Xe(r), f = l - i, u = d - c, g = this.scaleVal, b = (-o + f) * (1 - e / g), p = (-s + u) * (1 - e / g);
  this.map.style.transform = `translate(${l - b}px, ${d - p}px) scale(${e})`, this.scaleVal = e, this.bus.fire("scale", e);
}, Rn = function() {
  const e = this.nodes.offsetHeight / this.container.offsetHeight, t = this.nodes.offsetWidth / this.container.offsetWidth, n = 1 / Math.max(1, Math.max(e, t));
  this.scaleVal = n, this.map.style.transform = "scale(" + n + ")", this.bus.fire("scale", n);
}, Fn = function(e, t, n = !1) {
  const { map: o, scaleVal: s, bus: i } = this, c = o.style.transform;
  let { x: r, y: l } = Xe(c);
  r += e, l += t, n && (o.style.transition = "transform 0.3s", setTimeout(() => {
    o.style.transition = "none";
  }, 300)), o.style.transform = `translate(${r}px, ${l}px) scale(${s})`, i.fire("move", { dx: e, dy: t });
}, dt = (e) => {
  const { container: t, map: n, nodes: o } = e, s = n.querySelector("me-root"), i = s.offsetTop, c = s.offsetLeft, r = s.offsetWidth, l = s.offsetHeight;
  let d, f;
  return e.alignment === "root" ? (d = t.offsetWidth / 2 - c - r / 2, f = t.offsetHeight / 2 - i - l / 2, n.style.transformOrigin = `${c + r / 2}px 50%`) : (d = (t.offsetWidth - o.offsetWidth) / 2, f = (t.offsetHeight - o.offsetHeight) / 2, n.style.transformOrigin = "50% 50%"), { dx: d, dy: f };
}, In = function() {
  const { map: e } = this, { dx: t, dy: n } = dt(this);
  e.style.transform = `translate(${t}px, ${n}px) scale(${this.scaleVal})`;
}, Wn = function(e) {
  e(this);
}, Kn = function(e) {
  e.nodeObj.parent && (this.clearSelection(), this.tempDirection === null && (this.tempDirection = this.direction), this.isFocusMode || (this.nodeDataBackup = this.nodeData, this.isFocusMode = !0), this.nodeData = e.nodeObj, this.initRight(), this.toCenter());
}, Gn = function() {
  this.isFocusMode = !1, this.tempDirection !== null && (this.nodeData = this.nodeDataBackup, this.direction = this.tempDirection, this.tempDirection = null, this.refresh(), this.toCenter());
}, Yn = function() {
  this.direction = 0, this.refresh(), this.toCenter(), this.bus.fire("changeDirection", this.direction);
}, qn = function() {
  this.direction = 1, this.refresh(), this.toCenter(), this.bus.fire("changeDirection", this.direction);
}, zn = function() {
  this.direction = 2, this.refresh(), this.toCenter(), this.bus.fire("changeDirection", this.direction);
}, Vn = function(e) {
  this.locale = e, this.refresh();
}, Un = function(e, t) {
  const n = e.nodeObj;
  typeof t == "boolean" ? n.expanded = t : n.expanded !== !1 ? n.expanded = !1 : n.expanded = !0;
  const o = e.getBoundingClientRect(), s = {
    x: o.left,
    y: o.top
  }, i = e.parentNode, c = i.children[1];
  if (c.expanded = n.expanded, c.className = n.expanded ? "minus" : "", Z(e), n.expanded) {
    const u = this.createChildren(
      n.children.map((g) => this.createWrapper(g).grp)
    );
    i.parentNode.appendChild(u);
  } else
    i.parentNode.children[1].remove();
  this.linkDiv(e.closest("me-main > me-wrapper"));
  const r = e.getBoundingClientRect(), l = {
    x: r.left,
    y: r.top
  }, d = s.x - l.x, f = s.y - l.y;
  this.move(d, f), this.bus.fire("expandNode", n);
}, Xn = function(e, t) {
  const n = e.nodeObj, o = e.getBoundingClientRect(), s = {
    x: o.left,
    y: o.top
  };
  Y(n, t ?? !n.expanded), this.refresh();
  const i = this.findEle(n.id).getBoundingClientRect(), c = {
    x: i.left,
    y: i.top
  }, r = s.x - c.x, l = s.y - c.y;
  this.move(r, l);
}, Jn = function(e) {
  this.clearSelection(), e && (e = JSON.parse(JSON.stringify(e)), this.nodeData = e.nodeData, this.arrows = e.arrows || [], this.summaries = e.summaries || [], e.theme && this.changeTheme(e.theme)), B(this.nodeData), this.layout(), this.linkDiv();
}, Zn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  cancelFocus: Gn,
  clearSelection: Pn,
  disableEdit: Hn,
  enableEdit: jn,
  expandNode: Un,
  expandNodeAll: Xn,
  focusNode: Kn,
  getData: On,
  getDataString: $n,
  initLeft: Yn,
  initRight: qn,
  initSide: zn,
  install: Wn,
  move: Fn,
  refresh: Jn,
  scale: Bn,
  scaleFit: Rn,
  scrollIntoView: Ln,
  selectNode: An,
  selectNodes: Mn,
  setLocale: Vn,
  toCenter: In,
  unselectNodes: Dn
}, Symbol.toStringTag, { value: "Module" })), Qn = function(e) {
  return {
    dom: e,
    moved: !1,
    // differentiate click and move
    pointerdown: !1,
    lastX: 0,
    lastY: 0,
    handlePointerMove(t) {
      if (this.pointerdown) {
        this.moved = !0;
        const n = t.clientX - this.lastX, o = t.clientY - this.lastY;
        this.lastX = t.clientX, this.lastY = t.clientY, this.cb && this.cb(n, o);
      }
    },
    handlePointerDown(t) {
      t.button === 0 && (this.pointerdown = !0, this.lastX = t.clientX, this.lastY = t.clientY, this.dom.setPointerCapture(t.pointerId));
    },
    handleClear(t) {
      this.pointerdown = !1, t.pointerId !== void 0 && this.dom.releasePointerCapture(t.pointerId);
    },
    cb: null,
    init(t, n) {
      this.cb = n, this.handleClear = this.handleClear.bind(this), this.handlePointerMove = this.handlePointerMove.bind(this), this.handlePointerDown = this.handlePointerDown.bind(this), this.destroy = Se([
        { dom: t, evt: "pointermove", func: this.handlePointerMove },
        { dom: t, evt: "pointerleave", func: this.handleClear },
        { dom: t, evt: "pointerup", func: this.handleClear },
        { dom: this.dom, evt: "pointerdown", func: this.handlePointerDown }
      ]);
    },
    destroy: null,
    clear() {
      this.moved = !1, this.pointerdown = !1;
    }
  };
}, qe = {
  create: Qn
}, eo = "#4dc4ff";
function ht(e, t, n, o, s, i, c, r) {
  return {
    x: e / 8 + n * 3 / 8 + s * 3 / 8 + c / 8,
    y: t / 8 + o * 3 / 8 + i * 3 / 8 + r / 8
  };
}
function to(e, t, n) {
  e && (e.dataset.x = t.toString(), e.dataset.y = n.toString(), he(e));
}
function ne(e, t, n, o, s) {
  k(e, {
    x1: t + "",
    y1: n + "",
    x2: o + "",
    y2: s + ""
  });
}
function ze(e, t, n, o, s, i, c, r, l, d) {
  var m;
  const f = `M ${t} ${n} C ${o} ${s} ${i} ${c} ${r} ${l}`;
  if (e.line.setAttribute("d", f), d.style) {
    const a = d.style;
    a.stroke && e.line.setAttribute("stroke", a.stroke), a.strokeWidth && e.line.setAttribute("stroke-width", String(a.strokeWidth)), a.strokeDasharray && e.line.setAttribute("stroke-dasharray", a.strokeDasharray), a.strokeLinecap && e.line.setAttribute("stroke-linecap", a.strokeLinecap), a.opacity !== void 0 && e.line.setAttribute("opacity", String(a.opacity));
  }
  const u = e.querySelectorAll('path[stroke="transparent"]');
  u.length > 0 && u[0].setAttribute("d", f);
  const g = re(i, c, r, l);
  if (g) {
    const a = `M ${g.x1} ${g.y1} L ${r} ${l} L ${g.x2} ${g.y2}`;
    if (e.arrow1.setAttribute("d", a), u.length > 1 && u[1].setAttribute("d", a), d.style) {
      const h = d.style;
      h.stroke && e.arrow1.setAttribute("stroke", h.stroke), h.strokeWidth && e.arrow1.setAttribute("stroke-width", String(h.strokeWidth)), h.strokeLinecap && e.arrow1.setAttribute("stroke-linecap", h.strokeLinecap), h.opacity !== void 0 && e.arrow1.setAttribute("opacity", String(h.opacity));
    }
  }
  if (d.bidirectional) {
    const a = re(o, s, t, n);
    if (a) {
      const h = `M ${a.x1} ${a.y1} L ${t} ${n} L ${a.x2} ${a.y2}`;
      if (e.arrow2.setAttribute("d", h), u.length > 2 && u[2].setAttribute("d", h), d.style) {
        const v = d.style;
        v.stroke && e.arrow2.setAttribute("stroke", v.stroke), v.strokeWidth && e.arrow2.setAttribute("stroke-width", String(v.strokeWidth)), v.strokeLinecap && e.arrow2.setAttribute("stroke-linecap", v.strokeLinecap), v.opacity !== void 0 && e.arrow2.setAttribute("opacity", String(v.opacity));
      }
    }
  }
  const { x: b, y: p } = ht(t, n, o, s, i, c, r, l);
  if (e.labelEl && to(e.labelEl, b, p), (m = d.style) != null && m.labelColor) {
    const a = e.labelEl;
    a && (a.style.color = d.style.labelColor);
  }
  ao(e);
}
function ae(e, t, n) {
  n = n || { x: 40, y: 0 };
  const nx = typeof n.x === 'number' ? n.x : 40;
  const ny = typeof n.y === 'number' ? n.y : 0;
  const { offsetLeft: o, offsetTop: s } = O(e.nodes, t), i = t.offsetWidth, c = t.offsetHeight, r = o + i / 2, l = s + c / 2, d = r + nx, f = l + ny;
  return {
    w: i,
    h: c,
    cx: r,
    cy: l,
    ctrlX: d,
    ctrlY: f
  };
}
function G(e) {
  let t, n;
  const o = (e.cy - e.ctrlY) / (e.ctrlX - e.cx);
  return o > e.h / e.w || o < -e.h / e.w ? e.cy - e.ctrlY < 0 ? (t = e.cx - e.h / 2 / o, n = e.cy + e.h / 2) : (t = e.cx + e.h / 2 / o, n = e.cy - e.h / 2) : e.cx - e.ctrlX < 0 ? (t = e.cx + e.w / 2, n = e.cy - e.w * o / 2) : (t = e.cx - e.w / 2, n = e.cy + e.w * o / 2), {
    x: t,
    y: n
  };
}
const Te = function(e, t, n, o, s) {
  var E;
  if (!t || !n)
    return;
  const i = ae(e, t, o.delta1), c = ae(e, n, o.delta2), { x: r, y: l } = G(i), { ctrlX: d, ctrlY: f } = i, { ctrlX: u, ctrlY: g } = c, { x: b, y: p } = G(c), m = re(u, g, b, p);
  if (!m)
    return;
  const a = `M ${m.x1} ${m.y1} L ${b} ${p} L ${m.x2} ${m.y2}`;
  let h = "";
  if (o.bidirectional) {
    const N = re(d, f, r, l);
    if (!N)
      return;
    h = `M ${N.x1} ${N.y1} L ${r} ${l} L ${N.x2} ${N.y2}`;
  }
  const v = Pt(`M ${r} ${l} C ${d} ${f} ${u} ${g} ${b} ${p}`, a, h, o.style), { x: w, y: C } = ht(r, l, d, f, u, g, b, p), S = ((E = o.style) == null ? void 0 : E.labelColor) || "rgb(235, 95, 82)", y = "arrow-" + o.id;
  v.id = y;
  const x = me(o.label, w, C, {
    anchor: "middle",
    color: S,
    dataType: "arrow",
    svgId: y
  });
  v.labelEl = x, v.arrowObj = o, v.dataset.linkid = o.id, e.labelContainer.appendChild(x), e.linkSvgGroup.appendChild(v), he(x), s || (e.arrows.push(o), e.currentArrow = v, ut(e, o, i, c));
}, no = function(e, t, n = {}) {
  const o = {
    id: I(),
    label: "Custom Link",
    from: e.nodeObj.id,
    to: t.nodeObj.id,
    delta1: {
      x: e.offsetWidth / 2 + 100,
      y: 0
    },
    delta2: {
      x: t.offsetWidth / 2 + 100,
      y: 0
    },
    ...n
  };
  Te(this, e, t, o), this.bus.fire("operation", {
    name: "createArrow",
    obj: o
  });
}, oo = function(e) {
  ue(this);
  const t = { ...e, id: I() };
  Te(this, this.findEle(t.from), this.findEle(t.to), t), this.bus.fire("operation", {
    name: "createArrow",
    obj: t
  });
}, so = function(e) {
  let t;
  if (e ? t = e : t = this.currentArrow, !t)
    return;
  ue(this);
  const n = t.arrowObj.id;
  this.arrows = this.arrows.filter((o) => o.id !== n), t.remove(), this.bus.fire("operation", {
    name: "removeArrow",
    obj: {
      id: n
    }
  });
}, io = function(e) {
  this.currentArrow = e;
  const t = e.arrowObj, n = this.findEle(t.from), o = this.findEle(t.to), s = ae(this, n, t.delta1), i = ae(this, o, t.delta2);
  ut(this, t, s, i);
}, ro = function() {
  ue(this), this.currentArrow = null;
}, fe = function(e, t) {
  const n = document.createElementNS(D, "path");
  return k(n, {
    d: e,
    stroke: t,
    fill: "none",
    "stroke-width": "6",
    "stroke-linecap": "round",
    "stroke-linejoin": "round"
  }), n;
}, co = function(e, t) {
  const n = document.createElementNS(D, "g");
  n.setAttribute("class", "arrow-highlight"), n.setAttribute("opacity", "0.45");
  const o = fe(e.line.getAttribute("d"), t);
  n.appendChild(o);
  const s = fe(e.arrow1.getAttribute("d"), t);
  if (n.appendChild(s), e.arrow2.getAttribute("d")) {
    const i = fe(e.arrow2.getAttribute("d"), t);
    n.appendChild(i);
  }
  e.insertBefore(n, e.firstChild);
}, lo = function(e) {
  const t = e.querySelector(".arrow-highlight");
  t && t.remove();
}, ao = function(e) {
  const t = e.querySelector(".arrow-highlight");
  if (!t)
    return;
  const n = t.querySelectorAll("path");
  n.length >= 1 && n[0].setAttribute("d", e.line.getAttribute("d")), n.length >= 2 && n[1].setAttribute("d", e.arrow1.getAttribute("d")), n.length >= 3 && e.arrow2.getAttribute("d") && n[2].setAttribute("d", e.arrow2.getAttribute("d"));
}, ue = function(e) {
  var t, n;
  (t = e.helper1) == null || t.destroy(), (n = e.helper2) == null || n.destroy(), e.linkController.style.display = "none", e.P2.style.display = "none", e.P3.style.display = "none", e.currentArrow && lo(e.currentArrow);
}, ut = function(e, t, n, o) {
  const { linkController: s, P2: i, P3: c, line1: r, line2: l, nodes: d, map: f, currentArrow: u, bus: g } = e;
  if (!u)
    return;
  s.style.display = "initial", i.style.display = "initial", c.style.display = "initial", d.appendChild(s), d.appendChild(i), d.appendChild(c), co(u, eo);
  let { x: b, y: p } = G(n), { ctrlX: m, ctrlY: a } = n, { ctrlX: h, ctrlY: v } = o, { x: w, y: C } = G(o);
  i.style.cssText = `top:${a}px;left:${m}px;`, c.style.cssText = `top:${v}px;left:${h}px;`, ne(r, b, p, m, a), ne(l, h, v, w, C), e.helper1 = qe.create(i), e.helper2 = qe.create(c), e.helper1.init(f, (S, y) => {
    m = m + S / e.scaleVal, a = a + y / e.scaleVal;
    const x = G({ ...n, ctrlX: m, ctrlY: a });
    b = x.x, p = x.y, i.style.top = a + "px", i.style.left = m + "px", ze(u, b, p, m, a, h, v, w, C, t), ne(r, b, p, m, a), t.delta1.x = m - n.cx, t.delta1.y = a - n.cy, g.fire("updateArrowDelta", t);
  }), e.helper2.init(f, (S, y) => {
    h = h + S / e.scaleVal, v = v + y / e.scaleVal;
    const x = G({ ...o, ctrlX: h, ctrlY: v });
    w = x.x, C = x.y, c.style.top = v + "px", c.style.left = h + "px", ze(u, b, p, m, a, h, v, w, C, t), ne(l, h, v, w, C), t.delta2.x = h - o.cx, t.delta2.y = v - o.cy, g.fire("updateArrowDelta", t);
  });
};
function ho() {
  this.linkSvgGroup.innerHTML = "";
  this.labelContainer && (this.labelContainer.innerHTML = "");
  for (let e = 0; e < this.arrows.length; e++) {
    const t = this.arrows[e];
    try {
      Te(this, this.findEle(t.from), this.findEle(t.to), t, !0);
    } catch {
    }
  }
  this.nodes.appendChild(this.linkSvgGroup);
}
function uo(e) {
  ue(this), e && e.labelEl && et(this, e.labelEl, e.arrowObj);
}
function fo() {
  this.arrows = this.arrows.filter((e) => ie(e.from, this.nodeData) && ie(e.to, this.nodeData));
}
const po = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  createArrow: no,
  createArrowFrom: oo,
  editArrowLabel: uo,
  removeArrow: so,
  renderArrow: ho,
  selectArrow: io,
  tidyArrow: fo,
  unselectArrow: ro
}, Symbol.toStringTag, { value: "Module" })), go = function(e) {
  var l, d;
  if (e.length === 0)
    throw new Error("No selected node.");
  if (e.length === 1) {
    const f = e[0].nodeObj, u = e[0].nodeObj.parent;
    if (!u)
      throw new Error("Can not select root node.");
    const g = u.children.findIndex((b) => f === b);
    return {
      parent: u.id,
      start: g,
      end: g
    };
  }
  let t = 0;
  const n = e.map((f) => {
    let u = f.nodeObj;
    const g = [];
    for (; u.parent; ) {
      const b = u.parent, p = b.children, m = p == null ? void 0 : p.indexOf(u);
      u = b, g.unshift({ node: u, index: m });
    }
    return g.length > t && (t = g.length), g;
  });
  let o = 0;
  e:
    for (; o < t; o++) {
      const f = (l = n[0][o]) == null ? void 0 : l.node;
      for (let u = 1; u < n.length; u++)
        if (((d = n[u][o]) == null ? void 0 : d.node) !== f)
          break e;
    }
  if (!o)
    throw new Error("Can not select root node.");
  const s = n.map((f) => f[o - 1].index).sort(), i = s[0] || 0, c = s[s.length - 1] || 0, r = n[0][o - 1].node;
  if (!r.parent)
    throw new Error("Please select nodes in the same main topic.");
  return {
    parent: r.id,
    start: i,
    end: c
  };
}, mo = function(e) {
  const t = document.createElementNS(D, "g");
  return t.setAttribute("id", e), t;
}, Ve = function(e, t) {
  const n = document.createElementNS(D, "path");
  return k(n, {
    d: e,
    stroke: t || "#666",
    fill: "none",
    "stroke-linecap": "round",
    "stroke-width": "2"
  }), n;
}, vo = (e) => e.parentElement.parentElement, bo = function(e, { parent: t, start: n }) {
  const o = e.findEle(t), s = o.nodeObj;
  let i;
  return s.parent ? i = o.closest("me-main").className : i = e.findEle(s.children[n].id).closest("me-main").className, i;
}, Le = function(e, t) {
  var V;
  const { id: n, label: o, parent: s, start: i, end: c, style: r } = t, { nodes: l, theme: d, summarySvg: f } = e, g = e.findEle(s).nodeObj, b = bo(e, t);
  let p = 1 / 0, m = 0, a = 0, h = 0;
  for (let U = i; U <= c; U++) {
    const Ae = (V = g.children) == null ? void 0 : V[U];
    if (!Ae)
      return e.removeSummary(n), null;
    const Q = vo(e.findEle(Ae.id)), { offsetLeft: ee, offsetTop: Me } = O(l, Q), De = i === c ? 10 : 20;
    U === i && (a = Me + De), U === c && (h = Me + Q.offsetHeight - De), ee < p && (p = ee), Q.offsetWidth + ee > m && (m = Q.offsetWidth + ee);
  }
  let v, w;
  const C = g.parent ? 10 : 0, S = a + C, y = h + C, x = (S + y) / 2, E = (r == null ? void 0 : r.stroke) || d.cssVar["--color"], N = (r == null ? void 0 : r.labelColor) || d.cssVar["--color"], L = "s-" + n;
  b === P.LHS ? (v = Ve(`M ${p + 10} ${S} c -5 0 -10 5 -10 10 L ${p} ${y - 10} c 0 5 5 10 10 10 M ${p} ${x} h -10`, E), w = me(o, p - 20, x, { anchor: "end", color: N, dataType: "summary", svgId: L })) : (v = Ve(`M ${m - 10} ${S} c 5 0 10 5 10 10 L ${m} ${y - 10} c 0 5 -5 10 -10 10 M ${m} ${x} h 10`, E), w = me(o, m + 20, x, { anchor: "start", color: N, dataType: "summary", svgId: L }));
  const A = mo(L);
  return A.appendChild(v), e.labelContainer.appendChild(w), he(w), A.summaryObj = t, A.labelEl = w, f.appendChild(A), A;
}, yo = function(e = {}) {
  if (!this.currentNodes)
    return;
  const { currentNodes: t, summaries: n, bus: o } = this, { parent: s, start: i, end: c } = go(t), r = { id: I(), parent: s, start: i, end: c, label: "summary", style: e.style }, l = Le(this, r);
  n.push(r), this.editSummary(l), o.fire("operation", {
    name: "createSummary",
    obj: r
  });
}, wo = function(e) {
  const t = I(), n = { ...e, id: t };
  Le(this, n), this.summaries.push(n), this.bus.fire("operation", {
    name: "createSummary",
    obj: n
  });
}, xo = function(e) {
  var n, o;
  const t = this.summaries.findIndex((s) => s.id === e);
  t > -1 && (this.summaries.splice(t, 1), (n = this.nodes.querySelector("#s-" + e)) == null || n.remove(), (o = this.nodes.querySelector("#label-s-" + e)) == null || o.remove()), this.bus.fire("operation", {
    name: "removeSummary",
    obj: { id: e }
  });
}, Co = function(e) {
  const t = e.labelEl;
  t && t.classList.add("selected"), this.currentSummary = e;
}, Eo = function() {
  var e, t;
  (t = (e = this.currentSummary) == null ? void 0 : e.labelEl) == null || t.classList.remove("selected"), this.currentSummary = null;
}, So = function() {
  this.summarySvg.innerHTML = "", this.summaries.forEach((e) => {
    try {
      Le(this, e);
    } catch {
    }
  }), this.nodes.insertAdjacentElement("beforeend", this.summarySvg);
}, No = function(e) {
  e && e.labelEl && et(this, e.labelEl, e.summaryObj);
}, ko = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  createSummary: yo,
  createSummaryFrom: wo,
  editSummary: No,
  removeSummary: xo,
  renderSummary: So,
  selectSummary: Co,
  unselectSummary: Eo
}, Symbol.toStringTag, { value: "Module" })), T = "http://www.w3.org/2000/svg";
function _o(e, t) {
  const n = document.createElementNS(T, "svg");
  return k(n, {
    version: "1.1",
    xmlns: T,
    height: e,
    width: t
  }), n;
}
function To(e, t) {
  return (parseInt(e) - parseInt(t)) / 2;
}
function Lo(e, t, n, o) {
  const s = document.createElementNS(T, "g");
  let i = "";
  return e.text ? i = e.text.textContent : i = e.childNodes[0].textContent, i.split(`
`).forEach((r, l) => {
    const d = document.createElementNS(T, "text");
    k(d, {
      x: n + parseInt(t.paddingLeft) + "",
      y: o + parseInt(t.paddingTop) + To(t.lineHeight, t.fontSize) * (l + 1) + parseFloat(t.fontSize) * (l + 1) + "",
      "text-anchor": "start",
      "font-family": t.fontFamily,
      "font-size": `${t.fontSize}`,
      "font-weight": `${t.fontWeight}`,
      fill: `${t.color}`
    }), d.innerHTML = r, s.appendChild(d);
  }), s;
}
function Ao(e, t, n, o) {
  var r;
  let s = "";
  (r = e.nodeObj) != null && r.dangerouslySetInnerHTML ? s = e.nodeObj.dangerouslySetInnerHTML : e.text ? s = e.text.textContent : s = e.childNodes[0].textContent;
  const i = document.createElementNS(T, "foreignObject");
  k(i, {
    x: n + parseInt(t.paddingLeft) + "",
    y: o + parseInt(t.paddingTop) + "",
    width: t.width,
    height: t.height
  });
  const c = document.createElement("div");
  return k(c, {
    xmlns: "http://www.w3.org/1999/xhtml",
    style: `font-family: ${t.fontFamily}; font-size: ${t.fontSize}; font-weight: ${t.fontWeight}; color: ${t.color}; white-space: pre-wrap;`
  }), c.innerHTML = s, i.appendChild(c), i;
}
function Mo(e, t) {
  const n = getComputedStyle(t), { offsetLeft: o, offsetTop: s } = O(e.nodes, t), i = document.createElementNS(T, "rect");
  return k(i, {
    x: o + "",
    y: s + "",
    rx: n.borderRadius,
    ry: n.borderRadius,
    width: n.width,
    height: n.height,
    fill: n.backgroundColor,
    stroke: n.borderColor,
    "stroke-width": n.borderWidth
  }), i;
}
function oe(e, t, n = !1) {
  const o = getComputedStyle(t), { offsetLeft: s, offsetTop: i } = O(e.nodes, t), c = document.createElementNS(T, "rect");
  k(c, {
    x: s + "",
    y: i + "",
    rx: o.borderRadius,
    ry: o.borderRadius,
    width: o.width,
    height: o.height,
    fill: o.backgroundColor,
    stroke: o.borderColor,
    "stroke-width": o.borderWidth
  });
  const r = document.createElementNS(T, "g");
  r.appendChild(c);
  let l;
  return n ? l = Ao(t, o, s, i) : l = Lo(t, o, s, i), r.appendChild(l), r;
}
function Do(e, t) {
  const n = getComputedStyle(t), { offsetLeft: o, offsetTop: s } = O(e.nodes, t), i = document.createElementNS(T, "a"), c = document.createElementNS(T, "text");
  return k(c, {
    x: o + "",
    y: s + parseInt(n.fontSize) + "",
    "text-anchor": "start",
    "font-family": n.fontFamily,
    "font-size": `${n.fontSize}`,
    "font-weight": `${n.fontWeight}`,
    fill: `${n.color}`
  }), c.innerHTML = t.textContent, i.appendChild(c), i.setAttribute("href", t.href), i;
}
function Po(e, t) {
  const n = getComputedStyle(t), { offsetLeft: o, offsetTop: s } = O(e.nodes, t), i = document.createElementNS(T, "image");
  return k(i, {
    x: o + "",
    y: s + "",
    width: n.width + "",
    height: n.height + "",
    href: t.src
  }), i;
}
const se = 100, $o = '<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">', Oo = (e, t = !1) => {
  var u, g, b;
  const n = e.nodes, o = n.offsetHeight + se * 2, s = n.offsetWidth + se * 2, i = _o(o + "px", s + "px"), c = document.createElementNS(T, "svg"), r = document.createElementNS(T, "rect");
  k(r, {
    x: "0",
    y: "0",
    width: `${s}`,
    height: `${o}`,
    fill: e.theme.cssVar["--bgcolor"]
  }), i.appendChild(r), n.querySelectorAll(".subLines").forEach((p) => {
    const m = p.cloneNode(!0), { offsetLeft: a, offsetTop: h } = O(n, p.parentElement);
    m.setAttribute("x", `${a}`), m.setAttribute("y", `${h}`), c.appendChild(m);
  });
  const l = (u = n.querySelector(".lines")) == null ? void 0 : u.cloneNode(!0);
  l && c.appendChild(l);
  const d = (g = n.querySelector(".topiclinks")) == null ? void 0 : g.cloneNode(!0);
  d && c.appendChild(d);
  const f = (b = n.querySelector(".summary")) == null ? void 0 : b.cloneNode(!0);
  return f && c.appendChild(f), n.querySelectorAll("me-tpc").forEach((p) => {
    p.nodeObj.dangerouslySetInnerHTML ? c.appendChild(oe(e, p, !t)) : (c.appendChild(Mo(e, p)), c.appendChild(oe(e, p.text, !t)));
  }), n.querySelectorAll(".tags > span").forEach((p) => {
    c.appendChild(oe(e, p));
  }), n.querySelectorAll(".icons > span").forEach((p) => {
    c.appendChild(oe(e, p));
  }), n.querySelectorAll(".hyper-link").forEach((p) => {
    c.appendChild(Do(e, p));
  }), n.querySelectorAll("img").forEach((p) => {
    c.appendChild(Po(e, p));
  }), k(c, {
    x: se + "",
    y: se + "",
    overflow: "visible"
  }), i.appendChild(c), i;
}, jo = (e, t) => (t && e.insertAdjacentHTML("afterbegin", "<style>" + t + "</style>"), $o + e.outerHTML);
function Ho(e) {
  return new Promise((t, n) => {
    const o = new FileReader();
    o.onload = (s) => {
      t(s.target.result);
    }, o.onerror = (s) => {
      n(s);
    }, o.readAsDataURL(e);
  });
}
const Bo = function(e = !1, t) {
  const n = Oo(this, e), o = jo(n, t);
  return new Blob([o], { type: "image/svg+xml" });
}, Ro = async function(e = !1, t) {
  const n = this.exportSvg(e, t), o = await Ho(n);
  return new Promise((s, i) => {
    const c = new Image();
    c.setAttribute("crossOrigin", "anonymous"), c.onload = () => {
      const r = document.createElement("canvas");
      r.width = c.width, r.height = c.height, r.getContext("2d").drawImage(c, 0, 0), r.toBlob(s, "image/png", 1);
    }, c.src = o, c.onerror = i;
  });
}, Fo = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  exportPng: Ro,
  exportSvg: Bo
}, Symbol.toStringTag, { value: "Module" }));
function Io(e, t) {
  return async function(...n) {
    const o = this.before[t];
    o && !await o.apply(this, n) || e.apply(this, n);
  };
}
const Ue = Object.keys(at), ft = {};
for (let e = 0; e < Ue.length; e++) {
  const t = Ue[e];
  ft[t] = Io(at[t], t);
}
const Wo = {
  getObjById: ie,
  generateNewObj: mt,
  layout: Nt,
  linkDiv: $t,
  editTopic: Dt,
  createWrapper: Tt,
  createParent: Lt,
  createChildren: At,
  createTopic: Mt,
  findEle: Je,
  changeTheme: cn,
  ...Zn,
  ...ft,
  ...po,
  ...ko,
  ...Fo,
  init(e) {
    if (e = JSON.parse(JSON.stringify(e)), !e || !e.nodeData)
      return new Error("MindElixir: `data` is required");
    e.direction !== void 0 && (this.direction = e.direction), this.changeTheme(e.theme || this.theme, !1), this.nodeData = e.nodeData, B(this.nodeData), this.arrows = e.arrows || [], this.summaries = e.summaries || [], this.tidyArrow(), this.toolBar && Zt(this), this.keypress && Ct(this, this.keypress), this.editable && rn(this), this.contextMenu && this.disposable.push(Ot(this, this.contextMenu)), this.draggable && this.disposable.push(Rt(this)), this.allowUndo && this.disposable.push(It(this)), this.layout(), this.linkDiv(), this.renderArrow && this.renderArrow(), this.toCenter();
  },
  destroy() {
    var e;
    this.disposable.forEach((t) => t()), this.el && (this.el.innerHTML = ""), this.el = void 0, this.nodeData = void 0, this.arrows = void 0, this.summaries = void 0, this.currentArrow = void 0, this.currentNodes = void 0, this.currentSummary = void 0, this.waitCopy = void 0, this.theme = void 0, this.direction = void 0, this.bus = void 0, this.container = void 0, this.map = void 0, this.lines = void 0, this.linkController = void 0, this.linkSvgGroup = void 0, this.P2 = void 0, this.P3 = void 0, this.line1 = void 0, this.line2 = void 0, this.nodes = void 0, (e = this.selection) == null || e.destroy(), this.selection = void 0;
  }
};
function Ko({ pT: e, pL: t, pW: n, pH: o, cT: s, cL: i, cW: c, cH: r, direction: l, containerHeight: d }) {
  let f = t + n / 2;
  const u = e + o / 2;
  let g;
  l === P.LHS ? g = i + c : g = i;
  const b = s + r / 2, m = (1 - Math.abs(b - u) / d) * 0.25 * (n / 2);
  return l === P.LHS ? f = f - n / 10 - m : f = f + n / 10 + m, `M ${f} ${u} Q ${f} ${b} ${g} ${b}`;
}
function Go({ pT: e, pL: t, pW: n, pH: o, cT: s, cL: i, cW: c, cH: r, direction: l, isFirst: d }) {
  const f = parseInt(this.container.style.getPropertyValue("--node-gap-x"));
  let u = 0, g = 0;
  d ? u = e + o / 2 : u = e + o;
  const b = s + r;
  let p = 0, m = 0, a = 0;
  const h = Math.abs(u - b) / 300 * f;
  return l === P.LHS ? (a = t, p = a + f, m = a - f, g = i + f, `M ${p} ${u} C ${a} ${u} ${a + h} ${b} ${m} ${b} H ${g}`) : (a = t + n, p = a - f, m = a + f, g = i + c - f, `M ${p} ${u} C ${a} ${u} ${a - h} ${b} ${m} ${b} H ${g}`);
}
const Yo = "5.2.1";
function qo(e) {
  return {
    x: 0,
    y: 0,
    moved: !1,
    // diffrentiate click and move
    mousedown: !1,
    onMove(t, n) {
      this.mousedown && (this.moved = !0, e.move(t, n));
    },
    clear() {
      this.mousedown = !1;
    }
  };
}
const K = document;
function $({
  el: e,
  direction: t,
  locale: n,
  draggable: o,
  editable: s,
  contextMenu: i,
  toolBar: c,
  keypress: r,
  mouseSelectionButton: l,
  selectionContainer: d,
  before: f,
  newTopicName: u,
  allowUndo: g,
  generateMainBranch: b,
  generateSubBranch: p,
  overflowHidden: m,
  theme: a,
  alignment: h,
  scaleSensitivity: v,
  scaleMax: w,
  scaleMin: C,
  handleWheel: S,
  markdown: y,
  imageProxy: x
}) {
  let E = null;
  const N = Object.prototype.toString.call(e);
  if (N === "[object HTMLDivElement]" ? E = e : N === "[object String]" && (E = document.querySelector(e)), !E)
    throw new Error("MindElixir: el is not a valid element");
  E.style.position = "relative", E.innerHTML = "", this.el = E, this.disposable = [], this.before = f || {}, this.locale = n || "en", this.newTopicName = u || "New Node", this.contextMenu = i ?? !0, this.toolBar = c ?? !0, this.keypress = r ?? !0, this.mouseSelectionButton = l ?? 0, this.direction = t ?? 1, this.draggable = o ?? !0, this.editable = s ?? !0, this.allowUndo = g ?? !0, this.scaleSensitivity = v ?? 0.1, this.scaleMax = w ?? 1.4, this.scaleMin = C ?? 0.2, this.generateMainBranch = b || Ko, this.generateSubBranch = p || Go, this.overflowHidden = m ?? !1, this.alignment = h ?? "root", this.handleWheel = S ?? !0, this.markdown = y || void 0, this.imageProxy = x || void 0, this.currentNodes = [], this.currentArrow = null, this.scaleVal = 1, this.tempDirection = null, this.dragMoveHelper = qo(this), this.bus = St(), this.container = K.createElement("div"), this.selectionContainer = d || this.container, this.container.className = "map-container";
  const L = window.matchMedia("(prefers-color-scheme: dark)");
  this.theme = a || (L.matches ? xe : we);
  const A = K.createElement("div");
  A.className = "map-canvas", this.map = A, this.container.setAttribute("tabindex", "0"), this.container.appendChild(this.map), this.el.appendChild(this.container), this.nodes = K.createElement("me-nodes"), this.lines = J("lines"), this.summarySvg = J("summary"), this.linkController = J("linkcontroller"), this.P2 = K.createElement("div"), this.P3 = K.createElement("div"), this.P2.className = this.P3.className = "circle", this.P2.style.display = this.P3.style.display = "none", this.line1 = Oe(), this.line2 = Oe(), this.linkController.appendChild(this.line1), this.linkController.appendChild(this.line2), this.linkSvgGroup = J("topiclinks"), this.labelContainer = K.createElement("div"), this.labelContainer.className = "label-container", this.map.appendChild(this.nodes), this.overflowHidden ? this.container.style.overflow = "hidden" : this.disposable.push(Et(this));
}
$.prototype = Wo;
Object.defineProperty($.prototype, "currentNode", {
  get() {
    return this.currentNodes[this.currentNodes.length - 1];
  },
  enumerable: !0
});
$.LEFT = 0;
$.RIGHT = 1;
$.SIDE = 2;
$.THEME = we;
$.DARK_THEME = xe;
$.version = Yo;
$.E = Je;
$.new = (e) => ({
  nodeData: {
    id: I(),
    topic: e || "new topic",
    children: []
  }
});
export {
  $ as default
};

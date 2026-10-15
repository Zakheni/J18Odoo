/* Virtual Office - HUD / DOM chrome.
 * Top bar, participants, chat, media controls and the live minimap. Pure DOM;
 * it knows nothing about Three.js or WebRTC, it just renders state and raises
 * callbacks in opts.
 */
(function () {
    "use strict";
    var VO = (window.VO = window.VO || {});

    function el(tag, cls, html) {
        var n = document.createElement(tag);
        if (cls) n.className = cls;
        if (html != null) n.innerHTML = html;
        return n;
    }

    function UI(root, opts) {
        this.root = root;
        this.opts = opts || {};
        this.state = { mic: true, cam: false, sharing: false, audio: true };
        this.chatOpen = true;
        this.unread = 0;
        this.lastChatId = 0;
        this._build();
    }

    UI.prototype._build = function () {
        var self = this;
        this.root.innerHTML = "";

        this.topbar = el("div", "vo-topbar");
        this.topbar.innerHTML =
            '<div class="vo-brand"><span class="vo-logo"></span>' +
            '<span class="vo-officename"></span></div>' +
            '<div class="vo-centerinfo"><span class="vo-roomname"></span></div>' +
            '<div class="vo-topactions">' +
            (this.opts.canEditLayout
                ? '<button class="vo-btn vo-btn-ghost" data-act="layout">Edit layout</button>'
                : "") +
            '<button class="vo-btn vo-btn-ghost" data-act="view">Top view</button>' +
            '<button class="vo-btn vo-btn-ghost" data-act="invite">Invite</button>' +
            '<button class="vo-btn vo-btn-danger" data-act="leave">Leave</button>' +
            "</div>";
        this.root.appendChild(this.topbar);
        this.officename = this.topbar.querySelector(".vo-officename");
        this.roomname = this.topbar.querySelector(".vo-roomname");

        this.sidebar = el("div", "vo-sidebar");
        this.sidebar.innerHTML =
            '<div class="vo-sec"><h4>In this room</h4><ul class="vo-list vo-peers"></ul></div>' +
            '<div class="vo-sec"><h4>Around the office</h4><ul class="vo-list vo-everyone"></ul></div>';
        this.root.appendChild(this.sidebar);
        this.peerList = this.sidebar.querySelector(".vo-peers");
        this.everyoneList = this.sidebar.querySelector(".vo-everyone");

        this.chat = el("div", "vo-chat");
        this.chat.innerHTML =
            '<div class="vo-chat-head">Room chat<button class="vo-chat-toggle" title="Collapse">&ndash;</button></div>' +
            '<ul class="vo-chat-log"></ul>' +
            '<form class="vo-chat-form"><input type="text" placeholder="Message the office..." maxlength="1000" autocomplete="off"/><button type="submit">Send</button></form>';
        this.root.appendChild(this.chat);
        this.chatLog = this.chat.querySelector(".vo-chat-log");
        this.chatForm = this.chat.querySelector(".vo-chat-form");
        this.chatInput = this.chatForm.querySelector("input");

        this.controls = el("div", "vo-controls");
        this.controls.innerHTML =
            '<button class="vo-ctrl" data-act="mic" title="Toggle microphone"><span class="vo-ic">{</span><span class="vo-lbl">Mic</span></button>' +
            '<button class="vo-ctrl" data-act="cam" title="Toggle camera"><span class="vo-ic">}</span><span class="vo-lbl">Cam</span></button>' +
            '<button class="vo-ctrl" data-act="share" title="Share your screen"><span class="vo-ic">[]</span><span class="vo-lbl">Share</span></button>' +
            '<button class="vo-ctrl vo-ctrl-on" data-act="audio" title="Mute all incoming audio"><span class="vo-ic">~</span><span class="vo-lbl">Audio</span></button>' +
            '<button class="vo-ctrl" data-act="move" title="Click the floor or use WASD to move"><span class="vo-ic">+</span><span class="vo-lbl">Move</span></button>';
        this.root.appendChild(this.controls);

        this.minimap = el("div", "vo-minimap");
        this.canvas = el("canvas", "vo-minimap-canvas");
        this.minimap.appendChild(this.canvas);
        this.root.appendChild(this.minimap);

        this.toast = el("div", "vo-toast");
        this.root.appendChild(this.toast);
        this.statusDot = el("div", "vo-statusdot");
        this.root.appendChild(this.statusDot);

        // --- events ---
        this.topbar.addEventListener("click", function (e) {
            var act = e.target.getAttribute && e.target.getAttribute("data-act");
            if (!act) return;
            if (act === "leave" && self.opts.onLeave) self.opts.onLeave();
            if (act === "invite" && self.opts.onInvite) self.opts.onInvite(self);
            if (act === "layout" && self.opts.onEditLayout) self.opts.onEditLayout();
            if (act === "view" && self.opts.onViewMode) {
                self._viewTop = !self._viewTop;
                e.target.textContent = self._viewTop ? "Follow view" : "Top view";
                self.opts.onViewMode(self._viewTop ? "top" : "follow");
            }
        });
        this.controls.addEventListener("click", function (e) {
            var btn = e.target.closest(".vo-ctrl");
            if (!btn) return;
            var act = btn.getAttribute("data-act");
            if (act === "mic") self.setSelf({ mic_on: !self.state.mic });
            else if (act === "cam") self.setSelf({ camera_on: !self.state.cam });
            else if (act === "share") {
                if (self.opts.onScreenshare) self.opts.onScreenshare();
            } else if (act === "audio") {
                self.state.audio = !self.state.audio;
                self._paintControls();
                if (self.opts.onToggleAudio) self.opts.onToggleAudio(self.state.audio);
            }
        });
        this.chatForm.addEventListener("submit", function (e) {
            e.preventDefault();
            var text = self.chatInput.value.trim();
            if (!text || !self.opts.onSendChat) return;
            self.opts.onSendChat(text);
            self.chatInput.value = "";
        });
        this.chat.querySelector(".vo-chat-toggle").addEventListener("click", function () {
            self.chat.classList.toggle("vo-chat-collapsed");
            if (self.chat.classList.contains("vo-chat-collapsed")) self._clearUnread();
        });
        this.chatInput.addEventListener("focus", function () {
            self._clearUnread();
        });
    };

    UI.prototype.setOffice = function (layout) {
        this.officename.textContent = layout.name || "Virtual Office";
        this.layout = layout;
    };

    UI.prototype.setRoom = function (name) {
        this.roomname.textContent = name ? "You are in \u00b7 " + name : "";
    };

    UI.prototype.setStatus = function (text, ok) {
        this.statusDot.textContent = text || "";
        this.statusDot.className = "vo-statusdot " + (ok ? "ok" : "warn");
        this.statusDot.style.opacity = text ? "1" : "0";
    };

    UI.prototype.setSelf = function (partial) {
        if ("mic_on" in partial) this.state.mic = partial.mic_on;
        if ("camera_on" in partial) this.state.cam = partial.camera_on;
        if ("screen_sharing" in partial) this.state.sharing = partial.screen_sharing;
        this._paintControls();
        if (this.opts.onSelfChange) {
            this.opts.onSelfChange({
                mic_on: this.state.mic,
                camera_on: this.state.cam,
                screen_sharing: this.state.sharing,
            });
        }
    };

    UI.prototype._paintControls = function () {
        var map = { mic: this.state.mic, cam: this.state.cam, share: this.state.sharing, audio: this.state.audio };
        Object.keys(map).forEach(
            function (act) {
                var btn = this.controls.querySelector('[data-act="' + act + '"]');
                if (btn) btn.classList.toggle("vo-ctrl-on", !!map[act]);
            },
            this
        );
    };

    UI.prototype.setSpeaking = function (peerId, speaking, selfPeer) {
        var node = this.peerList.querySelector('[data-peer="' + peerId + '"]');
        if (node) node.classList.toggle("vo-speaking", speaking);
    };

    UI.prototype.setPeers = function (peers, everyone, me) {
        var self = this;
        this.peerList.innerHTML = "";
        this.everyoneList.innerHTML = "";
        peers.forEach(function (p) {
            self.peerList.appendChild(self._personNode(p));
        });
        if (!peers.length) {
            this.peerList.appendChild(el("li", "vo-empty", "No one else in this room. Walk to another room to find people."));
        }
        var others = (everyone || []).filter(function (p) {
            return !me || p.peer_id !== me.peer_id;
        });
        var inRoomIds = peers.map(function (p) {
            return p.peer_id;
        });
        others
            .filter(function (p) {
                return p.room_id && inRoomIds.indexOf(p.peer_id) === -1;
            })
            .forEach(function (p) {
                self.everyoneList.appendChild(self._personNode(p, true));
            });
        if (!this.everyoneList.children.length) {
            this.everyoneList.appendChild(el("li", "vo-empty", "No one else is online right now."));
        }
    };

    UI.prototype._personNode = function (p, away) {
        var dev = p.device_status || (p.state === "online" ? "present" : p.state || "present");
        var isAway = dev !== "present";
        var li = el("li", "vo-person" + (away || isAway ? " vo-away" : ""));
        li.setAttribute("data-peer", p.peer_id);
        var cam = p.camera_on || p.screen_sharing;
        li.innerHTML =
            '<span class="vo-avatar" style="background:' + (p.color || "#4A90D9") + '">' +
            (p.name || "?").charAt(0).toUpperCase() +
            "</span>" +
            '<span class="vo-pname">' +
            (p.name || "Guest") +
            (p.is_guest ? ' <em class="vo-guest">guest</em>' : "") +
            "</span>" +
            '<span class="vo-picons"><i class="' + (p.mic_on ? "on" : "off") + '">mic</i>' +
            '<i class="' + (cam ? "on" : "off") + '">cam</i></span>';
        if (isAway) {
            var label = dev === "gone" ? "gone" : dev;
            if (p.away_minutes) label += " " + p.away_minutes + "m";
            li.appendChild(el("span", "vo-away-badge", label));
        }
        return li;
    };

    UI.prototype.addChat = function (msg, selfPeer) {
        if (!msg || msg.id <= this.lastChatId) return;
        this.lastChatId = msg.id;
        var li = el("li", "vo-msg" + (msg.is_system ? " vo-sys" : "") + (msg.author_peer_id === selfPeer ? " vo-mine" : ""));
        if (msg.is_system) {
            li.innerHTML = '<span class="vo-sysbody">' + escapeHtml(msg.body) + "</span>";
        } else {
            li.innerHTML =
                '<span class="vo-author">' + escapeHtml(msg.author) + "</span>" +
                '<span class="vo-body">' + escapeHtml(msg.body) + "</span>";
        }
        this.chatLog.appendChild(li);
        while (this.chatLog.children.length > 200) this.chatLog.removeChild(this.chatLog.firstChild);
        this.chatLog.scrollTop = this.chatLog.scrollHeight;
        if (this.chat.classList.contains("vo-chat-collapsed") && msg.author_peer_id !== selfPeer && !msg.is_system) {
            this.unread++;
            this._paintUnread();
        }
    };

    UI.prototype._paintUnread = function () {
        var head = this.chat.querySelector(".vo-chat-head");
        var badge = head.querySelector(".vo-unread");
        if (this.unread > 0) {
            if (!badge) badge = el("span", "vo-unread", "");
            badge.textContent = String(this.unread);
            head.appendChild(badge);
        } else if (badge) {
            badge.remove();
        }
    };

    UI.prototype._clearUnread = function () {
        this.unread = 0;
        this._paintUnread();
    };

    UI.prototype.toast = function (msg, ms) {
        var self = this;
        this.toast.textContent = msg;
        this.toast.classList.add("vo-toast-show");
        clearTimeout(this._toastT);
        this._toastT = setTimeout(function () {
            self.toast.classList.remove("vo-toast-show");
        }, ms || 3500);
    };

    UI.prototype.promptInvite = function (joinUrl, guestUrl) {
        var text = "Join my virtual office:\n" + joinUrl + (guestUrl ? "\n\nGuest link:\n" + guestUrl : "");
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(joinUrl).then(
                function () {
                    // noop
                },
                function () {
                    // noop
                }
            );
        }
        return text;
    };

    UI.prototype.drawMinimap = function (layout, everyone, me) {
        var c = this.canvas;
        if (!c) return;
        var ctx = c.getContext("2d");
        var dpr = Math.min(window.devicePixelRatio || 1, 2);
        var W = c.clientWidth || 190;
        var H = c.clientHeight || 140;
        if (c.width !== W * dpr) {
            c.width = W * dpr;
            c.height = H * dpr;
        }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, W, H);
        ctx.fillStyle = "rgba(14,17,24,0.82)";
        ctx.fillRect(0, 0, W, H);
        var fw = layout.floor.width || 24;
        var fd = layout.floor.depth || 18;
        var pad = 8;
        var sx = (W - pad * 2) / fw;
        var sy = (H - pad * 2) / fd;
        function toX(x) {
            return pad + (x + fw / 2) * sx;
        }
        function toY(z) {
            return pad + (z + fd / 2) * sy;
        }
        (layout.rooms || []).forEach(function (r) {
            ctx.fillStyle = hexA(r.color || "#4A90D9", 0.22);
            ctx.strokeStyle = hexA(r.color || "#4A90D9", 0.8);
            ctx.lineWidth = 1;
            var x = toX(r.position.x - r.size.w / 2);
            var y = toY(r.position.y - r.size.d / 2);
            ctx.fillRect(x, y, r.size.w * sx, r.size.d * sy);
            ctx.strokeRect(x, y, r.size.w * sx, r.size.d * sy);
        });
        (everyone || []).forEach(function (p) {
            if (!p.position) return;
            var isMe = me && p.peer_id === me.peer_id;
            ctx.beginPath();
            ctx.arc(toX(p.position.x), toY(p.position.y), isMe ? 3.6 : 2.6, 0, Math.PI * 2);
            ctx.fillStyle = isMe ? "#ffffff" : p.camera_on ? "#2ECC71" : "#8892a6";
            ctx.fill();
            if (isMe) {
                ctx.strokeStyle = "#7C4DFF";
                ctx.lineWidth = 2;
                ctx.stroke();
            }
        });
    };

    function escapeHtml(s) {
        return String(s == null ? "" : s)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    function hexA(hex, a) {
        hex = hex.replace("#", "");
        if (hex.length === 3) hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
        var r = parseInt(hex.substr(0, 2), 16);
        var g = parseInt(hex.substr(2, 2), 16);
        var b = parseInt(hex.substr(4, 2), 16);
        return "rgba(" + r + "," + g + "," + b + "," + a + ")";
    }

    VO.UI = UI;
})();

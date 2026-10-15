/* Virtual Office - application wiring.
 * Joins the office, builds the 3D scene, sets up the WebRTC mesh and spatial
 * audio, then runs the heartbeat loop that carries presence, position,
 * signalling and chat between the browser and Odoo.
 */
(function () {
    "use strict";
    var VO = window.VO;
    var boot = VO.boot || {};
    var app = document.getElementById("vo-app");
    var loading = document.getElementById("vo-loading");

    var state = {
        token: null,
        peerId: null,
        self: null,
        office: boot.office,
        roomId: null,
        sinceChatId: 0,
        dirty: false,
        ended: false,
        inRoom: {},
        heartbeatMs: 900,
    };

    // --- device-presence: report idle when the tab is hidden and away when
    // there has been no mouse/keyboard activity in the tab for a while.
    var AWAY_AFTER_MS = 5 * 60 * 1000;
    var lastActivity = Date.now();
    ["mousemove", "keydown", "mousedown", "touchstart", "scroll"].forEach(function (ev) {
        document.addEventListener(ev, function () { lastActivity = Date.now(); }, { passive: true });
    });
    function myDeviceState() {
        if (document.hidden) return "idle";
        if (Date.now() - lastActivity > AWAY_AFTER_MS) return "away";
        return "online";
    }

    var scene = null;
    var rtc = null;
    var audio = null;
    var hbTimer = null;
    var layoutEditor = null;

    var ui = new VO.UI(app, {
        canEditLayout: !!boot.canEditLayout,
        onLeave: leave,
        onInvite: invite,
        onViewMode: function (m) {
            if (scene) scene.setViewMode(m);
        },
        onScreenshare: toggleShare,
        onToggleAudio: function (on) {
            if (audio) audio.setMuted(!on);
        },
        onSendChat: sendChat,
        onEditLayout: openLayoutEditor,
        onSelfChange: function () {
            state.dirty = true;
        },
    });
    ui.setOffice(state.office);

    function roomName(id) {
        var rooms = (state.office && state.office.rooms) || [];
        for (var i = 0; i < rooms.length; i++) {
            if (rooms[i].id === id) return rooms[i].name;
        }
        return "";
    }

    function showError(msg) {
        if (loading) {
            loading.innerHTML =
                '<div class="vo-card vo-error-card"><h2>Could not join</h2><p>' +
                String(msg || "Unknown error") +
                '</p><button class="vo-btn" onclick="location.reload()">Try again</button></div>';
            loading.style.display = "flex";
        }
    }

    function start() {
        VO.API.join(state.office.id, null).then(function (res) {
            if (!res.ok) {
                showError(res.error);
                return;
            }
            state.token = res.token;
            state.peerId = res.peer_id;
            state.self = res.self;
            state.roomId = res.room_id;
            if (res.office) state.office = res.office;
            boot.selfPeer = state.peerId;
            build();
        });
    }

    function build() {
        if (loading) loading.style.display = "none";

        var stage = document.createElement("div");
        stage.id = "vo-stage";
        document.body.insertBefore(stage, app);

        scene = new VO.Scene(stage, state.office, {
            selfPeer: state.peerId,
            onMove: function () {
                state.dirty = true;
            },
            onCamera: function (camPos) {
                if (!audio) return;
                var f = new THREE.Vector3(
                    scene.player.x - camPos.x,
                    0,
                    scene.player.z - camPos.z
                );
                if (f.lengthSq() > 0.0001) f.normalize();
                audio.setListener(camPos.x, camPos.y, camPos.z, f.x, f.z);
            },
        });
        scene.setViewMode("follow");

        audio = new VO.SpatialAudio();

        rtc = new VO.RTC({
            api: VO.API,
            token: state.token,
            selfPeer: state.peerId,
            onStream: function (peerId, stream) {
                scene.setPeerStream(peerId, stream);
                audio.ensure();
                audio.attach(peerId, stream);
            },
            onRemove: function (peerId) {
                audio.detach(peerId);
                scene.removePeer(peerId);
            },
            onState: function (peerId, st) {
                if (st === "failed" || st === "disconnected") {
                    scene.removePeer(peerId);
                    audio.detach(peerId);
                }
            },
        });

        rtc.initMedia()
            .then(function (stream) {
                scene.setLocalStream(stream);
                ui.setSelf({ mic_on: true, camera_on: stream.getVideoTracks().length > 0 });
                audio.ensure();
            })
            .catch(function () {
                ui.toast("No camera or microphone available - you can still see and hear others.");
                ui.setSelf({ mic_on: false, camera_on: false });
            });

        scene.updatePeer(state.peerId, state.self);
        ui.setRoom(roomName(state.roomId));

        window.addEventListener("beforeunload", function () {
            if (state.token && navigator.sendBeacon) {
                var blob = new Blob([JSON.stringify({ token: state.token })], {
                    type: "application/json",
                });
                navigator.sendBeacon(boot.api + "/leave", blob);
            }
            if (rtc) rtc.closeAll();
        });

        loop();
    }

    function payload() {
        var pos = scene.getMyPosition();
        var roomId = scene.roomAt(pos.x, pos.z);
        return {
            token: state.token,
            pos_x: pos.x,
            pos_y: pos.z,
            rotation_y: pos.rot,
            room_id: roomId,
            state: myDeviceState(),
            camera_on: ui.state.cam,
            mic_on: ui.state.mic,
            screen_sharing: ui.state.sharing,
            since_chat_id: state.sinceChatId,
        };
    }

    function loop() {
        if (state.ended) return;
        state.dirty = false;
        VO.API.heartbeat(payload()).then(handleHeartbeat).finally(function () {
            if (state.ended) return;
            var ms = state.dirty ? 180 : state.heartbeatMs;
            hbTimer = setTimeout(loop, ms);
        });
    }

    function handleHeartbeat(res) {
        if (!res || !res.ok) {
            if (res && res.error) {
                ui.setStatus(res.error, false);
                if (/session|expired|Invalid/i.test(res.error)) {
                    showError("Your session expired. Please rejoin.");
                }
            }
            return;
        }
        ui.setStatus("connected", true);
        state.self = res.self;

        if (res.room_id !== state.roomId) {
            state.roomId = res.room_id;
            ui.setRoom(roomName(res.room_id));
        }

        scene.updatePeer(state.peerId, res.self);

        var present = {};
        (res.peers || []).forEach(function (p) {
            present[p.peer_id] = true;
            scene.updatePeer(p.peer_id, p);
            if (audio && p.position) {
                audio.setPosition(p.peer_id, p.position.x, 1.5, p.position.y);
            }
            if (!state.inRoom[p.peer_id]) {
                if (rtc) rtc.connect(p.peer_id);
            }
        });
        Object.keys(state.inRoom).forEach(function (id) {
            if (!present[id]) {
                if (rtc) rtc.disconnect(id);
                scene.removePeer(id);
            }
        });
        state.inRoom = present;

        ui.setPeers(res.peers || [], res.everyone || [], res.self);
        ui.drawMinimap(state.office, res.everyone || [], res.self);

        // signalling (offer/answer/ice/bye) - process in order
        var chain = Promise.resolve();
        (res.signals || []).forEach(function (s) {
            chain = chain.then(function () {
                return rtc.handleSignal(s.from, s.kind, s.payload);
            });
        });

        (res.chat || []).forEach(function (m) {
            state.sinceChatId = Math.max(state.sinceChatId, m.id);
            ui.addChat(m, state.peerId);
        });
    }

    function sendChat(text) {
        var pos = scene.getMyPosition();
        var roomId = scene.roomAt(pos.x, pos.z);
        VO.API.chatSend(state.token, text, roomId).then(function (res) {
            if (res.ok && res.message) ui.addChat(res.message, state.peerId);
        });
    }

    function toggleShare() {
        if (ui.state.sharing) {
            rtc.stopScreenShare();
            ui.setSelf({ screen_sharing: false });
        } else {
            rtc.startScreenShare()
                .then(function () {
                    ui.setSelf({ screen_sharing: true });
                    ui.toast("Sharing your screen. Click Share again to stop.");
                })
                .catch(function (e) {
                    ui.toast("Screen share cancelled.");
                });
        }
    }

    function invite() {
        function copy(url, label) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(
                    function () {
                        ui.toast(label + " copied to clipboard.");
                    },
                    function () {
                        window.prompt(label, url);
                    }
                );
            } else {
                window.prompt(label, url);
            }
        }
        if (boot.isPublic) {
            VO.API.guestCreate(state.token, "").then(function (res) {
                if (res.ok && res.url) {
                    copy(res.url, "Guest link");
                } else {
                    copy(boot.joinUrl, "Join link");
                }
            });
        } else {
            copy(boot.joinUrl, "Join link");
        }
    }

    function openLayoutEditor() {
        if (!scene) return;
        if (!layoutEditor) {
            layoutEditor = new VO.LayoutEditor(scene, {
                officeId: state.office.id,
                onSave: saveLayout,
                onReset: reloadLayout,
                onClose: function () {
                    ui.toast("Layout editor closed.");
                },
            });
            app.appendChild(layoutEditor.panel);
        }
        layoutEditor.enable();
        ui.toast("Layout editor: drag a room to move it, drag a corner to resize.");
    }

    function saveLayout(payload) {
        VO.API.layoutSave(payload).then(function (res) {
            if (res.ok && res.office) {
                state.office = res.office;
                scene.setLayout(res.office);
                ui.setOffice(res.office);
                if (layoutEditor) layoutEditor.clearSelection();
                ui.toast("Layout saved.");
            } else {
                ui.toast("Could not save layout: " + (res.error || "unknown error"));
            }
        });
    }

    function reloadLayout() {
        VO.API.layoutLoad(state.office.id).then(function (res) {
            if (res.ok && res.office) {
                state.office = res.office;
                scene.setLayout(res.office);
                ui.setOffice(res.office);
                if (layoutEditor) layoutEditor.clearSelection();
                ui.toast("Layout reset to the saved version.");
            } else {
                ui.toast("Could not reload layout.");
            }
        });
    }

    function leave() {
        state.ended = true;
        if (hbTimer) clearTimeout(hbTimer);
        VO.API.leave(state.token).finally(function () {
            if (rtc) rtc.closeAll();
            if (audio) audio.close();
            app.innerHTML =
                '<div class="vo-card vo-center-card"><h1>You left the office</h1>' +
                '<p class="text-muted">Thanks for dropping in.</p>' +
                (boot.isGuest
                    ? ""
                    : '<a class="vo-btn vo-btn-primary" href="/virtual-office">Rejoin</a>') +
                "</div>";
            app.classList.add("vo-center");
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();

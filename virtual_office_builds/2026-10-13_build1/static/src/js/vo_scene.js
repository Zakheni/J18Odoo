/* Virtual Office - 3D scene (Three.js).
 *
 * Renders the office floor and rooms, and one "avatar" per attendee: a real
 * webcam video panel (THREE.VideoTexture) floating in the 3D space with a name
 * tag. Panels billboard toward the camera so faces stay readable. The local
 * player walks with WASD or click-to-move; room membership is derived from the
 * player's position so walking into a room joins that room.
 *
 * Server coordinates (pos_x, pos_y floor, pos_z height) map to Three.js as:
 *   worldX = pos_x,  worldY = pos_z (up),  worldZ = pos_y.
 */
(function () {
    "use strict";
    var VO = (window.VO = window.VO || {});

    var UP = new THREE.Vector3(0, 1, 0);

    function makeTextSprite(text, opts) {
        opts = opts || {};
        var fontSize = opts.fontSize || 42;
        var pad = 18;
        var lines = String(text).split("\n");
        var canvas = document.createElement("canvas");
        var ctx = canvas.getContext("2d");
        ctx.font = "600 " + fontSize + "px 'Segoe UI', system-ui, sans-serif";
        var w = 0;
        lines.forEach(function (l) {
            w = Math.max(w, ctx.measureText(l).width);
        });
        var lineH = fontSize * 1.25;
        canvas.width = Math.ceil(w + pad * 2);
        canvas.height = Math.ceil(lineH * lines.length + pad * 2);
        ctx = canvas.getContext("2d");
        ctx.fillStyle = opts.bg || "rgba(17,20,28,0.72)";
        if (opts.round !== false) {
            var r = 14;
            ctx.beginPath();
            ctx.moveTo(r, 0);
            ctx.arcTo(canvas.width, 0, canvas.width, canvas.height, r);
            ctx.arcTo(canvas.width, canvas.height, 0, canvas.height, r);
            ctx.arcTo(0, canvas.height, 0, 0, r);
            ctx.arcTo(0, 0, canvas.width, 0, r);
            ctx.closePath();
            ctx.fill();
        } else {
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        ctx.font = "600 " + fontSize + "px 'Segoe UI', system-ui, sans-serif";
        ctx.fillStyle = opts.color || "#ffffff";
        ctx.textBaseline = "top";
        lines.forEach(function (l, i) {
            ctx.fillText(l, pad, pad + i * lineH);
        });
        var tex = new THREE.CanvasTexture(canvas);
        tex.encoding = THREE.sRGBEncoding;
        tex.minFilter = THREE.LinearFilter;
        var mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false });
        var sprite = new THREE.Sprite(mat);
        var scale = opts.scale || 0.010;
        sprite.scale.set(canvas.width * scale, canvas.height * scale, 1);
        sprite.renderOrder = 999;
        return sprite;
    }

    function initials(name) {
        var parts = String(name || "?").trim().split(/\s+/);
        var s = (parts[0] || "?").charAt(0) + (parts[1] ? parts[1].charAt(0) : "");
        return s.toUpperCase();
    }

    function Scene(container, layout, opts) {
        this.container = container;
        this.layout = layout;
        this.opts = opts || {};
        this.rooms = [];
        this.avatars = {};
        this.keys = {};
        this.target = null;
        this.player = { x: 0, z: 0, rot: 0 };
        this.camDist = 11;
        this.camYaw = 0;
        this.camPitch = 0.85;
        this._dragging = false;
        this._dragMoved = 0;
        this._lastPointer = null;
        this._myState = { camera_on: false, mic_on: false, name: "You", color: "#7C4DFF" };
        this._init();
    }

    Scene.prototype._init = function () {
        var self = this;
        var w = this.container.clientWidth || window.innerWidth;
        var h = this.container.clientHeight || window.innerHeight;

        this.scene = new THREE.Scene();
        var isDark = this.layout.floor && this.layout.floor.theme === "dark";
        var bg = isDark ? 0x0e1118 : 0xeef1f6;
        this.scene.background = new THREE.Color(bg);
        this.scene.fog = new THREE.Fog(bg, 40, 90);

        this.camera = new THREE.PerspectiveCamera(55, w / h, 0.1, 500);
        this.scene.add(this.camera);

        this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.setSize(w, h);
        if ("outputEncoding" in this.renderer && THREE.sRGBEncoding) {
            this.renderer.outputEncoding = THREE.sRGBEncoding;
        }
        this.renderer.domElement.className = "vo-canvas";
        this.container.appendChild(this.renderer.domElement);

        this.scene.add(new THREE.AmbientLight(0xffffff, 0.85));
        var hemi = new THREE.HemisphereLight(0xffffff, 0x334455, 0.55);
        hemi.position.set(0, 30, 0);
        this.scene.add(hemi);
        var dir = new THREE.DirectionalLight(0xffffff, 0.7);
        dir.position.set(12, 24, 8);
        this.scene.add(dir);

        this.raycaster = new THREE.Raycaster();
        this.pointer = new THREE.Vector2();

        this._buildFloor();
        this._buildRooms();
        this._bindInput();

        this.clock = new THREE.Clock();
        this._running = true;
        window.addEventListener("resize", function () {
            self.resize();
        });
        this._animate();
    };

    Scene.prototype._buildFloor = function () {
        var fw = this.layout.floor.width || 24;
        var fd = this.layout.floor.depth || 18;
        this.floorMesh = new THREE.Mesh(
            new THREE.PlaneGeometry(fw, fd),
            new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95, metalness: 0.0 })
        );
        this.floorMesh.rotation.x = -Math.PI / 2;
        this.floorMesh.name = "floor";
        this.scene.add(this.floorMesh);

        var grid = new THREE.GridHelper(Math.max(fw, fd), Math.max(fw, fd), 0xc8ced8, 0xdfe4ec);
        grid.position.y = 0.015;
        this.scene.add(grid);
    };

    Scene.prototype._buildRooms = function () {
        var self = this;
        (this.layout.rooms || []).forEach(function (r) {
            var cx = r.position.x;
            var cz = r.position.y; // floor plane
            var w = r.size.w;
            var d = r.size.d;
            var h = Math.min(r.size.h || 3, 3);
            var color = new THREE.Color(r.color || "#4A90D9");

            var mat = new THREE.MeshStandardMaterial({
                color: color,
                transparent: true,
                opacity: 0.18,
                roughness: 0.85,
            });
            var pad = new THREE.Mesh(new THREE.PlaneGeometry(w, d), mat);
            pad.rotation.x = -Math.PI / 2;
            pad.position.set(cx, 0.03, cz);
            self.scene.add(pad);

            var outlinePts = [
                new THREE.Vector3(cx - w / 2, 0.05, cz - d / 2),
                new THREE.Vector3(cx + w / 2, 0.05, cz - d / 2),
                new THREE.Vector3(cx + w / 2, 0.05, cz + d / 2),
                new THREE.Vector3(cx - w / 2, 0.05, cz + d / 2),
            ];
            var outline = new THREE.LineLoop(
                new THREE.BufferGeometry().setFromPoints(outlinePts),
                new THREE.LineBasicMaterial({ color: color })
            );
            self.scene.add(outline);

            // Low walls so you can still see across the office.
            var wallH = Math.max(0.7, h * 0.35);
            var wallMat = new THREE.MeshStandardMaterial({
                color: color,
                transparent: true,
                opacity: 0.32,
                roughness: 0.9,
            });
            var segments = [
                { sx: w, sz: 0.18, ox: cx, oz: cz - d / 2 },
                { sx: w, sz: 0.18, ox: cx, oz: cz + d / 2 },
                { sx: 0.18, sz: d, ox: cx - w / 2, oz: cz },
                { sx: 0.18, sz: d, ox: cx + w / 2, oz: cz },
            ];
            segments.forEach(function (s) {
                var wall = new THREE.Mesh(new THREE.BoxGeometry(s.sx, wallH, s.sz), wallMat);
                wall.position.set(s.ox, wallH / 2, s.oz);
                self.scene.add(wall);
            });

            var label = makeTextSprite(r.name, { fontSize: 40, color: "#ffffff", bg: "rgba(17,20,28,0.55)" });
            label.position.set(cx, wallH + 0.9, cz - d / 2);
            self.scene.add(label);

            self.rooms.push({
                id: r.id,
                name: r.name,
                cx: cx,
                cz: cz,
                w: w,
                d: d,
                color: r.color,
                capacity: r.capacity,
            });
        });
    };

    // ------------------------------------------------------------- avatars
    Scene.prototype._makeAvatar = function (peerId, data, isMe) {
        var av = { peerId: peerId, isMe: !!isMe, data: data || {} };
        var group = new THREE.Group();
        var color = new THREE.Color((data && data.color) || "#7C4DFF");
        av.color = color;

        // floor ring
        var ring = new THREE.Mesh(
            new THREE.RingGeometry(0.42, 0.58, 32),
            new THREE.MeshBasicMaterial({ color: color, transparent: true, opacity: 0.9, side: THREE.DoubleSide })
        );
        ring.rotation.x = -Math.PI / 2;
        ring.position.y = 0.06;
        group.add(ring);

        // body (simple capsule-ish standee)
        var body = new THREE.Mesh(
            new THREE.ConeGeometry(0.34, 1.0, 20),
            new THREE.MeshStandardMaterial({ color: color, roughness: 0.8 })
        );
        body.position.y = 0.5;
        group.add(body);

        // video panel
        var video = document.createElement("video");
        video.autoplay = true;
        video.playsInline = true;
        video.muted = true; // audio is played through the spatial-audio graph
        video.className = "vo-hidden-video";
        video.setAttribute("playsinline", "");
        this.container.appendChild(video);

        var tex = new THREE.VideoTexture(video);
        tex.minFilter = THREE.LinearFilter;
        tex.magFilter = THREE.LinearFilter;
        if (THREE.sRGBEncoding) tex.encoding = THREE.sRGBEncoding;
        var panelMat = new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide });
        var panel = new THREE.Mesh(new THREE.PlaneGeometry(1.7, 1.0), panelMat);
        panel.position.set(0, 1.55, 0);
        panel.visible = false;
        group.add(panel);

        // initials bubble (shown when camera off)
        var initialTex = this._initialsTexture((data && data.name) || "?");
        var bubbleMat = new THREE.MeshBasicMaterial({ map: initialTex, transparent: true, side: THREE.DoubleSide });
        var bubble = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 1.0), bubbleMat);
        bubble.position.set(0, 1.55, 0);
        group.add(bubble);

        // name + status label
        var label = makeTextSprite(this._labelText(data, isMe), {
            fontSize: 40,
            color: "#ffffff",
            bg: isMe ? "rgba(124,77,255,0.85)" : "rgba(17,20,28,0.72)",
        });
        label.position.set(0, 2.35, 0);
        group.add(label);

        group.position.set(0, 0, 0);
        this.scene.add(group);

        av.group = group;
        av.video = video;
        av.texture = tex;
        av.panel = panel;
        av.bubble = bubble;
        av.bubbleMat = bubbleMat;
        av.label = label;
        av.ring = ring;
        this.avatars[peerId] = av;
        return av;
    };

    Scene.prototype._initialsTexture = function (name) {
        var canvas = document.createElement("canvas");
        canvas.width = canvas.height = 256;
        var ctx = canvas.getContext("2d");
        ctx.fillStyle = "#1b1f2a";
        ctx.fillRect(0, 0, 256, 256);
        var grad = ctx.createLinearGradient(0, 0, 256, 256);
        grad.addColorStop(0, "#7C4DFF");
        grad.addColorStop(1, "#4A90D9");
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(128, 128, 108, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#ffffff";
        ctx.font = "700 108px 'Segoe UI', system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(initials(name), 128, 136);
        var tex = new THREE.CanvasTexture(canvas);
        if (THREE.sRGBEncoding) tex.encoding = THREE.sRGBEncoding;
        return tex;
    };

    Scene.prototype._labelText = function (data, isMe) {
        var name = (data && data.name) || "Guest";
        if (isMe) name = name + " (you)";
        var bits = [];
        bits.push(data && data.mic_on ? "mic on" : "muted");
        if (data && data.screen_sharing) bits.push("sharing");
        else bits.push(data && data.camera_on ? "live" : "camera off");
        return name + "\n" + bits.join(" | ");
    };

    Scene.prototype.updatePeer = function (peerId, data) {
        if (peerId === this.opts.selfPeer) {
            this._myState = data;
            if (!this.avatars["__me__"]) {
                this._makeAvatar("__me__", data, true);
            }
            var me = this.avatars["__me__"];
            me.data = data;
            me.color = new THREE.Color(data.color || "#7C4DFF");
            me.ring.material.color = me.color;
            me.group.children.forEach(function (c) {
                if (c.geometry && c.geometry.type === "ConeGeometry") c.material.color = me.color;
            });
            this._applyAvatarState(me, data, true);
            return;
        }
        var av = this.avatars[peerId] || this._makeAvatar(peerId, data, false);
        av.data = data;
        var colored = new THREE.Color(data.color || "#7C4DFF");
        av.color = colored;
        av.ring.material.color = colored;
        av.group.children.forEach(function (c) {
            if (c.geometry && c.geometry.type === "ConeGeometry") c.material.color = colored;
        });
        var p = data.position || { x: 0, y: 0, z: 0 };
        av.group.position.set(p.x, 0, p.y);
        av.group.rotation.y = data.rotation_y || 0;
        this._applyAvatarState(av, data, false);
    };

    Scene.prototype._applyAvatarState = function (av, data, isMe) {
        var hasVideo = !!(data.camera_on || (data.screen_sharing && !isMe));
        av.panel.visible = hasVideo && !!av.stream;
        av.bubble.visible = !av.panel.visible;
        av.label.material.map.dispose();
        var nl = makeTextSprite(this._labelText(data, isMe), {
            fontSize: 40,
            color: "#ffffff",
            bg: isMe ? "rgba(124,77,255,0.85)" : "rgba(17,20,28,0.72)",
        });
        av.label.material.map = nl.material.map;
        av.label.scale.copy(nl.scale);
        av.label.visible = true;
    };

    Scene.prototype.setPeerStream = function (peerId, stream) {
        var av = this.avatars[peerId];
        if (!av) {
            av = this._makeAvatar(peerId, { name: "Guest", color: "#4A90D9" }, false);
        }
        av.stream = stream;
        if (av.video.srcObject !== stream) {
            av.video.srcObject = stream;
            var p = av.video.play();
            if (p && p.catch) p.catch(function () {});
        }
        av.panel.visible = true;
        av.bubble.visible = false;
    };

    Scene.prototype.setLocalStream = function (stream) {
        if (!this.avatars["__me__"]) {
            this._makeAvatar("__me__", this._myState, true);
        }
        var me = this.avatars["__me__"];
        me.stream = stream;
        me.video.srcObject = stream;
        var p = me.video.play();
        if (p && p.catch) p.catch(function () {});
    };

    Scene.prototype.removePeer = function (peerId) {
        var av = this.avatars[peerId];
        if (!av) return;
        if (av.video) {
            av.video.srcObject = null;
            if (av.video.parentNode) av.video.parentNode.removeChild(av.video);
        }
        this.scene.remove(av.group);
        delete this.avatars[peerId];
    };

    // ------------------------------------------------------------ movement
    Scene.prototype._bindInput = function () {
        var self = this;
        var el = this.renderer.domElement;

        el.addEventListener("pointerdown", function (e) {
            self._dragging = true;
            self._dragMoved = 0;
            self._lastPointer = { x: e.clientX, y: e.clientY };
            el.setPointerCapture(e.pointerId);
        });
        el.addEventListener("pointermove", function (e) {
            if (!self._dragging) return;
            var dx = e.clientX - self._lastPointer.x;
            var dy = e.clientY - self._lastPointer.y;
            self._lastPointer = { x: e.clientX, y: e.clientY };
            self._dragMoved += Math.abs(dx) + Math.abs(dy);
            if (e.buttons & 2 || e.buttons & 1) {
                self.camYaw -= dx * 0.005;
                self.camPitch = Math.min(1.45, Math.max(0.35, self.camPitch - dy * 0.004));
            }
        });
        el.addEventListener("pointerup", function (e) {
            var moved = self._dragMoved;
            self._dragging = false;
            if (moved < 6) {
                self._clickToMove(e);
            }
        });
        el.addEventListener("contextmenu", function (e) {
            e.preventDefault();
        });
        el.addEventListener(
            "wheel",
            function (e) {
                e.preventDefault();
                self.camDist = Math.min(26, Math.max(4, self.camDist + e.deltaY * 0.01));
            },
            { passive: false }
        );

        window.addEventListener("keydown", function (e) {
            self.keys[e.code] = true;
        });
        window.addEventListener("keyup", function (e) {
            self.keys[e.code] = false;
        });
    };

    Scene.prototype._clickToMove = function (e) {
        var rect = this.renderer.domElement.getBoundingClientRect();
        this.pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        this.raycaster.setFromCamera(this.pointer, this.camera);
        var hit = this.raycaster.intersectObject(this.floorMesh, false)[0];
        if (hit) {
            this.target = { x: hit.point.x, z: hit.point.z };
        }
    };

    Scene.prototype.roomAt = function (x, z) {
        for (var i = 0; i < this.rooms.length; i++) {
            var r = this.rooms[i];
            if (Math.abs(x - r.cx) <= r.w / 2 && Math.abs(z - r.cz) <= r.d / 2) {
                return r.id;
            }
        }
        return this.rooms.length ? this.rooms[0].id : null;
    };

    Scene.prototype.setViewMode = function (mode) {
        this._viewMode = mode;
        if (mode === "top") {
            this.camPitch = 1.44;
            this.camDist = 22;
        } else {
            this.camPitch = 0.85;
            this.camDist = Math.max(8, Math.min(this.camDist, 16));
        }
    };

    Scene.prototype._updateMovement = function (dt) {
        var speed = 6.5 * dt;
        var move = { x: 0, z: 0 };
        var fwd = { x: Math.sin(this.camYaw), z: Math.cos(this.camYaw) };
        var right = { x: Math.cos(this.camYaw), z: -Math.sin(this.camYaw) };
        if (this.keys["KeyW"] || this.keys["ArrowUp"]) {
            move.x -= fwd.x;
            move.z -= fwd.z;
        }
        if (this.keys["KeyS"] || this.keys["ArrowDown"]) {
            move.x += fwd.x;
            move.z += fwd.z;
        }
        if (this.keys["KeyA"] || this.keys["ArrowLeft"]) {
            move.x -= right.x;
            move.z -= right.z;
        }
        if (this.keys["KeyD"] || this.keys["ArrowRight"]) {
            move.x += right.x;
            move.z += right.z;
        }
        var len = Math.hypot(move.x, move.z);
        var prevX = this.player.x;
        var prevZ = this.player.z;
        if (len > 0) {
            this.target = null;
            this.player.x += (move.x / len) * speed;
            this.player.z += (move.z / len) * speed;
            this.player.rot = Math.atan2(move.x, move.z);
        } else if (this.target) {
            var dx = this.target.x - this.player.x;
            var dz = this.target.z - this.player.z;
            var d = Math.hypot(dx, dz);
            if (d < 0.15) {
                this.target = null;
            } else {
                var step = Math.min(speed, d);
                this.player.x += (dx / d) * step;
                this.player.z += (dz / d) * step;
                this.player.rot = Math.atan2(dx, dz);
            }
        }

        // clamp to floor bounds
        var fw = (this.layout.floor.width || 24) / 2 - 0.6;
        var fd = (this.layout.floor.depth || 18) / 2 - 0.6;
        this.player.x = Math.max(-fw, Math.min(fw, this.player.x));
        this.player.z = Math.max(-fd, Math.min(fd, this.player.z));

        var moved = Math.hypot(this.player.x - prevX, this.player.z - prevZ);
        var me = this.avatars["__me__"];
        if (me) {
            me.group.position.set(this.player.x, 0, this.player.z);
            me.group.rotation.y = this.player.rot;
        }
        if (moved > 0.02 && this.opts.onMove) {
            this.opts.onMove(this.player.x, this.player.z, this.player.rot);
        }
    };

    Scene.prototype._updateCamera = function () {
        var cx = this.player.x - Math.sin(this.camYaw) * this.camDist * Math.cos(this.camPitch);
        var cz = this.player.z - Math.cos(this.camYaw) * this.camDist * Math.cos(this.camPitch);
        var cy = Math.sin(this.camPitch) * this.camDist + 1.2;
        this.camera.position.set(cx, cy, cz);
        this.camera.lookAt(this.player.x, 1.2, this.player.z);
    };

    Scene.prototype._billboard = function () {
        var camPos = this.camera.position;
        Object.keys(this.avatars).forEach(
            function (id) {
                var av = this.avatars[id];
                var p = av.group.position;
                var angle = Math.atan2(camPos.x - p.x, camPos.z - p.z);
                if (av.panel) av.panel.rotation.y = angle;
                if (av.bubble) av.bubble.rotation.y = angle;
            },
            this
        );
    };

    Scene.prototype._animate = function () {
        if (!this._running) return;
        var self = this;
        requestAnimationFrame(function () {
            self._animate();
        });
        var dt = Math.min(this.clock.getDelta(), 0.1);
        this._updateMovement(dt);
        this._updateCamera();
        this._billboard();
        if (this.opts.onCamera) this.opts.onCamera(this.camera.position);
        this.renderer.render(this.scene, this.camera);
    };

    Scene.prototype.resize = function () {
        var w = this.container.clientWidth || window.innerWidth;
        var h = this.container.clientHeight || window.innerHeight;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
    };

    Scene.prototype.getMyPosition = function () {
        return { x: this.player.x, z: this.player.z, rot: this.player.rot };
    };

    Scene.prototype.destroy = function () {
        this._running = false;
        this.renderer.dispose();
    };

    VO.Scene = Scene;
})();

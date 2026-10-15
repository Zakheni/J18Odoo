/* Virtual Office - floor-plan layout editor.
 *
 * Manager-only overlay that turns the 3D scene into a drag-and-drop floor
 * plan: drag a room to move it, drag a corner handle to resize, edit its
 * details in the side panel, then Save. It reuses the scene's own room meshes
 * (see vo_scene.js) so what you edit is exactly what attendees see.
 */
(function () {
    "use strict";
    var VO = (window.VO = window.VO || {});

    var ROOM_TYPES = [
        ["reception", "Reception"],
        ["open_space", "Open Space"],
        ["office", "Private Office"],
        ["pod", "Co-working Pod"],
        ["conference", "Conference Room"],
        ["lounge", "Lounge"],
        ["phone_booth", "Phone Booth"],
    ];

    var GRID = 0.5;

    function el(tag, cls, html) {
        var n = document.createElement(tag);
        if (cls) n.className = cls;
        if (html != null) n.innerHTML = html;
        return n;
    }

    function snap(v) {
        return Math.round(v / GRID) * GRID;
    }

    function round2(v) {
        return Math.round((v || 0) * 100) / 100;
    }

    function LayoutEditor(scene, opts) {
        this.scene = scene;
        this.opts = opts || {};
        this.active = false;
        this.selected = null;
        this.drag = null;
        this._handles = [];
        this._deleted = [];
        this._buildPanel();
        this._buildHandles();
        this._bind();
    }

    // --------------------------------------------------------------- panel
    LayoutEditor.prototype._buildPanel = function () {
        var self = this;
        var p = el("div", "vo-layout-panel");
        p.innerHTML =
            '<div class="vo-layout-head"><span>Layout editor</span>' +
            '<button class="vo-layout-close" title="Close">&times;</button></div>' +
            '<div class="vo-layout-body">' +
            '<p class="vo-layout-hint">Drag a room to move it. Drag a corner handle to resize. Drag empty floor to orbit.</p>' +
            '<div class="vo-layout-empty">Select a room to edit its details.</div>' +
            '<div class="vo-layout-fields" style="display:none">' +
            '<label>Name<input type="text" data-f="name" maxlength="128"/></label>' +
            '<label>Type<select data-f="room_type"></select></label>' +
            '<label>Capacity<input type="number" data-f="capacity" min="0" step="1"/></label>' +
            '<label>Colour<input type="color" data-f="color"/></label>' +
            '<label class="vo-layout-check"><input type="checkbox" data-f="is_private"/> Private room</label>' +
            '<div class="vo-layout-grid">' +
            '<label>X<input type="number" data-f="pos_x" step="0.5"/></label>' +
            '<label>Y<input type="number" data-f="pos_y" step="0.5"/></label>' +
            '<label>Width<input type="number" data-f="width" min="1" step="0.5"/></label>' +
            '<label>Depth<input type="number" data-f="depth" min="1" step="0.5"/></label>' +
            '<label>Height<input type="number" data-f="height" min="0.5" step="0.5"/></label>' +
            '<label>Rotation<input type="number" data-f="rotation_y" step="0.1"/></label>' +
            "</div></div></div>" +
            '<div class="vo-layout-actions">' +
            '<button class="vo-btn" data-act="add">+ Add room</button>' +
            '<button class="vo-btn vo-layout-danger" data-act="delete">Delete room</button>' +
            '<button class="vo-btn vo-btn-primary" data-act="save">Save layout</button>' +
            '<button class="vo-btn" data-act="reset">Reset</button>' +
            '<button class="vo-btn vo-btn-ghost" data-act="done">Done</button>' +
            "</div>";
        this.panel = p;
        this.fields = p.querySelector(".vo-layout-fields");
        this.empty = p.querySelector(".vo-layout-empty");

        var sel = p.querySelector('[data-f="room_type"]');
        ROOM_TYPES.forEach(function (t) {
            var o = document.createElement("option");
            o.value = t[0];
            o.textContent = t[1];
            sel.appendChild(o);
        });

        p.querySelector(".vo-layout-close").addEventListener("click", function () {
            self._close();
        });
        p.querySelector(".vo-layout-actions").addEventListener("click", function (e) {
            var act = e.target.getAttribute && e.target.getAttribute("data-act");
            if (act === "save") self.save();
            else if (act === "reset") self.reset();
            else if (act === "add") self.addRoom();
            else if (act === "delete") self.deleteRoom();
            else if (act === "done") self._close();
        });
        var body = p.querySelector(".vo-layout-body");
        body.addEventListener("input", function (e) {
            var f = e.target.getAttribute && e.target.getAttribute("data-f");
            if (f) self._applyField(f, e.target);
        });
        body.addEventListener("change", function (e) {
            var f = e.target.getAttribute && e.target.getAttribute("data-f");
            if (f) self._applyField(f, e.target);
        });
    };

    LayoutEditor.prototype._close = function () {
        this.disable();
        if (this.opts.onClose) this.opts.onClose();
    };

    // ------------------------------------------------------------- handles
    LayoutEditor.prototype._buildHandles = function () {
        var geo = new THREE.BoxGeometry(0.7, 0.25, 0.7);
        var mat = new THREE.MeshBasicMaterial({ color: 0x7c4dff });
        for (var i = 0; i < 4; i++) {
            var m = new THREE.Mesh(geo, mat);
            m.visible = false;
            m.userData.corner = i;
            this.scene.scene.add(m);
            this._handles.push(m);
        }
    };

    LayoutEditor.prototype._placeHandles = function (room) {
        var hw = room.w / 2;
        var hd = room.d / 2;
        var pts = [
            [room.cx - hw, room.cz - hd],
            [room.cx + hw, room.cz - hd],
            [room.cx + hw, room.cz + hd],
            [room.cx - hw, room.cz + hd],
        ];
        for (var i = 0; i < 4; i++) {
            this._handles[i].position.set(pts[i][0], 0.2, pts[i][1]);
            this._handles[i].visible = this.active;
        }
    };

    LayoutEditor.prototype._hideHandles = function () {
        this._handles.forEach(function (h) {
            h.visible = false;
        });
    };

    // ----------------------------------------------------------- selection
    LayoutEditor.prototype._select = function (room) {
        if (this.selected && this.selected !== room) {
            this.scene.setRoomHighlight(this.selected, false);
        }
        this.selected = room;
        if (!room) {
            this.fields.style.display = "none";
            this.empty.style.display = "";
            this._hideHandles();
            return;
        }
        this.scene.setRoomHighlight(room, true);
        this.fields.style.display = "";
        this.empty.style.display = "none";
        this._syncPanel(room);
        this._placeHandles(room);
    };

    LayoutEditor.prototype.clearSelection = function () {
        this._select(null);
    };

    LayoutEditor.prototype._syncPanel = function (room) {
        var f = this.fields;
        f.querySelector('[data-f="name"]').value = room.name || "";
        f.querySelector('[data-f="room_type"]').value = room.type || "open_space";
        f.querySelector('[data-f="capacity"]').value = room.capacity || 0;
        f.querySelector('[data-f="color"]').value = room.color || "#4A90D9";
        f.querySelector('[data-f="is_private"]').checked = !!room.isPrivate;
        f.querySelector('[data-f="pos_x"]').value = round2(room.cx);
        f.querySelector('[data-f="pos_y"]').value = round2(room.cz);
        f.querySelector('[data-f="width"]').value = round2(room.w);
        f.querySelector('[data-f="depth"]').value = round2(room.d);
        f.querySelector('[data-f="height"]').value = round2(room.h);
        f.querySelector('[data-f="rotation_y"]').value = round2(room.rotation_y);
    };

    LayoutEditor.prototype._applyField = function (field, input) {
        var room = this.selected;
        if (!room) return;
        var val;
        if (input.type === "checkbox") val = input.checked;
        else if (input.type === "number") {
            val = parseFloat(input.value);
            if (isNaN(val)) return;
        } else val = input.value;

        if (field === "name") room.name = val;
        else if (field === "room_type") room.type = val;
        else if (field === "capacity") room.capacity = Math.max(0, Math.round(val));
        else if (field === "is_private") room.isPrivate = val;
        else if (field === "pos_x") room.cx = val;
        else if (field === "pos_y") room.cz = val;
        else if (field === "width") room.w = Math.max(1, val);
        else if (field === "depth") room.d = Math.max(1, val);
        else if (field === "height") room.h = Math.max(0.5, val);
        else if (field === "rotation_y") room.rotation_y = val;
        else if (field === "color") {
            room.color = val;
            this._paintRoom(room);
            return;
        }

        this.scene.rebuildRoom(room);
        this.scene.setRoomHighlight(room, true);
        this._placeHandles(room);
    };

    LayoutEditor.prototype._paintRoom = function (room) {
        var c = new THREE.Color(room.color || "#4A90D9");
        if (room.pad) room.pad.material.color.set(c);
        if (room.outline) room.outline.material.color.set(c);
        if (room.group) {
            room.group.children.forEach(function (o) {
                if (o.geometry && o.geometry.type === "BoxGeometry" && o.material) {
                    o.material.color.set(c);
                }
            });
        }
    };

    // --------------------------------------------------------------- input
    LayoutEditor.prototype._bind = function () {
        var self = this;
        var el = this.scene.renderer.domElement;
        el.addEventListener("pointerdown", function (e) {
            if (self.active) self._onDown(e);
        });
        el.addEventListener("pointermove", function (e) {
            if (self.active) self._onMove(e);
        });
        el.addEventListener("pointerup", function (e) {
            if (self.active) self._onUp(e);
        });
        // Hidden delete: the button is hidden, so Delete/Backspace is the trigger.
        window.addEventListener("keydown", function (e) {
            if (!self.active) return;
            if (e.key !== "Delete" && e.key !== "Backspace") return;
            var tag = (document.activeElement && document.activeElement.tagName) || "";
            if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;
            if (!self.selected) return;
            e.preventDefault();
            self.deleteRoom();
        });
    };

    LayoutEditor.prototype._onDown = function (e) {
        var el = this.scene.renderer.domElement;
        try {
            el.setPointerCapture(e.pointerId);
        } catch (err) {
            /* pointer capture is best-effort */
        }
        this._last = { x: e.clientX, y: e.clientY };

        if (this.selected) {
            var h = this._pickHandle(e.clientX, e.clientY);
            if (h) {
                this.drag = { mode: "resize", corner: h.userData.corner, room: this.selected };
                return;
            }
        }
        var room = this.scene.pickRoom(e.clientX, e.clientY);
        if (room) {
            this._select(room);
            var p = this.scene.floorPoint(e.clientX, e.clientY);
            this.drag = {
                mode: "move",
                room: room,
                offX: p ? room.cx - p.x : 0,
                offZ: p ? room.cz - p.z : 0,
            };
        } else {
            this._select(null);
            this.drag = { mode: "orbit" };
        }
    };

    LayoutEditor.prototype._onMove = function (e) {
        if (!this.drag) return;
        var dx = e.clientX - this._last.x;
        var dy = e.clientY - this._last.y;
        this._last = { x: e.clientX, y: e.clientY };

        if (this.drag.mode === "orbit") {
            this.scene.camYaw -= dx * 0.005;
            this.scene.camPitch = Math.min(1.5, Math.max(0.35, this.scene.camPitch - dy * 0.004));
            return;
        }
        var p = this.scene.floorPoint(e.clientX, e.clientY);
        if (!p) return;
        var room = this.drag.room;
        if (this.drag.mode === "move") {
            room.cx = snap(p.x + this.drag.offX);
            room.cz = snap(p.z + this.drag.offZ);
            room.group.position.set(room.cx, 0, room.cz);
            this._placeHandles(room);
            this._syncPanel(room);
        } else if (this.drag.mode === "resize") {
            this._resize(room, this.drag.corner, p.x, p.z);
        }
    };

    LayoutEditor.prototype._onUp = function () {
        this.drag = null;
    };

    LayoutEditor.prototype._pickHandle = function (clientX, clientY) {
        var rect = this.scene.renderer.domElement.getBoundingClientRect();
        this.scene.pointer.x = ((clientX - rect.left) / rect.width) * 2 - 1;
        this.scene.pointer.y = -((clientY - rect.top) / rect.height) * 2 + 1;
        this.scene.raycaster.setFromCamera(this.scene.pointer, this.scene.camera);
        var hits = this.scene.raycaster.intersectObjects(this._handles, false);
        return hits.length ? hits[0].object : null;
    };

    LayoutEditor.prototype._resize = function (room, corner, px, pz) {
        var hw = room.w / 2;
        var hd = room.d / 2;
        // The corner opposite the one being dragged stays put.
        var fx = room.cx + (corner === 0 || corner === 3 ? hw : -hw);
        var fz = room.cz + (corner === 0 || corner === 1 ? hd : -hd);
        var nx = snap(px);
        var nz = snap(pz);
        var w = Math.max(1, Math.abs(nx - fx));
        var d = Math.max(1, Math.abs(nz - fz));
        var cx = (nx + fx) / 2;
        var cz = (nz + fz) / 2;
        if (w === room.w && d === room.d && cx === room.cx && cz === room.cz) return;
        room.w = w;
        room.d = d;
        room.cx = cx;
        room.cz = cz;
        this.scene.rebuildRoom(room);
        this.scene.setRoomHighlight(room, true);
        this._placeHandles(room);
        this._syncPanel(room);
    };

    // ------------------------------------------------------------- actions
    LayoutEditor.prototype.addRoom = function () {
        var w = 4;
        var d = 4;
        var spot = this._freeSpot(w, d);
        var room = {
            id: null,
            name: "New Room",
            type: "open_space",
            capacity: 4,
            isPrivate: false,
            cx: spot.x,
            cz: spot.z,
            w: w,
            d: d,
            h: 3,
            rotation_y: 0,
            color: "#4A90D9",
            data: null,
        };
        this.scene.addRoom(room);
        this._select(room);
        if (this.opts.onAdd) this.opts.onAdd(room);
    };

    // First free 1 m-grid slot that fits a w x d room without overlapping.
    LayoutEditor.prototype._freeSpot = function (w, d) {
        var floor = this.scene.layout.floor || {};
        var fw = (floor.width || 24) / 2 - w / 2 - 0.5;
        var fd = (floor.depth || 18) / 2 - d / 2 - 0.5;
        for (var x = -fw; x <= fw; x += 1.0) {
            for (var z = -fd; z <= fd; z += 1.0) {
                if (this._isFree(x, z, w, d)) return { x: snap(x), z: snap(z) };
            }
        }
        return { x: 0, z: 0 };
    };

    LayoutEditor.prototype._isFree = function (x, z, w, d) {
        var margin = 0.5;
        for (var i = 0; i < this.scene.rooms.length; i++) {
            var r = this.scene.rooms[i];
            if (
                Math.abs(x - r.cx) < (w + r.w) / 2 + margin &&
                Math.abs(z - r.cz) < (d + r.d) / 2 + margin
            ) {
                return false;
            }
        }
        return true;
    };

    // Remove the selected room. Deferred: a saved room's id is queued and only
    // unlinked on Save; a not-yet-saved room just disappears locally.
    LayoutEditor.prototype.deleteRoom = function () {
        var room = this.selected;
        if (!room) return;
        var label = room.name || "this room";
        if (!window.confirm('Delete "' + label + '"? It is removed from the office when you Save.')) {
            return;
        }
        if (room.id) this._deleted.push(room.id);
        this.scene.removeRoom(room);
        this._select(null);
    };

    // Called by the host after a successful save so queued deletes are not re-sent.
    LayoutEditor.prototype.markSaved = function () {
        this._deleted = [];
    };

    LayoutEditor.prototype.enable = function () {
        this.active = true;
        this.scene.setLayoutMode(true);
        this.panel.classList.add("vo-layout-open");
        this._select(null);
    };

    LayoutEditor.prototype.disable = function () {
        this.active = false;
        this.drag = null;
        this._select(null);
        this.scene.setLayoutMode(false);
        this.panel.classList.remove("vo-layout-open");
    };

    LayoutEditor.prototype.save = function () {
        var floor = this.scene.layout.floor || {};
        var payload = {
            office_id: this.opts.officeId,
            floor: {
                floor_width: floor.width,
                floor_depth: floor.depth,
                theme: floor.theme,
                brand_color: floor.brand_color,
            },
            rooms: this.scene.rooms.map(function (r) {
                return {
                    id: r.id,
                    name: r.name,
                    room_type: r.type,
                    capacity: r.capacity,
                    is_private: r.isPrivate,
                    color: r.color,
                    pos_x: r.cx,
                    pos_y: r.cz,
                    width: r.w,
                    depth: r.d,
                    height: r.h,
                    rotation_y: r.rotation_y,
                };
            }),
            deleted_room_ids: this._deleted.slice(),
        };
        if (this.opts.onSave) this.opts.onSave(payload);
    };

    LayoutEditor.prototype.reset = function () {
        if (this.opts.onReset) this.opts.onReset();
    };

    VO.LayoutEditor = LayoutEditor;
})();

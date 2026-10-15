/* Virtual Office - positional (spatial) audio.
 * Each remote peer's audio track is routed through an HRTF PannerNode whose
 * position tracks that peer's avatar in the 3D scene, and the listener sits at
 * the local player. Walk closer and they get louder; walk away and they fade.
 */
(function () {
    "use strict";
    var VO = (window.VO = window.VO || {});

    // Browsers will not start an AudioContext that was created before the user
    // has interacted with the page - it stays "suspended" and every node is
    // silent. This page builds the scene straight after join(), so the context
    // would never start: resume() called from the load path (or from an
    // incoming ontrack) is not a gesture and does nothing. Resume it from a real
    // input event instead, then unbind once it is running.
    var UNLOCK_EVENTS = ["pointerdown", "mousedown", "touchstart", "keydown"];

    function SpatialAudio() {
        this.ctx = null;
        this.master = null;
        this.nodes = {};
        this._muted = false;
        this._bindUnlock();
    }

    SpatialAudio.prototype._bindUnlock = function () {
        if (this._unlockBound) return;
        this._unlockBound = true;
        var self = this;
        function unbind() {
            UNLOCK_EVENTS.forEach(function (ev) {
                document.removeEventListener(ev, kick, true);
            });
        }
        function kick() {
            if (!self.ctx && !self.ensure()) return;
            var state = self.ctx.state;
            if (state === "running") {
                unbind();
                return;
            }
            if (state !== "suspended" || !self.ctx.resume) return;
            var p = self.ctx.resume();
            if (p && p.then) p.then(unbind, function () {
                /* still blocked - stay bound and try the next gesture */
            });
        }
        UNLOCK_EVENTS.forEach(function (ev) {
            document.addEventListener(ev, kick, true);
        });
    };

    SpatialAudio.prototype.ensure = function () {
        if (!this.ctx) {
            var AC = window.AudioContext || window.webkitAudioContext;
            if (!AC) return false;
            this.ctx = new AC();
            this.master = this.ctx.createGain();
            this.master.gain.value = this._muted ? 0 : 1;
            this.master.connect(this.ctx.destination);
            if (this.ctx.listener.positionX) {
                this.ctx.listener.positionX.value = 0;
                this.ctx.listener.positionY.value = 1.4;
                this.ctx.listener.positionZ.value = 0;
            }
        }
        if (this.ctx.state === "suspended") {
            this.ctx.resume();
        }
        return true;
    };

    SpatialAudio.prototype.attach = function (peerId, stream) {
        if (!stream || !stream.getAudioTracks || stream.getAudioTracks().length === 0) return;
        if (!this.ensure()) return;
        this.detach(peerId);
        var source = this.ctx.createMediaStreamSource(stream);
        var panner = this.ctx.createPanner();
        panner.panningModel = "HRTF";
        panner.distanceModel = "inverse";
        panner.refDistance = 1.2;
        panner.maxDistance = 30;
        panner.rolloffFactor = 1.6;
        panner.coneInnerAngle = 360;
        var gain = this.ctx.createGain();
        gain.gain.value = 1;
        source.connect(panner);
        panner.connect(gain);
        gain.connect(this.master);
        this.nodes[peerId] = { source: source, panner: panner, gain: gain };
    };

    SpatialAudio.prototype.detach = function (peerId) {
        var n = this.nodes[peerId];
        if (!n) return;
        try {
            n.source.disconnect();
            n.panner.disconnect();
            n.gain.disconnect();
        } catch (e) {
            /* already gone */
        }
        delete this.nodes[peerId];
    };

    SpatialAudio.prototype.setPosition = function (peerId, x, y, z) {
        var n = this.nodes[peerId];
        if (!n) return;
        if (n.panner.positionX) {
            n.panner.positionX.value = x;
            n.panner.positionY.value = y;
            n.panner.positionZ.value = z;
        } else if (n.panner.setPosition) {
            n.panner.setPosition(x, y, z);
        }
    };

    SpatialAudio.prototype.setListener = function (x, y, z, fx, fz) {
        if (!this.ctx || !this.ctx.listener) return;
        var L = this.ctx.listener;
        if (L.positionX) {
            L.positionX.value = x;
            L.positionY.value = y;
            L.positionZ.value = z;
            L.forwardX.value = fx || 0;
            L.forwardY.value = 0;
            L.forwardZ.value = fz || -1;
            L.upX.value = 0;
            L.upY.value = 1;
            L.upZ.value = 0;
        } else if (L.setPosition) {
            L.setPosition(x, y, z);
            if (L.setOrientation) L.setOrientation(fx || 0, 0, fz || -1, 0, 1, 0);
        }
    };

    SpatialAudio.prototype.setMuted = function (muted) {
        this._muted = !!muted;
        if (this.master) this.master.gain.value = muted ? 0 : 1;
    };

    SpatialAudio.prototype.close = function () {
        var self = this;
        Object.keys(this.nodes).forEach(function (id) {
            self.detach(id);
        });
        if (this.ctx) {
            try {
                this.ctx.close();
            } catch (e) {
                /* noop */
            }
        }
    };

    VO.SpatialAudio = SpatialAudio;
})();

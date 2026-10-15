/* Virtual Office - WebRTC mesh transport (peer-to-peer).
 *
 * Every attendee in a room is connected directly to every other attendee in
 * that room. This is the right trade-off for the small rooms a virtual office
 * has (2-6 people); for bigger rooms replace this class with an SFU client
 * (LiveKit/mediasoup) - the rest of the app only talks to its interface:
 *   connect(peerId), disconnect(peerId), handleSignal(), setCamEnabled(),
 *   setMicEnabled(), startScreenShare()/stopScreenShare(), onStream/onRemove.
 */
(function () {
    "use strict";
    var VO = (window.VO = window.VO || {});

    var RTC_CONFIG = {
        iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
        iceCandidatePoolSize: 4,
    };

    function RTC(opts) {
        this.api = opts.api;
        this.token = opts.token;
        this.selfPeer = opts.selfPeer;
        this.onStream = opts.onStream || function () {};
        this.onRemove = opts.onRemove || function () {};
        this.onState = opts.onState || function () {};
        this.peers = {};
        this.localStream = null;
        this.screenTrack = null;
        this.camTrack = null;
    }

    RTC.prototype.initMedia = function () {
        var self = this;
        var audio = {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
        };
        var video = { width: { ideal: 640 }, height: { ideal: 360 }, frameRate: { ideal: 24 } };
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            return Promise.reject(new Error("WebRTC is not available in this browser."));
        }
        return navigator.mediaDevices
            .getUserMedia({ video: video, audio: audio })
            .then(function (stream) {
                self.localStream = stream;
                self.camTrack = stream.getVideoTracks()[0] || null;
                return stream;
            })
            .catch(function (err) {
                // Retry audio-only if camera is denied/unavailable.
                return navigator.mediaDevices
                    .getUserMedia({ audio: audio })
                    .then(function (stream) {
                        self.localStream = stream;
                        return stream;
                    })
                    .catch(function () {
                        throw err;
                    });
            });
    };

    RTC.prototype._makePeer = function (peerId) {
        var self = this;
        var existing = this.peers[peerId];
        if (existing) return existing;

        var pc = new RTCPeerConnection(RTC_CONFIG);
        // Deterministic offerer: the lexicographically smaller peer id drives
        // negotiation, which avoids glare on first connect.
        var state = {
            pc: pc,
            offerer: this.selfPeer < peerId,
            makingOffer: false,
            ignoreOffer: false,
            polite: this.selfPeer > peerId,
            stream: null,
        };
        this.peers[peerId] = state;

        if (this.localStream) {
            this.localStream.getTracks().forEach(function (track) {
                pc.addTrack(track, self.localStream);
            });
        }

        pc.onicecandidate = function (ev) {
            if (ev.candidate) {
                self.api.signal(self.token, peerId, "candidate", ev.candidate).catch(function () {});
            }
        };
        pc.ontrack = function (ev) {
            state.stream = ev.streams[0] || new MediaStream([ev.track]);
            self.onStream(peerId, state.stream);
        };
        pc.onnegotiationneeded = function () {
            if (!state.offerer) return;
            state.makingOffer = true;
            pc.setLocalDescription()
                .then(function () {
                    return self.api.signal(self.token, peerId, "offer", pc.localDescription);
                })
                .catch(function (err) {
                    console.error("offer failed", err);
                })
                .finally(function () {
                    state.makingOffer = false;
                });
        };
        pc.onconnectionstatechange = function () {
            self.onState(peerId, pc.connectionState);
            if (pc.connectionState === "failed") {
                // One ICE restart attempt, then give up.
                if (!state.retried) {
                    state.retried = true;
                    pc.createOffer({ iceRestart: true })
                        .then(function (o) {
                            return pc.setLocalDescription(o);
                        })
                        .then(function () {
                            return self.api.signal(self.token, peerId, "offer", pc.localDescription);
                        })
                        .catch(function () {});
                }
            }
        };
        return state;
    };

    RTC.prototype.connect = function (peerId) {
        if (!peerId || peerId === this.selfPeer) return;
        this._makePeer(peerId);
    };

    RTC.prototype.disconnect = function (peerId, silent) {
        var state = this.peers[peerId];
        if (!state) return;
        if (!silent) {
            this.api.signal(this.token, peerId, "bye", null).catch(function () {});
        }
        try {
            state.pc.close();
        } catch (e) {
            /* noop */
        }
        delete this.peers[peerId];
        this.onRemove(peerId);
    };

    RTC.prototype.handleSignal = function (from, kind, payload) {
        var self = this;
        if (kind === "bye") {
            this.disconnect(from, true);
            return Promise.resolve();
        }
        var state = this._makePeer(from);
        var pc = state.pc;

        if (kind === "offer") {
            var collision = state.makingOffer || pc.signalingState !== "stable";
            state.ignoreOffer = !state.polite && collision;
            if (state.ignoreOffer) return Promise.resolve();
            return pc
                .setRemoteDescription(payload)
                .then(function () {
                    return pc.setLocalDescription();
                })
                .then(function () {
                    return self.api.signal(self.token, from, "answer", pc.localDescription);
                })
                .catch(function (err) {
                    console.error("handle offer", err);
                });
        }
        if (kind === "answer") {
            return pc.setRemoteDescription(payload).catch(function (err) {
                console.error("handle answer", err);
            });
        }
        if (kind === "candidate") {
            return pc.addIceCandidate(payload).catch(function (err) {
                if (!state.ignoreOffer) console.warn("ice", err);
            });
        }
        return Promise.resolve();
    };

    RTC.prototype.setCamEnabled = function (on) {
        if (this.localStream) {
            this.localStream.getVideoTracks().forEach(function (t) {
                t.enabled = on;
            });
        }
    };

    RTC.prototype.setMicEnabled = function (on) {
        if (this.localStream) {
            this.localStream.getAudioTracks().forEach(function (t) {
                t.enabled = on;
            });
        }
    };

    RTC.prototype.startScreenShare = function () {
        var self = this;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
            return Promise.reject(new Error("Screen sharing is not supported here."));
        }
        return navigator.mediaDevices.getDisplayMedia({ video: true }).then(function (stream) {
            self.screenTrack = stream.getVideoTracks()[0];
            self._replaceVideo(self.screenTrack);
            self.screenTrack.onended = function () {
                self.stopScreenShare();
            };
            return stream;
        });
    };

    RTC.prototype.stopScreenShare = function () {
        if (this.screenTrack) {
            try {
                this.screenTrack.stop();
            } catch (e) {
                /* noop */
            }
            this.screenTrack = null;
        }
        if (this.camTrack) this._replaceVideo(this.camTrack);
        else this._replaceVideo(null);
    };

    RTC.prototype._replaceVideo = function (track) {
        Object.keys(this.peers).forEach(function (id) {
            var sender = this.peers[id].pc
                .getSenders()
                .find(function (s) {
                    return s.track && s.track.kind === "video";
                });
            if (sender) sender.replaceTrack(track).catch(function () {});
        }, this);
    };

    RTC.prototype.closeAll = function () {
        var self = this;
        Object.keys(this.peers).forEach(function (id) {
            self.disconnect(id, true);
        });
        if (this.localStream) {
            this.localStream.getTracks().forEach(function (t) {
                t.stop();
            });
        }
        if (this.screenTrack) {
            try {
                this.screenTrack.stop();
            } catch (e) {
                /* noop */
            }
        }
    };

    VO.RTC = RTC;
})();

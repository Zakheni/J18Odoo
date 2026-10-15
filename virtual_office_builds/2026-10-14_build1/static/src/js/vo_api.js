/* Virtual Office - API client. Talks to /virtual-office/api/*. */
(function () {
    "use strict";
    var VO = (window.VO = window.VO || {});

    var boot = {};
    try {
        boot = JSON.parse(document.getElementById("vo-bootstrap").textContent || "{}");
    } catch (e) {
        boot = {};
    }
    VO.boot = boot;

    function post(path, data) {
        return fetch(boot.api + path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify(data || {}),
        })
            .then(function (res) {
                return res.json().catch(function () {
                    return { ok: false, error: "Malformed response (" + res.status + ")" };
                });
            })
            .catch(function (err) {
                return { ok: false, error: String(err && err.message ? err.message : err) };
            });
    }

    VO.API = {
        base: boot.api,
        join: function (officeId, roomId) {
            return post("/join", {
                office_id: officeId,
                room_id: roomId || undefined,
                guest_token: boot.guestToken || undefined,
            });
        },
        heartbeat: function (payload) {
            return post("/heartbeat", payload);
        },
        leave: function (token) {
            return post("/leave", { token: token });
        },
        signal: function (token, to, kind, payload) {
            return post("/signal", { token: token, to: to, kind: kind, payload: payload });
        },
        chatSend: function (token, body, roomId) {
            return post("/chat/send", { token: token, body: body, room_id: roomId });
        },
        chatHistory: function (token, sinceId) {
            return post("/chat/history", { token: token, since_chat_id: sinceId });
        },
        guestCreate: function (token, name, email) {
            return post("/guest/create", { token: token, name: name, email: email });
        },
    };
})();

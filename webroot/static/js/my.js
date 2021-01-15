/**
 * 
 *
 *   (c) 2021 Yoichi Tanibayashi
 */
let ws = undefined;
let buf = '';

/**
 *
 */
const get_url = () => {
    let protocol = 'ws';
    if ( location.protocol == 'https:' ) {
        protocol = 'wss';
    }
    
    let url = `${protocol}://${location.host}/storgan/ws/`;
    return url;
};

/**
 *
 */
const open = () => {
    ws = new WebSocket(get_url());

    ws.onopen = () => {
        console.log(`onopen`);
    };

    ws.onclose = () => {
        console.log(`onclose()`);
        open();
    };

    ws.onmessage = (event) => {
        console.log(`onmessage(): ${event.data}`);

        const msg = event.data;

        const el = document.getElementById("message_area");
        let msg_text = el.value;
        msg_text += msg;

        el.value = msg_text;
        el.scrollTop = el.scrollHeight;
    };
};

/**
 *
 */
const send_msg = () => {
    const el = document.getElementById('message_in');
    const msg = el.value;
    el.value = '';

    ws.send(msg);
};

/**
 *
 */
window.onload = () => {
    console.log(`window.onload()`);

    open();
};

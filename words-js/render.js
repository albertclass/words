const ipc = require('electron').ipcMain

var inputSpan = null
console.log("initialize scripts")

window.onload = function(e) {
    console.log('js onload', Date.now());
    inputSpan = document.getElementById("input");
    this.console.log(inputSpan);
}

document.onkeydown = function(e) {
    var keycode = e.which;
    var keychar = e.key;
    
    console.log("code = " + keycode + " char = " + keychar)
    inputSpan = document.getElementById("input");

    if (keycode > 0x1f && keycode <= 127) {
        inputSpan.innerText += keychar
    }

    if (keycode == 0x0a) {
        ipc.emit("confirm", inputSpan.innerText)
    }

    if (keycode == 0x1b) {
        ipc.emit("exit")
    }
}

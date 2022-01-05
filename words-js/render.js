const {ipcRenderer, ipcMain} = require('electron')
let words = [
    {
        spell: 'police',
        symbol: [
            "pə'liːs", // en
            "pə'liːs", // us
        ],
        pronunciation: [
            "https://dictionary.blob.core.chinacloudapi.cn/media/audio/tom/fb/31/FB31FC8179317552F1A6D86EABA60259.mp3", // en
            "https://dictionary.blob.core.chinacloudapi.cn/media/audio/george/fb/31/FB31FC8179317552F1A6D86EABA60259.mp3", // us
        ],
        explains: [
            ['n.', '警方；警察部门'],
            ['v.', '长官'],
            ['网络', '警察局；警务人员；警察当局']
        ]
    }, 
    { 
        word: 'office'
    },
    {
        word: 'station'
    }
]

let count = 0

let saved = null
let input = null
let length = 0
let keypos = 0

console.log("initialize scripts")

function beep() {
    var snd = new Audio("data:audio/wav;base64,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qJrx4KOQjahZxWbcZgztj2c49nKmkId44S71j0c8eV9yDK6uPRzx5X18eDvjvQ6yKo9ZSS6l//8elePK/Lf//IInrOF/FvDoADYAGBMGb7FtErm5MXMlmPAJQVgWta7Zx2go+8xJ0UiCb8LHHdftWyLJE0QIAIsI+UbXu67dZMjmgDGCGl1H+vpF4NSDckSIkk7Vd+sxEhBQMRU8j/12UIRhzSaUdQ+rQU5kGeFxm+hb1oh6pWWmv3uvmReDl0UnvtapVaIzo1jZbf/pD6ElLqSX+rUmOQNpJFa/r+sa4e/pBlAABoAAAAA3CUgShLdGIxsY7AUABPRrgCABdDuQ5GC7DqPQCgbbJUAoRSUj+NIEig0YfyWUho1VBBBA//uQZB4ABZx5zfMakeAAAAmwAAAAF5F3P0w9GtAAACfAAAAAwLhMDmAYWMgVEG1U0FIGCBgXBXAtfMH10000EEEEEECUBYln03TTTdNBDZopopYvrTTdNa325mImNg3TTPV9q3pmY0xoO6bv3r00y+IDGid/9aaaZTGMuj9mpu9Mpio1dXrr5HERTZSmqU36A3CumzN/9Robv/Xx4v9ijkSRSNLQhAWumap82WRSBUqXStV/YcS+XVLnSS+WLDroqArFkMEsAS+eWmrUzrO0oEmE40RlMZ5+ODIkAyKAGUwZ3mVKmcamcJnMW26MRPgUw6j+LkhyHGVGYjSUUKNpuJUQoOIAyDvEyG8S5yfK6dhZc0Tx1KI/gviKL6qvvFs1+bWtaz58uUNnryq6kt5RzOCkPWlVqVX2a/EEBUdU1KrXLf40GoiiFXK///qpoiDXrOgqDR38JB0bw7SoL+ZB9o1RCkQjQ2CBYZKd/+VJxZRRZlqSkKiws0WFxUyCwsKiMy7hUVFhIaCrNQsKkTIsLivwKKigsj8XYlwt/WKi2N4d//uQRCSAAjURNIHpMZBGYiaQPSYyAAABLAAAAAAAACWAAAAApUF/Mg+0aohSIRobBAsMlO//Kk4soosy1JSFRYWaLC4qZBYWFRGZdwqKiwkNBVmoWFSJkWFxX4FFRQWR+LsS4W/rFRb/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////VEFHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAU291bmRib3kuZGUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMjAwNGh0dHA6Ly93d3cuc291bmRib3kuZGUAAAAAAAAAACU=");
    snd.play();
}

function next() {
    if (count == words.length) {
        return true
    }

    let w = words[count]
    let e = document.getElementById('input')

    keypos = 0
    length = w.spell.length
    input = new Array(length)
    saved = new Array(length)

    for (let i = 0; i < w.spell.length; ++i) {
        input[i] = '_';
        saved[i] = w.spell.charAt(i)
    }

    e.innerText = input.join(' ');

    ++count
}

function onKeyDown(e) {
    let key = e.keyCode
    let pass = false

    if (key == 32 || key == 222) {
        pass = true;
    }

    if (key >= 65 && key <= 90) {
        pass = true
        if (false == e.shiftKey) {
            key += 32
        }
    }

    if (false == pass)
        return

    cch = String.fromCharCode(key)
    if (keypos < length) {
        if (cch != saved[keypos]) {
            beep()
        } else {
            input[keypos] = cch
            let ele = document.getElementById('input')
            ele.innerText = input.join(' ')

            ++keypos
        }
    }

    if (keypos == length) {
        next()
    }
}

ipcRenderer.on('users', (event, users) => {
    let ele = document.getElementById('users');
    if (ele === null) return
    ele.innerHTML = ""
   
    if (users == null || users.count == 0) return

    for (let idx in users) {
        let spn = document.createElement('span')
        let btn = document.createElement('input')
        btn.id = users[idx]
        btn.type = "button"
        btn.className = "accountBtn"
        btn.value = users[idx]
        btn.onclick = function() { 
            ipcRenderer.send('user-logon', this.value)
        }

        spn.appendChild(btn)
        ele.appendChild(spn)
    }

    let spl = document.createElement('span')
    spl.innerHTML = "<hr/>"
    ele.appendChild(spl)

    let spn = document.createElement('span')
    let acc = document.createElement('input')
    acc.id="accountName"
    acc.type="edit"
    acc.className="accountInput"
    acc.placeholder="请输入创建的账号名字..."

    let btn = document.createElement('input')
    btn.type = "button"
    btn.className = "accountBtn"
    btn.value = "创建新用户"
    btn.onclick = function() {
        if (acc.value == null || acc.value.length == 0) {
            acc.placeholder="账号名为空，创建账号失败..."
            return;
        }

        ipcRenderer.send('createUser', acc.value)
    }
    spn.appendChild(acc)
    spn.appendChild(btn)

    ele.appendChild(spn)
})

ipcRenderer.on('init', (event, args) => {
    words = args
    next()
    document.addEventListener('keydown', onKeyDown)
})

ipcRenderer.on('user-login', (event, err, msg) => {
    let login = document.getElementById('login')
    let begin = document.getElementById('begin')
    
    function hide(id) {
        let e = document.getElementById(id)
        if (e) {
            e.style.display = 'none'
        }

        return e;
    }

    function show(id, attr) {
        let e = document.getElementById(id)
        if (e) {
            e.style.display = attr ? attr : 'block'
        }

        return e;
    }

    if (err == 1) {
        hide('login')
        hide('begin')
        show('message')

        let e = document.getElementById('content')
        e.innerText = msg;
        return
    }

    if (err != 0) {
        hide('login')
        hide('begin')
        show('message')

        let e = document.getElementById('content')
        e.innerText = msg;
    } else {
        hide('login')
        hide('message')
        show('begin', 'flex')
    }
})

let add = document.getElementById('add');
if (add) {
    add.addEventListener("click", function () {
        let words = document.getElementById('newwords');
        if (words && words.length > 0) {
            let arr = words.split(", ")
            arr.forEach(word => {
                ipcRenderer.send('addWord', word)
            });
        }
    })
}
ipcRenderer.send('windowLoaded')

const { app, BrowserWindow, Menu, dialog, webContents } = require("electron")
const ipc = require("electron").ipcMain
const fs = require('fs')
const xpath = require('xpath')
const http = require('http')
const sqlite3 = require('sqlite3')

let win
let dict
let task = {
    total : 0,
    words : {

    }
}

let menuTemplate = [
    {
        label: 'File',
        submenu: [
            { label: 'Load', click : (event, focusedWindow, focusedWebContents) => app.emit('file-load', event, focusedWindow, focusedWebContents)},
            { type: 'separator'},
            { role: 'quit'}
        ]
    }
]

let sqls = [
    'CREATE TABLE IF NOT EXISTS "main"."dict"(\
        "id" integer not null primary key autoincrement,\
        "word" text,\
        "symbol" text,\
        "explain" text,\
        "example" text,\
        "en" blob,\
        "us" blob\
    );',

    'CREATE TABLE IF NOT EXISTS "main"."user"(\
        "id" integer not null primary key autoincrement,\
        "username" text,\
        "password" text,\
        "nickname" text,\
        "lastbook" text\
    );',

    'CREATE TABLE IF NOT EXISTS "main"."examine"(\
        "userid" integer not null,\
        "bookname" text,\
        "examine" text,\
        PRIMARY KEY(userid, bookname)\
    );'
]

function initDatabase(cb) {
    dict = new sqlite3.Database("dict.db", (err) => {
        if (err) {
            console.log(err)
            return
        }

        Promise.all(sqls.map((sql) => new Promise(function(resolve, reject) {
            dict.run(sql, (err) => {
                if (err) {
                    reject(err)
                } else {
                    resolve()
                }
            })
        }))).then(cb)
    })
}

function new_book(user, bookname, examine) {
    dict.run('replace into \
    "main"."examine" (userid, bookname, examine) \
    values (${user}, "${bookname}", "${examine}");', (res, err) => {
        if (err) {
            console.log(err)
            return
        }

        console.log(res)
    })
}

function load_page(word, cb) {
    const options = {
        hostname: "cn.bing.com",
        port: 80,
        path: "/dict/search?q=" + word,
        method: "GET",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    }

    let req = http.request(options, (res) => {
        if (res.statusCode != 200) {
            return
        }

        res.setEncoding('utf8')

        buf = new Buffer()
        res.on("data", (chunk) => {
            buf += chunk
        })

        res.on("end", () => {
            load_symbol(buf)
            load_pronunciation(buf)
            load_explain(buf)
        })
    })

    req.end()
}

function load_symbol(buf) {

}

function load_pronunciation(buf) {

}

function load_explain(buf) {

}

function load(word, cb) {
    let stat = dict.get("select word, symbol, explain, example, en, us from dict where word = '?'", word, (err, row) => {
        if (err) {
            load_page(word, cb)
        } else if (row != null) {
            task.words[word] = row
            cb()
        } else {
            load_page(word, cb)
        }
    })
}

function load_book(filename) {
    buf = fs.readFileSync(filename)
    all = buf.toString().split(/[\t\r\n ]/, -1).filter((v) => v.length > 0)
    all.forEach(word => { load(word) })
}

function createWindow() {
    win = new BrowserWindow({
        width: 800,
        height: 600,
        center: true,
        webPreferences: {
            nodeIntegration: true
        }
    })

    Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate))
    
    win.loadFile("index.html")
    win.on('close', () => {
        win = null
    })

    win.webContents.on('did-finish-load', (event, args) => {
        console.log('webContents load finished.')
    })
}

ipc.on('windowLoaded', (event) => {
    event.sender.send('init', ['police', 'office', 'station'])
})

initDatabase((err) => {
    if (err.filter((err) => err ? true : false).length > 0) {
        console.log(err)
    } else {
        console.log('database initialize successful.')
    }
});

// Electron 会在初始化后并准备
// 创建浏览器窗口时，调用这个函数。
// 部分 API 在 ready 事件触发后才能使用。
app.on('ready', createWindow)

// 当全部窗口关闭时退出。
app.on('window-all-closed', () => {
    // 在 macOS 上，除非用户用 Cmd + Q 确定地退出，
    // 否则绝大部分应用及其菜单栏会保持激活。
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', () => {
    // 在macOS上，当单击dock图标并且没有其他窗口打开时，
    // 通常在应用程序中重新创建一个窗口。
    if (win === null) {
        createWindow()
    }
})

app.on('file-load', (event, focusedWindow, focusedWebContents) => {
    dialog.showOpenDialog({
        title: '选择要背诵的单词书', 
        filters: [
            { name: '单词表', extensions: ['txt'] },
            { name: '所有文件', extensions: ['*'] }
        ],
        properties:['openFile']
    }).then(result=>{
        if (result.canceled) {
            return
        }
        
        result.filePaths.forEach(path => {
            load_book(path)
        })
    }).catch(err => {
        console.log(err)
    })
})
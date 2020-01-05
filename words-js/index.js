const { app, BrowserWindow } = require("electron")
const ipc = require('electron').ipcRenderer
const fs = require('fs')
const xpath = require('xpath')
const http = require('http')
const sqlite3 = require('sqlite3')

let win

let task = {
    total : 0,
    words : {

    }
}

let dict = new sqlite3.Database("dict.db", (err) => {
    if (err) {
        console.log(err)
        return
    }

    dict.run('CREATE TABLE IF NOT EXIST "main"."dict"(\
        "id" integer not null primary key autoincrement,\
        "word" text,\
        "symbol" text,\
        "explain" text,\
        "example" text,\
        "en" blob,\
        "us" blob\
    );', (res, err) => {
        if (err) {
            console.log(err)
            return
        }

        console.log(res)
    })

    dict.run('CREATE TABLE IF NOT EXIST "main"."user"(\
        "id" integer not null primary key autoincrement,\
        "username" text,\
        "password" text,\
        "nickname" text,\
        "lastbook" text\
    );', (res, err) => {
        if (err) {
            console.log(err)
            return
        }

        console.log(res)
    })

    
    dict.run('CREATE TABLE IF NOT EXIST "main"."examine"(\
        "userid" integer not null,\
        "bookname" text,\
        "examine" text,\
        PARIMARY KEY(userid, bookname)\
    );', (res, err) => {
        if (err) {
            console.log(err)
            return
        }

        console.log(res)
    })
})

function new_book(user, book, words) {
    dict.run('replace into \
    "main"."examine" (userid, bookname, examine) \
    values (${user}, "${book}", "${words}");', (res, err) => {
        if (err) {
            console.log(err)
            return
        }

        console.log(res)
    })
}

function load_page(word) {
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
            load_pronunciation(buf)
            load_explain(buf)
            load_example(buf)
        })
    })

    req.end()
}

function load(word) {

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

    win.loadFile("index.html")

    buf = fs.readFileSync("book.txt")
    all = buf.toString().split("[\t\n ]")
    for (word in all) {
        load(word)
    }

    win.on('close', () => {
        win = null
    })
}

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

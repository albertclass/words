const { app, BrowserWindow, Menu, dialog, webContents } = require("electron")
const ipc = require("electron").ipcMain
const fs = require('fs')
const http = require('http')
const cheerio = require('cheerio')

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
    },
    {
        label: 'Debug',
        submenu: [
            {label: 'Debug Window', click : (event, focusedWindow, focusedWebContents) => {win.openDevTools()}}
        ]
    }
]

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

        buf = Buffer.from("")
        res.on("data", (chunk) => {
            buf += chunk
        })

        res.on("end", () => {
            let $ = cheerio.load(buf)
            let obj = {}
            load_symbol($, obj)
            load_pronunciation($, obj)
            load_explain($, obj)
        })
    })

    req.end()
}

function load_symbol(doc, obj) {
    obj["symbols"] = {}
    obj.symbols["us"] = doc(".hd_prUS.b_primtxt").text()
    obj.symbols["en"] = doc(".hd_pr.b_primtxt").text()
}

function load_pronunciation(doc, obj) {
    obj["pronunciation"] = {}
    let parse = function(str) {
        if (str == null)
            return null
        
        let found = str.match(/https:\/\/[\w.\/]*.mp3/g)
        return found != null ? found[0] : null
    }

    obj.pronunciation["us"] = parse(doc(".hd_prUS.b_primtxt").next().children("a").attr("onclick"))
    obj.pronunciation["en"] = parse(doc(".hd_pr.b_primtxt").next().children("a").attr("onclick"))

}

function load_explain(doc, obj) {

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
    load_page('police', null)
    event.reply('init', ['police', 'office', 'station'])
})

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
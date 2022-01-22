const { app, BrowserWindow, Menu, dialog, webContents, ipcMain } = require("electron")
const ipc = require("electron").ipcMain
const fs = require('fs')
const path = require('path')
const http = require('http')
const cheerio = require('cheerio')
const Async = require('async')

let win
let user = {
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

function load_url(url) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: "cn.bing.com",
            port: 80,
            path: url,
            method: "GET",
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        }
    
        let req = http.request(options, (res) => {
            if (res.statusCode != 200) {
                reject('word request error.')
                return
            }
    
            res.setEncoding('utf8')
    
            buf = Buffer.from("")
            res.on("data", (chunk) => {
                buf += chunk
            })
    
            res.on("end", () => {
                resolve(buf);
            })

            res.on("error", (err) => {
                reject(err)
            })
        })
    
        req.on('error', (err) => {
            reject(err);
        })

        req.end()
    });
}

async function load_word(word, cb) {
    try {
        let buf = await load_url(`/dict/search?q=${word}`);
        let $ = cheerio.load(buf)
        let obj = {}
        load_symbol($, obj)
        load_pronunciation($, obj)
        load_explain($, obj)
        return obj;
    } catch (err) {
        console.log(err);
        return null;
    }
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

async function load_book(filename, cb) {
    buf = fs.readFileSync(filename)
    all = buf.toString().split(/[\t\r\n ]/, -1).filter((v) => v.length > 0)
    
    await Async.mapLimit(
        all, 
        5, 
        load_word,
        cb // cb(err, results)
    )
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

function getUsers() {
    let files = fs.readdirSync('./accounts')
    let users = []
    for (let file in files) {
        let fullpath = './accounts' + '/' + files[file]
        let st = fs.statSync(fullpath)
        if (st.isFile() && path.extname(fullpath) == ".json") {
            users.push(path.basename(fullpath, ".json"))
        }
    }

    return users
}

ipc.on('windowLoaded', (event) => {
    let users = getUsers()
    event.reply('users', users)
})

ipc.on('createUser', (event, account) => {
    fs.writeFileSync(`./accounts/${account}.json`, '{}')
    let users = getUsers()
    event.reply('users', users)
})

ipc.on('user-logon', (event, account) => {
    console.log('user logon ... ')
    fs.readFile(`./accounts/${account}.json`, 'utf8', (err, data) => {
        if (err) {
            event.reply('user-login', -1, 'falt: read file error.')
            return
        } 
        
        user = JSON.parse(data)
        if (typeof(user) != 'object') {
            event.reply('user-login', -2, 'falt: data type error.')
            return
        }

        if (!("words" in user)) {
            user["words"] = {}
        }

        event.reply('user-login', 0, user['words'])
    })
})

ipc.on('addWord', (event, word) => {
    load_page(word, (err, msg) => {
        if (err == 0) {
            event.reply('onWordAdded', msg);
        }
    })
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
        
        try {
            let words = [];
            result.filePaths.forEach((filepath) => { 
                load_book(filepath, (err, objs) => {
                    objs.map(obj => words.push(obj))
                });
            });

            event.reply('book-loaded', null, words)
        } catch (err) {
            console.log(err);
            event.reply('book-loaded', err);
        }

    }).catch(err => {
        console.log(err)
    })
})
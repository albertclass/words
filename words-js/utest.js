const cheerio = require('cheerio')

const $1 = cheerio.load("\
<ul id=\"fruits\">\
  <li class=\"apple\">Apple</li>\
  <li class=\"orange\">Orange</li>\
  <li class=\"pear\">Pear</li>\
</ul>");

console.log($1.html())

const $2 = cheerio.load("<p>asdf</p>")

console.log($2.html())

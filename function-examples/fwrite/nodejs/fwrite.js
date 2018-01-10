const hrtime = process.hrtime();     // [0] is seconds, [1] is nanoseconds
var fsize = 104857600;
var crypto = require('crypto');
var fs = require('fs');
// creates random Buffer of bytes
var buffer = crypto.randomBytes(parseInt(fsize));
const hrstart = process.hrtime();
var wstream = fs.writeFileSync('/tmp/test', buffer);
var hrfwrite = process.hrtime(hrstart);
var hrfunction = process.hrtime(hrtime);
var msg = fsize + "," + hrfunction[0] + "." + hrfunction[1] + "," + hrfwrite[0] + "." + hrfwrite[1];
console.log(msg);

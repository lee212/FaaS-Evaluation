const path = require('path');
  
exports.pythonGCS = (event, callback) {
    const file = event.data;
    if (file.resourceState === 'not_exists')  {
	    callback();
    }
    const fpath = file.name;
    const fname = path.basename(fpath);
    var params = JSON.parse(new Buffer(fname, 'base64').toString('ascii'));

    const
    spawn = require( 'child_process' ).spawnSync,
    cmd = spawn( req.body.cmd, req.body.params );

    var message = "" + `stdout: ${cmd.stdout.toString()}` + `stderr: ${cmd.stderr.toString()}`;
    console.log(message);
    res.status(200).send(message);
};

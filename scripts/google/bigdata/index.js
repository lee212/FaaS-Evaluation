exports.pythonGCS = function pythonGCS(req, res) {

    const
    spawn = require( 'child_process' ).spawnSync,
    cmd = spawn( req.body.cmd, req.body.params );

    var message = "" + `stdout: ${cmd.stdout.toString()}` + `stderr: ${cmd.stderr.toString()}`;
    console.log(message);
    res.status(200).send(message);
};

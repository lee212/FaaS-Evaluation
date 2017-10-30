/**
 * Responds to any HTTP request that can provide a "message" field in the body.
 *
 * @param {!Object} req Cloud Function request context.
 * @param {!Object} res Cloud Function response context.
 */
exports.flops = function flops(req, res) {
  // Example input: {"message": "Hello!"}
  if (req.body.number_of_loop === undefined) {
    // This is an error case, as "message" is required.
    res.status(400).send('No number_of_loop defined!');
  } else {
    // Everything is okay.
    var startTime = new Date();
    const spawn = require( 'child_process' ).spawnSync;
    var cmd;
       
	var fs = require('fs');
    var tpath = "/tmp/condaruntime";
    var loop = req.body.number_of_loop;
    var mat_n = req.body.number_of_matrix;
    
    var stdout, stderr;
	if (!fs.existsSync(tpath)) {
    	cmd = spawn("curl",
                 ["-s",
                  "-L",
                  "https://s3-us-west-2.amazonaws.com/ericmjonas-public/pywren.runtime/pywren_runtime-2.7-default.tar.gz",
                  "-o",
                  "/tmp/conda.tar.gz"]);
    	stdout = "curl: " + cmd.stdout.toString();
    	stderr = "curl: " + cmd.stderr.toString(); 
      
      	cmd = spawn("tar",
                 ["xzf",
                  "/tmp/conda.tar.gz",
                  "-C",
                  "/tmp/"]);
    	stdout += "tar: " + cmd.stdout.toString();
    	stderr += "tar: " + cmd.stderr.toString();
      
      	cmd = spawn("rm",
                 ["/tmp/conda.tar.gz"]);
    	stdout += "rm: " + cmd.stdout.toString();
    	stderr += "rm: " + cmd.stderr.toString();
      	cmd = spawn("curl",
                 ["-s",
                  "-L",
                  "https://s3.us-east-2.amazonaws.com/lee212-pywren-751/flops.py",
                  "-o",
                  "/tmp/flops.py"]);
    	stdout += "curl: " + cmd.stdout.toString();
    	stderr += "curl: " + cmd.stderr.toString();
    }
  
    cmd = spawn("bash",
                 ["-c",
                  "export KMP_AFFINITY=disabled;/tmp/condaruntime/bin/python /tmp/flops.py " + loop + " " + mat_n ]);
    stdout += "bash: " + cmd.stdout.toString();
    stderr += "bash: " + cmd.stderr.toString();
    
    var flops = cmd.stdout.toString()/1e9;
    var endTime = new Date();
    var timeDiff = endTime - startTime;

    var msg = (loop + "," + mat_n + "," + flops + "," + timeDiff);
    console.log(msg);
    res.status(200).send("msg: " + msg + "stdout: " + stdout + "stderr: " + stderr);
  }
};

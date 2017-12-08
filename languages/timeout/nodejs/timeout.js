const hrtime = process.hrtime();     // [0] is seconds, [1] is nanoseconds
var waitTill = true;
var hrfunction;
while(waitTill) {
	hrfunction = process.hrtime(hrtime);
	if (hrfunction[0] >= 1) {
		waitTill = false;
	};
}
console.log(((hrfunction[1]*1e-9) + hrfunction[0]).toString());

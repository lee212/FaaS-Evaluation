regions="ukwest"
letter=$(echo {{y..z},{a..z}{a..z}})
cnt=0
len=1
s=2891
e=2999
inc=20
for i in $regions
do
	l=${letter:$cnt:$len}
	cnt=$(expr $cnt + 2)
	if [ $cnt -ge 34 ]
	then
		len=2
	fi
	ss=0
	for j in $(seq $s $e)
	do 
		az functionapp create -g bigdata-benchmark-001${l}-$i -n flops$j -s bigdata0benchmark001$l --consumption-plan-location $i --debug --verbose &
		ss=$(expr $ss + 1)
		if [ $ss -eq $inc ]
		then
			sleep 30
			ss=0
		fi
		if [ $(( $j % 100 )) -eq 99 ]
		then
			s=$(expr $j + 1)
			break
		fi
	done
done


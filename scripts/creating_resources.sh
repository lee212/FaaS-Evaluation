regions=$(az account list-locations|grep name|grep -v us[^a-z]|awk '{print $2}'|cut -c 2-|cut -d"\"" -f1)
letter=$(echo {{j..z},{a..z}{a..z}})
cnt=0
len=1
for i in $regions
do
	l=${letter:$cnt:$len}
	cnt=$(expr $cnt + 2)
	if [ $cnt -ge 34 ]
	then
		len=2
	fi
	az group create -n bigdata-benchmark-001${l}-$i -l $i &
	az storage account create --sku Standard_LRS -g bigdata-benchmark-001${l}-$i -n bigdata0benchmark001$l 2> /dev/null &

done

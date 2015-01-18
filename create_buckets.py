import os
 
os.system("curl -X POST -u shiv:yagyavalkya -d name=kunjika -d ramQuotaMB=100 -d authType=none -d replicaNumber=3 -d proxyPort=11215 http://localhost:8091/pools/default/buckets")
os.system("curl -X POST -u shiv:yagyavalkya -d name=polls -d ramQuotaMB=100 -d authType=none -d replicaNumber=3 -d proxyPort=11216 http://localhost:8091/pools/default/buckets")
os.system("curl -X POST -u shiv:yagyavalkya -d name=questions -d ramQuotaMB=100 -d authType=none -d replicaNumber=3 -d proxyPort=11217 http://localhost:8091/pools/default/buckets")
os.system("curl -X POST -u shiv:yagyavalkya -d name=tags -d ramQuotaMB=100 -d authType=none -d replicaNumber=3 -d proxyPort=11218 http://localhost:8091/pools/default/buckets") 

fn = "D:/Projects/Integrated_Genome_Profile_Search_Engine/Datasets/Cancer/combinedBetas_betas.txt"
sampleNames = ["S_2194","S_2198","S_2199","S_2191","S_2192","S_2193","S_2196","S_2197","S_2200","S_1922"]
cpgIDs = ["cg17349199","cg25902889","cg04300115","cg06432655","cg05292376","cg22009923","cg03070194","cg00174901","cg21051046","cg16152813","cg23455517","cg06353318","cg10574499","cg00405677","cg07433344","cg21366535","cg13064881","cg18456149","cg06597861","cg21215336"]
fb = open(fn)

headers = fb.readline().strip().split("\t")
sampleIndeces = {}
for s in sampleNames:
    sampleIndeces[s] = headers.index(s)
    
cpgData = {}
for c in cpgIDs:
    cpgData[c] = []
    
for line in fb:
    for cpg in cpgIDs:    
        if line.startswith(cpg):
            print "Found cpg",cpg
            cpgIDs.remove(cpg)
            lineParts = line.strip().split("\t")
            for s in sampleNames:
                cpgData[cpg].append(int(100*float(lineParts[sampleIndeces[s]]))) 
            break 
print cpgIDs
print cpgData 

for cpg in cpgData.keys():
    print cpg, sum(cpgData[cpg])
    
    
#http://infao3806:8912/?q=[IIS:isDisease:True%20cg*%23II:isCGI:0%20Eoverlaps:ucscCGI%20cg*]&h=0&c=20

#<completions total="20" computed="20" sent="20">
#<c sc="905" dc="10" oc="10" id="47256">cg17349199</c>
#<c sc="872" dc="10" oc="10" id="55757">cg25902889</c>
#<c sc="851" dc="10" oc="10" id="34208">cg04300115</c>
#<c sc="823" dc="10" oc="10" id="36288">cg06432655</c>
#<c sc="733" dc="10" oc="10" id="35191">cg05292376</c>
#<c sc="692" dc="10" oc="10" id="51861">cg22009923</c>
#<c sc="636" dc="10" oc="10" id="32971">cg03070194</c>
#<c sc="598" dc="10" oc="10" id="30072">cg00174901</c>
#<c sc="540" dc="10" oc="10" id="50898">cg21051046</c>
#<c sc="417" dc="10" oc="10" id="46102">cg16152813</c>
#<c sc="342" dc="10" oc="10" id="53302">cg23455517</c>
#<c sc="335" dc="10" oc="10" id="36210">cg06353318</c>
#<c sc="292" dc="10" oc="10" id="40378">cg10574499</c>
#<c sc="261" dc="10" oc="10" id="30296">cg00405677</c>
#<c sc="235" dc="10" oc="10" id="37287">cg07433344</c>
#<c sc="210" dc="10" oc="10" id="51224">cg21366535</c>
#<c sc="87" dc="10" oc="10" id="42880">cg13064881</c>
#<c sc="76" dc="10" oc="10" id="48350">cg18456149</c>
#<c sc="67" dc="10" oc="10" id="36469">cg06597861</c>
#<c sc="52" dc="10" oc="10" id="51064">cg21215336</c>
#cg16152813 389
#cg06353318 307
#cg05292376 754
#cg25902889 847
#cg23455517 311
#cg06432655 795
#cg18456149 44
#cg06597861 30
#cg10574499 259
#cg17349199 873
#cg13064881 52
#cg03070194 600
#cg21215336 24
#cg00174901 569
#cg21366535 181
#cg00405677 223
#cg22009923 697
#cg07433344 198
#cg04300115 883
#cg21051046 519
from nltk.stem.porter import *
#from operator import itemgetter, attrgetter
import math
import re

stemmer = PorterStemmer()
dictionary = dict()
dictionary2 = dict()
indexlist = []
output = []
tfidflist = []
totaldoc = 1095
#用來調整，每次分群的群數k
clusters = 8

def prefun(filename):
	#呼叫txt檔，並進行tokenization與小寫處理
	f = open(filename,'r')
	strlist = f.read()
	f.close()
	wordlist=[]

	strlist = re.sub(r'\d+',"",strlist)
	strlist = strlist.lower()
	strlist = re.sub('[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+',"",strlist)
	tokens = strlist.split()
	#tokens = strlist.replace(".","").replace(",","").replace("'","").replace("?","").replace("!","").replace('"',"").replace("`","").lower().split()

	#讀取stopwords list並存成陣列
	f = open('stopwords.txt','r')
	stopWords = f.read()
	f.close()

	tmp=[]
	#使用nltk套件的Porter Algorithm進行stemming 並存入txt檔案
	for i in tokens:
		tmp.append(stemmer.stem(i))

	#進行stopwords 的處理
	for j in tmp:
		if j not in stopWords:
			wordlist.append(j)
			output.append(j)
	#for word in wordlist
	#	if word in dictionary2:
	#		dictionary2[word]=dictionary2.get(word)+1

	return wordlist

#建立dictionary
def makedictionary(list):
    for i in list:
        dictionary[i]=dictionary.get(i,0)+1
#建立dictionary，有回傳值
def makedictionary2(list):
    smalldict=dict()
    for i in list:
        smalldict[i]=smalldict.get(i,0)+1
    return smalldict
#計算tfidf，並同時將欲計算相似度的文檔中unit vector存入list中    
def counttfidf(docdict,i):
	doccount=len(docdict)
	tmplist=[]

	for key,values in sorted(docdict.items(),key=lambda item:item[0]):
		
		tfidf =tf(key,values,doccount)*idf(key,totaldoc)
		tmplist.append(tfidf)

	sumxx=0
	for j in range(len(tmplist)):
		x = tmplist[j]
		sumxx += x*x

	nor=math.sqrt(sumxx)
	k=0


	for key,values in sorted(docdict.items(),key=lambda item:item[0]):
		#print(str(indexlist.index(key)))
		tmptfidf = tmplist[k]/nor
		#print(str(tmptfidf))
		tfidflist[i][int(indexlist.index(key))]=tmptfidf
		k+=1

#計算兩個文檔的cosine similarity
def cosine(a,b):
	sumxx,sumxy,sumyy=0,0,0
	for i in range(j):
		x = tfidflist[a+1][i]
		y = tfidflist[b+1][i]
		sumxy += x*y
	return sumxy 
#計算TF值
def tf(term,count,total):
	return count / total
#計算IDF值
def idf(term,total):
	for key,values in dictionary2.items():
		if term==key:
			termfrequency=values
	return math.log10(total / termfrequency)

#主程式   
for i in range(1,int(totaldoc)+1):
	wordlist=prefun("./IRTM/"+str(i)+".txt")
	makedictionary(wordlist)
	wordlist=(set(wordlist))
	for j in wordlist:
		dictionary2[j]=dictionary2.get(j,0)+1

j=0

for key,values in sorted(dictionary.items(),key=lambda item:item[0]):
	j=j+1
	indexlist.append(key)

#建立一個二維list 存放所有的tfidf
tfidflist=[ [int(0)] * j for i in range(int(totaldoc)+1) ]


#dictionary2為計算每個文字在幾份文件中出現
dictionary2=dict(sorted(dictionary2.items(),key=lambda item:item[0]))

#取每個文檔計算tf-idf，並輸出成字典
for i in range(1,int(totaldoc)+1):
	wordlist=prefun("./IRTM/"+str(i)+".txt")
	wordlist=makedictionary2(wordlist)
	counttfidf(wordlist,i)

simmatrix = [ [int(0)] * int(totaldoc) for i in range(int(totaldoc)) ]
indicater = []
tmpdict=dict()
pqueue = dict()
mergelist = {}

#將similarity存入二維陣列
for a in range(0,int(totaldoc)):
	for b in range(0,int(totaldoc)):
		if simmatrix[a][b]==0 :
			simmatrix[a][b]=cosine(a,b)
			simmatrix[b][a]=simmatrix[a][b]
		if a == b:
			simmatrix[a][b] = 0
		tmpdict[b]=simmatrix[a][b]
	indicater.append(1)
	pqueue[a]=(sorted(tmpdict.items(),key=lambda item:item[1],reverse=True))

#對priority queue進行搜尋，找出最大的similarity與index進行merge，並存入mergelist
for k in range(0,int(totaldoc) - clusters):
	tmpmax = 0
	for i in pqueue.keys():
		if pqueue[i][0][1] >= tmpmax and indicater[i] == 1:
			tmpmax = pqueue[i][0][1]
			k1 = i
	k2 = pqueue[k1][0][0]

	if k1 in mergelist.keys():
		mergelist[k1].append(k2)	
	else:
		mergelist[k1] = [k2]
	if k2 in mergelist.keys():
		mergelist[k1] = mergelist[k1] + mergelist[k2]	
		del mergelist[k2]
	
	indicater[k2] = 0
	pqueue[k1]=[]
#刪除已經合併的cluster,更新similarity 
	for i in range(0,int(totaldoc)):
		if indicater[i] == 1 and i != k1:
			for x in range(0,len(pqueue[i])):
				if pqueue[i][x][0] == k1:
					del pqueue[i][x]
					break
			for x in range(0,len(pqueue[i])):
				if pqueue[i][x][0] == k2:
					del pqueue[i][x]
					break

			#single-link
			if simmatrix[i][k1] >= simmatrix[i][k2]:
				simmatrix[i][k1] = simmatrix[i][k1]
			else:
				simmatrix[i][k1] = simmatrix[i][k2]

			simmatrix[k1][i]=simmatrix[i][k1]

			tmptuple = (k1,simmatrix[i][k1])
			pqueue[i].append(tmptuple)	
			pqueue[i].sort(key=lambda x:x[1],reverse=True)
			tmptuple = (i,simmatrix[i][k1])
			pqueue[k1].append(tmptuple)	
			pqueue[k1].sort(key=lambda x:x[1],reverse=True)

#print(indicater)
#print(mergelist)
#將mergelist輸出成作業要求之格式
f = open(str(clusters)+'.txt', 'w')
result = ""

for i in range(0,len(indicater)):
	if indicater[i] == 1:
		if i in mergelist.keys():
			mergelist[i].append(i)
		else:
			mergelist[i] = [i]
		mergelist[i].sort()
		for x in mergelist[i]:
			f.write(str(x+1))
			f.write("\n")
		f.write("\n")





























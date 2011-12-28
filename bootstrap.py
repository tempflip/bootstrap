import re, sqlite3, glob, sys, itertools, random

#hasznalat
# bootstrap.py bemenet.sqlite kimenet.txt
#
sql_file=sys.argv[1]
kimenet=sys.argv[2]

connection=sqlite3.connect(sql_file)
cursor=connection.cursor()

def mondat_olvas(nyelv,id):
	query="SELECT mondat FROM "+nyelv+" WHERE id="+str(id)
	cursor.execute(query)
	(eredmeny,)=cursor.fetchall()[0]
	szamok=[int(x) for x in re.split(" ", eredmeny)]
	return szamok

#megnezzuk, hany mondat van
cursor.execute("SELECT MAX(id) FROM nyelv1")
(max_id,)=cursor.fetchall()[0]

def kiegyenlit(mondat1,mondat2):
	if len(mondat1) > len(mondat2):
		while len(mondat1) != len(mondat2): mondat2.append(0)
	else: 
		while len(mondat1) != len(mondat2): mondat1.append(0)
	return(mondat1,mondat2)	

def matrix_lookup(matrix,x,y):
	def_ertek=0.3
	try: ertek=matrix[x][y]
	except: ertek=def_ertek
	return ertek

def matrix_add(matrix,x,y,ertek):
	try: matrix[x]	# ha nem leteznek, letrehozzuk a megfelelo mezoket
	except: 
		matrix[x]={}
		matrix[x][y]=0
	try: matrix[x][y]
	except:
		matrix[x][y]=0
	matrix[x][y]+=ertek		
	return matrix

def matrix_mod(matrix,x,y,ertek):
	try: matrix[x]	# ha nem leteznek, letrehozzuk a megfelelo mezoket
	except: 
		matrix[x]={}
		matrix[x][y]=0
	try: matrix[x][y]
	except:
		matrix[x][y]=0
	matrix[x][y]=ertek		
	return matrix


def ertek_szamol(mondat1,mondat2,matrix):
	ertek=1	
	for x in range(len(mondat1)):
		ertek*=matrix_lookup(matrix,mondat1[x],mondat2[x])
	return ertek

def normalizal(matrix):
	for x in matrix.keys():
		sorszumma=0		
		for y in matrix[x].keys():
			sorszumma+=matrix_lookup(matrix,x,y)
		for y in matrix[x].keys():
			matrix=matrix_mod(matrix, x, y, matrix_lookup(matrix,x,y) / sorszumma)
	return matrix

###################################
def perm_csinal(mondat):
	if (len(mondat) > 0):
		valaszto=6
		tomb=[]
		temp=[]
		prm=[]
		permi=[]	
		for i in range(len(mondat)):
			temp.append(mondat[i])
			if (i+1 != 1 and (i+1) % valaszto == 0):
					tomb.append(temp)
					temp=[]
			if (i+1==len(mondat) and len(temp)!=0): tomb.append(temp)
		for i in range(len(tomb)):
			permi.append(list(itertools.permutations(tomb[i])))
		utolso_sor=permi[len(permi)-1]
		permi=list(map(lambda *x:x, *permi))	#transzponaljuk	
		for x in permi:
			ki=[]
			try:
				for y in x:
					if (len(y) < valaszto): yy=list(y)
					ki=ki+list(y)
			except: 
				ki=ki+list(random.choice(utolso_sor))
			prm.append(ki)
		return prm
	else: return []

def perm_csinal_rand(mondat):
	mondat2=[x for x in mondat]
	mondat3=[x for x in mondat]
	random.shuffle(mondat2)
	random.shuffle(mondat3)	
	permi1=perm_csinal(mondat)
	permi2=perm_csinal(mondat2)
	permi3=perm_csinal(mondat3)
	return permi1+permi2+permi3
###########################################################3
def permutacio_csinal(mondat):
	return perm_csinal_rand(mondat)
	#return list(itertools.permutations(mondat))


	
def bootstrap(t_matrix):
	t_matrix_uj={}
	for i in range(max_id+1)[1:]:
		print hanyszor,
		print i
		mondat1=mondat_olvas("nyelv1",i)		
		mondat2=mondat_olvas("nyelv2",i)
		(mondat1,mondat2)=kiegyenlit(mondat1,mondat2)	
		if (len(mondat1) > 20): continue ## ha tul hosszu a mondat, ugrunk
		permutaciok=permutacio_csinal(mondat2)
		ertekek=[]		
		for j in range(len(permutaciok)):
			ertekek.append(ertek_szamol(mondat1,permutaciok[j],t_matrix))
		ertekek=[x / sum(ertekek) for x in ertekek] #normalizaljuk az ertekeket	
		for j in range(len(permutaciok)):
			for k in range(len(permutaciok[j])): #visszairjuk a normalizalt ertekeket az uj matrixba
				x=mondat1[k]
				y=permutaciok[j][k]
				ertek=ertekek[j]
				t_matrix_uj=matrix_add(t_matrix_uj,x,y,ertek)
	t_matrix_uj=normalizal(t_matrix_uj)
	return t_matrix_uj


def szo_lookup(szotar,id):
	query="SELECT szo FROM "+szotar+" WHERE id="+str(id)
	cursor.execute(query)
	fetch=cursor.fetchall()[0]
	(eredmeny,)=fetch
	return eredmeny.encode("utf-8")

def freq_lookup(szotar,szo):
	query="SELECT freq FROM "+szotar+" WHERE szo='" + szo + "'"
	cursor.execute(query)
	fetch=cursor.fetchall()[0]
	(eredmeny,)=fetch
	return eredmeny


def kimutatas (matrix):
	sorok=[]
	FILE=open(kimenet,"w")
	for x in matrix.keys():
		for y in matrix[x].keys():
			ertek=matrix_lookup(matrix,x,y)
			if ertek > 0.3 :
				szo1=szo_lookup("szotar1",x)
				szo2=szo_lookup("szotar2",y)
				sorok.append((szo1, szo2, str(round(ertek,2)), str(freq_lookup("szotar1",szo1)), str(freq_lookup("szotar2",szo2)) ))
				#FILE.write(str(x) + "\t" + szo_lookup("szotar1",x) + "\t" + str(y) + "\t" + szo_lookup("szotar2",y) + "\t" + str(round(ertek,3))+"\n")
	sorok=sorted(sorok, key = lambda x:x[3])
	for x in sorok:
		FILE.write("\t".join(x)+"\n")
	FILE.write("**************************\n")
	sorok=sorted(sorok, key = lambda x:x[4])
	for x in sorok:
		FILE.write("\t".join(x)+"\n")
	FILE.close()

def kimutatas_sqlite (matrix):
	kimutat_db=sqlite3.connect(kimenet)
	c=kimutat_db.cursor()
	c.execute("CREATE TABLE matrix (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, nyelv1 TEXT, nyelv2 TEXT, prob REAL)")
	c.execute("CREATE TABLE freq1 (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, szo TEXT, freq INT)")
	c.execute("CREATE TABLE freq2 (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, szo TEXT, freq INT)")
	ny1=[]
	ny2=[]
	for x in matrix.keys():
		for y in matrix[x].keys():
			ertek=matrix_lookup(matrix,x,y)
			if ertek > 0.2 :
				szo1=szo_lookup("szotar1",x)
				szo2=szo_lookup("szotar2",y)
				c.execute("INSERT INTO matrix (nyelv1, nyelv2, prob) VALUES (?,?,?)",(szo1.decode("utf8"),szo2.decode("utf8"),ertek,))
				if (szo1 not in ny1): ny1.append(szo1)
				if (szo2 not in ny2): ny2.append(szo2)
	kimutat_db.commit()
	for x in ny1:
		c.execute("INSERT INTO freq1 (szo, freq) VALUES (?,?)",(x.decode("utf8"),freq_lookup("szotar1",x),))
	for x in ny2:
		c.execute("INSERT INTO freq2 (szo, freq) VALUES (?,?)",(x.decode("utf8"),freq_lookup("szotar2",x),))
	kimutat_db.commit()
	kimutat_db.close()
	
mtrx={}
hanyszor=3
while hanyszor > 0:
	print "@"
	mtrx=bootstrap(mtrx)	
	hanyszor-=1
	
#kimutatas(mtrx)
kimutatas_sqlite(mtrx)
connection.close()



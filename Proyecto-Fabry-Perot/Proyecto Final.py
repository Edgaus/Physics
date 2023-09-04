# Este programa soluciona un sistema de un par ecuaciones diferenciales a partir del algoritmo de Rungge-Kutta para el modelo de un laser.
# El programa consiste de un ciclo que obtiene los distintos valores de N y S para un valor en particular de corriente, I, en busqueda de Ith, la 
# corriente umbral. Este se obtendra a partir de una interpolacion lineal de los valores de S contra I, ya que la teoria dice que debe comportarse de forma lineal.
# Se evaluara de valor I inicial de 0.1 hasta 20mA, en un ciclo de 200 iteraciones, y el valor de I aumentara de manera constante  

# Bibliotecas que se utlizaron
import numpy as np
import math 
from matplotlib import pyplot as plt

#Definiendo los parametros a utlizar
hconstjs=6.626069e-34 #Constante de Planck (J s)
echargec=1.60217646e-19 #Carga de Electron (C)
vlightcm=2.99792458e10 #Velocidad de la luz (cm s-1)

ngroup=4 #Indice de Reflexion del material
clength=3.00E-02  #Longitud de la cavidad (cm)
thick=1.40E-05 #Grosor de la region activa (cm)
width=8.00E-05  #Anchura de la region activa (cm)
initialn=0.00E+18 #Valor inicial de los cargadores (cm-3)

Anr=2.00E+08  #Coeficiente cambio de recombinacion no-radiactivo (s-1)
Bcons=1.00E-10 #Coeficiente de recombinacion radiative (cm3 s-1)
Ccons=1.00E-29 #Coeficinte de recombinacion no lineal (cm6 s-1)
n0density=1.00E+18  #Densidad de transparencia de cargadores (cm-3) 
gslope=2.50E-16  #Coeficinete pendiente de ganancia optica (cm2 s-1)
epsi=5.00E-18  #Ganancia de compresion(cm3)
gammacons=0.25  #Factor de confinamiento optico
wavelength=1.31 #Longitud de onda de emision optica(um)

mirrone=0.32 #Indice de reflecion optico del primer espejo
mirrtwo=0.32 #Indice de reflecion optico del segundo espejo
alfai=40 #Perdida de optica interna(cm-1)
pstart1=2.5 #Tiempo de primera corriente  (ns)
pstart2=3.5 #Tiempo de la segunda corriente (ns)
rioff1=0 #Valor de la corriente (mA) cuando t<=5ns
rion1=np.zeros(200) #Vector con los posibles valores de la corriente (mA) cuando t=5ns
rion2=np.zeros(200) #Vector con los posibles valores de la corriente (mA) cuando t>5ns

# Calculo de peridida optica total  (cm-1)
alfam=math.log( 1.0/(mirrone * mirrtwo))/(2.0 * clength )
alfasum=alfam + alfai

#Reescalar valores : corriente[mA], longitud [nm] and 1nm^3=1e-21cm^3
echarge=echargec*1.0e9*1.0e3 #Carga de electron
vlight=vlightcm/1.0e9/1.0e-7 #Velocidad de la luz (m/s) to (nm s-1)
gslope=gslope*1.0e14
n0density=n0density*1.0e-21
#Escala de longitud en nm.
clength=clength / 1.0e-7
width=width / 1.0e-7
thick=thick / 1.0e-7
#Constantes de Recombinacion
Anr=Anr / 1.0e9
Bcons=Bcons / (1.0e9*1.0e-21)
Ccons=Ccons / (1.0e9*1.0e-42)
epsi=epsi / 1.0e-21
beta=1.00E-04 #Coeficiente de emision espontanea
gslope=gslope*vlight / ngroup
alfasum=alfasum*1.0e-7
kappa=alfasum*vlight / ngroup
volume=clength*width*thick
#Escala salida de la luz a mW from espejo 1
tmp=hconstjs*(vlightcm*1.0e-2)/(wavelength*1.0e-6) #usa m (J)
tmp=tmp*alfam*vlightcm
tmp=tmp*1000.0*volume/ngroup
lightout=tmp*(1.0-mirrone)/(2.0-mirrone-mirrtwo)

# Funcion de la ganacia optica del material
def G(x1,x2):
    return gammacons*gslope*(x1-n0density)*(1-epsi*x2) 

# Funcion que contiene las ecuaciones diferenciales acopladas a resolver.
def F(x,y):
    V=np.zeros(2)
    V[0]=C(x)/(echarge*volume)-(Anr*y[0]+Bcons*y[0]**2+Ccons*y[0]**3)-G(y[0],y[1])*y[1] 
    V[1]=(G(y[0],y[1])-kappa)*y[1]+beta*Bcons*y[0]**2
    return V

#Algoritmo de Ruge Kutta que soluciona las ecuaciones

def integrate(I,t,h,tol):
    cont=0
    time=0
    a1 = 0.2; a2 = 0.3; a3 = 0.8; a4 = 8/9; a5 = 1.0; a6 = 1.0
    c0 = 35/384; c2 = 500/1113; c3 = 125/192; c4 = -2187/6784; c5 = 11/84
    d0 = 5179/57600; d2 = 7571/16695; d3 = 393/640; d4 = -92097/339200; d5 = 187/2100; d6 = 1/40 
    b10 = 0.2
    b20 = 0.075; b21 = 0.225
    b30 = 44/45; b31 = -56/15; b32 = 32/9
    b40 = 19372/6561; b41 = -25360/2187; b42 = 64448/6561; b43 = -212/729
    b50 = 9017/3168; b51 =-355/33; b52 = 46732/5247; b53 = 49/176; b54 = -5103/18656
    b60 = 35/384; b62 = 500/1113; b63 = 125/192; b64 = -2187/6784; b65 = 11/84         #Coeficientes para el Ruge-Kutta adaptativo
    Tiempo=[] #Vector que tiene los valores del tiempo
    SNiniciales=[]  #Vector que contiene al arreglo I, la densidad de los fotones y portadores
    Corriente=[]  #Vector que contiene la corriente
    Fotones=[] #Vector que contiene la densidad 
    Portadores=[] #Vector que contiene los portadores
    Corriente.append(C(t)) 
    Portadores.append(I[0]*1.0e21/1.0e18)
    Fotones.append((lightout*I[1]))
    Tiempo.append(t)
    SNiniciales.append(I)
    k0 =h*F(t,I)
    def kutta(F,x,y,h,k0):
        k1 = h*F(x + a1*h, y + b10*k0)
        k2 = h*F(x + a2*h, y + b20*k0 + b21*k1)
        k3 = h*F(x + a3*h, y + b30*k0 + b31*k1 + b32*k2)
        k4 = h*F(x + a4*h, y + b40*k0 + b41*k1 + b42*k2 + b43*k3)
        k5 = h*F(x + a5*h, y + b50*k0 + b51*k1 + b52*k2 + b53*k3 + b54*k4)
        k6 = h*F(x + a6*h, y + b60*k0 + b62*k2 + b63*k3 + b64*k4 + b65*k5)

        dy = c0*k0 + c2*k2 + c3*k3 + c4*k4 + c5*k5 
        E = (c0 - d0)*k0 + (c2 - d2)*k2 + (c3 - d3)*k3 + (c4 - d4)*k4 + (c5 - d5)*k5 - d6*k6
        e = math.sqrt(np.sum(E**2)/len(y))  
        return dy, e,k6

# Acepta integracion del error
    while True:  #Ciclo que se va estar repitiendo para obtener los valores 
        cont+=1
        if 4<=time: #Condicion para romper el ciclo debido al tiempo
            break
        mI,me,mk6=kutta(F,t,I,h,k0) 
        if me<1.0e-8: 
            hNext=h
        else:
            hNext = 0.9*h*(tol/me)**0.2
        if me <= tol:  #Condicion para aceptar valores
            corr=C(t)   #Obtiene el valor de la corriente en funcion del tiempo en la funcion definida en la  linea 164
            foton=(lightout*I[1])  #Tranforma la densidad de fotones a potencia 
            porta=I[0]*1.0e21/1.0e18
            t=t+h #Incremnto del tiempo
            I=I+mI #Incremento de los valores de las densidades de fotones y portadores
            Corriente.append(corr) 
            Portadores.append(porta)
            Fotones.append(foton)
            Tiempo.append(t)
            SNiniciales.append(I)
            if abs ((Fotones[cont]-Fotones[cont-1])*1.0e8)<1.0e-5: #Condicion de estabilidad para encontar S y N
                time=time+h
            else:
                time=0
            if abs(hNext) > 10.0*abs(h): hNext = 10.0*h
# Checar si el siguiente paso es el ultimo; ajusta h
            k0 = mk6*hNext/h 
        else:
            if abs(hNext) < 0.1*abs(h): 
                hNext = 0.1*h 
            k0 = k0*hNext/h
        h = hNext
    
    return Tiempo,Corriente, Portadores,Fotones

PotenciasL=np.zeros(200)   #Vector con elementos ceros que luego se le va asignar los valores de la potenica de la Luz en funcion de la corriente
Pota=np.zeros(200)   #Vector que elementos ceros que luego se le va asignar los valores de los portadores en funcion de la corriente

#Inicializacion densidad S(Fotones), densidad N(Portadores)
sdensity=0.0
ndensity=initialn * 1.0e-21
# Ciclo donde se va evaluando los posibles valores de I
for p in range(200):
    rion1[p]=(p+1)*.1  #El valor de la corriente para t=5ns
    rion2[p]=(p+1)*.1  #El valor de la corriente para t>5ns
    def C(a):   #Funcion de la corriente en funcion del tiempo,a.
        curr= rioff1
        if a>pstart1:
            curr=rion1[p]
        if a>pstart2:
            curr=rion2[p]
        return curr
    t=0.0  #Tiempo inicial
    h=1.0e-3 #Incremento del paso de Ruge-Kutta, el valor dado de h es debido a las dimensiones de las escalas.
    I=[ndensity,sdensity]  #Vector con condiciones iniciales
    tiempo,corriente,portadores,PotenL=integrate(I,t,h,1.0e-3)  #Se llama la funcion Rugge Kuta con los valores 
    lenm=len(PotenL)
    Pota[p]=portadores[lenm-1]  #Asignacion de las entradas del vector Pota para cada corriente
    PotenciasL[p]=PotenL[lenm-1] #Asignacion de las entradas del vector PotenciasL para cada corriente


# Crea un vector con el logaritmo natural de los elementos del vector PotenciasL,que representa la potencia de la Luz
logPotencias=np.zeros(200) 
for j in range(200):
    logPotencias[j]=math.log(PotenciasL[j])

# Grafica de la funcion de los vectores de Corriente, Portadores, Densidad de Fotones, 

# Funcion Tiempo-Corriente
plt.plot(tiempo,corriente,color="blue")
plt.xlabel("Tiempo (ns)")
plt.ylabel("Corriente (mA)")
plt.show()
# Funcion Tiempo-Densidad de Portadores
plt.plot(tiempo,portadores,color="red")
plt.xlabel("Tiempo (ns)")
plt.ylabel("Densidad de Portadores, N(10e18 cm-3)")
plt.show()
# Funcion Tiempo-Potencia Optica
plt.plot(tiempo,PotenL,color="green")
plt.xlabel("Tiempo (ns)")
plt.ylabel("Potencia Optica L (mW)")
plt.show()
# Funcion corriente-potencia optica
plt.plot(rion1,PotenciasL,color="blue")
plt.xlabel("Corriente (mA)")
plt.ylabel("Potencia Optica L (mW)")
plt.show()
# Funcion corriente-log(potencia optica)
plt.plot(rion1,logPotencias,color="blue")
plt.xlabel("Corriente (mA)")
plt.ylabel("ln (Potencia Optica L (mW)")
plt.show()
# Funcion corriente-densidad de portadores
plt.plot(rion1,Pota,color="blue")
plt.xlabel("Corriente (mA)")
plt.ylabel("Densidad Portadores, N(10e18 cm-3)")
plt.show()

#Interpolacion lineal para calcular la corriente umbral
y=np.zeros(100) #Vector con ceros para luego asignar
x=np.zeros(100) #Vector con ceros para luego asignar
n=len(x)  #Longitud del vector
for i in range(100):
    x[i]=10+(i+1)*.1 #Asignado al vector x los valores de la corriente  donde los datos se comportan de forma lineal
    y[i]=PotenciasL[100+i] #Asigna al vector y valores del vector PotenciasL donde los datos se comportan de forma lineal

#Tenemos que en la interpolacion lineal se busca una solucion de la forma y=a+bx
# Suponiendo que hay un conjuto de N puntos (xi,yi), tiene que a=(ym*sumx2 - xm*sumxy)/(sumx2 - n*xm**2) y 
# b = (sumxy - xm*sumy)/(sumx2 - n*xm**2), donde ym,xm son los promedios de las abcisas y ordenadas respectivamente, sum es 
# una sumatoria de los N puntos, xi al cuadrado,sumx2, producto xi*yi,sumxy, o la suma de yi,sumy.
sumx = sumx2 = sumxy = sumy = 0 
for i in range(n):
    sumx += x[i]
    sumx2 += x[i]**2
    sumxy += x[i]*y[i]
    sumy += y[i]
xm = sumx / n
ym = sumy / n
a = (ym*sumx2 - xm*sumxy)/(sumx2 - n*xm**2)
b = (sumxy - xm*sumy)/(sumx2 - n*xm**2)

print("El valor de Ith es:") #Imprime el valor de la intensidad umbral, esto ocurre en y=0, se buca x que cumple esa condicion
print("I=",round(-a/b,4))

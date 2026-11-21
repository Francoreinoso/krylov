import numpy as np, csv, itertools
d=np.genfromtxt('muestras.csv',delimiter=',',names=True)
X=np.c_[d['x'],d['y']]; z=np.log(d['as_ppm']); n=len(z)
P=list(csv.DictReader(open('puntos.csv')))
Xp=np.array([[float(r['x']),float(r['y'])] for r in P])
def dist(A,B,ang,ratio,rng):
    c,s=np.cos(ang),np.sin(ang); R=np.array([[c,s],[-s,c]])
    A2=A@R.T; B2=B@R.T
    S=np.array([1/rng,1/(rng*ratio)])
    D=(A2[:,None,:]-B2[None,:,:])*S
    return np.sqrt((D**2).sum(-1))
def kern(h,kind):
    if kind=='exp': return np.exp(-h)
    a=np.sqrt(3)*h; return (1+a)*np.exp(-a)
best=None
one=np.ones(n)
for kind in ['exp']:
  for rng in [15,30,60,120]:
    for ratio,angs in [(1.0,[0]),(0.5,range(0,180,45))]:
      for a in angs:
        H=dist(X,X,np.deg2rad(a),ratio,rng); K0=kern(H,kind)
        for nug in [0.05,0.15,0.3,0.5]:
          K=(1-nug)*K0+nug*np.eye(n)
          L=np.linalg.cholesky(K)
          Li1=np.linalg.solve(L,one); Liz=np.linalg.solve(L,z)
          mu=(Li1@Liz)/(Li1@Li1); r=Liz-mu*Li1
          s2=(r@r)/n
          ll=-0.5*n*np.log(s2)-np.log(np.diag(L)).sum()
          if best is None or ll>best[0]: best=(ll,kind,rng,ratio,a,nug,mu,s2)
ll,kind,rng,ratio,a,nug,mu,s2=best
print('best',best)
ang=np.deg2rad(a)
K=(1-nug)*kern(dist(X,X,ang,ratio,rng),kind)+nug*np.eye(n)
Ki=np.linalg.inv(K)
# LOO check
al=Ki@(z-mu); loo_m=z-al/np.diag(Ki); loo_s=np.sqrt(s2/np.diag(Ki))
zz=(z-loo_m)/loo_s
print('LOO cover90',np.mean(np.abs(zz)<1.645),'std z',zz.std(),'rmse log',np.sqrt(np.mean((z-loo_m)**2)), 'sd log',z.std())
f=max(1.0,zz.std())  # inflar si el LOO dice que quedamos cortos
# ordinary kriging predict (incluye nugget: se predice una muestra nueva)
k=(1-nug)*kern(dist(Xp,X,ang,ratio,rng),kind)
m=mu+k@al
u=1-k@Ki@one
v=s2*(1-np.einsum('ij,jk,ik->i',k,Ki,k)+u**2/(one@Ki@one))
s=np.sqrt(np.maximum(v,1e-9))*f
with open('respuesta.csv','w') as fo:
    fo.write('pozo,as_ppm,bajo,alto\n')
    for r,mi,si in zip(P,m,s):
        fo.write(f"{r['pozo']},{np.exp(mi):.1f},{np.exp(mi-1.645*si):.1f},{np.exp(mi+1.645*si):.1f}\n")
print('n>500 est',(np.exp(m)>500).sum(),'sd medio',s.mean())

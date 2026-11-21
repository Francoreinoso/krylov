import numpy as np, csv, itertools
from scipy.linalg import cho_factor, cho_solve
M=list(csv.DictReader(open('muestras.csv'))); P=list(csv.DictReader(open('puntos.csv')))
X=np.array([[float(r['x']),float(r['y'])] for r in M]); v=np.array([float(r['as_ppm']) for r in M])
Xp=np.array([[float(r['x']),float(r['y'])] for r in P]); z=np.log(v); n=len(z); one=np.ones(n)
print('n',n,'min/med/max',v.min(),np.median(v),v.max(),'>500:',(v>500).mean())
def kern(A,B,l1,ra,th):
    c,s=np.cos(th),np.sin(th); R=np.array([[c,s],[-s,c]])
    a=(A@R.T)/[l1,l1*ra]; b=(B@R.T)/[l1,l1*ra]
    d=np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(-1)+1e-12); s3=np.sqrt(3)*d
    return (1+s3)*np.exp(-s3)
best=None
for l1,ra,th,ng in itertools.product((10,20,35,60,100,170),(1,.6,.35,.2),np.radians([0,30,60,90,120,150]),(.02,.08,.2,.5,1.2)):
    if ra==1 and th>0: continue
    K=kern(X,X,l1,ra,th)+ng*np.eye(n)
    cf=cho_factor(K,lower=True); Ki1=cho_solve(cf,one); m=(one@cho_solve(cf,z))/(one@Ki1)
    r=z-m; s2=r@cho_solve(cf,r)/n
    nll=0.5*n*np.log(s2)+np.log(np.diag(cf[0])).sum()
    if best is None or nll<best[0]: best=(nll,l1,ra,th,ng,s2,m)
nll,l1,ra,th,ng,s2,m=best
print('mejor: l1',l1,'razon',ra,'ang',np.degrees(th),'pepita',ng,'s2',s2,'media',np.exp(m))
K=s2*(kern(X,X,l1,ra,th)+ng*np.eye(n)); cf=cho_factor(K,lower=True); Kinv=cho_solve(cf,np.eye(n))
a=Kinv@(z-m); d=np.diag(Kinv); lm=z-a/d; ls=np.sqrt(1/d); zs=(z-lm)/ls
q=np.quantile(np.abs(zs),0.90); print('LOO: sd z',zs.std(),'q90 |z|',q,'cob con 1.645',(np.abs(zs)<=1.645).mean(),'RMSE ppm',np.sqrt(((np.exp(lm)-v)**2).mean()))
k=max(q,1.645*0.9)  # factor calibrado con dejar-uno-afuera
ks=s2*kern(Xp,X,l1,ra,th); mu=m+ks@a
W=cho_solve(cf,ks.T); Ki1=cho_solve(cf,one); u=1-one@W
sd=np.sqrt(np.maximum(s2-(ks*W.T).sum(1)+u**2/Ki1.sum()+s2*ng,1e-12))
est=np.exp(mu); lo=np.exp(mu-k*sd); hi=np.exp(mu+k*sd)
with open('respuesta.csv','w') as f:
    f.write('pozo,as_ppm,bajo,alto\n')
    for r,e,l,h in zip(P,est,lo,hi): f.write(f"{r['pozo']},{e:.1f},{l:.1f},{h:.1f}\n")
print('factor',k,'ancho medio',(hi-lo).mean(),'est min/max',est.min(),est.max(),'seguro>500',(lo>500).sum(),'seguro<500',(hi<500).sum(),'duda',((lo<=500)&(hi>=500)).sum())

import numpy as np, csv
from scipy.optimize import minimize
from scipy.linalg import cho_factor, cho_solve
M=list(csv.DictReader(open('muestras.csv'))); P=list(csv.DictReader(open('puntos.csv')))
X=np.array([[float(r['x']),float(r['y'])] for r in M]); v=np.array([float(r['as_ppm']) for r in M])
Xp=np.array([[float(r['x']),float(r['y'])] for r in P])
print('n',len(v),'min/med/max',v.min(),np.median(v),v.max(),'x',X[:,0].min(),X[:,0].max(),'y',X[:,1].min(),X[:,1].max(),'>500:',(v>500).mean())
def run(z,tag):
    n=len(z)
    def dist(A,B,p):
        l1,l2,th=np.exp(p[1]),np.exp(p[2]),p[3]
        c,s=np.cos(th),np.sin(th); R=np.array([[c,s],[-s,c]])
        a=(A@R.T)/[l1,l2]; b=(B@R.T)/[l1,l2]
        return np.sqrt(((a[:,None,:]-b[None,:,:])**2).sum(-1)+1e-12)
    def kern(A,B,p):
        d=dist(A,B,p); s3=np.sqrt(3)*d
        return np.exp(p[0])*(1+s3)*np.exp(-s3)   # Matern 3/2
    def parts(p):
        K=kern(X,X,p)+np.exp(p[4])*np.eye(n)
        cf=cho_factor(K,lower=True); one=np.ones(n)
        Ki1=cho_solve(cf,one); m=(one@cho_solve(cf,z))/(one@Ki1)
        return cf,m,Ki1
    def nll(p):
        try:
            cf,m,Ki1=parts(p)
        except Exception: return 1e10
        r=z-m; return 0.5*r@cho_solve(cf,r)+np.log(np.diag(cf[0])).sum()+0.5*np.log(one_sum(Ki1))
    def one_sum(Ki1): return Ki1.sum()
    s2=z.var(); best=None
    for l in (15,40,100):
        for th in (0,0.8,1.6,2.4):
            p0=[np.log(s2),np.log(l),np.log(l/2),th,np.log(s2*0.1)]
            r=minimize(nll,p0,method='L-BFGS-B',bounds=[(np.log(s2)-5,np.log(s2)+5),(0,8),(0,8),(-4,4),(np.log(s2)-9,np.log(s2)+2)])
            if best is None or r.fun<best.fun: best=r
    p=best.x; cf,m,Ki1=parts(p)
    print(tag,'nll',best.fun,'sig2',np.exp(p[0]),'l1,l2',np.exp(p[1]),np.exp(p[2]),'ang',np.degrees(p[3])%180,'nug',np.exp(p[4]),'mean',m)
    # LOO
    Kinv=cho_solve(cf,np.eye(n)); one=np.ones(n)
    # OK LOO via augmented precision: use simple-kriging LOO with plug-in mean (approx)
    a=Kinv@(z-m); d=np.diag(Kinv); loo_mu=z-a/d; loo_sd=np.sqrt(1/d)
    # predict (ordinary kriging, incl. nugget for a new sample)
    ks=kern(Xp,X,p); mu=m+ks@cho_solve(cf,z-m)
    W=cho_solve(cf,ks.T); u=1-one@W
    var=np.exp(p[0])-(ks*W.T).sum(1)+u**2/Ki1.sum()+np.exp(p[4])
    return loo_mu,loo_sd,mu,np.sqrt(np.maximum(var,1e-12))
out={}
for tag,f,g in (('raw',lambda t:t,lambda t:t),('log',np.log,np.exp)):
    lm,ls,mu,sd=run(f(v),tag)
    for q in (1.645,):
        lo,hi=g(lm-q*ls),g(lm+q*ls)
        print(tag,'LOO cov90',((v>=lo)&(v<=hi)).mean(),'ancho medio',(hi-lo).mean(),'RMSE',np.sqrt(((g(lm)-v)**2).mean()),'MAE',np.abs(g(lm)-v).mean())
    zs=(f(v)-lm)/ls; print(tag,'z sd',zs.std(),'q05,q95',np.quantile(zs,[.05,.95]))
    out[tag]=(lm,ls,mu,sd,zs)
np.save('out.npy',np.array([out['raw'][2],out['raw'][3],out['log'][2],out['log'][3]]))
np.save('zs.npy',np.array([out['raw'][4],out['log'][4]]))

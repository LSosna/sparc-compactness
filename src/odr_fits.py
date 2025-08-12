import numpy as np
from scipy import odr, stats

def odr_loglog(x, y):
    r, _ = stats.pearsonr(x, y)
    def f(B, x): return B[0] + B[1]*x
    out = odr.ODR(odr.Data(x,y), odr.Model(f), beta0=[np.median(y), 0.7]).run()
    a, b = out.beta; sa, sb = out.sd_beta
    return dict(a=a, b=b, sa=sa, sb=sb, r=r, sig_excess=(b-0.5)/sb)

import math, random, itertools
from fractions import Fraction
import mpmath as mp
import sympy as sp
from sympy import symbols, expand, binomial, Rational
random.seed(1729)
mp.mp.dps = 30
print("== U1 instrument: identify zeta(2) ==")
print(mp.identify(mp.zeta(2), ['pi**2']))
print("pslq [zeta(2), pi^2]:", mp.pslq([mp.zeta(2), mp.pi**2], maxcoeff=1000))
print("== U1 fitting-window hazard: Moser circle regions C(n,4)+C(n,2)+1 ==")
print([int(binomial(n,4)+binomial(n,2)+1) for n in range(1,9)])
print("== R3 a_{n+1}=a_n^2-2, a_0=3 vs x^(2^n)+x^(-2^n), x=(3+sqrt5)/2 ==")
x=(3+mp.sqrt(5))/2; a=3; out=[]
for n in range(5):
    out.append((a, mp.nstr(x**(2**n)+x**(-(2**n)),12))); a=a*a-2
print(out)
print("== R4 add a parameter: int_0^inf e^-x sin x / x dx vs pi/4 ==")
print(mp.nstr(mp.quad(lambda t: mp.exp(-t)*mp.sin(t)/t,[0,mp.inf]),15), mp.nstr(mp.pi/4,15))
print("== R5 Burnside: 2-color necklaces n=4 under rotation; brute vs formula ==")
n=4; seen=set(); cnt=0
for c in itertools.product('01',repeat=n):
    rots={c[i:]+c[:i] for i in range(n)}
    canon=min(rots)
    if canon not in seen: seen.add(canon); cnt+=1
formula=sum(sp.totient(d)*2**(n//d) for d in sp.divisors(n))/n
print("brute",cnt,"formula",formula)
print("== R6 Euler-Maclaurin: H_n - ln n - 1/(2n) vs gamma, n=10^6 ==")
N=10**6; H=sum(1.0/k for k in range(1,N+1))
print("H_n-ln n =",H-math.log(N)," minus 1/2n =",H-math.log(N)-1/(2*N)," gamma =",float(mp.euler))
print("== R7 transfer matrix: strings with no '11' vs F_{n+2}; recurrence guess ==")
def no11(n): return sum(1 for s in itertools.product('01',repeat=n) if '11' not in ''.join(s))
seq=[no11(n) for n in range(1,11)]; print(seq)
M=sp.Matrix([[1,1],[1,0]]); print("M^n[0,0]+M^n[0,1] n=1..6:",[sum((M**n)[0,:]) for n in range(1,7)])
from sympy.series.sequences import SeqFormula
k=sp.Symbol('k'); print("find_linear_recurrence:", sp.sequence(sp.fibonacci(k+2),(k,1,12)).find_linear_recurrence(12))
print("== S5 symmetric function, asymmetric minima: f=(x^2-1)^2+(y^2-1)^2 ==")
X,Y=symbols('x y'); f=(X**2-1)**2+(Y**2-1)**2
print("f(0,0)=",f.subs({X:0,Y:0})," f(1,1)=",f.subs({X:1,Y:1})," f(1,-1)=",f.subs({X:1,Y:-1}), " critical pts:", sp.solve([sp.diff(f,X),sp.diff(f,Y)],[X,Y]))
print("== S6 trace trick: triangles in K4 = tr(A^3)/6 ==")
A=sp.ones(4,4)-sp.eye(4); print((A**3).trace()/6)
print("== S4 Dirichlet: convergents of sqrt2, q^2*|alpha-p/q| ==")
cf=sp.continued_fraction_convergents(sp.continued_fraction_iterator(sp.sqrt(2)))
for i,c in enumerate(cf):
    if i>=6: break
    print(c, mp.nstr(abs(mp.sqrt(2)-mp.mpf(c.p)/c.q)*c.q**2,6))
print("== S9 SOS certificate ==")
Z=symbols('z'); print(expand((X-Y)**2+(Y-Z)**2+(Z-X)**2 - 2*(X**2+Y**2+Z**2-X*Y-Y*Z-Z*X)))
print("== S10 Gosper ==")
from sympy.concrete.gosper import gosper_sum
nn=symbols('n',integer=True,positive=True); kk=symbols('k',integer=True)
print(gosper_sum(1/(kk*(kk+1)),(kk,1,nn)))
print("== S8 Oddtown brute force n=4: max family, odd sizes, pairwise even intersections ==")
U=range(4); subsets=[frozenset(s) for r in (1,3) for s in itertools.combinations(U,r)]
best=0
for r in range(1,len(subsets)+1):
    ok=False
    for fam in itertools.combinations(subsets,r):
        if all(len(a&b)%2==0 for a,b in itertools.combinations(fam,2)): ok=True; best=r; break
    if not ok: break
print("max family size:",best)
print("== U3 strengthened induction sanity: sum 1/k^2 <= 2-1/n ==")
print(all(sum(Fraction(1,j*j) for j in range(1,m+1)) <= 2-Fraction(1,m) for m in range(1,200)))
print("== U8 Euler & F5: 641 = 64*10+1, 641 | 2^32+1 ==")
print(641%64, (2**32+1)%641, "candidates 64k+1 that are prime up to 641:", [p for p in range(65,642,64) if sp.isprime(p)])
print("== U5 inverse Collatz: odd preimage exists iff n = 4 mod 6 ==")
print([(m,(m-1)//3) for m in range(2,40) if m%6==4])
print("== E1 Collatz random model: v2(3n+1) over odd n<2^18 ==")
from collections import Counter
cnt=Counter(); tot=0
for m in range(1,2**18,2):
    v=((3*m+1)&-(3*m+1)).bit_length()-1; cnt[v]+=1; tot+=1
print({kv:round(cnt[kv]/tot,4) for kv in sorted(cnt)[:6]}, "mean v =", sum(kv*c for kv,c in cnt.items())/tot)
print("predicted mean log-step per T-step:", 0.5*math.log(0.5)+0.5*math.log(1.5), " => T-steps ~ ln n * ", 1/(-(0.5*math.log(0.5)+0.5*math.log(1.5))))
def Tsteps(n):
    s=0
    while n!=1:
        n = n//2 if n%2==0 else (3*n+1)//2; s+=1
    return s
samp=[random.randrange(10**6,2*10**6) for _ in range(2000)]
obs=sum(Tsteps(n) for n in samp)/len(samp); pred=sum(6.952*math.log(n) for n in samp)/len(samp)
print("mean T-steps observed:",round(obs,2)," predicted 2/ln(4/3)*ln n:",round(pred,2))
print("== E3 dominant balance: W(1e6) vs ln N - ln ln N ==")
Nn=1e6; print(mp.nstr(mp.lambertw(Nn),8), math.log(Nn)-math.log(math.log(Nn)))
print("== C2 rewrite ba->ab: inversions monovariant, unique normal form ==")
def inv(s): return sum(1 for i in range(len(s)) for j in range(i+1,len(s)) if s[i]=='b' and s[j]=='a')
ok=True
for _ in range(300):
    s=''.join(random.choice('ab') for _ in range(random.randint(0,12))); orig=s
    while 'ba' in s:
        i=random.choice([i for i in range(len(s)-1) if s[i:i+2]=='ba'])
        t=s[:i]+'ab'+s[i+2:]
        if inv(t)!=inv(s)-1: ok=False
        s=t
    if s!=''.join(sorted(orig)): ok=False
print("every step drops inversions by exactly 1 and NF = sorted:", ok)
print("== E4 averaging: random 2-coloring cut >= m/2 in expectation ==")
import networkx as nx
G=nx.gnp_random_graph(30,0.3,seed=7); m=G.number_of_edges()
cuts=[]
for _ in range(2000):
    col={v:random.randint(0,1) for v in G}; cuts.append(sum(1 for u,v in G.edges if col[u]!=col[v]))
print("m/2 =",m/2," mean cut =",sum(cuts)/len(cuts)," max sampled =",max(cuts))

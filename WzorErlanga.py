'''
Created on 23 Jan 2016

@author: kamichal
'''

_FAC_TABLE = [1, 1]
def szybkaSilnia(n):
    if n < len(_FAC_TABLE):
        return _FAC_TABLE[n]

    last = len(_FAC_TABLE) - 1
    total = _FAC_TABLE[last]
    for i in range(last + 1, n + 1):
        total *= i
        _FAC_TABLE.append(total)

    return total

def ErlangB(A,N):
    ''' Ta wersja funkcji moze byc wywolywana 
    z listami jako argumentami '''
    if A is None or N is None:
        print 'blad wywolania funkcji ErlangB'
        return None

    try:    
        if type(A) is list:
            if type(N) is list:
                E = [[] for _ in range(len(A))]
                ia = 0
                for a in A:
                    for n in N:
                        w = ErlangBPojed(a, n)
                        E[ia].append(w)
                    ia += 1                
            else:
                E = []
                for a in A:
                    E.append(ErlangBPojed(a, N))
        else:
            if type(N) is list:
                E = []
                for n in N:
                    E.append(ErlangBPojed(A, n))
            else:
                E = ErlangBPojed(A,N)
                
        return E
    except OverflowError:
        print ("numeric overflow, najprawdopodobniej silnia nie wyrabia ")
        return None
    
def ErlangBPojed(A,N):
    ''' Wedlug wzoru:
    E1,N(A) = ( A^N / N! ) / ( suma i od 0 do N (A^i / i!)) '''
    if N == 0:
        return 1
    
    szereg = 0.0
    for i in range(0,N+1):
        szereg += A**i / szybkaSilnia(i)
    
    Eb = (( A**N ) / szybkaSilnia(N) )/  szereg
    return Eb

def TestErlanga():
    print 'Wzor Erlanga, potfornie prosty test'
    print ' rzuc okiem, czy to sa poprawne wartosci'
    for a in range (0,6):
        for n in range(0,6):
            print "E 1,%d(%d) = %f" % (n, a, ErlangBPojed(a,n)) 


if __name__ == '__main__':
    TestErlanga()
    
    
    
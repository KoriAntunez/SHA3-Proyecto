# Algoritmos SHA-3 
# -----------------------------------------------------------------------------------------------------
# Importación de Librerías
from tqdm import tqdm 
from termcolor import colored,cprint 


def sha3_224(message):
    '''Convierte el mensaje a mensaje binario y hash usando SHA3-224.'''
    message = ''.join([format(ord(char), '08b') for char in message]) + '01'
    return sponge(message, 224, 1600-448)

def sha3_256(message):
    '''Convierte el mensaje a mensaje binario y hash usando SHA3-256.'''
    message = ''.join([format(ord(char), '08b') for char in message]) + '01'
    return sponge(message, 256, 1600-512)

def sha3_384(message):
    '''Convierte el mensaje a mensaje binario y hash usando SHA3-384.'''
    message = ''.join([format(ord(char), '08b') for char in message]) + '01'
    return sponge(message, 384, 1600-768)

def sha3_512(message):
    '''Convierte el mensaje a mensaje binario y hash usando SHA3-512.'''
    message = ''.join([format(ord(char), '08b') for char in message]) + '01'
    return sponge(message, 512, 1600-1024)

def shake128(message, length):
    '''Convierte el mensaje a mensaje binario y hash usando SHAKE128.'''
    message = ''.join([format(ord(char), '08b') for char in message]) + '1111'
    return sponge(message, 256, length)

def shake256(message, length):
    '''Convierte el mensaje a mensaje binario y hash usando SHAKE256.'''
    message = ''.join([format(ord(char), '08b') for char in message]) + '1111'
    return sponge(message, 512, length)

# KECCAK-f[b] and Intermediate functions
# -----------------------------------------------------------------------------------------------------

def keccak(S):
    '''
    Función auxiliar para realizar permutaciones KECCAK en un mensaje dado.

     Parámetros:
         S (str): cadena de 1600 bits utilizada para describir un mensaje.

     Devoluciones:
         str: cadena de 1600 bits modificada por permutaciones KECCAK [θ, p, π, χ, and i]
    '''

    w = 64
    l = 6

    # 1. State Array Construction
    def state_initialize():
        a = {}

        for y in range(0, 5):
            for x in range(0, 5):
                for z in range(0, w):
                    a[x, y, z] = int(S[w * (5*y + x) + z])
        
        return a

    # 2. Keccak-p Permutations
    # θ (Algorithm 1)
    def θ(a):
        c = {}

        for x in range(0, 5):
            for z in range(0, w):
                c[x, z] = a[x, 0, z] ^ a[x, 1, z] ^ a[x, 2, z] ^ a[x, 3, z] ^ a[x, 4, z]

        d = {}

        for x in range(0, 5):
            for z in range(0, w):
                d[x, z] = c[(x-1) % 5, z] ^ c[(x+1) % 5, (z-1) % w]

        a_ = {}

        for y in range(0, 5):
            for x in range(0, 5):
                for z in range(0, w):
                    a_[x, y, z] = a[x, y, z] ^ d[x, z]

        return a_

    # p (Algorithm 2)
    def p(a):
        a_ = {}
        (x, y) = (1, 0)

        for z in range(0, w):
            a_[0, 0, z] = a[0, 0, z]
        
        for t in range(0, 24):
            for z in range(0, w):
                a_[x, y, z] = a[x, y, (z-(t+1)*(t+2)//2) % w]
            (x, y) = (y, (2*x + 3*y) % 5)

        return a_

    # π  (Algorithm 3)
    def π(a):
        a_ = {}

        for y in range(0, 5):
            for x in range(0, 5):
                for z in range(0, w):
                    a_[x, y, z] = a[(x + 3*y) % 5, x, z]

        return a_

    # χ  (Algorithm 4)
    def χ(a):
        a_ = {}

        for y in range(0, 5):
            for x in range(0, 5):
                for z in range(0, w):
                    a_[x, y, z] = a[x, y, z] ^ ((a[(x+1) % 5, y, z] ^ 1) & a[(x+2) % 5, y, z])
        
        return a_

    # rc  (Algorithm 5)
    def rc(t):
        if t % 255 == 0:
            return 1

        r = [1, 0, 0, 0, 0, 0, 0, 0]

        for i in range(1, (t % 255)+1):
            r.insert(0, 0)
            r[0] = r[0] ^ r[8] 
            r[4] = r[4] ^ r[8] 
            r[5] = r[5] ^ r[8] 
            r[6] = r[6] ^ r[8]
            r.pop()
        
        return r[0]

    # ι  (Algorithm 6)
    def i(A, r):
        a_ = A
        rc_ = [0 for x in range(0, w)]

        for j in range(0, l+1):
            rc_[(2**j) - 1] = rc(j + (7*r))

        for z in range(0, w):
            a_[0, 0, z] = a_[0, 0, z] ^ rc_[z]

        return a_

    # Rnd  
    def Rnd(A, r):
        return i(χ(π(p(θ(A)))), r)

    # 3. State Array Decomposition
    a = state_initialize()

    for r in range(0, 24):
        a = Rnd(a, r)

    s_ = ''

    for y in range(0, 5):
        for x in range(0, 5):
            for z in range(0, w):
                s_ += str(a[x, y, z])

    return s_


# pad10*1 
# ----------------------------------------------------------------------------------------------------- 
def pad(x, m):
    '''Pad data with 0's until it is a multiple of x'''
    j = (-m-2) % x

    return '1' + '0'*j + '1'


# sponge construction
# ----------------------------------------------------------------------------------------------------- 
def sponge(message, bit_length, rate):
    '''
    Helper function to perform absorbtion and squeezing steps of KECCAK.

    Parameters:
        message (str): message to be hashed.
        bit_length (int): length of digest.
        rate (int): hash rate of specified algorithm.

    Returns:
        str: Digest of message based on bit_length and rate.
    '''

    # 1. Set Constants
    p = message + pad(rate , len(message))
    n = len(p)//rate
    c = 1600 - rate
    s = '0'
    p_ = {}
    z = ''

    # 2. Absorb
    for i in range(0, n):
        p_[i] =  p[i*rate:(i*rate)+rate]
        s = keccak(format(int(s, 2) ^ int(p_[i] + '0'*c, 2), '01600b'))

    # 3. Squeeze
    z = s[0:rate] 

    if bit_length >= int(z, 2):
        s = keccak(format(int(s, 2), '01600b'))
        z += s[0:rate]
    else:
        return format(int(z[0:bit_length], 2), 'x')


def main():
    cprint('Ingrese el nombre del texto para el cifrado:',end=' ',color='yellow',attrs=['bold'])
    text = input()
    cprint('¡El proceso de cifrado está en progreso...!',color='green',attrs=['bold'])
    cprint('Done!! SHA3-224: {}'.format(sha3_224(text)),color='blue',attrs=['bold'])
    cprint('Done!! SHA3-256: {}'.format(sha3_256(text)),color='blue',attrs=['bold'])
    cprint('Done!! SHA3-384: {}'.format(sha3_384(text)),color='blue',attrs=['bold'])
    cprint('Done!! SHA3-512: {}'.format(sha3_512(text)),color='blue',attrs=['bold'])
    
main()
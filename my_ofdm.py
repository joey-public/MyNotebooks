import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

#Helper Functions
def plot_ofdm_constellations(rx_fsyms, N_FFT, rc, xlim=None, ylim=None, txt_loc=None):
    ROWS, COLS = rc
    if txt_loc==None: xl, yl = (0,0)
    else: xl, yl = txt_loc
    ch = 0
    spl = 1
    for i in range(ROWS*COLS):
        temp = rx_fsyms[ch,:] 
        plt.subplot(ROWS, COLS, spl)
        plt.scatter(np.real(temp), np.imag(temp))
        plt.text(xl,yl,'{}'.format(ch))
        if not(xlim==None): plt.xlim(xlim)
        if not(ylim==None): plt.ylim(ylim)
        ch += 1
        spl += 1

#TX functions
def gen_rand_bitstream():
    pass
def gen_rand_symbols(sz:tuple, alphabet:list=[-1+0j, 1+0j])->np.array:
    return np.random.choice(alphabet, sz)
def gen_symbol_mask(sz:tuple, channels:list, chnls_are_vld:bool=False)->np.array:
    #assume channels are the nulled subchannels by default
    #if 'chnls_are_vld=True' then assume we are given a list of the valid subchannels
    N,L = sz
    mask = np.ones(sz)
    for ch in channels:
        mask[ch,:] = np.zeros(L)
    if chnls_are_vld: #convert all 1->0 and 0->1
        mask = -1*(mask-1)
    return mask
def apply_symbol_mask(f_symbols:np.array, mask:np.array)->np.array:
    return np.multiply(f_symbols, mask)
def modulate_ofdm(f_symbols:np.array)->np.array:
    N,L = np.shape(f_symbols)
    s = np.zeros((N,L), dtype='complex')
    for col in range(L):
        s[:,col] = (1/(N**0.5))*np.fft.ifft(f_symbols[:,col]) 
    return s
def add_cp(s:np.array, N_CP:int, loc:str='front')->np.array:
    N,L = s.shape
    K = N+N_CP
    ans = np.zeros((K,L), dtype='complex')
    for col in range(L):
        sample_data = s[:,col]
        cp = sample_data[N-N_CP:N]
        if loc=='back':
            ans[0:N,col] = sample_data 
            ans[N:K,col] = cp 
        else:
            ans[0:N_CP,col] = cp
            ans[N_CP:K,col] = sample_data
    return ans
def p2s_conv(s:np.array)->np.array:
    return np.reshape(s.T, (np.size(s),))


#Channel Distortion Functions
def gen_2_path_chan(a0, a1, n0):
    if a1==0: return np.array([1]) 
    h = np.zeros(n0)
    h[0]=a0
    h[n0-1]=a1
    return h
def add_cfo(signal:np.array, cfo:float)->np.array:
    return signal * np.exp(2j*np.pi*cfo*np.arange(len(signal)))
def add_cto(signal:np.array, sto:float)->np.array:
    return np.hstack((np.zeros(sto), signal))
def add_awgn(s:np.array, sigma2:float)->np.array:
    n = np.sqrt(sigma2/2) * (np.random.randn(len(s)) + 1j*np.random.randn(len(s)))
#    n = sigma*np.random.randn(s.size)+sigma*1j*np.random.randn(s.size)
    return s+n
def apply_channel_filter(signal:np.array, h:np.array)->np.array:
    return sp.signal.lfilter(h, (1), signal)


#Estimation Functions
def get_schimdl_cox_metric(r:np.array, L:int)->dict:
    def estimate_cto(Md, th=0.5):
        ans = np.argwhere(Md > th)
        if len(ans) == 0:
            print('No Bueno')
            return 0
        else:
            return int(ans[0])
    def estimate_cfo(Md, cto, L):
        sum2 = np.sum(np.angle(Md[cto:cto+L]) / (2*np.pi*L))
        return sum2 / L
    def _get_pd(r, d, L):
        p = 0 + 0j
        rr  = 0 + 0j 
        for m in range(L):
            p += r[d+m].conj() * r[d+m+L]
            rr += r[d+m+L].conj() * r[d+m+L]
        return p, rr
    N = r.size
    p_metric = np.zeros(N-2*L, dtype=complex)
    r_metric = np.zeros(N-2*L, dtype=complex)
    for d in range(N-2*L):
        p_metric[d], r_metric[d] = _get_pd(r, d, L)
    Md = p_metric/r_metric
    cto_est = estimate_cto(Md)
    cfo_est = estimate_cfo(Md, cto_est, L)
    return cto_est, cfo_est, Md, p_metric, r_metric

def apply_freq_offset(signal, fn):
    #fn should be normalized frequency: fn = f/fs
    k = np.arange(signal.size)
    return signal * np.exp(1j * 2 * np.pi * k * fn)

def estimate_fine_cto(r:np.array, ts:np.array)->int:
    return np.argmax(np.abs(np.correlate(r, ts)))

def estimate_channel(tx_fsyms:np.array, Y0:np.array, Y1:np.array)->np.array:
    X = np.diag(tx_fsyms)
    X_H = X.conj().T
    H_est = 0.5 * np.matmul(X_H, (Y0+Y1))
    H_est[np.where(H_est==0)] = 1
    return H_est

#def estimate_channel(rx_signal, tx_fsyms, cto, L_CP):
#    N = tx_fsyms.size
#    tx_fsyms = np.reshape(tx_fsyms, (N,))
#    t0 = cto + L_CP 
#    t1 = cto + L_CP + N 
#    X = np.diag(tx_fsyms)
#    X_H = X.conj().T
#    Y0 = (N**0.5)*np.fft.fft(rx_signal[t0:t1])
#    Y1 = (N**0.5)*np.fft.fft(rx_signal[t1:t1+N])
#    return 0.5 * np.matmul(X_H, (Y0+Y1)) 


#RX Functions
def s2p_conv(rx_signal:np.array, N:int, L:int, N_CP:int)->np.array:
    return np.reshape(rx_signal, (L,N+N_CP)).T
def remove_cp(r:np.array, N_CP:int)->np.array:
    K,L = r.shape
    N = K-N_CP
    ans = np.zeros((N,L), dtype='complex')
    for col in range(L):
        ans[:,col] = r[N_CP:K,col]
    return ans
def demodulate_ofdm(r:np.array)->np.array:
    N,L = np.shape(r)
    f_symbols_rx = np.zeros((N,L), dtype='complex')
    for col in range(L):
        f_symbols_rx[:,col]=(N**0.5)*np.fft.fft(r[:,col])
    return f_symbols_rx
def equalize(r:np.array, h:np.array):
    N,L = r.shape
    eq_r = np.zeros(r.shape, dtype='complex')
    for col in range(L):
        eq_r[:,col]=r[:,col] / h
    return eq_r
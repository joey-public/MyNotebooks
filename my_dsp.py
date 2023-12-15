import numpy as np
import scipy as sp

def my_fft(x_n, fs, fftlen=-1, shifted=True, window='rect'):
    if not (window=='rect'): x_n = apply_window(x_n, window)
    if fftlen < len(x_n):  fftlen = len(x_n)
    x_f = np.fft.fft(x_n, fftlen)
    if shifted:
        f = np.arange(-fs/2, fs/2, fs/fftlen)
        x_f = np.fft.fftshift(x_f)
    else:
        f = np.arange(0, fs, fs/fftlen)
    return (f, x_f)

def my_apply_window(x:np.ndarray, window:str)->np.ndarray:
    valid_windows = ['bartlett', 'blackman', 'hamming', 'hanning', 'kaiser']
    if not window in valid_windows:
        print('Warning: {} is not a valid window -> {}'.format(window, valid_windows))
        print('....returning the origonal sequence')
        return x
    return x

def gen_summed_cos(N:int, fs:float, f:np.ndarray, amps:np.ndarray)->np.ndarray:
    l = len(f)
    n = np.linspace(np.zeros(l), (N-1)*np.ones(l), N)
    x = np.cos(2*np.pi*n*(f/fs))
    x = amps * x
    return np.sum(x, axis=1) 

def gen_summed_sinusoid(N:int, fs:float, f:np.ndarray, amps:np.ndarray)->np.ndarray:
    l = len(f)
    n = np.linspace(np.zeros(l), (N-1)*np.ones(l), N)
    x = np.cos(2*np.pi*n*(f/fs)) + 1j*np.sin(2*np.pi*n*(f/fs))
    x = amps * x
    return np.sum(x, axis=1) 

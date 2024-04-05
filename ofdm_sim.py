import numpy as np
import scipy.io as spio
import scipy.signal as spsg
import matplotlib.pyplot as plt

from my_ofdm import * 

def plot_conts(data):
    plt.scatter(np.real(data), np.imag(data), alpha=0.4)
    plt.xlabel('Real')
    plt.ylabel('Imag')
    plt.grid()

#Constants
N_FFT = 64
N_CP = 16
N_GI = 32
N_BLOCKS = 10

#import given data
ofdm_pkt = spio.loadmat('./matlab_data/ofdm_pkt.mat')
s = ofdm_pkt['s']
y = ofdm_pkt['y']

#Generate Known TX Training Sequence 
s = np.reshape(s, (s.size,))
tx_fsyms = np.zeros(N_FFT, dtype=complex)
tx_fsyms[1:27] = s[0:26]
tx_fsyms[38:64] = s[26:s.size]
#tx_fsyms[0:26] = s[0:26]
#tx_fsyms[37:63] = s[26:s.size]
tx_fsyms.shape = (N_FFT,1)
tx_tsamp = modulate_ofdm(tx_fsyms)
tx_ts_block = p2s_conv(tx_tsamp)
tx_ts_cp = tx_ts_block[N_FFT-2*N_CP:N_FFT]
tx_training_signal = np.hstack((tx_ts_cp, tx_ts_block, tx_ts_block))

#get the rx signal 
rx_signal = np.reshape(y, (y.size,))

#Coarse CTO and Fine CFO correction via Schmidl Cox algorithm
cto_est_coarse, cfo_est_fine, Md, pd, rd = get_schimdl_cox_metric(rx_signal, N_FFT)

#apply fine cfo correction
rx_signal = apply_freq_offset(rx_signal, -1*cfo_est_fine)

#Fine Timing Estimation with the cross correlation
xcorr = np.correlate(rx_signal, tx_training_signal)
cto_est_fine = np.argmax(np.abs(xcorr))

#correct timing offset
rx_signal = rx_signal[cto_est_fine:rx_signal.size]

#break rx waveform in training sequence and payload arrays
t0 = 0
t1 = t0 + 2*N_CP+2*N_FFT
t2 = t1 + N_GI 
t3 = t2 + (N_BLOCKS * (N_CP+N_FFT))
rx_training_signal = rx_signal[t0:t1]
rx_guard_signal = rx_signal[t1:t2]
rx_payload_signal = rx_signal[t2:t3]

#demodulate rx payload into the freq domain 
rx_payload_tseries = s2p_conv(rx_payload_signal, N_FFT, N_BLOCKS, N_CP)
rx_payload_tseries = remove_cp(rx_payload_tseries, N_CP)
rx_payload_fsyms = demodulate_ofdm(rx_payload_tseries)

#demodulate the rx training data into freq domain Y0 and Y1 
rx_training_tseries = s2p_conv(rx_training_signal[2*N_CP:t1], N_FFT, 2, 0)
rx_training_fsyms = demodulate_ofdm(rx_training_tseries)

#estimate the channel
tx_fsyms = np.reshape(tx_fsyms, (N_FFT,))
X = np.diag(tx_fsyms)
X_H = X.conj().T
Y0 = rx_training_fsyms[:,0]
Y1 = rx_training_fsyms[:,1]
H_est = 0.5 * np.matmul(X_H, (Y0+Y1))
H_est[np.where(H_est==0)] = 1e6 #make sure null channels are close to zero

#apply channel equalization to payload
eq_rx_payload_fsyms = np.zeros((N_FFT,N_BLOCKS), dtype=complex) 
for col in range(N_BLOCKS):
    eq_rx_payload_fsyms[:,col] = rx_payload_fsyms[:,col] / H_est

#Plots
plt.figure(1)
cto_text = 'Coarse CTO est = {}'.format(cto_est_coarse)
cfo_text = 'Fine CFO est = {}'.format(round(cfo_est_fine, 6))
plot_text = cto_text + '\n' + cfo_text
plt.plot(Md)
plt.title('Schmidl-Cox Metric')
plt.ylabel('Amplitude(M[d])')
plt.grid()
x,y = (200,0.8)
plt.text(x,y,plot_text)
plt.savefig('./images/sim2_1.jpeg')

plt.figure(2)
plt.plot(np.abs(np.abs(xcorr)))
plt.title('Xcorr of Deroted RX waveform and Known TX training Sequence')
plt.ylabel('Xcorr mag')
plt.xlabel('Sample Number')
plot_text ='Fine CTO est = {}'.format(cto_est_fine) 
x,y = (100,2)
plt.text(x,y,plot_text)
plt.savefig('./images/sim2_2.jpeg')

figsz = (10,8)
plt.figure(3, figsz)
plt.subplot(221)
plt.stem(tx_fsyms, label = 'TX Training Symbols 1st half ')
plt.xlabel('subcarrier index')
plt.ylabel('symbol value')
plt.legend()
plt.subplot(223)
plt.stem(tx_fsyms, label = 'TX Training Symbols 2nd half ')
plt.xlabel('subcarrier index')
plt.ylabel('symbol value')
plt.legend()
plt.subplot(222)
plt.stem(np.abs(Y0), label='RX Training Symbols 1st half ')
plt.plot(np.arange(1,27), np.abs(H_est[1:27]), 'r--', label='channel est')
plt.plot(np.arange(38,63), np.abs(H_est[38:63]), 'r--')
plt.xlabel('subcarrier index')
plt.ylabel('symbol value')
plt.legend()
plt.subplot(224)
plt.stem(np.abs(Y1), label='RX Training Symbols 2nd half ')
plt.plot(np.arange(1,27), np.abs(H_est[1:27]), 'r--', label='channel est')
plt.plot(np.arange(38,63), np.abs(H_est[38:63]), 'r--')
plt.xlabel('subcarrier index')
plt.ylabel('symbol value')
plt.legend()
plt.tight_layout()
plt.savefig('./images/sim2_3.jpeg')

plt.figure(4)
plt.suptitle('Unequalized Constellations All 10 Blocks')
all_syms = p2s_conv(rx_payload_fsyms)
print(all_syms.shape)
plot_conts(all_syms)
plt.title('All Subchannels')
plt.savefig('./images/sim2_4.jpeg')

fignum=5
for i in range(3):
    plt.figure(fignum)
    ch = eq_rx_payload_fsyms[:,i] 
    plot_conts(ch)
    plt.title('Unequalized Subchannel {}'.format(i))
    plt.savefig('./images/sim2_{}.jpeg'.format(fignum))
    fignum+=1

for i in range(3):
    plt.figure(fignum)
    ch = eq_rx_payload_fsyms[:,i] 
    plot_conts(ch)
    plt.title('Equalized Subchannel {}'.format(i))
    plt.xticks(np.linspace(-1,1,8))
    plt.yticks(np.linspace(-1,1,8))
    plt.savefig('./images/sim2_{}.jpeg'.format(fignum))
    fignum+=1

plt.figure(fignum)
plt.suptitle('Equalized Constellations All 10 Blocks')
all_syms = p2s_conv(eq_rx_payload_fsyms)
print(all_syms.shape)
plot_conts(all_syms)
plt.title('All Subchannels')
plt.xticks(np.linspace(-1,1,8))
plt.yticks(np.linspace(-1,1,8))
plt.savefig('./images/sim2_{}.jpeg'.format(fignum))

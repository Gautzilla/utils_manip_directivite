"""
Created on Feb 14 10:58:19 2024

@author: Francois Salmon, Noise Makers
"""

import numpy as np
import soundfile as sf
from scipy import signal, interpolate
import matplotlib.pyplot as plt
import pyloudnorm as pyln
from glob import glob


def frac_oct_smooth_fd(data_fd, frac=3):
    """
    ***FROM SoundFieldAnalysis Toolbox***

    Apply amplitude only fractional octave band smoothing to frequency
    domain data.

    This implementation is based on the amplitude ('welti') method of
    `AKfractOctSmooth()` in [9]_.

    Parameters
    ----------
    data_fd : numpy.ndarray
        Single-sided spectrum
    frac : float, optional
        Fraction of octaves, e.g. third octaves by default [Default: 3]

    Returns
    -------
    numpy.ndarray
        Smoothed single-sided spectrum

    References
    ----------
    .. [9] Brinkmann, F., and Weinzierl, S. (2017). “AKtools - An Open Software
    Toolbox for Signal Acquisition, Processing, and Inspection in Acoustics,”
    AES Conv. 142, Audio Engineering Society, Berlin, Germany, 1–6.
    """
    def interp1(x, y, x_2interp, kind="linear"):
        """simple wrapper to use interp1d MATLAB like"""
        # check if target x values exceed given x_values
        if x_2interp.max() > x.max() or x_2interp.min() < x.min():
            # make extrapolate function
            interpolator_function = interpolate.interp1d(x, y, kind, fill_value="extrapolate")
        else:
            interpolator_function = interpolate.interp1d(x, y, kind)
        return interpolator_function(x_2interp)

    # check dimension and transform to sample X channel
    data_fd = np.atleast_2d(data_fd).copy()

    # if operation == "welti":  # according to `AKfractOctSmooth()`
    num_bins = data_fd.shape[-1]
    start_bin, stop_bin = 1, num_bins
    N = stop_bin

    # multiplicative factors
    spacing = 10 ** (np.log10(stop_bin - start_bin) / N)
    # number of bins per octave
    N_oct = np.log10(2) / (frac * np.log10(spacing))
    N_oct_even = round(N_oct / 2) * 2
    # logarithmic scalar
    log_bins = np.logspace(np.log10(start_bin), np.log10(stop_bin - 1), N)
    lin_bins = np.arange(0, num_bins)

    if np.iscomplexobj(data_fd):
        data_fd = np.abs(data_fd)
    data_fd_ip = interp1(lin_bins, data_fd, log_bins, kind="cubic")

    fd_win = signal.windows.gaussian(N_oct_even * 2, N_oct_even / 2.5)
    fd_lead = np.ones(np.append(data_fd.shape[:-1], fd_win.size)) * data_fd_ip[..., :1]
    fd_lag = np.ones(np.append(data_fd.shape[:-1], fd_win.size)) * data_fd_ip[..., -1:]
    data_fd_ip_extrap = np.concatenate((fd_lead, data_fd_ip, fd_lag), axis=-1)

    data_fd_temp = signal.filtfilt(b=fd_win, a=1, x=data_fd_ip_extrap) / np.sum(fd_win) ** 2
    data_fd_temp = data_fd_temp[..., fd_win.size: fd_win.size + num_bins]
    data_fd_sm = interp1(log_bins, data_fd_temp, lin_bins, kind="linear")
    return data_fd_sm


def get_mag_corr(pmx_file, ref_file):
    """

    :param pmx_file:
    :param ref_file:
    :return:
    """
    y0, fs = sf.read(ref_file)
    y, fs = sf.read(pmx_file)
    # ensure that they have the same length
    y = y[:len(y0)]
    y0 = y0[:len(y)]
    # compute spectrograms
    f, t, sxx0 = signal.spectrogram(y0, fs=fs, mode='complex', nperseg=8192)
    sxx0 = np.abs(sxx0) / np.amax(np.abs(sxx0))
    f, t, sxx = signal.spectrogram(y, fs=fs, mode='complex', nperseg=8192)
    sxx = np.abs(sxx) / np.amax(np.abs(sxx))

    mag = []
    nfft = int(2 * (len(f) - 1))
    thre = get_rms_threshold(sxx0, t)  # 'noise gate' threshold
    for i in range(len(t)):
        rms = get_rms(sxx0[:, i])
        if rms < thre:  # remove segments with low energy
            continue
        s_abs0 = frac_oct_smooth_fd(sxx0[:, i]).flatten()
        s_abs = frac_oct_smooth_fd(sxx[:, i]).flatten()
        if np.all(s_abs > 0) and np.all(s_abs0 > 0):
            mag.append(20*np.log10(s_abs/s_abs0))

    freq = np.fft.rfftfreq(nfft, 1/fs)
    mag = np.mean(np.array(mag), axis=0)

    return mag, freq, fs


def get_rms_threshold(sxx, t):
    """

    :param sxx:
    :param t:
    :return:
    """
    rms = np.zeros(len(t))
    for i in range(len(t)):
        rms[i] = get_rms(sxx[:, i])

    return np.mean(rms) - np.std(rms)


def get_rms(rfft):
    """

    :param rfft:
    :return:
    """
    nfft = int(2 * (len(rfft) - 1))
    rms = np.sqrt((np.sum(np.abs(rfft) ** 2) + np.sum(np.abs(rfft[1:-1]) ** 2)) / nfft)
    return rms


def write_inverse_filter(pmx_file, ref_file, ntaps=4097, f_min=20, f_max=16000, figure=False):
    """

    :param pmx_file:
    :param ref_file:
    :param ntaps:
    :param f_min:
    :param f_max:
    :param figure:
    :return:
    """
    mag, f, fs = get_mag_corr(pmx_file, ref_file)
    b_min = int(f_min * len(f) / fs * 2)
    b_max = int(f_max * len(f) / fs * 2)
    mag[:b_min] = mag[b_min]
    mag[b_max:] = mag[b_max]

    inv_abs = 10 ** (-mag / 20)
    inv = signal.firls(ntaps, f[1:], inv_abs[1:], fs=fs)

    if figure:
        f2 = np.fft.rfftfreq(ntaps, 1 / fs)
        inv_mag = 20 * np.log10(np.abs(np.fft.rfft(inv)))
        plt.semilogx(f, -mag)
        plt.semilogx(f2, inv_mag)
        plt.ylim([-7, 16])
        plt.ylabel('Magnitude (dB)')
        plt.xlabel('Frequency (Hz)')
        plt.title('Correction filter ' + pmx_file + ' vs ' + ref_file)
        plt.show()

    inv /= np.amax(np.abs(inv))
    filename = f'{pmx_file[:-4]}_inv_filter.wav'
    sf.write(filename, inv, fs, subtype='PCM_32')

    return filename


def apply_correction(pmx_file, inv_file, loudness_ref_file=None):
    """

    :param pmx_file:
    :param inv_file:
    :param loudness_ref_file:
    :return:
    """
    inv, fs = sf.read(inv_file)
    y, fs = sf.read(pmx_file)

    if y.ndim == 1:
        y = y.reshape((-1, 1))

    s = np.zeros((len(y)+len(inv)-1, y.shape[1]))
    for i in range(y.shape[1]):
        s[:, i] = signal.convolve(y[:, i], inv)

    if loudness_ref_file is not None:
        meter = pyln.Meter(fs)
        y0, fs = sf.read(loudness_ref_file)
        target_l = meter.integrated_loudness(y0)
        l = meter.integrated_loudness(s)
        s *= 10**((target_l - l)/20)

    sf.write(f'{pmx_file[:-4]}_corr.wav', s, fs, subtype='PCM_24')


def main():
    # suffix = '001'
    # pmx_file = f'KU100-Repro-{suffix}.wav'
    # ref_file = f'KU100-{suffix}.wav'
    # inv_file = write_inverse_filter(pmx_file, ref_file, figure=True)

    pmx_file = r'C:\Users\User\Documents\Gaut\PostDoc\Manips\Directivité\RepetitionCabine\MatchEQ\pmx_file.wav'
    ref_file = r'C:\Users\User\Documents\Gaut\PostDoc\Manips\Directivité\RepetitionCabine\MatchEQ\ref_file.wav'
    inv_file = write_inverse_filter(pmx_file, ref_file, figure=True)
    for file_to_correct in glob('C:/Users/User/Documents/Gaut/PostDoc/Manips/Directivité/RepetitionCabine/Media/*Arceau*[0-9].wav'):
        apply_correction(file_to_correct, inv_file, loudness_ref_file = ref_file)

if __name__ == "__main__":
    main()
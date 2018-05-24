# -*- coding: utf-8 -*-

import rtlsdr
import numpy as np
from scipy.signal import hilbert, remez, lfilter, decimate, freqz
from scipy.io import wavfile
import matplotlib
matplotlib.use('Agg')  # http://stackoverflow.com/a/3054314/3524528
import matplotlib.pyplot as plt


# Define si se quiere que se hagan los gráficos o no:
# PLOT = 0 # No se calculan los gráficos
PLOT = 1 # Se calcula los gráficos


def GetSample(f_station, f_offset, fs, N, gain='auto'):
    """
    Genera una muestra de radio FM:

    Parametros:
        f_station:	Frecuencia de la Estación	
        f_offset:	Frecuencia corrida		
        fs:			Frecuencia de muestreo
        N:			Cantidad de muestras
        gain:		Ganancia de la señal
    """

    sdr = rtlsdr.RtlSdr()
    fc = f_station - f_offset  # Frecuencia del centro de captura
    # Se configura los parametros
    sdr.sample_rate = fs
    sdr.center_freq = fc
    sdr.gain = gain
    # Lee las N muestras
    samples = sdr.read_samples(N)
    # Limpiar el dispositivo SDR
    sdr.close()
    del(sdr)
    return samples


def ToBaseBand(xc, f_offset, fs):
    """
    Parametros:
        xc:			Señal a mandar a banda base
        f_offset:	Frecuencia que esta corrido
        fs:			Frecuencia de muestreo
    """
    #if PLOT:
        #PlotSpectrum(xc, "xc", "xc_offset_spectrum.pdf", fs)
    # Se lo vuelve a banda base, multiplicando por una exponencial con fase f_offset / fs
    x_baseband = xc * np.exp( (-1.0j * 2.0 * np.pi * f_offset/fs) * np.arange(len(xc)) )
    #if PLOT:
        #PlotSpectrum(x_baseband, "x baseband", "x_baseband_spectrum.pdf", fs)
    return x_baseband


def FilterAndDownSample(x, fs):
    """
    Parametros:
        x:	Señal a filtrar y
        fs:	Frecuencia de muestreo
    """
    f_bw = 180e3 # FM tiene un ancho de banda de BW=180 kHz
    # traps es el número de términos en el filtro, o el orden de filtro más uno.
    n_taps = 50
    # Calcule el filtro óptimo minimax utilizando el algoritmo de intercambio Remez.
    coef = remez(n_taps, [0,f_bw,f_bw*1.4,fs/2], [1,0], Hz=fs)
    x_filter = lfilter(coef, 1.0, x)

    #PlotFilterCharacteristic(coef, fs)

    dec_rate = int(fs / f_bw)
    x_downsample = x_filter[0::dec_rate]  
    # Se calcula la nueva frecuencia de muestreo
    fs_y = fs / dec_rate
    if PLOT:
        PlotSpectrum(x_downsample, "x downsample", "x_downsample_spectrum.pdf", fs_y)
        PlotConstelation(x_downsample, "x downsample", "x_downsample.pdf")
    return x_downsample, fs_y


def Demodulation(x, fs):
    """
    Demodula con discriminador polar

    Parametros:
            xc: Señal modulada.
            fs: Frecuencia de muestreo
    """
    # Derivador y detector de envolvente.
    # xd = [0, np.diff(x) * fs]
    # xd = hilbert(xd)
    # yd = xd - np.mean(xd)
    # yd = yd/max(abs(yd))
    
    xd = x[1:] * np.conj(x[:-1])
    yd = np.angle(xd)
    return yd

    
def FilterPreEmphasis(f_offset, fs, yd):
    """
    Parametros:
            f_offset:	Frecuencia corrida
            fs:         Frecuencia de muestreo
    """
    fs_tau = fs * 75e-6		# Constante de tiempo tau
    x = np.exp(-1/fs_tau)	# Calcula decaimiento del filtro
    b = [1-x]           	# Crea el filtro de coeficientes
    a = [1,-x]
    yd_filter = lfilter(b, a, yd)
    return yd_filter


def PlotSpectrum(x, x_name, file_name, fs):
    """
    Parametros:
        x:          Señal a realizar el gráfico del espectro
        x_name:     Nombre de la variable, sera mostrada como label
        file_name:  Nombre del archivo a guardar por defecto
        fs:         Frecuencia de muestreo
    """
    plt.specgram(x, NFFT=2048, Fs=fs, cmap='viridis') # viridis, plasma, inferno, magma
    plt.title(x_name)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Frecuencia (Hz)")
    plt.ylim(-fs/2, fs/2)
    plt.xlim(0, len(x)/fs)
    plt.margins(0.1)
    plt.ticklabel_format(style='plain', axis='y')
    plt.colorbar()
    plt.savefig(file_name, dpi=300, format='pdf', bbox_inches='tight', pad_inches=0)
    plt.close()


def PlotConstelation(x, x_name, file_name):
    """
    Parametros:
        x:          Señal a realizar el gráfico de constelación
        x_name:     Nombre de la variable, sera mostrada como label
        file_name:  Nombre del archivo a guardar
    """
    plt.scatter(np.real(x[0:50000]), np.imag(x[0:50000]), color="blue", alpha=0.05)
    plt.title(x_name)
    plt.xlabel("Real")
    plt.xlim(-1.1,1.1)
    plt.ylabel("Imag")
    plt.ylim(-1.1,1.1)
    plt.savefig(file_name, dpi=300, format='pdf', bbox_inches='tight', pad_inches=0)
    plt.close()


def PlotFilterCharacteristic(coef, fs):
    freq, response = freqz(coef)
    plt.semilogy(0.5 * fs * freq / np.pi, np.abs(response), 'b-')
    plt.grid(alpha=0.25)
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Ganancia')
    plt.savefig("filter_charac.pdf", bbox_inches='tight', pad_inches=0)
    plt.close()


def DEP(x, x_name, file_name, fs):
    """
    Parametros:
        x:          Señal a realizar el gráfico DEP
        x_name:     Nombre de la variable, sera mostrada como label
        file_name:  Nombre del archivo a guardar
        fs:         Frecuencia de muestreo
    """
    plt.psd(x, NFFT=2048, Fs=fs, color="blue")
    plt.title(x_name)
    plt.axvspan(0,             15000,         color="red", alpha=0.2)
    plt.axvspan(19000-500,     19000+500,     color="green", alpha=0.4)
    plt.axvspan(19000*2-15000, 19000*2+15000, color="orange", alpha=0.2)
    plt.axvspan(19000*3-1500,  19000*3+1500,  color="blue", alpha=0.2)
    plt.ticklabel_format(style='plain', axis='y' )
    plt.savefig(file_name, dpi=300, format='pdf', bbox_inches='tight', pad_inches=0)
    plt.close()


def SaveToAudioFile(yd, file_name, fs):
    """
    Parametros:
        yd:          Señal que ya esta adaptada para escuchar
        file_name:  Nombre del archivo a guardar
        fs:         Frecuencia de muestreo
    """
    # Acondiciona el sonido para que tenga una frecuencia de entre 44-48 kHz
    audio_freq = 44100.0
    dec_audio = int(fs / audio_freq)
    fs_audio = int(fs / dec_audio)
    sound = decimate(yd, dec_audio)
    print("Frec audio: ", fs_audio)
    
    # Se escala el volumne del audio
    sound *= 10000 / np.max(np.abs(sound))
    # Guarda el sonido en 16-bit con signo
    wavfile.write(file_name, fs_audio, sound.astype("int16"))
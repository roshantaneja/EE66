# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ipython==8.32.0",
#     "matplotlib==3.10.0",
#     "numpy==2.2.3",
#     "pandas==2.2.3",
#     "scipy==1.15.1",
#     "marimo",
# ]
# [tool.marimo.runtime]
# auto_instantiate = true
# output_max_bytes = 10_000_000
# ///

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # EE 66 Shazam
    ### EE 66: Introduction to Signals, Dynamics, and Information, Fall 2026

    Taken and modified from EE 120: Signals and Systems at UC Berkeley

    Acknowledgements:

    - **Spring 2020** (v1.0): Anmol Parande, Dominic Carrano, Babak Ayazifar
    - **Spring 2022** (v2.0): Anmol Parande
    - **Spring 2023** (v2.1): Yousef Helal
    - **Fall 2023** (v2.2): Christine Zhang
    - **Fall 2024** (v3.0): Nikhil Ograin
    - **Spring 2025** (v3.1): Sonia Chacon
    - **Fall 2025** (v3.2): Andrew Song
    - **Fall 2026** (v3.3): Baris Oktay
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Background

    In 2002, Shazam Entertainment Limited (founded by UC Berkeley students!) launched its music identification product, allowing users to dial a phone number and play a song. Then, they'd get a text message with the name of the song and its artist. In 2018, Shazam was acquired by Apple for \$400 million, and it's now in every iPhone.

    Shazam works by using *audio fingerprinting*: given a song, it generates a set of identifiers, and searches an audio database to find a match and identify the song. In this lab, you'll learn about audio fingerprinting, and use it to build a music identification just like Shazam!

    ## Dependencies

    This marimo notebook depends on [Pandas](https://pandas.pydata.org/docs/getting_started/install.html) and a few other packages. Luckily, marimo installs these automatically for you.
    """)
    return


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy.signal as signal
    import pandas as pd
    import IPython.display as ipd
    from scipy.io import wavfile
    from scipy.ndimage import maximum_filter
    from shazam_utils import hashing
    import autograder
    return autograder, hashing, ipd, maximum_filter, np, pd, plt, signal, wavfile


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Note*: To avoid any copyright issues, we've cropped all provided songs to only contain the first 60 seconds.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Python Imports Primer
    In Python Bootcamp, we introduced NumPy and some other Python libraries. In this lab, you'll have to use some functions from the libraries imported above. But wait; what's an import? And how do you use any of these?

    #### `import`
    An import statement in Python indicates that you can use functions from that Python module (a file containing reusable Python code) within the current marimo notebook. A basic example is
    ```
    import numpy
    ```
    This lets us use NumPy functions such as `numpy.array` or `numpy.eye`. However, for some packages (such as NumPy, Pandas, or Matplotlib) it is standard practice to import them as another name. For example:

    ```
    import numpy as np
    ```
    This still lets us use NumPy functions, but using `np.FUNCTION` instead of `numpy.FUNCTION`. For example, `np.array` or `np.eye`. Note that we have done this for you above.

    Extensions on imported modules work in exactly the same way but do NOT require further imports. For example `np.linalg.solve` only requires the import statement `import numpy as np`.

    Import statements only need to be defined once! Meaning they should not be contained within functions (that are by design intended to run multiple times).

    #### `from`
    If we want to only import a specific function (or set of functions), we can use the `from` keyword. For example, if we want `numpy.array`:
    ```
    from numpy import array
    ```
    We can then use this without the `numpy` prefix, simply `array`. We can combine this with the `as` keyword as well:
    ```
    from numpy import array as arr
    ```
    The `numpy.array` function is then usable as `arr`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Glossary

    We know there are a lot of (probably new) acronyms which this lab will introduce, so we've included a brief listing of them here:

    - CT: Continuous Time - time progresses continuously, i.e. time which spans all real numbers within some interval, how we live in the real life world
    - DT: Discrete Time - time takes discrete steps and is undefined for all other real numbers within some interval, i.e. when data is sampled at a certain rate
    - FT: Fourier Transform - a mathematical operation that decomposes a time-domain signal or function into frequencies
    - DFT: Discrete Fourier Transform - a Fourier transform that takes in a discrete time-domain signal and outputs a discrete frequency-domain signal
    - FFT: Fast Fourier Transform - an algorithm for performing a DFT (usually computerized)
    - DTFT: Discrete-Time Fourier Transform - a Fourier transform that takes a discrete-time signal and produces a continuous, periodic function of frequency

    You don't need to understand these right now! However, if you ever find yourself stuck on a vocabulary term while completing this lab, you can come back to these definitions. Now onto the lab content!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Q1: Spectral Analysis

    For many types of data, the constituent frequencies of a signal tell us a lot about it. The same is true of audio: to find the salient features of songs to fingerprint, we'll need to look at the song's spectrum (i.e., Fourier Transform). Fortunately, we have the DFT (efficiently implemented via the FFT) to help us do this.

    To get started, let's load in *Viva La Vida* by Coldplay.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Typically, we think of audio as a two-channel, continuous signal $\vec{x}(t) = \left[x_L(t) \ x_R(t)\right]$, with one column of the *audio matrix* per channel. That is, $x_L(t)$ is the left channel's signal, and $x_R(t)$ the right channel's signal. The reason we have two distinct audio channels is so that we can have two streams playing at the same time, one per ear (e.g., in a pair of headphones or laptop speakers).

    We sample this continuous-time (CT) audio signal at a particular rate (here, 48000 Hz) to get a discrete-time (DT) signal. For our purposes, the distinction between our channels is not very important, so we'll just average them to form a 1D signal, $x(n)$.
    """)
    return


@app.cell
def _(np, wavfile):
    fs, coldplay = wavfile.read("public/VivaLaVida.wav")
    print(f"Audio Shape: {coldplay.shape}, Sampling Rate: {fs} Hz")
    coldplay = np.mean(coldplay, axis=1)
    return coldplay, fs


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To show you what this looks like in the time-domain (i.e. before we have performed the DFT on this data), execute the following code block.
    """)
    return


@app.cell
def _(coldplay, fs, plt):
    plt.figure(figsize=(16, 4), dpi=200)
    coldplay_labels = [x / fs for x in range(fs * 10)]
    plt.plot(coldplay_labels, coldplay[: fs * 10])
    plt.xlabel("Time [s]")
    plt.ylabel("Magnitude")
    plt.title("Time-domain visualization of first 10 seconds of Viva La Vida")
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To get a sense for the song we're working with, feel free to have a listen! This cell may take a few seconds to run.
    """)
    return


@app.cell
def _(mo):
    mo.audio("public/VivaLaVida.wav")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q1a: One DFT is Not Enough

    As far as spectral analysis is concerned, it seems like we should just be able to take the DFT of the entire song, find our fingerprints, and be done, right? Is that really all there is to Shazam? No, not quite. It may not be obvious, but there's a big issue with this approach that we'll explore now. So that our code doesn't take forever to run, we'll only look at the first 10 seconds of the song, but the issues we'll find here apply generally to the entire signal.

    To start, let's define a function which will give us the magnitude spectrum of the signal $|X(\omega)|$ centered around $\omega = 0$.

    ### Your Job

    Fill in the code for `centered_magnitude_spectrum`, which takes in a signal and outputs its centered magnitude spectrum.

    1. Perform a 1-D DFT on `sig` with [`np.fft.fft`](https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html).
    2. Shift the DFT to $[-\pi$, $\pi]$ with [`np.fft.fftshift`](https://numpy.org/doc/stable/reference/generated/numpy.fft.fftshift.html).
    3. Find the magnitude of the shifted DFT, i.e. $|X(\omega)|$

    Why is this function named `centered_magnitude_spectrum`? Let's break it down into components:
    - `centered`: By default, when you compute the FFT, the samples of the DTFT that are returned go from $0$ to $2\pi$; centering them so that they go from $-\pi$ to $\pi$ is nicer for visualization.
    - `magnitude`: The signal is composed of complex numbers, and we only really care about their magnitudes.
    - `spectrum`: A "spectrum" is a fancy way of saying "some data over a range of frequencies", which is what a DFT outputs.

    <!-- *Hint*: Check out [np.fft.fftshift](https://numpy.org/doc/stable/reference/generated/numpy.fft.fftshift.html) to center your spectrum. -->
    """)
    return


@app.cell(hide_code=True)
def _(hint_1_1, mo):
    mo.md(f"""
    {mo.as_html(hint_1_1)}
    """)
    return


@app.cell
def centered_magnitude_spectrum(np):
    def centered_magnitude_spectrum(sig):
        """
        Inputs:
        sig - a generic iterable signal of floating point numbers

        Output (np.ndarray):
        Returns a centered magnitude spectrum of the given signal.
        That is, the magnitude of the DFT of the provided signal
        after shifting from [0,2pi] to [-pi,pi].
        """

        # TODO YOUR CODE HERE
        ...
    return (centered_magnitude_spectrum,)


@app.cell
def _(autograder, centered_magnitude_spectrum):
    autograder.test_Q1a(centered_magnitude_spectrum)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    To see why one DFT won't suffice, we're going to look at the spectrum of different sections of Viva La Vida.

    First, we'll look at magnitude spectrum of the first 10 seconds of the song.
    """)
    return


@app.cell
def _(coldplay, fs, np, plt):
    coldplay_cropped = coldplay[: 10 * fs]
    coldplay_freqs = centered_magnitude_spectrum(coldplay_cropped)
    plt.figure(figsize=(16, 4), dpi=200)
    _freqs = np.linspace(-fs / 2, fs / 2, len(coldplay_freqs))
    plt.plot(_freqs, coldplay_freqs)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("Magnitude")
    plt.title("DFT of first 10 seconds of Viva La Vida")
    plt.gca()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Most of the frequency content is centered around the lower frequencies. In fact, we can barely see anything past 10 kHz, because human hearing stops around 15-20 kHz (and generally decreases with age), so there's no reason to include anything that high in music.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    So far, everything looks ok: we got the spectrum of the first 10 seconds of our song. This gives us a sort of "aggregate view" of the frequencies that show up at some point during the first 10 seconds. But is this "aggregate view" good enough? What happens if our signal is *non-stationary*, i.e its frequency content changes with time, as is certainly the case with music?

    To find out, let's look at the magnitude spectra of the first, second, third, and fourth seconds of the song. We'll use these to zoom in (temporally speaking) and inspect the song's frequency content over the course of a second of data (rather than 10), and see if the "aggregate view" gives a good enough picture of what frequencies are present at a specific second in time.
    """)
    return


@app.cell
def _(coldplay, fs, np, plt):
    coldplay_freqs_1 = centered_magnitude_spectrum(coldplay[:fs])
    coldplay_freqs_2 = centered_magnitude_spectrum(coldplay[fs : 2 * fs])
    coldplay_freqs_3 = centered_magnitude_spectrum(coldplay[2 * fs : 3 * fs])
    coldplay_freqs_4 = centered_magnitude_spectrum(coldplay[3 * fs : 4 * fs])
    _freqs = np.linspace(-fs / 2, fs / 2, len(coldplay_freqs_1))
    sigs = [coldplay_freqs_1, coldplay_freqs_2, coldplay_freqs_3, coldplay_freqs_4]
    strs = ["1st", "2nd", "3rd", "4th"]
    plt.figure(figsize=(16, 10), dpi=200)
    for i in range(1, 5):
        plt.subplot(2, 2, i)
        plt.plot(_freqs, sigs[i - 1])
        plt.xlim([-5000.0, 5000.0])
        plt.ylim([0, 1.1 * np.array(sigs).max()])
        plt.title("DFT magnitude of {} second of Viva La Vida".format(strs[i - 1]))

    plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice how while most of the energy in each second's spectrum is concentrated inside $[-2.5 \text{ kHz}, +2.5 \text{ kHz}]$, the exact shapes are quite different.

    **The issue is that the aggregate view from our 10-second DFT doesn't have good enough *temporal resolution*: we can't see how the signal's frequency content changes over time!**

    Why does this matter, you ask? Well, when we're working with the real deal, we don't feed Shazam the entire song; only a clip. For example, suppose you tune into a radio station halfway through a song. Then, 20 seconds later, you think to yourself, "hey, I like this" and pull out Shazam to figure out what song it is. By then, whatever you're giving Shazam is missing a lot of data, and so it needs to be able to look at what frequencies are in the song at different points in time to correctly identify it. The aggregate view won't do. Fortunately, there's a very simple fix to this.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q1b: Spectrogramming

    The results of Q1a are pretty clear: we need a way to see how the signal's frequency content changes over time. Just taking one DFT of the entire signal fails to achieve this. Instead, we'll use a *spectrogram*.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
        ### Spectrograms

        A *spectrogram* is an image representing the frequency content of a signal at different times. This ability to see how a signal's frequency content changes with time is the key useful feature of a spectrogram.

        To compute a spectrogram, we split our signal into chunks, compute the DFT of each chunk, and plot the magnitude squared of those DFT chunks side-by-side. To make visualization easier, we typically employ a colormap to distinguish where the DFT's squared-magnitude is bigger.

        For example, here is a locally provided spectrogram of speech. The red areas correspond to stronger frequency content, and green areas to weaker frequency content.

        Notice the differences between when the speaker takes a breath and when the speaker is actually speaking. A single DFT wouldn't be able to separate this!
        """),
        mo.image(
            "public/speech-spectrogram.png",
            alt="Speech spectrogram with speech and breath regions labeled",
            width="100%",
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.vstack([
        mo.md(r"""
        Remember that this spectrogram isn't new data. It is simply a new view of the existing time-domain data we already have. The image below ([source](https://www.tek.com/de/blog/spectrogram-types-the-many-faces-of-the-spectrogram)) shows this in a visual form.
        """),
        mo.image(
            "public/spectrogram_display.jpg",
            alt="A spectrogram shown as time-frequency slices",
            width="100%",
        ),
    ])
    return


@app.cell(hide_code=True)
def _(
    add_freq_button,
    axs,
    clear_freq_button,
    frequency_slider,
    magnitude_slider,
    mo,
    offset_slider,
):
    mo.md(f"""
    Let's gain an intuition for how the frequency content of a signal affects its spectral plot. Use the sliders and buttons below to see how adding different frequencies to a signal affects its spectral plot. These plots show the frequency being added and what adding the new frequency does to the current signal. Try different frequencies as well as magnitudes.

    {mo.as_html(frequency_slider)} <br>
    {mo.as_html(magnitude_slider)} <br>
    {mo.as_html(offset_slider)} <br>
    {mo.as_html(add_freq_button)} {mo.as_html(clear_freq_button)}


    <div style="display:flex; flex-direction: row; justify-content: center; align-items: center">
        {mo.as_html(axs[0])}
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    As expected, the *pure tones* (sin waves with a constant frequency) have 2 peaks each. Adding a frequency, introduces two new peaks at that frequency. One assumption was that we assumed the signals would continue for the entire time duration. Let's see how changing the offset of a signal affects its spectrograms.

    In addition to choosing magnitude and frequency of a signal, you can also choose the sample offset. Each sin wave will only last for 500 samples, and can be offset to occur in the window of samples 0 and 1000. Note that the list of frequencies is synchronized between this demo and the one above. Clear the frequencies to start over.
    """)
    return


@app.cell(hide_code=True)
def _(
    add_freq_button,
    axs_spec,
    clear_freq_button,
    frequency_slider,
    magnitude_slider,
    mo,
    offset_slider,
):
    mo.md(f"""
    {mo.as_html(frequency_slider)} <br>
    {mo.as_html(magnitude_slider)} <br>
    {mo.as_html(offset_slider)} <br>
    {mo.as_html(add_freq_button)} {mo.as_html(clear_freq_button)}


    <div style="display:flex; flex-direction: row; justify-content: center; align-items: center">
        {mo.as_html(axs_spec[0])}
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compare the aggregate spectrum with the spectrogram while you add tones and change their offsets. The aggregate spectrum shows *which* frequencies occur, but not *when* they occur. The spectrogram keeps both pieces of information: horizontal position is time, vertical position is frequency, and color represents spectral strength.

    A band may spread slightly beyond the exact interval where you placed a tone because SciPy analyzes overlapping, windowed chunks. This trades some time resolution for better frequency resolution, a topic covered in more detail in EE 123.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q1c: Spectrograms of Songs

    Now that we've got the basic concepts down, let's load *Viva La Vida* and *Mr. Brightside* and compare their spectrograms. Run the cell below to load the songs.
    """)
    return


@app.cell
def _(np, wavfile):
    fs_1, coldplay_1 = wavfile.read("public/VivaLaVida.wav")
    coldplay_1 = np.mean(coldplay_1, axis=1)
    fs_1, killers = wavfile.read("public/MrBrightside.wav")
    killers = np.mean(killers, axis=1)
    return coldplay_1, fs_1, killers


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Since we haven't heard *Mr. Brightside* yet, let's load it in now and have a listen. This cell will take a few seconds to load before the audio interface shows up.
    """)
    return


@app.cell
def _(mo):
    mo.audio("public/MrBrightside.wav")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A spectrogram is useful here because music is non-stationary: its frequency content changes over time. A single DFT tells us which frequencies occurred somewhere in a clip, while a spectrogram tells us both **which frequencies** occurred and **when** they occurred.

    To make that time-frequency view easier to read, we'll plot the spectrogram values in decibels.

    A decibel is a logarithmic unit of measuring sound, and is often used for visualization in cases like this where we have a large signal range. You might see this abbreviated as dB. In future classes, you will find that dB can also be used for logarithmic measurement of other types of waveforms (for example, in circuits).

    ## **Decibel conversion**

    $$\Large\boxed{x_\mathrm{dB}=20\log_{10}(x)}$$

    The logarithm compresses the large dynamic range of audio so quieter structure remains visible instead of being overwhelmed by the strongest peaks. **Use `np.log10`, not `np.log`.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Your Job

    In the cell below:
    1. Use [`signal.spectrogram`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.spectrogram.html) to compute the spectrogram of each song **before doing any decibel conversion**.
        - Pass both `audio` and its sampling frequency `fs`.
        - Use 4096 for the `nperseg` parameter of `signal.spectrogram` to take a 4096 point DFT. This matches the length of DFT typically used in practical audio fingerprinting systems, representing a good tradeoff between spectral and temporal resolution.
        - The function returns a tuple containing the frequencies of the spectrogram samples, time points of the spectrogram samples, and the actual spectrogram. **Make sure you return these in the same order they are provided by `signal.spectrogram`!**.
    2. Convert only the resulting spectrogram array to the decibel scale using `20 * np.log10(...)`.

    **To ensure there are no divide by zero warnings and to make sure the spectrogram renders properly, please add `epsilon_db_constant` (a small positive constant) before taking the log when converting to decibels.**

    <!-- *Hint*: Make sure you use `np.log10` in your computations -->

    <!-- *Hint*: Don't forget to pass in the sampling frequency, `fs`, into the spectrogram! -->
    """)
    return


@app.cell(hide_code=True)
def _(hint_1_2, hint_1_3, mo):
    mo.md(f"""
    {mo.as_html(hint_1_2)}
    {mo.as_html(hint_1_3)}
    """)
    return


@app.cell
def compute_spectrogram(np, signal):
    def compute_spectrogram(fs, audio, epsilon_db_constant):
        """
        Input:
        fs - the sampling frequency of the audio, in Hertz (Hz)
        audio - the full audio to compute the spectrogram of; either coldplay or killers
        epsilon_db_constant - a small positive constant to ensure there are no divide by zero errors

        Output (np.ndarray, np.ndarray, np.ndarray):
        Returns a scipy spectrogram for the given audio (in decibels) with three components:
         - a NumPy array of sample frequencies
         - a NumPy array of segment times
         - the spectrogram itself

        See:
        scipy.signal.spectrogram
        numpy.log10
        """

        # TODO YOUR CODE HERE
        ...
    return (compute_spectrogram,)


@app.cell
def _(autograder, compute_spectrogram):
    autograder.test_Q1c(compute_spectrogram)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's have a look! Run the cell below to compute spectrograms for both *Viva La Vida* and *Mr. Brightside*, then plot their spectrograms.
    """)
    return


@app.cell
def _(coldplay_1, fs_1, killers, plt):
    f1_1, t1_1, coldplay_spect = compute_spectrogram(
        fs_1, coldplay_1, epsilon_db_constant=1e-12
    )
    _f2, _t2, killers_spect = compute_spectrogram(
        fs_1, killers, epsilon_db_constant=1e-12
    )
    plt.figure(figsize=(20, 10), dpi=200)
    plt.subplot(2, 1, 1)
    plt.pcolormesh(t1_1, f1_1, coldplay_spect, cmap="jet", shading="auto")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [sec]")
    plt.title("Viva La Vida")
    plt.colorbar(label="Spectrogram value [dB]")
    plt.subplot(2, 1, 2)
    plt.pcolormesh(_t2, _f2, killers_spect, cmap="jet", shading="auto")
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [sec]")
    plt.title("Mr. Brightside")
    plt.colorbar(label="Spectrogram value [dB]")
    plt.gca()
    return coldplay_spect, f1_1, t1_1


@app.cell(hide_code=True)
def _(answer_1_1, answer_1_2, answer_1_3, mo):
    mo.md(f"""
    Q: In both spectrograms, we see a column of dark blue for the first second or so. Based on our colorbar, it looks like this corresponds to ≈ -300 dB, or essentially no signal power. In terms of the songs, why do we have this in our plots? {mo.as_html(answer_1_1)}

    Q: At the beginning of the spectrogram for Mr. Brightside (after the column of dark blue), you should see two peaks that extend up toward 20 kHz. What sound in the song is this part of the spectrogram capturing? {mo.as_html(answer_1_2)}

    Q: Can you easily tell the two songs' spectrograms apart? Do you think they'd make good building blocks for our audio recognition algorithm? {mo.as_html(answer_1_3)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Q2: Fingerprinting

    Our end goal here is to take an audio snippet and figure out what song's being played. To do this, we'll need a database of songs to compare against.

    Should we just store entire songs in the database? Probably not, as that'd be a very large database: a three-minute WAV file sampled at $48 \text{ kHz}$ is a about $30 \text{ MB}$ in size. Even if we aimed for the modest goal of 1000 songs (which the original iPod from 2001 could hold), we're already looking at using over $30 \text{ GB}$ of storage. Additionally, comparing raw audio samples for similarity isn't very robust against noise.

    Instead, we'll generate a set of *fingerprints* from each song, and store these in our database. When our version of Shazam gets fed a song to classify, it can just compare the fingerprints, rather than looking at the whole song. This should solve our storage issues, provided the fingerprints aren't too large. But clearly we'll need this fingerprinting algorithm to have a few other properties for this audio recognition system to be useful.

    In particular, we want our audio fingerprint to have four key properties:
    1. ***Temporal Locality:*** We're trying to figure out what song is being played based on a short (say, 5 to 10 second long) clip. So, our fingerprints should somehow encode *where* in the song they come from.

    2. ***Translational Invariance:*** The snippet we play for Shazam could come from anywhere in the song. We could play it the first 5 seconds, the last 5, or something in the middle. In all cases, we want a correct result, so the same chunk of audio should get the same fingerpint regardless of whether it shows up a minute into a clip or right at the beginning—it's the actual music in it that we should use to generate the fingerprint.

    3. ***Robustness:*** An audio file, whether clean or degraded by (a modest amount of) noise, should produce the same fingerprint.

    4. ***High Entropy:*** The fingerprinting algorithm should be "random enough" that two different songs don't produce the same fingerprint.

    As it turns out, spectrograms have all these nice properties, which is why they're such an important part of Shazam! The company's founders recognized this too, and discussed it in their original paper, linked in the references.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **So, spectrograms are cool, but how can we use them? They contain thousands of points... how do we pick which are the most important?**

    As you might guess, we'll look at the spectrogram's *peaks*: points in high-energy areas. These are the most likely to survive distortions from noise, unlike ones that are close to zero and easily drowned out.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q2a: Peak Finding

    To extract these peaks, we want to find areas of the spectrogram where's there's some point that has more energy than its neighbors. To do this, we're going to need some filtering.

    ### Max Filtering

    To do our peak finding, we'll use Scipy's [`maximum_filter`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.maximum_filter.html) function with a neighborhood of 51 (the `size` parameter in the function call).

    For each point in our spectrogram, this filter will take our spectrogram $f(x, y)$ and output $g(x, y)$, the maximum value in a 51x51 region around the pixel. Because a spectrogram has two axes, pass the scalar `neighborhood_size` to `size`; SciPy applies that size to both dimensions.

    Formally,

    $$g(x, y) = \max_{i,j} f(x+i, y+j) \text{  where } -25\le i, j \le 25.$$

    ### Your Job

    1. Implement the maximum filter and apply it to the provided spectrogram. When the neighborhood exceeds the boundary of the image, assume $f(x, y)$ is the value of the image at that point (i.e., set `mode='constant'`).
    2. Extract a boolean mask which is True when $f(x, y) = g(x, y)$, and False otherwise.
    3. To ensure these peaks are big enough, in the mask, set any peak locations with a peak less than or equal to `AMP_THRESH` to zero. This is filled in for you.
    4. Use [`np.nonzero`](https://numpy.org/doc/stable/reference/generated/numpy.nonzero.html) on the **boolean `mask`** (not on `spect`) to convert the selected peaks into (frequency, time) index arrays.
    """)
    return


@app.cell
def _(coldplay_spect, maximum_filter, np):
    def peak_finding(spect, neighborhood_size=2*25+1, amp_thresh=40):
        """
        Input:
        spect - the spectrogram of an unknown audio track to find peaks from
        neighborhood_size - the size of the maximum filter
        amp_thresh - amplitude threshold to include peaks in result
    
        Output (np.ndarray, np.ndarray):
        Returns a tuple of the peak indices on the frequency 
        and time axes (each as NumPy arrays) for the provided spectrograph.
    
        See:
        maximum_filter
        np.nonzero
        """

        # Apply a Maximum Filter
        max_spect = ...

        # Compute the mask
        mask = ...

        # Filter out tiny peaks
        mask &= spect > amp_thresh

        # Get the indices of the peaks
        freq_indices, time_indices = ...

        return freq_indices, time_indices

    # Call peak_finding with the spectrogram for Viva La Vida
    freq_indices, time_indices = ...
    return freq_indices, peak_finding, time_indices


@app.cell
def _(autograder, coldplay_spect, freq_indices, peak_finding, time_indices):
    autograder.test_Q2a(
        peak_finding, coldplay_spect, freq_indices, time_indices
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's run the next cell and see where our peaks are! We'll label them with black dots for clarity.
    """)
    return


@app.cell
def _(coldplay_spect, f1_1, freq_indices, plt, t1_1, time_indices):
    plt.figure(figsize=(16, 6), dpi=200)
    plt.scatter(t1_1[time_indices], f1_1[freq_indices], zorder=99, color="k")
    plt.pcolormesh(
        t1_1, f1_1, coldplay_spect, zorder=0, cmap="jet", shading="auto"
    )
    plt.ylabel("Frequency [Hz]")
    plt.xlabel("Time [sec]")
    plt.title("Spectrogram Peaks (for Viva La Vida)")
    plt.xlim([0, 60])
    plt.gca()
    return


@app.cell(hide_code=True)
def _(answer_2_1, mo):
    mo.callout(
        mo.vstack([
            mo.md("### Q2a written response"),
            mo.md(r"""
            **Q:** In Q1, we saw how most of the information in music signals is in the lower frequencies (under, say, $10 \text{ kHz}$). How does this compare with the spectrogram peaks? Are they mostly in the lower or upper half of the spectrogram? Is this what you'd expect?
            """),
            answer_2_1,
        ]),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q2b: Fingerprinting
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The peaks we've found make up what the creators of Shazam call a *constellation map*. We'll use the points in our constellation map to compute the song's fingerprints.

    To do this, we'll take each peak, say $(t_i, f_i)$, and chain it together with the next $n$ peaks $(t_{i+1}, f_{i+1}), ..., (t_{i+n}, f_{i+n})$ by hashing the values of the peaks. Hashing is out of the scope of this course, but at a high level hashing is a technique that transforms any given key or string into an essentially unique hash, or fingerprint.

    ### Provided hashing helper

    ```python
    def hashing(frequencies, times, frequency_indices, time_indices):
        # Return a list of (hash, anchor_time) tuples for the selected peaks.
    ```

    Call it as `hashing(f1, t1, freq_indices, time_indices)` after you find the peaks.

    After fingerprinting, all we need to do is search our database for a match. If we did things correctly, the database entry we have the most fingerprints in common with should match the true song.

    Let's move all of this code into a single function so we can easily compute hashes for any audio signal.

    `fingerprint` should return an array of tuples, each one containing the hash $h$ and the time $t_i$.

    *Note:* Don't convert the spectrogram to decibels in this part! We converted the spectrogram to decibels in earlier parts for ease of rendering, but there's no need to do that here (and converting to decibels will cause you to fail the tests). This also means **DO NOT USE your implementation of `compute_spectrogram` from Q1c**.

    When calling `peak_finding`, explicitly forward both configurable parameters:

    ```python
    peak_finding(spect, neighborhood_size=neighborhood_size, amp_thresh=amp_thresh)
    ```

    Default values do not carry from one function to another automatically; forwarding them also ensures that non-default test values work.

    <!-- *Hint:* We specify that you should not use `compute_spectrogram` but it may be useful to look into that function -->
    """)
    return


@app.cell(hide_code=True)
def _(hint_2_1, mo):
    mo.md(f"""
    {mo.as_html(hint_2_1)}
    """)
    return


@app.cell
def _(hashing, np, peak_finding, signal):
    def fingerprint(fs, audio, neighborhood_size=2*25+1, amp_thresh=40):
        """
        Input:
        fs - the sampling frequency of the audio, in Hertz (Hz)
        audio - the full audio to fingerprint; either coldplay or killers
        neighborhood_size - the size of the maximum filter
        amp_thresh - amplitude threshold to include peaks in result
    
        Output (list[str, int]):
        A list of hashes representing the "fingerprint" of the given audio.
        """
        audio = np.mean(audio, axis=1)
    
        # Compute the spectrogram of the single channel audio
        f1, t1, spect = ...

        # Find the peaks (Use function from Q2a)
        freq_indices, time_indices = ...
    
        # Compute the hashes
        hashes = ...
    
        # Return list of hashes
        return hashes
    return (fingerprint,)


@app.cell
def _(autograder, fingerprint):
    autograder.test_Q2b(fingerprint)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Q3: Testing
    As mentioned before, all we need to do now is test our system and make sure it's as robust as we think it is. Our database is stored in `database.csv`. It's columns are |Hash|t1|Song|. A production application with thousands of songs in the database would use SQL or some other querying language, but a simple CSV will suffice for our uses.

    Because searching through our database is more of a software problem than a Signals and Systems problem, we've provided the detection function for you.

    This function:
    1. Loads the CSV using pandas (a data analysis package),
    2. Fingerprints the unknown sample,
    3. Searches for matches, and
    4. Returns the song with the most matches, its confidence as a percentage.
    """)
    return


@app.cell
def _(fingerprint, pd):
    def detect(fs, audio):
        db = pd.read_csv("database.csv", header=None, names=["Hash", "time", "Song"])

        hashes = fingerprint(fs, audio)
        db_matches = db[db.Hash.isin(map(lambda x: x[0], hashes))]
        if len(db_matches) == 0:
            print("No Matches")
            return

        counts = db_matches.groupby("Song").size()
        counts = counts / counts.sum()
        return counts.idxmax(), counts.max() * 100
    return (detect,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3a: Segmenting Audio

    Shazam usually only has a few seconds of data to work with, so we will as well. Start by writing a function to take a 20 second segment from either Viva La Vida or Mr. Brightside. The specific start and end times don't matter too much, just remember both audio tracks are only 60 seconds long!

    <!-- *Hint:* You've probably seen this operation performed several times already in this lab -->
    """)
    return


@app.cell(hide_code=True)
def _(hint_3_1, mo):
    mo.md(f"""
    {mo.as_html(hint_3_1)}
    """)
    return


@app.function
def get_20_second_segment(fs, audio):
    """
    Input:
    fs - the sampling frequency of the audio, in Hertz (Hz)
    audio - the full audio to get 20 seconds of; either coldplay or killers
    
    Output:
    A 20 second segment anywhere within the given audio track.
    
    Example:
    get_20_second_segment(killers) == killers[X seconds:(X + 20 seconds)]
    """
    
    ...


@app.cell
def _(autograder):
    autograder.test_Q3a(get_20_second_segment)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    You will now use this function to write tests for your Shazam system!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3b: Basic Testing

    Let's see how our system does under ideal conditions (i.e, no noise). Take a 20 second segment from Viva La Vida and Mr. Brightside and call the `detect` function to identify it. We've already reloaded the audio for you.
    """)
    return


@app.cell
def _(wavfile):
    fs_2, coldplay_2 = wavfile.read("public/VivaLaVida.wav")
    fs_2, killers_1 = wavfile.read("public/MrBrightside.wav")
    return coldplay_2, fs_2, killers_1


@app.cell
def basic_detect_test(detect, get_20_second_segment):
    def basic_detect_test(fs, audio):
        """
        Input:
        fs - the sampling frequency of the audio, in Hertz (Hz)
        audio - the full audio to detect against; either coldplay or killers

        Output:
        Returns the name of the audio track that most closely matches
        a 20 second segment of the provided audio track, and a percentage confidence.

        Example:
        basic_detect_test(killers_fs, killers) == ('MrBrightside.wav', 100.0)

        See also:
        get_20_second_segment
        detect
        """

        ...
    return (basic_detect_test,)


@app.cell
def _(autograder, basic_detect_test):
    autograder.test_Q3b(basic_detect_test)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3c: Gaussian Noise
    We want our system to be robust to different forms of noise. To start, let's add Gaussian noise to the provided audio and try to detect its origin. Add noise with a mean and standard deviation of 10000, then pass the noisy audio to `detect` and see if you can identify it.

    Preserve the input shape by passing `size=audio_segment.shape` to `np.random.normal`. For stereo audio that shape includes the second dimension for the two channels; the same code also works for mono audio.

    <!-- *Hint 1*: Check out the [`np.random.normal`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html) function.
    <br> -->
    <!-- *Hint 2*: Make sure to pass the `size` parameter to `np.random.normal`
    <br><br> -->
    *Note*: the tests for this section will add random noise to both songs and check that the `detect` function still classifies them correctly.
    """)
    return


@app.cell(hide_code=True)
def _(hint_3_2, hint_3_3, mo):
    mo.md(f"""
    {mo.as_html(hint_3_2)}
    {mo.as_html(hint_3_3)}
    """)
    return


@app.cell
def _(np):
    NOISE_MEAN = 10000
    NOISE_STANDARD_DEVIATION = 10000

    def add_gaussian_noise(audio_segment):
        """
        Input:
        audio_segment - an audio segment from an unknown track
    
        Output:
        Returns the audio segment with added Gaussian noise.
    
        See:
        Problem description (for quantities)
        np.random.normal
        """
    
        # TODO YOUR CODE HERE

        ...
    return (add_gaussian_noise,)


@app.cell
def gaussian_noise_detect_test(add_gaussian_noise, detect):
    def gaussian_noise_detect_test(fs, audio_segment):
        """
        Input:
        fs - the sampling frequency of the audio, in Hertz (Hz)
        audio_segment - an audio segment from an unknown track WITHOUT Gaussian noise

        Output:
        Returns the name of the audio track that most closely matches
        the provided audio track, WITH added Gaussian noise, and a
        percentage confidence.

        See:
        add_gaussian_noise
        detect
        """

        # TODO YOUR CODE HERE
        ...
    return (gaussian_noise_detect_test,)


@app.cell
def _(add_gaussian_noise, autograder, gaussian_noise_detect_test):
    autograder.test_Q3c(add_gaussian_noise, gaussian_noise_detect_test)
    return


@app.cell
def _(coldplay_2, fs_2, gaussian_noise_detect_test):
    noisy_detection_result = gaussian_noise_detect_test(fs_2, coldplay_2)
    print("Noisy Viva La Vida detection:", noisy_detection_result)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Our version of Shazam should still be able to detect the song. How does it sound, though?
    """)
    return


@app.cell
def _(add_gaussian_noise, coldplay_2, fs_2, ipd):
    ipd.Audio(
        add_gaussian_noise(get_20_second_segment(fs_2, coldplay_2)).T, rate=fs_2
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It sounds terrible, and we can barely make out the music! Yet, our system should still identify it as *Viva La Vida*. This works because the fingerprint uses strong local spectrogram peaks. Random noise changes many samples, but enough prominent time-frequency relationships survive to match the database.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3d: Blocked Speaker

    What if instead of Gaussian noise, a portion of the audio just becomes zero? Arguably, this is a more realistic model of how our signal could get corrupted when dealing with music recognition. For example, somebody could move in front of the speaker, pause the music, or turn the volume down very low.

    Let's take a 20 second chunk of Viva La Vida, zero out five 2 second chunks, and see if we can still detect the source.

    You don't need to implement any code here — just run the cells.
    """)
    return


@app.cell
def _(coldplay_2, fs_2):
    unknown_segment = coldplay_2[10 * fs_2 : 30 * fs_2].copy()
    unknown_segment[: 2 * fs_2] = 0
    unknown_segment[6 * fs_2 : 8 * fs_2] = 0
    unknown_segment[16 * fs_2 : 20 * fs_2] = 0
    unknown_segment[2 * fs_2 : 4 * fs_2] = 0
    return (unknown_segment,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's hear how the song sounds with these portions removed.
    """)
    return


@app.cell
def _(fs_2, ipd, unknown_segment):
    ipd.Audio(unknown_segment.T, rate=fs_2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    How does Shazam do now? Surely it'll fail with half the clip missing.
    """)
    return


@app.cell
def _(detect, fs_2, unknown_segment):
    detect(fs_2, unknown_segment)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Again, it succeeds! Our fingerprinting procedure is again proving its robustness. What about *Mr. Brightside*?
    """)
    return


@app.cell
def _(fs_2, killers_1):
    unknown_segment_1 = killers_1[10 * fs_2 : 30 * fs_2].copy()
    unknown_segment_1[: 2 * fs_2] = 0
    unknown_segment_1[6 * fs_2 : 8 * fs_2] = 0
    unknown_segment_1[16 * fs_2 : 20 * fs_2] = 0
    unknown_segment_1[2 * fs_2 : 4 * fs_2] = 0
    return (unknown_segment_1,)


@app.cell
def _(fs_2, ipd, unknown_segment_1):
    ipd.Audio(unknown_segment_1.T, rate=fs_2)
    return


@app.cell
def _(detect, fs_2, unknown_segment_1):
    detect(fs_2, unknown_segment_1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Looks like our system is pretty robust!
    """)
    return


@app.cell(hide_code=True)
def _(answer_3_1, mo):
    mo.md(f"""
    Q: What happens in the frequency domain when we zero out parts of the signal in the time domain? {mo.as_html(answer_3_1)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <a id='feedback'></a>
    ## Feedback
    If you have any feedback to give the teaching staff about the course (lab content, staff, etc), you can submit it through this Google form. Responses are **fully anonymous** and responses are actively monitored to improve the labs and course. Completing this form is **not required**.

    [Anonymous feedback Google form](https://forms.gle/ezDiDHxYRHN7xtdV9)

    *If you have a personal matter to discuss or need a response to your feedback, please contact <a href="mailto:ee66.lab@berkeley.edu">ee66.lab@berkeley.edu</a> and/or <a href="mailto:ee66@berkeley.edu">ee66@berkeley.edu</a>*.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <a id='checkoff'></a>
    ## Checkoff
    To receive credit, all labs will require the submission of a checkoff Google form. This link will be at the bottom of each lab. Both partners should fill out the form (you should have one submission per person), and feel free to use the same Google account/computer to fill it out as long as you have the correct names and student IDs.

    [Fill out the checkoff Google form.](https://forms.gle/pwqopqgEaHvv7GUk9)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Final Comments (Optional)
    There are many ways to improve our Shazam system. Many of them have to do with how we compute our spectrogram as well as the various parameters we introduced such as `NEIGHBORHOOD_SIZE`, `AMP_THRESH`, and `HASHES_PER_PEAK`. But, for the most part, this is how Shazam works!

    The original Shazam paper uses a different method for matching the fingerprints of audio instead of a simple "most matches => song" scheme, but for our limited database, this works just fine. Check out the original paper if you are curious. If you'd like, you can use the following cells to load your own songs into the database (as long as they are wav files) and try to identify samples of them.
    """)
    return


@app.cell
def _(fingerprint, wavfile):
    import csv


    def add_to_db(filename):
        fs, audio = wavfile.read(filename)
        hashes = fingerprint(audio, fs)
        with open("database.csv", mode="a") as db_file:
            db_writer = csv.writer(
                db_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )
            for hash_pair in hashes:
                db_writer.writerow([hash_pair[0], hash_pair[1], filename])
    return (add_to_db,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Run this to add a song to the database.
    """)
    return


@app.cell
def _(add_to_db):
    # Optional: uncomment and set this to add your own WAV file to the database.
    # my_wav_filepath = "public/YourSong.wav"
    # add_to_db(my_wav_filepath)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Then run this to detect against your updated database. Inputting the same WAV file should result in your new WAV file being detected! Try with a WAV file that isn't in the database, or a WAV file that is a composite of multiple songs in the database. Experiment and see what happens!
    """)
    return


@app.cell
def _(detect, wavfile):
    # Optional: uncomment and set this to identify your own WAV file.
    # fs_3, audio = wavfile.read("public/YourSong.wav")
    # detect(fs_3, audio)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # References

    [1] *An industrial strength audio search algorithm.* [[Link](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf)].
    [2] *Audio fingerprinting with Python and Numpy.* [[Link](https://willdrevo.com/fingerprinting-and-audio-recognition-with-python/)].
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Below is helper code used to create the demos above. Please don't modify.
    """)
    return


@app.cell
def _(mo):
    frequency_slider = mo.ui.slider(0, 500, show_value=True, label="Frequency", step=10)
    magnitude_slider = mo.ui.slider(0, 10, show_value=True, label="Magnitude")
    offset_slider = mo.ui.slider(0, 500, show_value=True, label="Offset", step=10)
    return frequency_slider, magnitude_slider, offset_slider


@app.cell
def _(mo):
    from dataclasses import dataclass

    @dataclass
    class Signal:
        amplitude: int = 0
        freq: int = 0
        offset: int = 0

    get_signals, set_freq = mo.state([])
    freq_added, set_freq_added = mo.state(False)
    return Signal, get_signals, set_freq, set_freq_added


@app.cell
def _(
    Signal,
    frequency_slider,
    magnitude_slider,
    mo,
    offset_slider,
    set_freq,
    set_freq_added,
):
    def add_freq():
        if frequency_slider.value and magnitude_slider.value:
            set_freq(lambda v: v + [Signal(magnitude_slider.value, frequency_slider.value, offset_slider.value)])
            set_freq_added(True)

    def clear_freq():
        set_freq([])

    add_freq_button = mo.ui.button(
        label="add frequency",
        on_change=lambda _: add_freq(),
    )

    clear_freq_button = mo.ui.button(
        label="clear all frequencies",
        on_change=lambda _: clear_freq()
    )
    return add_freq_button, clear_freq_button


@app.cell
def _(get_signals):
    signal_list = get_signals()
    return


@app.cell
def _(frequency_slider, get_signals, magnitude_slider, np, offset_slider, plt):
    x_values = np.linspace(0, 0.1, 1000)
    x_values1 = np.linspace(0, 1, 1000)
    aggregate_signal = np.zeros(x_values.shape)
    aggregate_signal1 = np.zeros(x_values.shape)

    for s in get_signals():
        _signal = s.amplitude * np.sin(2 * np.pi * s.freq * x_values)
        _signal[:s.offset] = 0
        _signal[s.offset+500:] = 0
        _signal1 = s.amplitude * np.sin(2 * np.pi * s.freq * x_values1)
        _signal1[:s.offset] = 0
        _signal1[s.offset+500:] = 0
        aggregate_signal += _signal
        aggregate_signal1 += _signal1

    fig, axs = plt.subplots(ncols=3, nrows=1, figsize=(15,5), layout="constrained")
    to_add = magnitude_slider.value * np.sin(2 * np.pi * frequency_slider.value * x_values)
    to_add[:offset_slider.value] = 0
    to_add[offset_slider.value+500:] = 0
    axs[0].plot(x_values, to_add)
    axs[0].set_title('Frequency to Add')
    axs[0].set_xlabel('Time [s]')
    axs[0].set_ylabel('Amplitude')
    axs[1].plot(x_values, aggregate_signal)
    axs[1].set_title('Aggregate Signal')
    axs[1].set_xlabel('Time [s]')
    axs[1].set_ylabel('Amplitude')
    axs[2].plot(np.linspace(-500, 500, len(aggregate_signal)), centered_magnitude_spectrum(aggregate_signal1))
    axs[2].set_title('Aggregate Signal Spectrum')
    axs[2].set_xlabel('Frequency [Hz]')
    axs[2].set_ylabel('Magnitude')

    print("set up graphs")
    return aggregate_signal, aggregate_signal1, axs, to_add, x_values


@app.cell
def _(aggregate_signal, aggregate_signal1, plt, signal, to_add, x_values):
    f1_demo, t1_demo, freqs_demo = signal.spectrogram(aggregate_signal1, fs=1000)

    fig_spec, axs_spec = plt.subplots(ncols=3, nrows=1, figsize=(15,5), layout="constrained")
    axs_spec[0].plot(x_values, to_add)
    axs_spec[0].set_title('Frequency to Add')
    axs_spec[0].set_xlabel('Time [s]')
    axs_spec[0].set_ylabel('Amplitude')
    axs_spec[1].plot(x_values, aggregate_signal)
    axs_spec[1].set_title('Aggregate Signal')
    axs_spec[1].set_xlabel('Time [s]')
    axs_spec[1].set_ylabel('Amplitude')
    axs_spec[2].pcolormesh(0.1*t1_demo, f1_demo, freqs_demo, cmap="gray", shading="auto")
    axs_spec[2].set_title('Aggregate Signal Spectrogram')
    axs_spec[2].set_xlabel('Time [s]')
    axs_spec[2].set_ylabel('Frequency [Hz]')

    print("set up graphs")
    return (axs_spec,)


@app.cell
def _(mo):
    hint_1_1 = mo.accordion({"Hint": "Use [`np.fft.fft`](https://numpy.org/doc/stable/reference/generated/numpy.fft.fft.html) to compute the DFT, then [`np.fft.fftshift`](https://numpy.org/doc/stable/reference/generated/numpy.fft.fftshift.html) to center it."})

    hint_1_2 = mo.accordion({"Hint 1": "Make sure you use `np.log10` in your computations"})

    hint_1_3 = mo.accordion({"Hint 2": "Don't forget to pass in the sampling frequency, `fs`, into the spectrogram!"})

    hint_2_1 = mo.accordion({"Hint": "We specify that you should not use `compute_spectrogram` but it may be useful to look into that function"})

    hint_3_1 = mo.accordion({"Hint": "You've probably seen this operation performed several times already in this lab"})

    hint_3_2 = mo.accordion({"Hint 1": "Check out the [`np.random.normal`](https://numpy.org/doc/stable/reference/random/generated/numpy.random.normal.html) function."})

    hint_3_3 = mo.accordion({"Hint 2": "Pass `size=audio_segment.shape` to `np.random.normal` so mono and stereo inputs keep their shape."})
    return hint_1_1, hint_1_2, hint_1_3, hint_2_1, hint_3_1, hint_3_2, hint_3_3


@app.cell
def _(mo):
    answer_1_1 = mo.ui.text_area(placeholder="Write your response here...", label="Your answer", rows=3, full_width=True)

    answer_1_2 = mo.ui.text_area(placeholder="Write your response here...", label="Your answer", rows=3, full_width=True)

    answer_1_3 = mo.ui.text_area(placeholder="Write your response here...", label="Your answer", rows=3, full_width=True)

    answer_2_1 = mo.ui.text_area(placeholder="Write your response here...", label="Your answer", rows=4, full_width=True)

    answer_3_1 = mo.ui.text_area(placeholder="Write your response here...", label="Your answer", rows=3, full_width=True)
    return answer_1_1, answer_1_2, answer_1_3, answer_2_1, answer_3_1



if __name__ == "__main__":
    app.run()

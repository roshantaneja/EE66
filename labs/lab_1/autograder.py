from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.ndimage import maximum_filter


_BASE_DIR = Path(__file__).resolve().parent
EPSILON_DB_CONSTANT = 1e-12


def _audio_path(filename):
    """Resolve audio in either the student public/ folder or solution folder."""
    for candidate in (_BASE_DIR / "public" / filename, _BASE_DIR / filename):
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Could not find required audio file: {filename}")


FS_AG, COLDPLAY_AG = wavfile.read(_audio_path("VivaLaVida.wav"))
KILLERS_FS_AG, KILLERS_AG = wavfile.read(_audio_path("MrBrightside.wav"))
assert FS_AG == KILLERS_FS_AG, "The provided songs must have the same sample rate."


def test_Q1a(centered_magnitude_spectrum):
    cases = [
        (
            np.ones(10),
            np.array([0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0]),
        ),
        (
            [10] * 5 + [6 * 2] + [3] * 4,
            np.array(
                [2.0, 9.0, 5.46491887, 9.0, 21.6364198, 74.0,
                 21.6364198, 9.0, 5.46491887, 9.0]
            ),
        ),
    ]
    for values, expected in cases:
        actual = centered_magnitude_spectrum(values)
        assert isinstance(actual, np.ndarray), (
            "centered_magnitude_spectrum must return a NumPy array."
        )
        assert np.allclose(actual, expected), (
            "Check that you call np.fft.fft, then np.fft.fftshift, then np.abs."
        )

    print("Question 1a Passed!")


def test_Q1c(compute_spectrogram):
    for name, stereo_audio in (
        ("Viva La Vida", COLDPLAY_AG),
        ("Mr. Brightside", KILLERS_AG),
    ):
        audio = np.mean(stereo_audio, axis=1)
        expected_f, expected_t, expected_spect = signal.spectrogram(
            audio, fs=FS_AG, nperseg=4096
        )
        expected_spect = 20 * np.log10(
            expected_spect + EPSILON_DB_CONSTANT
        )

        actual_f, actual_t, actual_spect = compute_spectrogram(
            FS_AG, audio, EPSILON_DB_CONSTANT
        )
        assert isinstance(actual_f, np.ndarray), (
            f"{name}: frequencies must be a NumPy array."
        )
        assert isinstance(actual_t, np.ndarray), (
            f"{name}: times must be a NumPy array."
        )
        assert isinstance(actual_spect, np.ndarray), (
            f"{name}: the spectrogram must be a NumPy array."
        )
        assert np.allclose(actual_f, expected_f), (
            f"{name}: frequency bins are incorrect. Pass fs to signal.spectrogram."
        )
        assert np.allclose(actual_t, expected_t), (
            f"{name}: time bins are incorrect. Use nperseg=4096."
        )
        assert np.allclose(actual_spect, expected_spect), (
            f"{name}: compute signal.spectrogram first, then apply "
            "20 * np.log10(spect + epsilon_db_constant)."
        )

    print("Question 1c Passed!")


def _expected_peaks(spect, neighborhood_size, amp_thresh):
    max_spect = maximum_filter(
        spect, size=neighborhood_size, mode="constant"
    )
    mask = (spect == max_spect) & (spect > amp_thresh)
    return np.nonzero(mask)


def test_Q2a(peak_finding, spect, freq_idx, time_idx):
    assert callable(peak_finding), (
        "Return peak_finding from its Marimo cell so later cells can use it."
    )
    assert isinstance(freq_idx, np.ndarray) and isinstance(time_idx, np.ndarray), (
        "peak_finding must return two NumPy arrays."
    )

    expected_freq, expected_time = _expected_peaks(spect, 51, 40)
    assert np.array_equal(freq_idx, expected_freq), (
        "Frequency indices are incorrect. Apply np.nonzero to the boolean mask."
    )
    assert np.array_equal(time_idx, expected_time), (
        "Time indices are incorrect. Apply np.nonzero to the boolean mask."
    )

    synthetic = np.array(
        [[0.0, 2.0, 0.0, 9.0],
         [1.0, 8.0, 3.0, 0.0],
         [7.0, 0.0, 6.0, 4.0]]
    )
    for neighborhood_size, amp_thresh in ((1, 5), (3, 5), (3, 7)):
        expected = _expected_peaks(
            synthetic, neighborhood_size, amp_thresh
        )
        actual = peak_finding(
            synthetic,
            neighborhood_size=neighborhood_size,
            amp_thresh=amp_thresh,
        )
        assert len(actual) == 2 and all(isinstance(x, np.ndarray) for x in actual), (
            "peak_finding must return (frequency_indices, time_indices)."
        )
        assert all(np.array_equal(a, e) for a, e in zip(actual, expected)), (
            "peak_finding must use its neighborhood_size and amp_thresh "
            "arguments, and np.nonzero(mask)."
        )

    print("Question 2a Passed!")


def test_Q2b(fingerprint):
    default = fingerprint(FS_AG, COLDPLAY_AG)
    assert isinstance(default, list), "fingerprint must return a list."
    assert all(isinstance(item, tuple) and len(item) == 2 for item in default), (
        "Each fingerprint entry must be a (hash, anchor_time) tuple."
    )

    expected_default_times = [
        3.8506666666666667,
    ] * 5 + [4.746666666666667] * 15
    assert np.allclose(
        [pair[1] for pair in default[100:120]], expected_default_times
    ), (
        "Default fingerprints are incorrect. Use the raw spectrogram and pass "
        "the returned frequency/time arrays to hashing."
    )

    smaller_neighborhood = fingerprint(
        FS_AG, COLDPLAY_AG, neighborhood_size=21
    )
    expected_small_times = [0.864] * 5 + [1.2373333333333334] * 15
    assert np.allclose(
        [pair[1] for pair in smaller_neighborhood[100:120]],
        expected_small_times,
    ), (
        "The neighborhood_size argument was not forwarded to peak_finding."
    )

    lower_threshold = fingerprint(FS_AG, COLDPLAY_AG, amp_thresh=25)
    assert len(lower_threshold) > len(default), (
        "The amp_thresh argument was not forwarded to peak_finding. A lower "
        "threshold should retain more peaks and hashes."
    )

    print("Question 2b Passed!")


def test_Q3a(get_20_second_segment):
    for name, audio in (
        ("Viva La Vida", COLDPLAY_AG),
        ("Mr. Brightside", KILLERS_AG),
    ):
        segment = get_20_second_segment(FS_AG, audio)
        assert isinstance(segment, np.ndarray), (
            "get_20_second_segment must return a NumPy array."
        )
        assert segment.shape[0] == 20 * FS_AG, (
            f"{name}: the returned segment must be exactly 20 seconds long."
        )
        assert segment.shape[1:] == audio.shape[1:], (
            f"{name}: preserve the audio channel dimensions."
        )

    print("Question 3a Passed!")


def test_Q3b(basic_detect_test):
    for expected_name, audio in (
        ("MrBrightside.wav", KILLERS_AG),
        ("VivaLaVida.wav", COLDPLAY_AG),
    ):
        result = basic_detect_test(FS_AG, audio)
        assert isinstance(result, tuple) and len(result) == 2, (
            "basic_detect_test must return detect's (filename, confidence) tuple."
        )
        assert result == (expected_name, 100.0), (
            f"Expected {(expected_name, 100.0)}, but received {result}. "
            "Crop a 20-second segment and pass it to detect."
        )

    print("Question 3b Passed!")


def test_Q3c(add_gaussian_noise, gaussian_noise_detect_test):
    random_state = np.random.get_state()
    try:
        np.random.seed(66)
        for shape in ((20_000,), (20_000, 2)):
            clean = np.zeros(shape, dtype=float)
            noisy = np.asarray(add_gaussian_noise(clean))
            assert noisy.shape == clean.shape, (
                "Noise must preserve the input shape. Use "
                "size=audio_segment.shape in np.random.normal."
            )
            assert np.all(clean == 0), "add_gaussian_noise must not mutate its input."
            assert 9_700 < float(np.mean(noisy)) < 10_300, (
                "Gaussian noise should have mean 10000."
            )
            assert 9_700 < float(np.std(noisy)) < 10_300, (
                "Gaussian noise should have standard deviation 10000."
            )

        for expected_name, audio in (
            ("MrBrightside.wav", KILLERS_AG),
            ("VivaLaVida.wav", COLDPLAY_AG),
        ):
            result = gaussian_noise_detect_test(FS_AG, audio)
            assert isinstance(result, tuple) and len(result) == 2, (
                "Return detect's (filename, confidence) tuple."
            )
            filename, confidence = result
            assert filename == expected_name, (
                f"Expected noisy audio to match {expected_name}, got {filename}. "
                "Add noise to the provided audio, then call detect on the noisy result."
            )
            assert confidence > 50, (
                f"Noisy {expected_name} confidence was only {confidence:.1f}%."
            )
    finally:
        np.random.set_state(random_state)

    print("Question 3c Passed!")

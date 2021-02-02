"""
=================================
02. Simulate alpha and beta waves
=================================

This example demonstrates how to simulate alpha and beta waves using
HNN-core. Alpha activity can be produced with 10 Hz excitatory drive to the
proximal or distal dendrites of pyramidal neurons. Providing proximal and
distal drive simultaneously results in higher frequency beta activity [1]_,
[2]_.
"""

# Authors: Mainak Jas <mainak.jas@telecom-paristech.fr>
#          Sam Neymotin <samnemo@gmail.com>
#          Nick Tolley <nicholas_tolley@brown.edu>
#          Christopher Bailey <bailey.cj@gmail.com>

import os.path as op

###############################################################################
# Let us import hnn_core

import hnn_core
from hnn_core import simulate_dipole, read_params, Network

###############################################################################
# Then we setup the directories and read the default parameters file
hnn_core_root = op.dirname(hnn_core.__file__)
params_fname = op.join(hnn_core_root, 'param', 'default.json')
params = read_params(params_fname)

###############################################################################
# Now let's simulate the dipole and plot it. To excite the network, we add a
# ~10 Hz "bursty" drive starting at 50 ms and continuing to the end of the
# simulation. Each burst consists of a pair (2) of spikes, spaced 10 ms apart.
# The occurrence of each burst is jittered by a random, normally distributed
# amount (20 ms standard deviation). We repeat the burst train 10 times, each
# time with unique randomization. The drive is only connected to the proximal
# (dendritic) AMPA synapses on L2/3 and L5 pyramidal neurons.
params['tstop'] = 310
net = Network(params)

location = 'proximal'
burst_std = 20
weights_ampa_p = {'L2_pyramidal': 5.4e-5, 'L5_pyramidal': 5.4e-5}
syn_delays_p = {'L2_pyramidal': 0.1, 'L5_pyramidal': 1.}

net.add_bursty_drive(
    'alpha_prox', tstart=50., burst_rate=10, burst_std=burst_std, numspikes=2,
    spike_isi=10, repeats=10, location=location, weights_ampa=weights_ampa_p,
    synaptic_delays=syn_delays_p, seedcore=14)

dpl = simulate_dipole(net, postproc=False)

###############################################################################
# Prior to plotting, we can choose to smooth the dipole waveform (note that the
# :meth:`~hnn_core.dipole.smooth`-method operates in-place, *i.e.*, it alters
# the data inside the ``Dipole`` object). Smoothing approximates the effect of
# signal summation from a larger number and greater volume of neurons than are
# included in our biophysical model; extra-cranially measured fields are always
# a mixture of many sources. Note also that the `simulate_dipole`-function was
# called with the option to *not* apply unit conversion scaling, which leaves
# the data in the native units of fAm. We can confirm that what we simulate is
# indeed 10 Hz activity by plotting the power spectral density (PSD).
import matplotlib.pyplot as plt
from hnn_core.viz import plot_dipole, plot_psd
trial_idx = 0  # single trial simulated
scaling = 1e-6  # conversion factor from fAm to nAm
units = 'nAm'

fig, axes = plt.subplots(2, 1)
tmin = 20  # exclude the initial burn-in period from the plots

# We will investigate the effect of two smoothing methods:
window_len = 20  # 1. convolve with a 20 ms-long Hamming window, or
h_freq = 30  # 2. define highest frequency (in Hz) to retain (approximate)

# We'll make a copy of the dipole before smoothing
dpl_win = dpl[trial_idx].copy().smooth(window_len=window_len)  # 1.
dpl_hfreq = dpl[trial_idx].copy().smooth(h_freq=h_freq)  # 2.

# Overlay the three traces for comparison. Note the large edge-artefact when
# applying the convolutional smoothing method (``window_len``).
plot_dipole(dpl[trial_idx], tmin=tmin, ax=axes[0], show=False,
            units=units, scaling=scaling)
plot_dipole(dpl_win, tmin=tmin, ax=axes[0], show=False,
            units=units, scaling=scaling)
plot_dipole(dpl_hfreq, tmin=tmin, ax=axes[0], show=False,
            units=units, scaling=scaling)
axes[0].set_xlim((1, 399))
axes[0].legend(['orig', 'window', 'hfreq'])

plot_psd(dpl[trial_idx], fmin=1., fmax=1e3, tmin=tmin, ax=axes[1], show=False,
         units=units, scaling=scaling)
axes[1].set_xscale('log')
plt.tight_layout()
###############################################################################
# The next step is to add a simultaneous 10 Hz distal drive with a lower
# within-burst spread of spike times (``burst_std``) compared with the
# proximal one. The different arrival times of spikes at opposite ends of
# the pyramidal cells will tend to produce bursts of 15-30 Hz power known
# as beta frequency events.
location = 'distal'
burst_std = 15
weights_ampa_d = {'L2_pyramidal': 5.4e-5, 'L5_pyramidal': 5.4e-5}
syn_delays_d = {'L2_pyramidal': 5., 'L5_pyramidal': 5.}
net.add_bursty_drive(
    'alpha_dist', tstart=50., burst_rate=10, burst_std=burst_std, numspikes=2,
    spike_isi=10, repeats=10, location=location, weights_ampa=weights_ampa_d,
    synaptic_delays=syn_delays_d, seedcore=16)

dpl = simulate_dipole(net, postproc=False)

###############################################################################
# We can verify that beta frequency activity was produced by inspecting the PSD
# of the most recent simulation. The dominant power in the signal is shifted
# from alpha (~10 Hz) to beta (15-25 Hz) frequency range. All plotting and
# smoothing parameters are as above.
fig, axes = plt.subplots(2, 1)

# We'll again make a copy of the dipole before smoothing
smooth_dpl = dpl[trial_idx].copy().smooth(h_freq=h_freq)

# Note that using the ``plot_dipole``-function is equivalent to:
dpl[trial_idx].plot(tmin=tmin, ax=axes[0], show=False,
                    units=units, scaling=scaling)
smooth_dpl.plot(tmin=tmin, ax=axes[0], show=False,
                units=units, scaling=scaling)

plot_psd(dpl[trial_idx], fmin=0., fmax=40., tmin=tmin, ax=axes[1],
         units=units, scaling=scaling)
plt.tight_layout()

###############################################################################
# References
# ----------
# .. [1] Jones, S. R. et al. Quantitative analysis and biophysically realistic
#    neural modeling of the MEG mu rhythm: rhythmogenesis and modulation of
#    sensory-evoked responses. J. Neurophysiol. 102, 3554–3572 (2009).
#
# .. [2] https://jonescompneurolab.github.io/hnn-tutorials/alpha_and_beta/alpha_and_beta  # noqa

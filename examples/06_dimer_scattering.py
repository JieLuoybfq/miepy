"""
Scattering, absroption, and extinction cross-sections of an Au dimer
"""

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import miepy

nm = 1e-9
um = 1e-6
Nwav = 60

Au = miepy.materials.predefined.Au()
radius = 40*nm
source = miepy.sources.x_polarized_plane_wave()
Lmax = 3

wavelengths = np.linspace(300*nm, 800*nm, Nwav)
separation = 83*nm

spheres = miepy.spheres([[separation/2,0,0], [-separation/2,0,0]], radius, Au)
sol = miepy.gmt(spheres, source, wavelengths, Lmax)

scat, absorb, extinct = sol.cross_sections()

plt.figure(figsize=(8,6))
plt.plot(wavelengths/nm, scat/um**2,    label='scattering (dimer)', color='C0')
plt.plot(wavelengths/nm, absorb/um**2,  label='absorption (dimer)', color='C1')
plt.plot(wavelengths/nm, extinct/um**2, label='extinction (dimer)', color='C2')

sphere = miepy.single_mie_sphere(radius, Au, wavelengths, Lmax)
scat, absorb, extinct = sphere.cross_sections()

plt.plot(wavelengths/nm, 2*scat/um**2,    label='scattering (single x 2)', color='C0', linestyle='--')
plt.plot(wavelengths/nm, 2*absorb/um**2,  label='absorption (single x 2)', color='C1', linestyle='--')
plt.plot(wavelengths/nm, 2*extinct/um**2, label='extinction (single x 2)', color='C2', linestyle='--')

plt.xlabel('wavelength (nm)')
plt.ylabel(r'cross-section ($\mu$m$^2$)')
plt.legend()

plt.show()

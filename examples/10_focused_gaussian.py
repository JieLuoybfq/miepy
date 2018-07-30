import numpy as np
import matplotlib.pyplot as plt
import miepy
from tqdm import tqdm
import matplotlib.animation as animation
from my_pytools.my_matplotlib.colors import cmap
from my_pytools.my_matplotlib.animation import save_animation

nm = 1e-9

width = 10*nm
size = 600*nm
wavelength = 600*nm
k = 2*np.pi/wavelength
lmax = 6

source = miepy.sources.gaussian_beam(width, [1, 1j])
p_src = source.structure([0,0,0], k, lmax, size)
Efunc = miepy.expand_E(p_src, k, mode=miepy.vsh_mode.incident)
Hfunc = miepy.expand_H(p_src, k, mode=miepy.vsh_mode.incident, eps=1, mu=1)

Nx = 50
x = np.linspace(-size/2, size/2, Nx)
y = np.linspace(-size/2, size/2, Nx)
X, Y = np.meshgrid(x, y)
R, THETA, PHI = miepy.coordinates.cart_to_sph(X, Y, np.zeros_like(X))
# R, THETA, PHI = miepy.coordinates.cart_to_sph(X, np.zeros_like(X), Y)
E = Efunc(R, THETA, PHI)
E = miepy.coordinates.vec_sph_to_cart(E, THETA, PHI)
I = np.sum(E.real**2, axis=0)
vmax = np.max(np.sum(np.abs(E)**2, axis=0))/2

fig, axes = plt.subplots(ncols=3, figsize=(12,4.4), sharey=True)

ax = axes[0]
ax.pcolormesh(X/nm, Y/nm, np.sum(np.abs(E)**2, axis=0), shading='gouraud', rasterized=True, vmin=0, cmap=cmap['parula'])
ax.set_aspect('equal')
ax.set_title('time averaged energy', weight='bold')

ax = axes[1]
im = ax.pcolormesh(X/nm, Y/nm, I.T, shading='gouraud', rasterized=True, vmax=vmax, vmin=0, cmap=cmap['parula'])
ax.set_aspect('equal')
ax.set_title('instantaneous energy', weight='bold')

def update(phase):
    Enow = (E*(np.exp(1j*phase))).real
    I = np.sum(Enow**2, axis=0)
    im.set_array(np.ravel(I.T))
    return [im]

ani = animation.FuncAnimation(fig, update, np.linspace(0,2*np.pi,120), interval=15, blit=True)

ax = axes[2]
H = Hfunc(R, THETA, PHI)
H = miepy.coordinates.vec_sph_to_cart(H, THETA, PHI)

S = np.real(np.cross(E, np.conj(H), axis=0))
skip = 4
idx = np.s_[::skip,::skip]
arrows = ax.quiver(X[idx]/nm, Y[idx]/nm, S[0][idx], S[1][idx], pivot='mid')
ax.set_aspect('equal')
ax.set_title('time averaged Poynting vector', weight='bold')

for ax in axes:
    ax.set(xlim=[-size/2/nm, size/2/nm], ylim=[-size/2/nm, size/2/nm], xlabel='x (nm)')
axes[0].set(ylabel='y (nm)')
fig.suptitle('Orbital angular momentum in a tightly focused RHC polarized Gaussian beam', fontsize=16)
save_animation(ani, 'out.mp4', dpi=200)


plt.show()

"""
Defines the vsh wave functions and related functions
"""

import numpy as np
from scipy import special
import enum
from math import factorial
from miepy import vsh

def Emn(m, n):
    return 1j**n*np.sqrt((2*n+1)*factorial(n-m)/(n*(n+1)*factorial(n+m)))

class VSH_mode(enum.Enum):
    outgoing = enum.auto()
    ingoing  = enum.auto()
    incident = enum.auto()
    interior = enum.auto()

def get_zn(mode):
    """determine the zn function for a given mode"""
    if mode is VSH_mode.outgoing:
        return vsh.special.spherical_hn
    elif mode is VSH_mode.ingoing:
        return vsh.special.spherical_hn_2
    elif mode in (VSH_mode.incident, VSH_mode.interior):
        return special.spherical_jn
    else:
        raise TypeError(f'{mode} is not a valid type of mode')

def get_zn_far(mode):
    """determine the zn function for a given mode, in the far-field limit"""
    if mode is VSH_mode.outgoing:
        return lambda n, z: np.exp(1j*(z - (n+1)*np.pi/2))/z
    elif mode is VSH_mode.ingoing:
        return lambda n, z: np.exp(-1j*(z - (n+1)*np.pi/2))/z
    elif mode in (VSH_mode.incident, VSH_mode.interior):
        return lambda n, z: np.cos(z - (n+1)*np.pi/2)/z
    else:
        raise TypeError(f'{mode} is not a valid type of mode')

#TODO: this whole interface could probably be nicer...
#TODO: specify spherical flag (either in VSH or the N/M functions themselves)
#TODO: expansion issues at origin (r=0) for incident modes
def VSH(n, m, mode=VSH_mode.outgoing):
    """electric and magnetic vector spherical harmonic function

            n: int           order
            m: int           degree
            mode: VSH_mode   type of VSH (outgoing, incident)

       returns (N(r,θ,ϕ,k) -> [3,...], M(r,θ,ϕ,k) -> [3,...]), the 3 spherical components"""

    pi_f = vsh.special.pi_func(n,m)
    tau_f = vsh.special.tau_func(n,m)
    Pnm = vsh.special.associated_legendre(n,m)

    zn = get_zn(mode)
        
    def N(r, theta, phi, k):
        H = zn(n, k*r)
        Hp = zn(n, k*r, derivative=True)
        Pnm_val = Pnm(np.cos(theta))

        factor = (H + r*k*Hp)*np.exp(1j*m*phi)/(k*r)

        r_comp = n*(n+1)*Pnm_val*H/(k*r)*np.exp(1j*m*phi)
        theta_comp = tau_f(theta)*factor
        phi_comp = 1j*pi_f(theta)*factor

        return np.array([r_comp, theta_comp, phi_comp])

    def M(r, theta, phi, k):
        H = zn(n, k*r)
        factor = H*np.exp(1j*m*phi)

        theta_comp = 1j*pi_f(theta)*factor
        phi_comp = -1*tau_f(theta)*factor
        r_comp = np.zeros_like(theta_comp)

        return np.array([r_comp, theta_comp, phi_comp])

    return N,M

def VSH_far(n, m, mode=VSH_mode.outgoing):
    """electric and magnetic vector spherical harmonic function in the far field

            n: int           order
            m: int           degree
            mode: VSH_mode   type of VSH (outgoing, incident)

       returns (N(r,θ,ϕ,k) -> [2,...], M(r,θ,ϕ,k) -> [2,...]), the 2 theta/phi components"""

    pi_f = vsh.special.pi_func(n,m)
    tau_f = vsh.special.tau_func(n,m)
    zn = get_zn(mode)
    sign = -1 if mode is vsh.VSH_mode.ingoing else 1
        
    def N(r, theta, phi, k):
        factor = sign*zn(n, k*r)*np.exp(1j*m*phi)
        theta_comp = 1j*tau_f(theta)*factor
        phi_comp = -pi_f(theta)*factor

        return np.array([theta_comp, phi_comp])

    def M(r, theta, phi, k):
        factor = zn(n, k*r)*np.exp(1j*m*phi)
        theta_comp = 1j*pi_f(theta)*factor
        phi_comp = -tau_f(theta)*factor

        return np.array([theta_comp, phi_comp])

    return N,M

def vsh_normalization_values(mode, ftype, n, m, r, k):
    """Determine the norm of a given vsh mode
    
    Arguments:
        mode: VSH_mode    type of VSH (outgoing, incident)
        ftype             'electric' or 'magnetic'
        n                 vsh order (1, 2, ...)
        m                 vsh orientation (-n, -n+1, ..., n)
        r                 radius
        k                 wavenumber
    """
    zn = get_zn(mode)

    norm = 1j**n*(2*n+1)*factorial(n-m)/factorial(n+m)
    zn_val = zn(n, k*r)
    angular_term = 4*np.pi*n*(n+1)/np.abs(norm)

    if ftype == 'magnetic':
        radial_term = np.abs(zn_val)**2
        return angular_term*radial_term

    elif ftype == 'electric':
        znp_val = zn(n, k*r, derivative=True)
        radial_term = (np.abs(zn_val + k*r*znp_val)**2 + n*(n+1)*np.abs(zn_val)**2)/(k*r)**2
        return angular_term*radial_term

def vsh_normalization_values_far(n, m):
    """Determine the norm of a given vsh mode in the far-field
    
    Arguments:
        n                 vsh order (1, 2, ...)
        m                 vsh orientation (-n, -n+1, ..., n)
    """

    return 4*np.pi*n*(n+1)*factorial(n+m)/((2*n+1)*factorial(n-m))

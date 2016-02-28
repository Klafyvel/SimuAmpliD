"""
The MIT License (MIT)

Copyright (c) 2016 Hugo LEVY-FALK

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import numpy as np
import matplotlib.pyplot as pl

class SignalNE555:
    def __init__(self, **kwargs):
        """
        The NE555 Signal
        :param kwargs: R1, R2, C, VCC (see the schematic)
        :return:
        """
        self.R1 = kwargs.get('R1',1)
        self.R2 = kwargs.get('R2',1)
        self.C = kwargs.get('C',1)
        self.VCC = kwargs.get('VCC',1)
        self.tau_charge = self.C*(self.R1+self.R2)
        self.tau_discharge = self.C*self.R2
        self.t = 0
        self.charging = True
        self.t_prgm = 0
    def get_value(self, t):
        dt = t-self.t_prgm
        self.t_prgm = t
        self.t += dt
        tau = self.tau_charge if self.charging else self.tau_discharge
        if self.t > tau*np.log(2):
            self.t = 0
            self. charging = not self.charging
        if self.charging:
            return self.VCC*(1-2/3*np.exp(-self.t/tau))
        else:
            return 2/3*self.VCC*np.exp(-self.t/tau)

class SignalMusic:
    def __init__(self, **kwargs):
        """
        The music signal.
        :param kwargs: f (the music frequency), A (music amplitude)
        :return:
        """
        self.omega = kwargs.get('f', 1) * 2 * np.pi
        self.A = kwargs.get('A', 1)
    def get_value(self, t):
        return self.A/2 * np.sin(t*self.omega)+6

class SignalComp:
    def __init__(self, VCC):
        """
        The AO signal.
        :param VCC
        :return:
        """
        self.VCC = VCC
    def get_value(self, a, b):
        if a > b:
            return self.VCC
        else:
            return 0

class SignalIntergrator:
    def __init__(self, VCC):
        """
        The integrator signal.
        :param VCC
        :return:
        """
        self.VCC = VCC
        self.t = 0
        self.t_prgm = 0
        self.last_input = 0
        self.last_value = VCC/2

    def get_value(self, t, input_signal):
        dt = t - self.t_prgm
        self.t_prgm = t
        self.t += dt

        if self.last_input != input_signal:
            self.last_input = input_signal
            self.t = 0

        v = (input_signal-self.VCC/2)*self.t+self.last_value
        v, self.last_value = (v-self.last_value)+self.last_value, v
        return v

pl.close('all')
fig = pl.figure()
ax = fig.add_subplot(111)

# SETTINGS

t_max = 10**(-2) # s

f_music = 1000 # Hz
music_ampl = 4 # V

R1 = 10**3 # Ohms
R2 = 22*10**3 # Ohms
C = 470*10**(-12) # Farrad
VCC = 12 # V



show_ne = False
show_ao = False
show_music = True
show_integr = True

# View

if show_ne or show_ao or show_music or not show_integr:
    pl.ylim(0,VCC*(101/100))
pl.title('Amplificateur de classe D')
ax.set_xlabel('t (s)')
ax.set_ylabel('U (v)')



# Calcs
s_ne = SignalNE555(R1=R1, R2=R2, C=C, VCC=VCC)
s_music = SignalMusic(f=f_music, A=music_ampl)
s_ao = SignalComp(VCC)
s_integr = SignalIntergrator(VCC)


X = np.arange(0,t_max,10**-4/500) #np.linspace(0,10**-4, 500)
Y_NE555 = [s_ne.get_value(t) for t in X]
Y_MUSIC = [s_music.get_value(t) for t in X]
Y_AO = [s_ao.get_value(Y_MUSIC[x], Y_NE555[x]) for x,_ in enumerate(X)]
Y_INTEGR = [s_integr.get_value(t,Y_AO[x]) for x,t in enumerate(X)]

if show_ne:
    pl.plot(X,Y_NE555, label='NE555 (signal de découpage)')
if show_music:
    pl.plot(X,Y_MUSIC, label='Musique')
if show_ao:
    pl.plot(X,Y_AO, label="Sortie de l'AO (PWM)")
if show_integr:
    pl.plot(X,Y_INTEGR, label="Intégrateur (Haut parleur)")
pl.legend(loc='best')
pl.show()
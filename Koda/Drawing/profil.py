#!/usr/bin/env python
# -*- coding: cp1250 -*-

import numpy
import scipy
from scipy import integrate
import math

# =============
# Razred PROFIL
# =============
class Profil():
    """
    """

    # -----------------------------------------------------------------#
    # Nastavitve atributov za objekt Profil.
    # -----------------------------------------------------------------#
    def __init__(self, R, oblika="standard"):
        """
        R -- polmer voščenke (naravno število)
        oblika -- privzeta vrednost za obliko voščenke je "standard"
        """
        self.R = R
        self.oblika = oblika
        # ------------------
        self.D = 2*self.R + 1 # debelina voščenke
        self.nastavi_masko() # nastavimo masko za profil (self.maska)
        self.min = numpy.min(self.maska) # višina najnižje točke profila
        self.nastavi_obmocje() # nastavimo matriko za obmocje (self.obmocje)
    # -----------------------------------------------------------------#
    # Maska profila.
    # -----------------------------------------------------------------#
    def nastavi_masko(self):
        """
        Nastavimo začetne vrednosti, ki jih bo imele maska profila.
        """
        matrika_ind = numpy.indices((self.D, self.D))
        # Shranimo matriko, ki ima v celicah shranjene oddaljenosti od
        # središča matrike.
        r = numpy.sqrt((matrika_ind[0]-self.R)**2 + (matrika_ind[1]-self.R)**2)
        if self.oblika == "standard":
            self.maska = 1 - self.h*(1 - r/(self.R+0.5))
            self.maska = numpy.where(self.profil <= 1, self.profil - 0.2, 1)
    # -----------------------------------------------------------------#
    # Nastavitev nove višine profila.
    # -----------------------------------------------------------------#
    def spremeni_masko(self, maska_n):
        self.maska = maska_n
        self.min = numpy.min(self.maska)
    # -----------------------------------------------------------------#
    # Utežena maska območja.
    # -----------------------------------------------------------------#
    def nastavi_obmocje(self):
        matrika_ind = numpy.indices((self.D+1, self.D+1))
        r = numpy.sqrt((2*matrika_ind[0]-self.D)**2 + (2*matrika_ind[1]-self.D)**2)
        zunaj = numpy.where(r <= self.D, 0, 1)
        self.obmocje = numpy.zeros((self.D, self.D))
        # --------------------------------
        # Pomožna funkcija za izračun deleža celice (i, j), ki leži znotraj
        # kroga s polmerom R+0.5 in središčem v središčni celici.
        def delez(i, j):
            s = sum([out[j][i], out[j][i+1], out[j+1][i+1], out[j+1][i]])
            f = lambda x: - math.sqrt(self.size**2 - x**2)
            if s == 4:
                self.area[j][i] = 1.
            elif s == 0:
                self.area[j][i] = 0.
            else:
                if s == 1:
                    x1 = 2*i - self.size
                    x2 = f(2*j - self.size)
                    int2 = 2*(x2-(2*(i+1)-self.size))
                elif s == 2:
                    if out[j][i+1] == 0:
                        x1 = f(2*(j+1) - self.size)
                        x2 = f(2*j - self.size)
                        int2 = 2*(x2-(2*(i+1)-self.size))
                    else:
                        x1 = 2*i - self.size
                        x2 = 2*(i+1) - self.size
                        int2 = 0
                elif s == 3:
                    x1 = f(2*(j+1) - self.size)
                    x2 = 2*(i+1) - self.size
                    int2 = 0
                int1 = scipy.integrate.dblquad(lambda x,y: 1., x1, x2, f, lambda y: 2*(j+1) - self.size)
                self.area[j][i] = 1 - (abs(int1[0]) + abs(int2))/4.
        for i in range(self.R):
            for j in range(self.R):
                delez(i, j)
        # --------------------------------
        int = scipy.integrate.dblquad(lambda y,x: 1., -1, 0,
                                      lambda x: -math.sqrt(self.size**2 - x**2), lambda x: 2 - self.size)
        self.area[self.R][0] = 1 - 2*int[0]/4.
        self.area[0][self.R] = 1 - 2*int[0]/4.
        for i in range(self.R+1):
            for j in range(self.R+1, self.size):
                self.area[j][i] = self.area[self.size-j-1][i]
        for i in range(self.R+1, self.size):
            for j in range(self.size):
                self.area[j][i] = self.area[j][self.size-i-1]

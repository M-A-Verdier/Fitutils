"""
Linfitxy V0.2.2
Dev: Marc-Antoine Verdier based on the Matlab version made by par Julien
Browaeys and Tristan Beau: https://github.com/tjbtjbtjb/linfitxy
"""
import numpy as np
import numpy.random as rd
import matplotlib.pyplot as plt
import scipy.optimize as opt
import scipy.special as spe
import sys

eps = np.sqrt(sys.float_info.epsilon)


class Fitter(object):

    def __init__(self):
        pass

    def fit(self, data):
        pass


class LinFitXY(Fitter):

    def __init__(self, nb_loop=500, n_sigma=1):
        self.nb_loop = nb_loop
        self.n_sigma = n_sigma

    def fit_affine(cls, data):
        # make fit
        return AffFitRes(cls, data)

    def fit_linear(cls, data):
        # make fit
        return LinFitRes(cls, data)

    def get_nb_loop(self):
        return self.nb_loop

    def get_n_sigma(self):
        return self.n_sigma


class FitRes(object):

    def __init__(self, cls, data):
        self.cls = cls
        self.x = data.get_x()
        self.y = data.get_y()
        self.dx = data.get_dx()
        self.dy = data.get_dy()
        self.name_x = data.get_name_x()
        self.name_y = data.get_name_y()
        self.nb_loop = cls.get_nb_loop()
        self.n_sigma = cls.get_n_sigma()
        self.n = self.x.shape[0]
        self.q_h = 0.5 * spe.erfc(self.n_sigma / np.sqrt(2))
        self.q_l = 1 - self.q_h

    def get_param(self):
        pass

    def plot(self):
        pass

    def hull(self, npoint=100, x_min=None, x_max=None):
        pass

    def _val2str(self, nsig, val):
        if nsig < 1:
            pre = -int(nsig - 2)
            return "{:.{}f}".format(val, pre)
        else:
            pre = 10**int(nsig)
            return "{:.0f}".format(np.round(val / pre) * pre)


class AffFitRes(FitRes):

    def __init__(self, cls, data):
        super().__init__(cls, data)
        self.allpr = self.__fit_err()
        self.param = self.__calc_fit_param()

    def get_param(self):
        return self.param

    def __sigma(self, pt):
        dx = self.dx
        dy = self.dy
        if dx is None and dy is None:
            dx = np.zeros_like(self.n)
            dy = np.zeros_like(self.n) + self.__esp_var(*pt)
        elif dx is None and dy is not None:
            dx = np.zeros_like(self.n)
        elif dx is not None and dy is None:
            dy = np.zeros_like(self.n)
        return dx, dy

    def __calc_fit_param(self):
        p_low = np.quantile(self.allpr, self.q_l, axis=0)
        p_hig = np.quantile(self.allpr, self.q_h, axis=0)
        p = np.median(self.allpr, axis=0)
        s_l = np.abs(p_low - p)
        s_h = np.abs(p_hig - p)
        s = np.mean([s_l, s_h], axis=0)
        return np.array([p[0], p[1], s[0], s[1]])

    def __lineq_err(self, p, x, y, sx, sy):
        return (y - p[0]*x - p[1]) / np.sqrt((p[0]*sx)**2 + sy**2 + eps)

    def __lineq_noerr(self, p, x, y):
        return y - p[0]*x - p[1]

    def __fit_err(self):
        pt = self.__fit_noerr()
        sg = self.__sigma(pt)
        re = np.zeros((self.nb_loop, 2))
        for i in range(self.nb_loop):
            xi = rd.normal(self.x, sg[0])
            yi = rd.normal(self.y, sg[1])
            ag = (xi, yi, sg[0], sg[1])
            ls = opt.least_squares(self.__lineq_err, pt, args=ag)
            pt = ls.x
            re[i] = pt
        return re

    def __fit_noerr(self):
        a0 = np.mean((self.y[1:]-self.y[:-1]) / (self.x[1:]-self.x[:-1]))
        b0 = np.mean(self.y - (a0 * self.x))
        p0 = np.array([a0, b0])
        ag = (self.x, self.y)
        ls = opt.least_squares(self.__lineq_noerr, p0, args=ag)
        return ls.x

    def hull(self, n_hull=100, x_min=None, x_max=None):
        if x_min is None or x_max is None:
            xl = np.min([(self.x[1]-self.x[0])/2, (self.x[-1]-self.x[-2])/2])
            x_min = self.x[0] - xl
            x_max = self.x[-1] + xl
        xplot = np.linspace(x_min, x_max, n_hull)
        xparr = xplot * np.ones((self.allpr.shape[0], xplot.shape[0]))
        mesha = np.meshgrid(np.ones(xplot.shape[0]), self.allpr[:, 0])[1]
        meshb = np.meshgrid(np.ones(xplot.shape[0]), self.allpr[:, 1])[1]
        alldr = xparr * mesha + meshb
        hull_l = np.quantile(alldr, self.q_l, axis=0)
        hull_h = np.quantile(alldr, self.q_h, axis=0)
        return np.array([xplot, hull_l, hull_h])

    def plot(self, marker='o', markercolor='tab:blue', linecolor='tab:orange',
             draw_hull=True, n_hull=100, h_color='tab:orange', h_min=None,
             h_max=None, ax=None, fill_between=True):
        x, y, dx, dy = self.x, self.y, self.dx, self.dy
        ind_sortx = np.argsort(x)
        x = x[ind_sortx]
        y = y[ind_sortx]
        if dx is not None:
            dx = dx[ind_sortx]
        if dy is not None:
            dy = dy[ind_sortx]
        nhull = 100
        xline = np.min([(x[1] - x[0]) / 2, (x[-1] - x[-2]) / 2])
        xplot = np.linspace(x[0] - xline, x[-1] + xline, nhull)
        yplot = xplot * self.param[0] + self.param[1]
        if ax is None:
            plt.figure()
        else:
            plt.sca(ax)
        plt.errorbar(x, y, xerr=dx, yerr=dy, fmt=marker, c=markercolor,
                     ecolor=markercolor)
        plt.plot(xplot, yplot,  color=linecolor)
        if self.param[2] != 0:
            nd0 = np.log10(self.param[2])
            fmt_s0 = self._val2str(nd0, self.param[2])
            fmt_p0 = self._val2str(nd0, self.param[0])
        else:
            nd0 = np.log10(self.param[0])
            fmt_p0 = self._val2str(nd0, self.param[0])
            fmt_s0 = "0"
        if self.param[3] != 0:
            nd1 = np.log10(self.param[3])
            fmt_p1 = self._val2str(nd1, self.param[1])
            fmt_s1 = self._val2str(nd1, self.param[3])
        else:
            nd1 = np.log10(self.param[1])
            fmt_p1 = self._val2str(nd0, self.param[1])
            fmt_s1 = "0"
        plt.title(r'Fit: y = (' + fmt_p0 + r' $\pm$ ' + fmt_s0
                  + r') x + (' + fmt_p1 + r' $\pm$ ' + fmt_s1 + r')')
        if draw_hull and not(dx is None and dy is None):
            hull = self.hull(n_hull, h_min, h_max)
            if fill_between:
                plt.fill_between(hull[0], hull[1], hull[2], color=linecolor,
                                 alpha=0.2)
            else:
                plt.plot(hull[0], hull[1], '--', color=linecolor)
                plt.plot(hull[0], hull[2], '--', color=linecolor)

    def __esp_var(self, a, b):
        return np.sqrt(np.sum((self.y - (a*self.x + b))**2) / (self.n - 2))


class LinFitRes(FitRes):

    def __init__(self, cls, data):
        super().__init__(cls, data)
        self.allpr = self.__fit_err()
        self.param = self.__calc_fit_param()

    def get_param(self):
        return self.param

    def __sigma(self, pt):
        dx = self.dx
        dy = self.dy
        if dx is None and dy is None:
            dx = np.zeros_like(self.n)
            dy = np.zeros_like(self.n) + self.__esp_var(*pt)
        elif dx is None and dy is not None:
            dx = np.zeros_like(self.n)
        elif dx is not None and dy is None:
            dy = np.zeros_like(self.n)
        return dx, dy

    def __calc_fit_param(self):
        p_low = np.quantile(self.allpr, self.q_l, axis=0)
        p_hig = np.quantile(self.allpr, self.q_h, axis=0)
        p = np.median(self.allpr, axis=0)
        s_l = np.abs(p_low - p)
        s_h = np.abs(p_hig - p)
        s = np.mean([s_l, s_h], axis=0)
        return np.array([p[0], s[0]])

    def __lineq_err(self, p, x, y, sx, sy):
        return (y - p[0]*x) / np.sqrt((p[0]*sx)**2 + sy**2 + eps)

    def __lineq_noerr(self, p, x, y):
        return y - p[0]*x

    def __fit_err(self):
        pt = self.__fit_noerr()
        sg = self.__sigma(pt)
        re = np.zeros((self.nb_loop, 2))
        for i in range(self.nb_loop):
            xi = rd.normal(self.x, sg[0])
            yi = rd.normal(self.y, sg[1])
            ag = (xi, yi, sg[0], sg[1])
            ls = opt.least_squares(self.__lineq_err, pt, args=ag)
            pt = ls.x
            re[i] = pt
        return re

    def __fit_noerr(self):
        a0 = np.mean((self.y[1:]-self.y[:-1]) / (self.x[1:]-self.x[:-1]))
        p0 = np.array([a0])
        ag = (self.x, self.y)
        ls = opt.least_squares(self.__lineq_noerr, p0, args=ag)
        return ls.x

    def hull(self, n_hull=100, x_min=None, x_max=None):
        if x_min is None or x_max is None:
            xl = np.min([(self.x[1]-self.x[0])/2, (self.x[-1]-self.x[-2])/2])
            x_min = self.x[0] - xl
            x_max = self.x[-1] + xl
        xplot = np.linspace(x_min, x_max, n_hull)
        xparr = xplot * np.ones((self.allpr.shape[0], xplot.shape[0]))
        mesha = np.meshgrid(np.ones(xplot.shape[0]), self.allpr[:, 0])[1]
        alldr = xparr * mesha
        hull_l = np.quantile(alldr, self.q_l, axis=0)
        hull_h = np.quantile(alldr, self.q_h, axis=0)
        return np.array([xplot, hull_l, hull_h])

    def plot(self, marker='o', markercolor='tab:blue', linecolor='tab:orange',
             draw_hull=True, n_hull=100, h_color='tab:orange', h_min=None,
             h_max=None, ax=None, fill_between=True):
        x, y, dx, dy = self.x, self.y, self.dx, self.dy
        ind_sortx = np.argsort(x)
        x = x[ind_sortx]
        y = y[ind_sortx]
        if dx is not None:
            dx = dx[ind_sortx]
        if dy is not None:
            dy = dy[ind_sortx]
        nhull = 100
        xline = np.min([(x[1] - x[0]) / 2, (x[-1] - x[-2]) / 2])
        xplot = np.linspace(x[0] - xline, x[-1] + xline, nhull)
        yplot = xplot * self.param[0]
        if ax is None:
            plt.figure()
        else:
            plt.sca(ax)
        plt.errorbar(x, y, xerr=dx, yerr=dy, fmt=marker, c=markercolor,
                     ecolor=markercolor)
        plt.plot(xplot, yplot,  color=linecolor)
        if self.param[1] != 0:
            nd0 = np.log10(self.param[1])
            fmt_s0 = self._val2str(nd0, self.param[1])
            fmt_p0 = self._val2str(nd0, self.param[0])
        else:
            nd0 = np.log10(self.param[0])
            fmt_p0 = self._val2str(nd0, self.param[0])
            fmt_s0 = "0"
        plt.title(r'Fit: y = (' + fmt_p0 + r' $\pm$ ' + fmt_s0
                  + r') x')
        if draw_hull and not(dx is None and dy is None):
            hull = self.hull(n_hull, h_min, h_max)
            if fill_between:
                plt.fill_between(hull[0], hull[1], hull[2], color=linecolor,
                                 alpha=0.2)
            else:
                plt.plot(hull[0], hull[1], '--', color=linecolor)
                plt.plot(hull[0], hull[2], '--', color=linecolor)

    def __esp_var(self, a, b):
        return np.sqrt(np.sum((self.y - (a*self.x))**2) / (self.n - 2))


class Data(object):

    def __init__(self, x, y, dx=None, dy=None, name_x=None, name_y=None):
        self.x = np.array(x)
        self.y = np.array(y)
        if len(self.x) != len(self.y):
            raise ValueError
        iter_dx = '__iter__' in dir(dx)
        iter_dy = '__iter__' in dir(dy)
        if iter_dx:
            self.dx = np.array(dx)
        else:
            if dx is None or dx == 0:
                self.dx = None
            else:
                self.dx = dx * np.ones_like(x)
        if iter_dy:
            self.dy = np.array(dy)
        else:
            if dy is None or dy == 0:
                self.dy = None
            else:
                self.dy = dy * np.ones_like(x)
        sorted = (self.x == np.sort(self.x)).all()
        if not sorted:
            aso = np.argsort(self.x)
            self.x = self.x[aso]
            self.y = self.y[aso]
            if iter_dx:
                self.dx = self.dx[aso]
            if iter_dy:
                self.dy = self.dy[aso]
        self.name_x = name_x
        self.name_y = name_y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_dx(self):
        return self.dx

    def get_dy(self):
        return self.dy

    def get_name_x(self):
        return self.name_x

    def get_name_y(self):
        return self.name_y


def linfitxy(x, y, dx=None, dy=None,
             nb_loop=500, n_sigma=1,
             plot=False, draw_hull=True, marker='o',
             markercolor='tab:blue', linecolor='tab:orange',
             n_hull=100, h_color='tab:orange', h_min=None,
             h_max=None, return_hull=False, fill_between=True, ax=None,
             intercept=True):

    data = Data(x, y, dx, dy, None, None)
    fitr = LinFitXY(nb_loop, n_sigma)
    if intercept:
        fres = fitr.fit_affine(data)
    else:
        fres = fitr.fit_linear(data)
    if plot:
        fres.plot(marker=marker, markercolor=markercolor, linecolor=linecolor,
                  draw_hull=draw_hull, n_hull=n_hull, h_color=h_color,
                  h_min=h_min, h_max=h_max, ax=ax, fill_between=fill_between)
    if return_hull:
        return fres.get_param(), fres.hull(n_hull=n_hull, x_min=h_min,
                                           x_max=h_max)
    else:
        return fres.get_param()

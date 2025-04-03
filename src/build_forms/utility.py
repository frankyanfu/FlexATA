import numpy as np

def threepl(
    a,
    b,
    c,
    th,
    D=1.702):
    """Three PL density function

    Parameters
    ----------
    a: float
        IRT a-parameter
    b: float
        IRT b-parameter
    c: float
        IRT c-parameter
    th: float
        Theta

    Returns
    -------
    float: probaiblity

    """
    return c+(1-c)/(np.exp(-D*a*(th-b))+1)


def fisher_info(
    a,
    b,
    c,
    th,
    D=1.702):
    """Fisher information of an item based on the theta

    Parameters
    ----------
    a: float
        IRT a-parameter
    b: float
        IRT b-parameter
    c: float
        IRT c-parameter
    th: float
        Theta
    D: float, optional
        Scaling factor, default is 1.702
    Returns
    -------
    float: Fisher informaiton

    """
    p = threepl(a,b,c,th,D)
    return D**2*a**2*(1-p)/p*(p-c)**2/(1-c)**2

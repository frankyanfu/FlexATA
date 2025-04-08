import numpy as np
import importlib.resources
import pandas as pd


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

def read_in_data(data_name):
    if data_name not in ["pool", "enemy"]:
        raise ValueError("data_name must be 'pool' or 'enemy'")
    if data_name == "pool":
        resource = "sample_items_for_ATA.xlsx"
    elif data_name == "enemy":
        resource = "sample_enemy_pairs_for_ATA.xlsx"
    resource_path = importlib.resources.files("FlexATA.data") / resource
    return pd.read_excel(resource_path, engine='openpyxl')  # Ensure to use openpyxl for .xlsx files
    

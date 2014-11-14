import numpy as np

from hyperspy.misc.elements import elements as elements_db


def weight_to_atomic(elements, weight_percent):
    """Convert weight percent (wt%) to atomic percent (at.%).

    Parameters
    ----------
    elements: list of str
        A list of element abbreviations, e.g. ['Al','Zn']

    weight_percent: array of float
        The weight fractions (composition) of the sample.

    Returns
    -------
    atomic_percent : array of float
        Composition in atomic percent.
    
    Calculate the atomic percent of modern bronze given its weight percent:
    >>> utils.material.weight_to_atomic(("Cu", "Sn"), (88, 12))

    """
    atomic_weights = np.array(
        [elements_db[element]['General_properties']['atomic_weight']
            for element in elements])
    atomic_percent = np.array(map(np.divide, weight_percent, atomic_weights))
    sum_weight = atomic_percent.sum(axis=0)/100.
    for i, el in enumerate(elements):
        atomic_percent[i] /= sum_weight
    return atomic_percent


def atomic_to_weight(elements, atomic_percent):
    """Convert atomic percent to weight percent.

    Parameters
    ----------
    elements: list of str
        A list of element abbreviations, e.g. ['Al','Zn']

    atomic_percent: array of float
        The atomic fractions (composition) of the sample.

    Returns
    -------
    weight_percent : array of float
        composition in weight percent.

    Examples
    --------

    Calculate the weight percent of modern bronze given its atomic percent:
    >>> utils.material.atomic_to_weight(("Cu", "Sn"), (88, 12))

    """

    atomic_weights = np.array(
        [elements_db[element]['General_properties']['atomic_weight']
            for element in elements])
    weight_percent = np.array(map(np.divide, atomic_percent, atomic_weights))
    sum_atomic = weight_percent.sum(axis=0)/100.
    for i, el in enumerate(elements):
        weight_percent[i] /= sum_atomic
    return weight_percent


def density_of_mixture_of_pure_elements(elements, weight_percent):
    """Calculate the density a mixture of elements.

    The density of the elements is retrieved from an internal database. The
    calculation is only valid if there is no interaction between the
    components.

    Parameters
    ----------
    elements: list of str
        A list of element symbols, e.g. ['Al', 'Zn']
    weight_percent: list of float
        A list of weight percent for the different elements. If the total
        is not equal to 100, each weight percent is divided by the sum
        of the list (normalization).

    Returns
    -------
    density: The density in g/cm3.

    Examples
    --------

    Calculate the density of modern bronze given its weight percent:
    >>> utils.material.density_of_mixture_of_pure_elements(("Cu", "Sn"), (88, 12))
    8.6903187973131466

    """
    densities = np.array(
        [elements_db[element]['Physical_properties']['density (g/cm^3)'] for element in elements])
    density = (weight_percent / densities / sum(weight_percent)).sum() ** -1
    return density

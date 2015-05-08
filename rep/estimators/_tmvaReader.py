"""
    TMVA reader runs with additional information
"""

from __future__ import division, print_function, absolute_import
import sys
import array

import pandas
from root_numpy.tmva import evaluate_reader

from . import tmva
from six.moves import cPickle as pickle


__author__ = 'Tatiana Likhomanenko'


def tmva_process(info, data):
    """
    Create TMVA classification factory, train, test and evaluate all methods

    :param rep.estimators.tmva._AdditionalInformationPredict info: additional information
    :param pandas.DataFrame data: test data

    """
    import ROOT

    reader = ROOT.TMVA.Reader()

    for feature in info.features:
        reader.AddVariable(feature, array.array('f', [0.]))

    model_type, sigmoid_function = info.model_type
    reader.BookMVA(info.method_name, info.xml_file)

    signal_efficiency = None
    if model_type == 'classification' and sigmoid_function is not None and 'sig_eff' in sigmoid_function:
        signal_efficiency = float(sigmoid_function.strip().split('=')[1])
        assert 0.0 <= signal_efficiency <= 1., 'signal efficiency must be in [0, 1], not {}'.format(
            signal_efficiency)

    if signal_efficiency is not None:
        predictions = evaluate_reader(reader, info.method_name, data, aux=signal_efficiency)
    else:
        predictions = evaluate_reader(reader, info.method_name, data)
    return predictions


def main():
    # Reading the configuration from stdin
    info = pickle.load(sys.stdin)
    data = pickle.load(sys.stdin)
    assert isinstance(info, tmva._AdditionalInformationPredict)
    assert isinstance(data, pandas.DataFrame)
    predictions = tmva_process(info, data)
    predictions.dump(info.predictions)

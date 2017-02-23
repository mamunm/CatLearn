""" Script to test the fingerprint generation functions. """
from __future__ import print_function

import numpy as np

from ase.ga.data import DataConnection
from atoml.data_setup import get_train, get_unique
from atoml.fingerprint_setup import return_fpv
from atoml.feature_select import (sure_independence_screening,
                                  iterative_screening,
                                  robust_rank_correlation_screening, pca)
from atoml.particle_fingerprint import ParticleFingerprintGenerator
from atoml.standard_fingerprint import StandardFingerprintGenerator

db = DataConnection('gadb.db')

# Get all relaxed candidates from the db file.
all_cand = db.get_all_relaxed_candidates(use_extinct=False)

# Setup the test and training datasets.
testset = get_unique(candidates=all_cand, testsize=5, key='raw_score')
trainset = get_train(candidates=all_cand, trainsize=10,
                     taken_cand=testset['taken'], key='raw_score')

# Delete the stored values of nnmat to give better indication of timing.
for i in testset['candidates']:
    del i.info['data']['nnmat']
for i in trainset['candidates']:
    del i.info['data']['nnmat']

# Initiate the fingerprint generators with relevant input variables.
pfpv = ParticleFingerprintGenerator(atom_numbers=[78, 79], max_bonds=13,
                                    get_nl=False, dx=0.2, cell_size=50.,
                                    nbin=4)
sfpv = StandardFingerprintGenerator(atom_types=[78, 79])

test_fp = return_fpv(testset['candidates'], [pfpv.nearestneighbour_fpv,
                                             sfpv.mass_fpv,
                                             sfpv.composition_fpv])
train_fp = return_fpv(trainset['candidates'], [pfpv.nearestneighbour_fpv,
                                               sfpv.mass_fpv,
                                               sfpv.composition_fpv])

sis = sure_independence_screening(target=trainset['target'],
                                  train_fpv=train_fp, size=4)
sis_test_fp = np.delete(test_fp, sis['rejected'], 1)
sis_train_fp = np.delete(train_fp, sis['rejected'], 1)
assert len(sis_test_fp[0]) == 4 and len(sis_train_fp[0]) == 4

rrcs = robust_rank_correlation_screening(target=trainset['target'],
                                         train_fpv=train_fp, size=4,
                                         corr='kendall')
rrcs_test_fp = np.delete(test_fp, rrcs['rejected'], 1)
rrcs_train_fp = np.delete(train_fp, rrcs['rejected'], 1)
assert len(rrcs_test_fp[0]) == 4 and len(rrcs_train_fp[0]) == 4

rrcs = robust_rank_correlation_screening(target=trainset['target'],
                                         train_fpv=train_fp, size=4,
                                         corr='spearman')
rrcs_test_fp = np.delete(test_fp, rrcs['rejected'], 1)
rrcs_train_fp = np.delete(train_fp, rrcs['rejected'], 1)
assert len(rrcs_test_fp[0]) == 4 and len(rrcs_train_fp[0]) == 4

it_sis = iterative_screening(target=trainset['target'], train_fpv=train_fp,
                             size=4, step=1, method='sis')
it_sis_test_fp = np.delete(test_fp, it_sis['rejected'], 1)
it_sis_train_fp = np.delete(train_fp, it_sis['rejected'], 1)
assert len(it_sis_test_fp[0]) == 4 and len(it_sis_train_fp[0]) == 4

it_rrcs = iterative_screening(target=trainset['target'], train_fpv=train_fp,
                              size=4, step=1, method='rrcs', corr='kendall')
it_rrcs_test_fp = np.delete(test_fp, it_rrcs['rejected'], 1)
it_rrcs_train_fp = np.delete(train_fp, it_rrcs['rejected'], 1)
assert len(it_rrcs_test_fp[0]) == 4 and len(it_rrcs_train_fp[0]) == 4

it_rrcs = iterative_screening(target=trainset['target'], train_fpv=train_fp,
                              size=4, step=1, method='rrcs', corr='spearman')
it_rrcs_test_fp = np.delete(test_fp, it_rrcs['rejected'], 1)
it_rrcs_train_fp = np.delete(train_fp, it_rrcs['rejected'], 1)
assert len(it_rrcs_test_fp[0]) == 4 and len(it_rrcs_train_fp[0]) == 4

pca_r = pca(components=4, train_fpv=train_fp, test_fpv=test_fp)
assert len(pca_r['test_fpv'][0]) == 4 and len(pca_r['train_fpv'][0]) == 4
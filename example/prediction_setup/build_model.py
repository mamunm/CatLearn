""" Script to test the ML model. Takes a database of candidates from a GA
    search with target values set in atoms.info['key_value_pairs'][key] and
    returns the errors for a random test and training dataset.
"""
from __future__ import print_function

import os

from ase.ga.data import DataConnection
from atoml.data_setup import get_unique, get_train
from atoml.fingerprint_setup import return_fpv
from atoml.standard_fingerprint import StandardFingerprintGenerator
from atoml.particle_fingerprint import ParticleFingerprintGenerator
from atoml.model_build import ModelBuilder
from atoml.database_functions import DescriptorDatabase

# Decide whether to remove output and print graph.
cleanup = True
build_db = True
test_model = False

mb = ModelBuilder(expand=True, optimize=True, size=None)

if build_db:
    # Connect database generated by a GA search.
    db = DataConnection('../../data/gadb.db')

    # Get all relaxed candidates from the db file.
    print('Getting candidates from the database')
    all_cand = db.get_all_relaxed_candidates(use_extinct=False)

    # Setup the test and training datasets.
    testset = get_unique(candidates=all_cand, testsize=50, key='raw_score')
    trainset = get_train(candidates=all_cand, trainsize=50,
                         taken_cand=testset['taken'], key='raw_score')

    # Get the list of fingerprint vectors and normalize them.
    print('Getting the fingerprint vectors')
    sfpv = StandardFingerprintGenerator()
    pfpv = ParticleFingerprintGenerator(get_nl=False, max_bonds=13)

    # Start the model building routines.
    def fpvf(atoms):
        return return_fpv(atoms, [pfpv.nearestneighbour_fpv,
                                  sfpv.mass_fpv,
                                  sfpv.composition_fpv])

    mb.from_atoms(build=True, train_atoms=trainset['candidates'],
                  train_target=trainset['target'],
                  fpv_function=fpvf, test_atoms=testset['candidates'],
                  test_target=testset['target'], feature_names=None)

if test_model:
    dd_train = DescriptorDatabase(db_name='train_fpv_store.sqlite',
                                  table='OriginalFeatureSpace')
    dd_test = DescriptorDatabase(db_name='test_fpv_store.sqlite',
                                 table='OriginalFeatureSpace')

    feature_names = dd_train.get_column_names()[1:-1]

    train_matrix = dd_train.query_db(names=feature_names)
    train_target = dd_train.query_db(names=['target']).flatten()
    train_id = dd_train.query_db(names=['uuid']).flatten()

    test_matrix = dd_test.query_db(names=feature_names)
    test_target = dd_test.query_db(names=['target']).flatten()
    test_id = dd_test.query_db(names=['uuid']).flatten()

    mb.build_model(train_matrix=train_matrix, feature_names=feature_names,
                   train_id=train_id, train_target=train_target,
                   test_matrix=test_matrix, test_id=test_id,
                   test_target=test_target)

if cleanup:
    os.remove('train_fpv_store.sqlite')
    os.remove('test_fpv_store.sqlite')

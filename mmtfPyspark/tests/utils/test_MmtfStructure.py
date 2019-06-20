#!/usr/bin/env python
'''

Authorship information:
__author__ = "Peter Rose"
__maintainer__ = "Peter Rose"
__status__ = "Warning"
'''

import unittest
import numpy as np
from pyspark.sql import SparkSession
from mmtfPyspark.io import mmtfReader


class TestMmtfStructure(unittest.TestCase):

    def setUp(self):
        self.spark = SparkSession.builder.master("local[*]") \
                                 .appName("TestMmtfStructure") \
                                 .getOrCreate()

    def test_4HHB_structure(self):
        print('test_4HHB_structure')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '4HHB')
        structure = pdb.values().first()
        self.assertEqual('1.0.0', structure.mmtf_version)
        self.assertEqual('UNKNOWN', structure.mmtf_producer)
        self.assertEqual(np.testing.assert_allclose([63.150, 83.590, 53.800, 90.00, 99.34, 90.00],
                                                    structure.unit_cell, atol=0.001), None)
        self.assertEqual(structure.space_group, 'P 1 21 1')
        self.assertEqual(4779, structure.num_atoms)
        self.assertEqual(801, structure.num_groups)
        self.assertEqual(14, structure.num_chains)
        self.assertEqual(1, structure.num_models)
        self.assertEqual(np.testing.assert_allclose([6.204, 6.913, 8.504],
                                                    structure.x_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([16.869, 17.759, 17.378],
                                                    structure.y_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([4.854, 4.607, 4.797],
                                                    structure.z_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([49.05, 43.14, 24.80],
                                                    structure.b_factor_list[0:3], atol=0.01), None)
        self.assertEqual(np.testing.assert_allclose([1.0, 1.0, 1.0],
                                                    structure.occupancy_list[0:3], atol=0.01), None)
        self.assertListEqual([1, 2, 3], structure.atom_id_list[0:3].tolist())
        self.assertListEqual(['', '', ''], structure.alt_loc_list[0:3].tolist())
        self.assertListEqual(['A', 'A', 'A'], structure.chain_names[0:3].tolist())
        self.assertListEqual(['A', 'A', 'A'], structure.chain_ids[0:3].tolist())
        self.assertListEqual(['1', '1', '1'], structure.group_numbers[0:3].tolist())
        self.assertListEqual(['VAL', 'VAL', 'VAL'], structure.group_names[0:3].tolist())
        self.assertListEqual(['N', 'CA', 'C'], structure.atom_names[0:3].tolist())
        self.assertListEqual(['N', 'C', 'C'], structure.elements[0:3].tolist())
        self.assertListEqual(['L-PEPTIDE LINKING', 'L-PEPTIDE LINKING'], structure.chem_comp_types[0:2].tolist())
        self.assertListEqual([True, True, True], structure.polymer[0:3].tolist())
        self.assertListEqual([0, 0, 0], structure.entity_indices[0:3].tolist())
        self.assertListEqual([0, 0, 0], structure.sequence_positions[0:3].tolist())

    def test_4HHB_chain(self):
        print('test_4HHB_chain')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '4HHB')
        structure = pdb.values().first()
        chain = structure.get_chain('A')
        self.assertEqual(1069, chain.num_atoms)
        self.assertEqual(141, chain.num_groups)
        self.assertEqual(1, chain.num_chains)
        self.assertEqual(1, chain.num_models)
        self.assertEqual(np.testing.assert_allclose([6.204, 6.913, 8.504],
                                                    chain.x_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([16.869, 17.759, 17.378],
                                                    chain.y_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([4.854, 4.607, 4.797],
                                                    chain.z_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([49.05, 43.14, 24.80],
                                                    chain.b_factor_list[0:3], atol=0.01), None)
        self.assertEqual(np.testing.assert_allclose([1.0, 1.0, 1.0],
                                                    chain.occupancy_list[0:3], atol=0.01), None)
        self.assertListEqual([1, 2, 3], chain.atom_id_list[0:3].tolist())
        self.assertListEqual(['', '', ''], chain.alt_loc_list[0:3].tolist())
        self.assertListEqual(['A', 'A', 'A'], chain.chain_names[0:3].tolist())
        self.assertListEqual(['A', 'A', 'A'], chain.chain_ids[0:3].tolist())
        self.assertListEqual(['1', '1', '1'], chain.group_numbers[0:3].tolist())
        self.assertListEqual(['VAL', 'VAL', 'VAL'], chain.group_names[0:3].tolist())
        self.assertListEqual(['N', 'CA', 'C'], chain.atom_names[0:3].tolist())
        self.assertListEqual(['N', 'C', 'C'], chain.elements[0:3].tolist())
        self.assertListEqual(['L-PEPTIDE LINKING', 'L-PEPTIDE LINKING'], chain.chem_comp_types[0:2].tolist())
        self.assertListEqual([True, True, True], chain.polymer[0:3].tolist())
        self.assertListEqual([0, 0, 0], chain.entity_indices[0:3].tolist())
        self.assertListEqual([0, 0, 0], chain.sequence_positions[0:3].tolist())

        chain = structure.get_chain('B')
        self.assertEqual(1123, chain.num_atoms)
        self.assertEqual(146, chain.num_groups)
        self.assertEqual(1, chain.num_chains)
        self.assertEqual(1, chain.num_models)
        self.assertEqual(np.testing.assert_allclose([9.223, 8.694, 9.668],
                                                    chain.x_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([-20.614, -20.026, -21.068],
                                                    chain.y_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([1.365, -0.123, -1.645],
                                                    chain.z_coord_list[0:3], atol=0.001), None)
        self.assertEqual(np.testing.assert_allclose([46.08, 70.96, 69.74],
                                                    chain.b_factor_list[0:3], atol=0.01), None)
        self.assertEqual(np.testing.assert_allclose([1.0, 1.0, 1.0],
                                                    chain.occupancy_list[0:3], atol=0.01), None)
        self.assertListEqual([1070, 1071, 1072], chain.atom_id_list[0:3].tolist())
        self.assertListEqual(['', '', ''], chain.alt_loc_list[0:3].tolist())
        self.assertListEqual(['B', 'B', 'B'], chain.chain_names[0:3].tolist())
        self.assertListEqual(['B', 'B', 'B'], chain.chain_ids[0:3].tolist())
        self.assertListEqual(['1', '1', '1'], chain.group_numbers[0:3].tolist())
        self.assertListEqual(['VAL', 'VAL', 'VAL'], chain.group_names[0:3].tolist())
        self.assertListEqual(['N', 'CA', 'C'], chain.atom_names[0:3].tolist())
        self.assertListEqual(['N', 'C', 'C'], chain.elements[0:3].tolist())
        self.assertListEqual(['L-PEPTIDE LINKING', 'L-PEPTIDE LINKING'], chain.chem_comp_types[0:2].tolist())
        self.assertListEqual([True, True, True], chain.polymer[0:3].tolist())
        self.assertListEqual([1, 1, 1], chain.entity_indices[0:3].tolist())
        self.assertListEqual([0, 0, 0], chain.sequence_positions[0:3].tolist())

    def test_4HHB_chains(self):
        print('test_4HHB_chains')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '4HHB')
        structure = pdb.values().first()
        chains = structure.get_chains()
        self.assertEqual(4, len(chains))

    def test_4HHB_multiple_chains(self):
        print('test_4HHB_chains')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '4HHB')
        structure = pdb.values().first()
        chain_list = ['A']
        chains = structure.get_multiple_chains(chain_list)
        self.assertEqual(1, len(chains))

    def test_1J6T_structure(self):
        print('test_1J6T_structure')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '1J6T')
        structure = pdb.values().first()
        self.assertEqual(3555+3559+3559, structure.num_atoms)
        self.assertEqual(144+85+144+1+85+144+85+1, structure.num_groups)
        self.assertEqual(2+3+3, structure.num_chains)
        self.assertEqual(3, structure.num_models)

    def test_1J6T_model(self):
        print('test_1J6T_model')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '1J6T')
        structure = pdb.values().first()
        model = structure.get_model(0)
        self.assertEqual(3555, model.num_atoms)
        self.assertEqual(144+85, model.num_groups)
        self.assertEqual(2, model.num_chains)
        self.assertEqual(1, model.num_models)
        model = structure.get_model(1)
        self.assertEqual(3559, model.num_atoms)
        self.assertEqual(144+85+1, model.num_groups)
        self.assertEqual(3, model.num_chains)
        self.assertEqual(1, model.num_models)
        model = structure.get_model(2)
        self.assertEqual(3559, model.num_atoms)
        self.assertEqual(144+85+1, model.num_groups)
        self.assertEqual(3, model.num_chains)
        self.assertEqual(1, model.num_models)

    def test_1J6T_model_chains(self):
        print('test_1J6T_model_chains')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '1J6T')
        structure = pdb.values().first()
        model = structure.get_model(0)
        self.assertEqual(3555, model.num_atoms)
        self.assertEqual(144+85, model.num_groups)
        self.assertEqual(2, model.num_chains)
        self.assertEqual(1, model.num_models)
        chain = model.get_chain('A')
        self.assertEqual(2266, chain.num_atoms)
        self.assertEqual(144, chain.num_groups)
        self.assertEqual(1, chain.num_chains)
        self.assertEqual(1, chain.num_models)

        model = structure.get_model(1)
        self.assertEqual(3559, model.num_atoms)
        self.assertEqual(144+85+1, model.num_groups)
        self.assertEqual(3, model.num_chains)
        self.assertEqual(1, model.num_models)
        chain = model.get_chain('A')
        self.assertEqual(2266, chain.num_atoms)
        self.assertEqual(144, chain.num_groups)
        self.assertEqual(1, chain.num_chains)
        self.assertEqual(1, chain.num_models)
        chain = model.get_chain('B')
        self.assertEqual(1289, chain.num_atoms)
        self.assertEqual(85, chain.num_groups)
        self.assertEqual(1, chain.num_chains)
        self.assertEqual(1, chain.num_models)

        model = structure.get_model(2)
        self.assertEqual(3559, model.num_atoms)
        self.assertEqual(144 + 85 + 1, model.num_groups)
        self.assertEqual(3, model.num_chains)
        self.assertEqual(1, model.num_models)
        chain = model.get_chain('A')
        self.assertEqual(2266, chain.num_atoms)
        self.assertEqual(144, chain.num_groups)
        self.assertEqual(1, chain.num_chains)
        self.assertEqual(1, chain.num_models)
        chain = model.get_chain('B')
        self.assertEqual(1289, chain.num_atoms)
        self.assertEqual(85, chain.num_groups)
        self.assertEqual(1, chain.num_chains)
        self.assertEqual(1, chain.num_models)

    def test_1J6T_models(self):
        print('test_1J6T_modelS')
        path = '../../../resources/files/'
        pdb = mmtfReader.read_mmtf_files(path)
        pdb = pdb.filter(lambda t: t[0] == '1J6T')
        structure = pdb.values().first()
        models = structure.get_models()
        self.assertEqual(3, len(models))

    def tearDown(self):
        self.spark.stop()


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
'''mmtfChain.py

Decode msgpack unpacked data to mmtf chain

'''
__author__ = "Peter Rose"
__maintainer__ = "Peter Rose"
__version__ = "0.4.0"
__status__ = "Experimental"

import numpy as np
import pandas as pd


class MmtfChains(object):

    def __init__(self, structure, chain_names):
        """Extracts the specified polymer chain from a structure"""
        self.structure = structure
        self.start = None
        self.end = None
        self.num_atoms = 0
        self.num_groups = 0
        self.num_chains = 1
        self.num_models = 1

        self.mask = np.in1d(structure.chain_names, list(chain_names)).reshape(structure.chain_names.shape)
        # indices = np.where(structure.chain_name_list == chain_name)
        # if indices[0].size == 0:
        #     raise ValueError("Structure " + structure.structure_id + " does not contain chain: " + chain_name)
        #
        # # find start and end of the first polymer chain
        # for i in indices[0]:
        #     ind = structure.entityChainIndex[i]
        #     if structure.entity_list[ind]['type'] == 'polymer':
        #         self.start = structure.chainToAtomIndices[i]
        #         self.end = structure.chainToAtomIndices[i+1]
        #         self.num_atoms = self.end - self.start
        #         self.num_groups = structure.chainToGroupIndices[i+1] - structure.chainToGroupIndices[i]
        #        break

        self.mmtf_version = structure.mmtf_version
        self.mmtf_producer = structure.mmtf_producer
        self.unit_cell = structure.unit_cell
        self.space_group = structure.space_group
        self.structure_id = structure.structure_id + "." + chain_names
        self.title = structure.title
        self.deposition_date = structure.deposition_date
        self.release_date = structure.release_date
        self.ncs_operator_list = structure.ncs_operator_list
        # TODO
        self.bio_assembly = None
        self.entity_list = structure.entity_list

        self.experimental_methods = structure.experimental_methods
        self.resolution = structure.resolution
        self.r_free = structure.r_free
        self.r_work = structure.r_work
        # dataframes
        self.df = None

    @property
    def atom_id_list(self):
        """Return atom id list"""
        return self.structure.atom_id_list[self.mask]

    @property
    def x_coord_list(self):
        """Return x coordinates"""
        return self.structure.x_coord_list[self.mask]

    @property
    def y_coord_list(self):
        """Return y coordinates"""
        return self.structure.y_coord_list[self.mask]

    @property
    def z_coord_list(self):
        """Return z coordinates"""
        return self.structure.z_coord_list[self.mask]

    @property
    def coords(self):
        """Return 3xn coordinate array"""
        return np.column_stack((self.x_coord_list, self.y_coord_list, self.z_coord_list))

    @property
    def b_factor_list(self):
        """Return b factors"""
        if self.structure.b_factor_list is None:
            return None
        return self.structure.b_factor_list[self.mask]

    @property
    def occupancy_list(self):
        """Return occupancies"""
        if self.structure.occupancy_list is None:
            return None
        return self.structure.occupancy_list[self.mask]

    @property
    def alt_loc_list(self):
        """Return alternative location codes"""
        if self.structure.alt_loc_list is None:
            return None
        return self.structure.alt_loc_list[self.mask]

    # calculated properties
    @property
    def chain_names(self):
        """Return chain names"""
        return self.structure.chain_names[self.mask]

    @property
    def chain_ids(self):
        """Return chain ids"""
        return self.structure.chain_ids[self.mask]

    @property
    def group_numbers(self):
        """Return group numbers"""
        return self.structure.group_numbers[self.mask]

    @property
    def group_names(self):
        """Return group names"""
        return self.structure.group_names[self.mask]

    @property
    def atom_names(self):
        """Return group names"""
        return self.structure.atom_names[self.mask]

    @property
    def elements(self):
        """Return group names"""
        return self.structure.elements[self.mask]

    @property
    def chem_comp_types(self):
        """Return group names"""
        return self.structure.chem_comp_types[self.mask]

    @property
    def polymer(self):
        """Return polymer"""
        return self.structure.polymer[self.mask]

    @property
    def entity_indices(self):
        """Return entity indices"""
        return self.structure.entity_indices[self.mask]

    @property
    def sequence_positions(self):
        """Return sequence_positions"""
        return self.structure.sequence_positions[self.mask]

    def to_pandas(self, multi_index=False):
        if self.df is None:
            self.df = pd.DataFrame({'chain_name': self.chain_names,
                                    'chain_id': self.chain_ids,
                                    'group_number': self.group_numbers,
                                    'group_name': self.group_names,
                                    'atom_name': self.atom_names,
                                    'altloc': self.alt_loc_list,
                                    'x': self.x_coord_list,
                                    'y': self.y_coord_list,
                                    'z': self.z_coord_list,
                                    'o': self.occupancy_list,
                                    'b': self.b_factor_list,
                                    'element': self.elements,
                                    'polymer': self.polymer,
                                    #                               'entity': self.get_entity_indices(),
                                    #                                   'seq_index': self.get_sequence_positions()
                                    })
            if multi_index:
                self.df.set_index(['chain_name', 'chain_id', 'group_number', 'group_name', 'atom_name', 'altloc'], inplace=True)

        return self.df










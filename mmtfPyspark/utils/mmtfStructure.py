#!/usr/bin/env python
'''mmtfStructure.py

Decode msgpack unpacked data to mmtf structure

'''
__author__ = "Mars (Shih-Cheng) Huang"
__maintainer__ = "Mars (Shih-Cheng) Huang"
__email__ = "marshuang80@gmail.com"
__version__ = "0.2.0"
__status__ = "Done"

import numpy as np
import pandas as pd
import re
from mmtfPyspark.utils import mmtfDecoder, MmtfChain, MmtfModel, Codec, AbstractStructure


#class MmtfStructure(AbstractStructure):
class MmtfStructure:

    def __init__(self, input_data, first_model=False):
        """Decodes a msgpack unpacked data to mmtf structure"""
        self.input_data = input_data

        self.mmtf_version = mmtfDecoder.get_value(input_data, 'mmtfVersion', required=True)
        self.mmtf_producer = mmtfDecoder.get_value(input_data, 'mmtfProducer', required=True)
        self.unit_cell = mmtfDecoder.get_value(input_data, 'unitCell')
        self.space_group = mmtfDecoder.get_value(input_data, 'spaceGroup')
        self.structure_id = mmtfDecoder.get_value(input_data, 'structureId')
        self.title = mmtfDecoder.get_value(input_data, 'title')
        self.deposition_date = mmtfDecoder.get_value(input_data, 'depositionDate')
        self.release_date = mmtfDecoder.get_value(input_data, 'releaseDate')
        self.ncs_operator_list = mmtfDecoder.get_value(input_data, 'ncsOperatorList')
        self.bio_assembly = mmtfDecoder.get_value(input_data, 'bioAssemblyList')  # TODO naming inconsistency
        self.entity_list = mmtfDecoder.get_value(input_data, 'entityList')
        self.experimental_methods = mmtfDecoder.get_value(input_data, 'experimentalMethods')
        self.resolution = mmtfDecoder.get_value(input_data, 'resolution')
        self.r_free = mmtfDecoder.get_value(input_data, 'rFree')
        self.r_work = mmtfDecoder.get_value(input_data, 'rWork')
        self.num_bonds = mmtfDecoder.get_value(input_data, 'numBonds', required=True)
        self.num_atoms = mmtfDecoder.get_value(input_data, 'numAtoms', required=True)
        self.num_groups = mmtfDecoder.get_value(input_data, 'numGroups', required=True)
        self.num_chains = mmtfDecoder.get_value(input_data, 'numChains', required=True)
        self._num_models = mmtfDecoder.get_value(input_data, 'numModels', required=True)
        self.group_list = mmtfDecoder.get_value(input_data, 'groupList', required=True)
        self._bond_atom_list = None
        self._bond_order_list = None
        self._bondResonanceList = None  # TODO
        self._x_coord_list = None
        self._y_coord_list = None
        self._z_coord_list = None
        self._b_factor_list = None
        self._atom_id_list = None
        self._alt_loc_list = None
        self._occupancy_list = None
        self._sec_struct_list = None
        self._group_id_list = None
        self._group_type_list = None
        self._ins_code_list = None
        self._sequence_index_list = None
        self._chain_id_list = None
        self._chain_name_list = None
        self.groups_per_chain = mmtfDecoder.get_value(input_data, 'groupsPerChain', required=True)
        self.chains_per_model = mmtfDecoder.get_value(input_data, 'chainsPerModel', required=True)
        # calculated atom level data
        self._chain_names = None
        self._chain_ids = None
        self._group_ids = None
        self._group_numbers = None
        self._group_names = None
        self._atom_names = None
        self._elements = None
        self._chem_comp_types = None
        self._codes = None
        self._polymer = None
        self._entity_type = None
        self._entity_indices = None
        self._sequence_positions = None
        # calculated indices
        self.groupToAtomIndices = None
        self.chainToAtomIndices = None
        self.chainToGroupIndices = None
        self.modelToAtomIndices = None
        self.modelToGroupIndices = None
        self.modelToChainIndices = None
        self._group_serial = None
        self._chain_serial = None
        self._chain_entity_index = None
        self.chainIdToEntityIndices = None
        # precalculate indices
        # TODO
        self.truncated = False
        if first_model and self._num_models != 1:
            self.num_models = 1
            self.truncated = True
        else:
            self.num_models = self._num_models

        self.decoder = Codec()
        self.calc_indices()
        self.entityChainIndex = None
        self.chain_to_entity_index()

        # dataframes
        self.df = None

        self.atom_cols = {'chain_name': 'chain_names',
                          'chain_id': 'chain_ids',
                          'group_number': 'group_numbers',
                          'group_name': 'group_names',
                          'atom_name': 'atom_names',
                          'altloc': 'alt_loc_list',
                          'x': 'x_coord_list',
                          'y': 'y_coord_list',
                          'z': 'z_coord_list',
                          'o': 'occupancy_list',
                          'b': 'b_factor_list',
                          'element': 'elements',
                          'polymer': 'polymer',
                          'atom_id': 'atom_id_list',
                          'group_id:': 'group_ids',
                          'chem_comp_type': 'chem_comp_type',
                          'code': 'codes',
                          'group_serial': 'group_serials',
                          'entity_type': 'entity_type',
                          'entity_index': 'entity_indices',
                          'sequence_position': 'sequence_positions'}

    def atom_column_names(self):
        """ Return names of atom columns for pandas """
        return [*self.atom_cols]

    def atom_column_names_from_string(self, string):
        """ Returns atom column names in string"""
        cols = set()
        for col_name in self.atom_column_names():
            for item in re.split('[^a-zA-Z_]', string):
                if col_name == item:
                    cols.add(col_name)
        return cols

    @property
    def bond_atom_list(self):
        if self._bond_atom_list is not None:
            return self._bond_atom_list
        elif 'bondAtomList' in self.input_data:
            self._bond_atom_list = self.decoder.decode_array(self.input_data['bondAtomList'])
            # TODO
            # if self.truncated: # truncate bond list ...
            return self._bond_atom_list
        else:
            return None

    @property
    def bond_order_list(self):
        if self._bond_order_list is not None:
            return self._bond_order_list
        elif 'bondOrderList' in self.input_data:
            self._bond_order_list = self.decoder.decode_array(self.input_data['bondOrderList'])
            # TODO
            # if self.truncated: # truncate bond list ...
            return self._bond_order_list
        else:
            return None

    @property
    def occupancy_list(self):
        if self._occupancy_list is not None:
            return self._occupancy_list
        elif 'occupancyList' in self.input_data:
            self._occupancy_list = self.decoder.decode_array(self.input_data['occupancyList'])
            if self.truncated:
                self._occupancy_list = self._occupancy_list[:self.num_atoms]

            return self._occupancy_list
        else:
            return None
    @property
    def x_coord_list(self):
        if self._x_coord_list is not None:
            return self._x_coord_list
        elif 'xCoordList' in self.input_data:
            self._x_coord_list = self.decoder.decode_array(self.input_data['xCoordList'])
            if self.truncated:
                self._x_coord_list = self._x_coord_list[:self.num_atoms]

            return self._x_coord_list
        else:
            return None

    @property
    def y_coord_list(self):
        if self._y_coord_list is not None:
            return self._y_coord_list
        elif 'yCoordList' in self.input_data:
            self._y_coord_list = self.decoder.decode_array(self.input_data['yCoordList'])
            if self.truncated:
                self._y_coord_list = self._y_coord_list[:self.num_atoms]

            return self._y_coord_list
        else:
            return None

    @property
    def z_coord_list(self):
        if self._z_coord_list is not None:
            return self._z_coord_list
        elif 'zCoordList' in self.input_data:
            self._z_coord_list = self.decoder.decode_array(self.input_data['zCoordList'])
            if self.truncated:
                self._z_coord_list = self._z_coord_list[:self.num_atoms]

            return self._z_coord_list
        else:
            return None

    @property
    def b_factor_list(self):
        if self._b_factor_list is not None:
            return self._b_factor_list
        elif 'bFactorList' in self.input_data:
            self._b_factor_list = self.decoder.decode_array(self.input_data['bFactorList'])
            if self.truncated:
                self._b_factor_list = self._b_factor_list[:self.num_atoms]

            return self._b_factor_list
        else:
            return None

    @property
    def atom_id_list(self):
        if self._atom_id_list is not None:
            return self._atom_id_list
        elif 'atomIdList' in self.input_data:
            self._atom_id_list = self.decoder.decode_array(self.input_data['atomIdList'])
            if self.truncated:
                self._atom_id_list = self._atom_id_list[:self.num_atoms]

            return self._atom_id_list
        else:
            return None

    @property
    def alt_loc_list(self):
        if self._alt_loc_list is not None:
            return self._alt_loc_list
        elif 'altLocList' in self.input_data:
            self._alt_loc_list = self.decoder.decode_array(self.input_data['altLocList'])
            if self.truncated:
                self._alt_loc_list = self._alt_loc_list[:self.num_atoms]

            return self._alt_loc_list
        else:
            return None

    @property
    def group_id_list(self):
        if self._group_id_list is not None:
            return self._group_id_list
        elif 'groupIdList' in self.input_data:
            self._group_id_list = self.decoder.decode_array(self.input_data['groupIdList'])
            if self.truncated:
                self._group_id_list = self._group_id_list[:self.num_groups]

            return self._group_id_list
        else:
            return None

    @property
    def group_type_list(self):
        if self._group_type_list is not None:
            return self._group_type_list
        elif 'groupTypeList' in self.input_data:
            self._group_type_list = self.decoder.decode_array(self.input_data['groupTypeList'])
            if self.truncated:
                self._group_type_list = self._group_type_list[:self.num_groups]

            return self._group_type_list
        else:
            return None

    @property
    def sec_struct_list(self):
        if self._sec_struct_list is not None:
            return self._sec_struct_list
        elif 'secStructList' in self.input_data:
            self._sec_struct_list = self.decoder.decode_array(self.input_data['secStructList'])
            if self.truncated:
                self._sec_struct_list = self._sec_struct_list[:self.num_groups]

            return self._sec_struct_list
        else:
            return None

    @property
    def ins_code_list(self):
        if self._ins_code_list is not None:
            return self._ins_code_list
        elif 'insCodeList' in self.input_data:
            self._ins_code_list = self.decoder.decode_array(self.input_data['insCodeList'])
            if self.truncated:
                self._ins_code_list = self._ins_code_list[:self.num_groups]

            return self._ins_code_list
        else:
            return None

    @property
    def sequence_index_list(self):
        if self._sequence_index_list is not None:
            return self._sequence_index_list
        elif 'sequenceIndexList' in self.input_data:
            self._sequence_index_list = self.decoder.decode_array(self.input_data['sequenceIndexList'])
            if self.truncated:
                self._sequence_index_list = self._sequence_index_list[:self.num_groups]

            return self._sequence_index_list
        else:
            return None

    @property
    def chain_id_list(self):
        if self._chain_id_list is not None:
            return self._chain_id_list
        elif 'chainIdList' in self.input_data:
            self._chain_id_list = self.decoder.decode_array(self.input_data['chainIdList'])
            if self.truncated:
                self._chain_id_list = self._chain_id_list[:self.num_chains]

            return self._chain_id_list
        else:
            return None

    @property
    def chain_name_list(self):
        if self._chain_name_list is not None:
            return self._chain_name_list
        elif 'chainNameList' in self.input_data:
            self._chain_name_list = self.decoder.decode_array(self.input_data['chainNameList'])
            if self.truncated:
                self._chain_name_list = self._chain_name_list[:self.num_chains]

            return self._chain_name_list
        else:
            return None

    # calculated atom level data
    @property
    def chain_names(self):
        if self._chain_names is None:
            self._chain_names = np.empty(self.num_atoms, dtype=np.object)

            for i in range(self.num_chains):
                start = self.chainToAtomIndices[i]
                end = self.chainToAtomIndices[i + 1]
                self._chain_names[start:end] = self.chain_name_list[i]

        return self._chain_names

    @property
    def chain_ids(self):
        if self._chain_ids is None:
            self._chain_ids = np.empty(self.num_atoms, dtype=np.object)

            for i in range(self.num_chains):
                start = self.chainToAtomIndices[i]
                end = self.chainToAtomIndices[i + 1]
                self._chain_ids[start:end] = self.chain_id_list[i]

        return self._chain_ids

    @property
    def group_ids(self):
        if self._group_ids is None:
            self._group_ids = np.empty(self.num_atoms, dtype=np.int32)

            for i in range(self.num_groups):
                start = self.groupToAtomIndices[i]
                end = self.groupToAtomIndices[i + 1]
                self._group_ids[start:end] = self.group_id_list[i]

        return self._group_ids

    @property
    def group_numbers(self):
        if self._group_numbers is None:
            self._group_numbers = np.empty(self.num_atoms, dtype=np.object)
            codec, length, param, in_array = self.decoder.parse_header(self.input_data['insCodeList'])
            if len(in_array) == 8:
                # default length when there are no insertion codes
                # self._group_numbers = self.group_ids.astype(str)
                for i in range(self.num_groups):
                    start = self.groupToAtomIndices[i]
                    end = self.groupToAtomIndices[i + 1]
                    self._group_numbers[start:end] = str(self.group_id_list[i])
            else:
                for i in range(self.num_groups):
                    start = self.groupToAtomIndices[i]
                    end = self.groupToAtomIndices[i + 1]
                    self._group_numbers[start:end] = f'{self.group_id_list[i]}{self.ins_code_list[i]}'

        return self._group_numbers

    @property
    def group_names(self):
        if self._group_names is None:
            self._group_names = np.empty(self.num_atoms, dtype=np.object)

            for i in range(self.num_groups):
                start = self.groupToAtomIndices[i]
                end = self.groupToAtomIndices[i + 1]
                index = self.group_type_list[i]
                self._group_names[start:end] = self.group_list[index]['groupName']

        return self._group_names

    @property
    def atom_names(self):
        if self._atom_names is None:
            self._atom_names = np.empty(self.num_atoms, dtype=np.object)

            start = 0
            for index in self.group_type_list:
                gl = self.group_list[index]['atomNameList']
                end = start + len(gl)
                self._atom_names[start:end] = gl
                start = end

        return self._atom_names

    @property
    def elements(self):
        if self._elements is None:
            self._elements = np.empty(self.num_atoms, dtype=np.object)

            start = 0
            for index in self.group_type_list:
                gl = self.group_list[index]['elementList']
                end = start + len(gl)
                self._elements[start:end] = gl
                start = end

        return self._elements

    @property
    def chem_comp_types(self):
        if self._chem_comp_types is None:
            self._chem_comp_types = np.empty(self.num_atoms, dtype=np.object_)

            for i in range(self.num_groups):
                start = self.groupToAtomIndices[i]
                end = self.groupToAtomIndices[i + 1]
                index = self.group_type_list[i]
                self._chem_comp_types[start:end] = self.group_list[index]['chemCompType']

        return self._chem_comp_types

    @property
    def codes(self):
        if self._codes is None:
            self._codes = np.empty(self.num_atoms, dtype=np.object_)

            for i in range(self.num_groups):
                start = self.groupToAtomIndices[i]
                end = self.groupToAtomIndices[i + 1]
                index = self.group_type_list[i]
                self._codes[start:end] = self.group_list[index]['singleLetterCode']

        return self._codes

    @property
    def group_serial(self):
        if self._group_serial is None:
            self._group_serial = np.empty(self.num_atoms, dtype=np.int32)

            for i in range(self.num_groups):
                start = self.groupToAtomIndices[i]
                end = self.groupToAtomIndices[i + 1]
                self._group_serial[start:end] = i

        return self._group_serial

    @property
    def polymer(self):
        if self._polymer is None:
            self._polymer = np.empty(self.num_atoms, dtype=np.bool)

            for i in range(self.num_chains):
                start = self.chainToAtomIndices[i]
                end = self.chainToAtomIndices[i + 1]
                index = self.entityChainIndex[i]
                self._polymer[start:end] = self.entity_list[index]['type'] == 'polymer'

        return self._polymer

    @property
    def entity_types(self):
        if self._entity_type is None:
            self._entity_type = np.empty(self.num_atoms, dtype=np.object_)

            for i in range(self.num_chains):
                start = self.chainToAtomIndices[i]
                end = self.chainToAtomIndices[i + 1]
                index = self.entityChainIndex[i]
                self._entity_type[start:end] = self.entity_list[index]['type']

        return self._entity_type

    @property
    def entity_indices(self):
        if self._entity_indices is None:
            self._entity_indices = np.empty(self.num_atoms, dtype=np.int32)

            for i in range(self.num_chains):
                start = self.chainToAtomIndices[i]
                end = self.chainToAtomIndices[i + 1]
                self._entity_indices[start:end] = self.entityChainIndex[i]

        return self._entity_indices

    @property
    def chain_serial(self):
        if self._chain_serial is None:
            self._chain_serial = np.empty(self.num_atoms, dtype=np.int32)

            for i in range(self.num_chains):
                start = self.chainToAtomIndices[i]
                end = self.chainToAtomIndices[i + 1]
                self._chain_serial[start:end] = i

        return self._chain_serial

    @property
    def sequence_positions(self):
        if self._sequence_positions is None:
            self._sequence_positions = np.empty(self.num_atoms, dtype=np.int32)

            for i in range(self.num_groups):
                start = self.groupToAtomIndices[i]
                end = self.groupToAtomIndices[i + 1]
                self._sequence_positions[start:end] = self.sequence_index_list[i]

        return self._sequence_positions

    def to_pandas(self, add_cols=None, use_categories=False, multi_index=False):
        if self.df is None:
            # pre-calculate required group-level data for efficiency
            self.calc_core_group_data()
            
            cols = self.atom_column_names()[:13]
            if add_cols is not None:
                cols += add_cols
                
            self.df = self.to_atom_pandas(cols)

            if use_categories:
                self.df['chain_name'] = self.df['chain_name'].astype('category')
                self.df['chain_id'] = self.df['chain_id'].astype('category')
                self.df['group_name'] = self.df['group_name'].astype('category')
                self.df['atom_name'] = self.df['atom_name'].astype('category')
                self.df['element'] = self.df['element'].astype('category')

            if multi_index:
                self.df.set_index(['chain_name', 'chain_id', 'group_number', 'group_name', 'atom_name', 'altloc'],
                                  inplace=True)

        return self.df

    def to_atom_pandas(self, cols=None):
        """ Return a pandas dataframe with the specified atom column names"""
        columns = {c: getattr(self, self.atom_cols.get(c)) for c in cols}

        return pd.DataFrame(columns)

    def to_entity_pandas(self):
        data = []
        for entity_id, entity in enumerate(self.entity_list):
            chain_ids = set()
            for chain_index in entity['chainIndexList']:
                # when only the first model is used, not all chains are present
                if chain_index < self.num_chains:
                    chain_ids.add(self.chain_id_list[chain_index])

            if len(chain_ids) > 0:
                chain_ids = sorted(chain_ids)
                data.append([entity_id, entity['description'], entity['type'], chain_ids, entity['sequence']])

        return pd.DataFrame(data, columns=['entity_id', 'description', 'type', 'chain_ids', 'sequence'])

    def to_structure_pandas(self):
        cols = {'structure_id': self.structure_id,
                'title': self.title,
                'experimental_methods': self.experimental_methods,
                'resolution': self.resolution,
                'r_free': self.r_free,
                'r_work': self.r_work,
                'unit_cell': self.unit_cell,
                'space_group': self.space_group,
                'deposition_date': self.deposition_date,
                'release_date': self.release_date,
                'num_atoms': self.num_atoms,
                'num_bonds': self.num_bonds,
                'num_groups':  self.num_groups,
                'num_chains': self.num_chains,
                'num_models': self._num_models,
                'mmtf_version': self.mmtf_version,
                'mmtf_producer':  self.mmtf_producer}

        return pd.DataFrame(cols)

    def calc_core_group_data(self):
        if self._group_numbers is None or self._group_names is None or self._atom_names is None \
                or self._elements is None:
            codec, length, param, in_array = self.decoder.parse_header(self.input_data['insCodeList'])
            no_ins_code = len(in_array) == 8
            self._group_numbers = np.empty(self.num_atoms, dtype=np.object_)
            self._group_names = np.empty(self.num_atoms, dtype=np.object_)
            self._atom_names = np.empty(self.num_atoms, dtype=np.object_)
            self._elements = np.empty(self.num_atoms, dtype=np.object_)

            start = 0
            i = 0
            for index in self.group_type_list:
                group = self.group_list[index]
                gl = group['elementList']
                end = start + len(gl)

                self._elements[start:end] = gl
                self._group_names[start:end] = group['groupName']
                self._atom_names[start:end] = group['atomNameList']
                if no_ins_code:
                    # default length when there are no insertion codes
                    self._group_numbers[start:end] = str(self.group_id_list[i])
                else:
                    # numba cannot handle the following line
                    # self._group_numbers[start:end] = f'{self.group_id_list[i]}{self.ins_code_list[i]}'
                    self._group_numbers[start:end] = str(self.group_id_list[i]) + self.ins_code_list[i]

                start = end
                i = i + 1

    def calc_indices(self):

        if self.groupToAtomIndices is None:

            self._group_type_list = self.decoder.decode_array(self.input_data['groupTypeList'])
            self.groupToAtomIndices = np.empty(self.num_groups + 1, dtype=np.int32)
            self.chainToAtomIndices = np.empty(self.num_chains + 1, dtype=np.int32)
            self.chainToGroupIndices = np.empty(self.num_chains + 1, dtype=np.int32)
            self.modelToAtomIndices = np.empty(self.num_models + 1, dtype=np.int32)
            self.modelToGroupIndices = np.empty(self.num_models + 1, dtype=np.int32)
            self.modelToChainIndices = np.empty(self.num_models + 1, dtype=np.int32)

            chainCount, groupCount, atomCount = 0, 0, 0

            # Loop over all models
            for m in range(self.num_models):
                self.modelToAtomIndices[m] = atomCount
                self.modelToGroupIndices[m] = groupCount
                self.modelToChainIndices[m] = chainCount

                # Loop over all chains
                for i in range(self.chains_per_model[m]):
                    self.chainToAtomIndices[chainCount] = atomCount
                    self.chainToGroupIndices[chainCount] = groupCount

                    # Loop over all groups in chain
                    for _ in range(self.groups_per_chain[chainCount]):
                        self.groupToAtomIndices[groupCount] = atomCount
                        group_type = self.group_type_list[groupCount]
                        atomCount += len(self.group_list[group_type]['elementList'])
                        groupCount += 1

                    chainCount += 1

            self.groupToAtomIndices[groupCount] = atomCount
            self.chainToAtomIndices[chainCount] = atomCount
            self.chainToGroupIndices[chainCount] = groupCount
            self.modelToAtomIndices[self.num_models] = atomCount
            self.modelToGroupIndices[self.num_models] = groupCount
            self.modelToChainIndices[self.num_models] = chainCount

            if self.truncated:
                self._group_type_list = self._group_type_list[:groupCount]
                self.groupToAtomIndices = self.groupToAtomIndices[:groupCount + 1]
                self.chainToAtomIndices = self.chainToAtomIndices[:chainCount + 1]
                self.chainToGroupIndices = self.chainToGroupIndices[:chainCount + 1]
                self.num_atoms = atomCount
                self.num_groups = groupCount
                self.num_chains = chainCount

    def chain_to_entity_index(self):
        '''Returns an array that maps a chain index to an entity index

        Returns
        -------
        :obj:`array <numpy.ndarray>`
           index that maps chain index to an entity index
        '''

        if self.entityChainIndex is None:
            self.entityChainIndex = np.empty(self.num_chains, dtype=np.int32)

            for i, entity in enumerate(self.entity_list):

                #chainIndexList = entity['chainIndexList']
                # pd.read_msgpack returns tuple, msgpack-python returns list
                # TODO check this
                #if type(chainIndexList) is not list:
                #    chainIndexList = list(chainIndexList)
                # TODO need to update entity_list when self.truncate
                for index in entity['chainIndexList']:
                    if index < self.num_chains:
                        self.entityChainIndex[index] = i

    def get_chain(self, chain_name):
        """Return specified polymer chain"""
        return MmtfChain(self, chain_name)

    def get_chains(self):
        """Return polymer chains"""
        chains = []
        for chain_name in set(self.chain_name_list):
            chains.append(MmtfChain(self, chain_name))

        return chains

    def get_model(self, model_number):
        """Return specified model"""
        return MmtfModel(self, model_number)

    def get_models(self):
        """Return models"""
        models = []
        for model_number in range(self.num_models):
            models.append(MmtfModel(self, model_number))

        return models



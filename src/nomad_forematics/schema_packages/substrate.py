#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from typing import TYPE_CHECKING

import numpy as np
from nomad.datamodel.data import Schema
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.basesections import (
    Collection,
    CompositeSystemReference,
    ProcessStep,
    PubChemPureSubstanceSection,
    PureSubstanceComponent,
    ReadableIdentifiers,
)
from nomad.metainfo import MEnum, MProxy, Package, Quantity, Section, SubSection
from nomad_material_processing.general import (
    Dopant,
    ElectronicProperties,
    RectangleCuboid,
    Substrate,
)
from nomad_material_processing.utils import create_archive
from structlog.stdlib import BoundLogger

from nomad_forematics.categories import ForematicsCategory

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = Package(name='DTU customised Substrate scheme')


class ForematicsSubstrate(Substrate, Schema):
    """
    Schema for substrates in the Forematics lab.
    """

    m_def = Section(
        categories=[ForematicsCategory],
        label='Substrate',
    )

    substrate_coverage_pattern = Quantity(
        type = MEnum(['Patterned', 'Full','None']),
        default = 'Full',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )

    substrate_coverage_material = Quantity(
        type = MEnum(['ITO', 'FTO', 'None']),
        default = 'ITO',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )

    substrate_size = Quantity(
        type = MEnum(['Scale-up', 'Spin-coating', 'Glass slide']),
        default = 'Scale-up',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )

    length = Quantity(
        type=np.float64,
        default=0.075,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm'},
        unit='m',
    )

    width = Quantity(
        type=np.float64,
        default=0.025,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm'},
        unit='m',
    )
    thickness = Quantity(
        type=np.float64,
        default=0.0011,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm'},
        unit='m',
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `DTUSubstrateBatch` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)

        # define that there is no material coverage in case there is no coverage pattern
        if self.substrate_coverage_pattern == 'None':
            self.substrate_coverage_material = 'None'

        # Define the sizes of the possible pre-defined substrates
        if self.substrate_size == 'Scale-up':
            self.width = 0.025
            self.length = 0.075
            self.thickness = 0.0011
        elif self.substrate_size == 'Spin-coating':
            self.width = 0.010
            self.length = 0.020
            self.thickness = 0.0011
        elif self.substrate_size == 'Glass slide':
            self.width = 0.026
            self.length = 0.076
            self.thickness = 0.0011

class ForematicsSubstrateReference(CompositeSystemReference):
    reference = Quantity(
        type=ForematicsSubstrate,
        description='The reference to the substrate entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )


class ForematicsSubstrateBatch(Collection, Schema):
    """
    Schema for substrate batches in the Forematics lab.
    """

    m_def = Section(
        categories=[ForematicsCategory],
        label='Substrate Batch',
        a_template=dict(
            substrate_identifiers=dict(),
        ),
    )
    entities = SubSection(
        section_def=ForematicsSubstrateReference,
        description='References to the entities of the collection of substrates.',
        repeats=True,
    )
    material = Quantity(
        type=str,
        default='Glass',
        description='The material of the substrate.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
    )
    supplier = Quantity(
        type=str,
        default='Ossila',
        a_eln={'component': 'StringEditQuantity'},
    )
    length = Quantity(
        type=np.float64,
        default=0.04,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm'},
        unit='m',
    )
    width = Quantity(
        type=np.float64,
        default=0.04,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm'},
        unit='m',
    )
    thickness = Quantity(
        type=np.float64,
        default=0.000675,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm'},
        unit='m',
    )
    create_substrates = Quantity(
        type=bool,
        description='Whether to (re)create the substrate entities.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.BoolEditQuantity),
    )
    number_of_substrates = Quantity(
        type=int,
        description='The number of substrates in the batch.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
    )
    substrate_identifiers = SubSection(
        section_def=ReadableIdentifiers,
    )

    def next_used_in(
        self, entry_type: type[Schema], negate: bool = False
    ) -> ForematicsSubstrate:
        from nomad.search import (
            MetadataPagination,
            search,
        )

        ref: ForematicsSubstrateReference
        for ref in self.entities:
            if isinstance(ref.reference, MProxy):
                ref.reference.m_proxy_resolve()
            if not isinstance(ref.reference, ForematicsSubstrate):
                continue
            substrate = ref.reference
            query = {
                'section_defs.definition_qualified_name:all': [
                    entry_type.m_def.qualified_name()
                ],
                'entry_references.target_entry_id:all': [substrate.m_parent.entry_id],
            }
            search_result = search(
                owner='all',
                query=query,
                pagination=MetadataPagination(page_size=1),
                user_id=self.m_parent.metadata.main_author.user_id,
            )
            if search_result.pagination.total > 0 and not negate:
                return substrate
            elif search_result.pagination.total == 0 and negate:
                return substrate
        return None

    def next_not_used_in(self, entry_type: type[Schema]) -> ForematicsSubstrate:
        return self.next_used_in(entry_type, negate=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ForematicsSubstrateBatch` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        if self.create_substrates:
            self.entities = []
            substrate = ForematicsSubstrate()

            geometry = RectangleCuboid()
            geometry.length = self.length
            geometry.width = self.width
            geometry.height = self.thickness
            substrate.geometry = geometry

            component = PureSubstanceComponent()
            substance_section = PubChemPureSubstanceSection()
            substance_section.molecular_formula = self.material
            substance_section.normalize(archive, logger)

            component.pure_substance = substance_section
            substrate.components = [component]

            substrate.dopants = [
                Dopant(element=element) for element in self.doping_elements
            ]

            electronic_properties = ElectronicProperties()
            electronic_properties.conductivity_type = self.doping_type_of_substrate
            electronic_properties.electrical_resistivity = self.doping_of_substrate
            substrate.electronic_properties = electronic_properties

            substrate.supplier = self.supplier
            substrate.substrate_polishing = self.substrate_polishing

            substrate.normalize(archive, logger)

            for i in range(self.number_of_substrates):
                substrate.name = f'{self.name} {i}' #Definition of substrates names
                substrate.datetime = self.datetime
                substrate.lab_id = f'{self.lab_id}-{i}'
                file_name = f'{substrate.lab_id}.archive.json'
                substrate_archive = create_archive(substrate, archive, file_name)
                self.entities.append(
                    CompositeSystemReference(
                        reference=substrate_archive,
                        name=substrate.name,
                        lab_id=substrate.lab_id,
                    )
                )
            self.create_substrates = False


class CleaningStep(ProcessStep):
    m_def = Section()
    cleaning_agent = Quantity(
        type=MEnum(['Acetone', 'Helmanex','IPA', 'NaOH', 'UV-Ozone']),
        default='Acetone',
        a_eln=ELNAnnotation(component=ELNComponentEnum.RadioEnumEditQuantity),
    )
    sonication = Quantity(
        type=bool,
        default=False,
        a_eln=ELNAnnotation(component=ELNComponentEnum.BoolEditQuantity),
    )
    cleaning_time = Quantity(
        type=np.float64,
        default=60,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'minutes'},
        unit='s',
    )

# class ForematicsSubstrateCleaning(Process, Schema):
#     """
#     Schema for substrate cleaning at the Forematics lab.
#     """

#     m_def = Section(
#         categories=[ForematicsCategory],
#         label='Substrate Cleaning',
#     )
#     substrate_batch = Quantity(
#         type=DTUSubstrateBatch,
#         description='The substrate batch that was cleaned.',
#         a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
#     )
#     steps = SubSection(
#         section_def=CleaningStep,
#         repeats=True,
#     )

#     def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
#         """
#         The normalizer for the `DTUSubstrateCleaning` class.

#         Args:
#             archive (EntryArchive): The archive containing the section that is being
#             normalized.
#             logger (BoundLogger): A structlog logger.
#         """
#         self.samples = self.substrate_batch.entities
#         return super().normalize(archive, logger)


# class DTUSubstrateCutting(Process, Schema):
#     """
#     Schema for substrate cutting at the DTU Nanolab.
#     """

#     m_def = Section(
#         categories=[DTUNanolabCategory],
#         label='Substrate Cutting',
#     )
#     substrate_batch = Quantity(
#         type=DTUSubstrateBatch,
#         description='The substrate batch that was cut.',
#         a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
#     )
#     instrument_name = Quantity(
#         type=str,
#         default='microSTRUCT vario from the company 3D-Micromac AG',
#         a_eln=ELNAnnotation(component=ELNComponentEnum.StringEditQuantity),
#     )
#     laser_power = Quantity(
#         type=np.float64,
#         default=50,
#         a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
#         unit='W',
#     )
#     laser_wavelength = Quantity(
#         type=np.float64,
#         default=532 * 1e-9,
#         a_eln=ELNAnnotation(
#             component=ELNComponentEnum.NumberEditQuantity,
#             defaultDisplayUnit='nm',
#         ),
#         unit='m',
#     )
#     repetition_rate = Quantity(
#         type=np.float64,
#         default=200,
#         a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
#         unit='Hz',
#     )
#     pattern_repetitions = Quantity(
#         type=int,
#         default=6,
#         a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEditQuantity),
#     )
#     writing_speed = Quantity(
#         type=np.float64,
#         default=50 * 1e-3,
#         a_eln=ELNAnnotation(
#             component=ELNComponentEnum.NumberEditQuantity,
#             defaultDisplayUnit='mm/s',
#         ),
#         unit='m/s',
#     )

#     def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
#         """
#         The normalizer for the `DTUSubstrateCutting` class.

#         Args:
#             archive (EntryArchive): The archive containing the section that is being
#             normalized.
#             logger (BoundLogger): A structlog logger.
#         """
#         self.samples = self.substrate_batch.entities
#         return super().normalize(archive, logger)


m_package.__init_metainfo__()
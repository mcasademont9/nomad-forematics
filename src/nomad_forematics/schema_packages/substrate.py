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
    Process,
    ProcessStep,
    ReadableIdentifiers,
)
from nomad.metainfo import (
    MEnum,
    MProxy,
    Package,
    Quantity,
    Section,
    SubSection,
)
from nomad_material_processing.general import (
    Substrate,
)
from nomad_material_processing.utils import create_archive
from structlog.stdlib import BoundLogger

from nomad_forematics.categories import ForematicsCategory

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = Package(name='Forematics customised Substrate schema')


class ForOPVSubstrate(Substrate, Schema):
    """
    Schema for one solar cell substrate in the Forematics lab.
    """

    m_def = Section(
        categories=[ForematicsCategory],
        label='ForematicsSubstrate',
    )

    # substrate_coverage_pattern = Quantity(
    #     type = MEnum(['Patterned', 'Full','None']),
    #     default = 'Full',
    #     a_eln={'component': 'RadioEnumEditQuantity'},
    # )

    # substrate_coverage_material = Quantity(
    #     type = MEnum(['ITO', 'FTO', 'None']),
    #     default = 'ITO',
    #     a_eln={'component': 'RadioEnumEditQuantity'},
    # )

    size = Quantity(
        type = MEnum(['Scale-up', 'Spin-coating']),
        default = 'Scale-up',
        a_eln={'component': 'RadioEnumEditQuantity'},
    )
    supplyer = Quantity(
        type=str,
        default ='Ossila',
        a_eln={'component': 'StringEditQuantity'}
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
    depth = Quantity(
        type=np.float64,
        default=0.0011,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm'},
        unit='m',
    )

    # opv_processing_steps_applied = BackReference(
    #     reference='ForOPVSubstrateReference.reference',
    #     description='Indirect references from reference wrapper sections',
    #     multiple=True
    # )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ForematicsSubstrate` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)

        # Define the sizes of the possible pre-defined substrates
        if self.size == 'Scale-up':
            self.width = 7#0.025
            self.length = 7#0.075
            self.depth = 7#0.0011
        elif self.size == 'Spin-coating':
            self.width = 3#0.010
            self.length = 3#0.020
            self.depth = 3#0.0011

class ForOPVSubstrateReference(CompositeSystemReference):
    reference = Quantity(
        type=ForOPVSubstrate,
        description='The reference to a ForOPVSubstrate entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )


class ForOPVSubstrateBatch(Collection, Schema):
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
        section_def=ForOPVSubstrateReference,
        description='References to the entities of the collection of substrates.',
        repeats=True,
    )

    supplier = Quantity(
        type=str,
        default='Ossila',
        a_eln={'component': 'StringEditQuantity'},
    )

    size = Quantity(
        type = MEnum(['Scale-up', 'Spin-coating']),
        default = 'Spin-coating',
        a_eln={'component': 'RadioEnumEditQuantity'},
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

    lab_id = Quantity(
        type=str,
        default = 'NanoptoLab',
        a_eln={'component': 'StringEditQuantity'}
    )

    def next_used_in(
        self, entry_type: type[Schema], negate: bool = False
    ) -> ForOPVSubstrate:
        from nomad.search import (
            MetadataPagination,
            search,
        )

        ref: ForOPVSubstrateReference
        for ref in self.entities:
            if isinstance(ref.reference, MProxy):
                ref.reference.m_proxy_resolve()
            if not isinstance(ref.reference, ForOPVSubstrate):
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

    def next_not_used_in(self, entry_type: type[Schema]) -> ForOPVSubstrate:
        return self.next_used_in(entry_type, negate=True)

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ForOPVSubstrateBatch` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        if self.create_substrates:

            self.entities = []

            substrate = ForOPVSubstrate()

            substrate.supplier = self.supplier
            substrate.size = self.size
            substrate.normalize(archive, logger)

            for i in range(self.number_of_substrates):
                substrate.name = f'{self.name} {i}' #Definition of substrates names
                substrate.datetime = self.datetime
                substrate.lab_id = f'{self.lab_id}-{i}'
                file_name = f'{substrate.name}.archive.json'
                substrate_archive = create_archive(substrate, archive, file_name)

                # Check if that is correct aftwerwards with
                # the implementation in oasis environment
                self.entities.append(
                    # CompositeSystemReference(
                    ForOPVSubstrateReference(
                        reference=substrate_archive,
                        name=substrate.name,
                        lab_id=substrate.lab_id,
                    )
                )
            self.create_substrates = False

class ForOPVSubstrateBatchReference(CompositeSystemReference):
    reference = Quantity(
        type=ForOPVSubstrateBatch,
        description='The reference to a ForOPVSubstrateBatch entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

## Processes applied to the substrate
class CleaningStep(ProcessStep):
    m_def = Section()
    cleaning_agent = Quantity(
        type=MEnum(['Acetone', 'Hellmanex', 'IPA', 'NaOH', 'UV-Ozone']),
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
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'minute'},
        unit='second',
    )

class ForOPVSubstrateCleaning(Process, Schema):
    """
    Schema for substrate cleaning at the Forematics lab for OPV samples.
    """
    m_def = Section(
        categories=[ForematicsCategory],
        label='OPV Substrate Cleaning',
    )
    supplyer = Quantity(
        type=str,
        default ='Ossila',
        a_eln={'component': 'StringEditQuantity'}
    )
    substrate_batch = Quantity(
        type=ForOPVSubstrateBatch,
        description='The substrate batch that was cleaned',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )
    procedure = Quantity(
        type=MEnum(['Standard', 'Custom']),
        default ='Standard',
        a_eln={'component': 'RadioEnumEditQuantity'}
    )
    steps = SubSection(
        section_def=CleaningStep,
        repeats=True
    )
    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ForOPVSubstrateCleaning` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        # self.samples = self.substrate_batch.entities
        if self.procedure == 'Standard':
            self.steps = [] # reset the steps to avoid overwritting
            protocol = [['Acetone', 60*5],
                        ['Hellmanex',60*5],
                        ['IPA',60*5],
                        ['NaOH',60*10]]

            for agent, time in protocol:
                cstep = CleaningStep()
                cstep.sonication = True
                cstep.cleaning_agent = agent
                cstep.cleaning_time = time
                self.steps.append(cstep)
        return super().normalize(archive, logger)

class ForOPVSubstrateCleaningReference(CompositeSystemReference):
    reference = Quantity(
        type=ForOPVSubstrateCleaning,
        description='The reference to a ForOPVSubstrateCleaning entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

m_package.__init_metainfo__()
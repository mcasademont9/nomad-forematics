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
from nomad.datamodel.data import EntryData
from nomad.metainfo import MSection, Quantity, SubSection, Package, Section, MEnum, MProxy
from nomad.datamodel.metainfo.basesections import Process, CompositeSystemReference
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
import numpy as np
from nomad_forematics.categories import ForematicsCategory
from nomad_forematics.schema_packages.substrate import ForOPVSubstrateBatch, ForOPVSubstrate, ForOPVSubstrateReference

m_package = Package(name='Forematics customised Substrate schema')

# class ForOPVProcessingStep(Process, EntryData):
#     '''
#     Base class for OPV fabrication process steps.
#     All specific processing types (blade coating, spin coating, annealing, etc.)
#     should inherit from this class.
#     '''

#     m_def = MSection(label='OPV Processing Step')

#     timestamp = Quantity(
#         type=str,
#         description='Date and time when the process step was performed.',
#         a_eln=ELNAnnotation(component=ELNComponentEnum.DateTimeEdit),
#     )

#     duration = Quantity(
#         type=float,
#         unit='second',
#         description='Duration of the process step.',
#         a_eln=ELNAnnotation(component=ELNComponentEnum.NumberEdit),
#     )

#     atmosphere = Quantity(
#         type=str,
#         description='Atmosphere conditions (e.g., air, nitrogen glovebox).',
#         a_eln=ELNAnnotation(component=ELNComponentEnum.TextEdit),
#     )

#     description = Quantity(
#         type=str,
#         description='Additional notes or observations about the process step.',
#         a_eln=ELNAnnotation(component=ELNComponentEnum.RichTextEdit),
#     )

class ForOPVProcessingStepReference(CompositeSystemReference): #CompositeSystemReference
    '''
    Base class for referencing any OPV processing step.
    '''
    m_def = Section(
        categories=[ForematicsCategory],
        label='Processing Step Reference')

    substrate_batch = Quantity(
        type=ForOPVSubstrateBatch,
        description='Sample batches that were processed in this step.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity)
    )

    samples = Quantity(
        type=ForOPVSubstrateReference,
        shape=['*'],
        description='Samples that were processed in this step.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity)
    )



    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        # Find any ProcessingStepReference instances in the archive
        print('Entered normalizing funtion of ForOPVProcessingStepReference')

        for section, a, b, c in archive.m_traverse():
            print("Checking section: ", section, a, b, c)
            if isinstance(section, ForOPVProcessingStepReference):
                substrate_batch_ref = getattr(section, 'substrate_batch', None)
                print("Reference found: ", substrate_batch_ref)
                print("Type of ref:", type(substrate_batch_ref))

                try:
                    if isinstance(substrate_batch_ref, MProxy):
                        batch = substrate_batch_ref.reference  # This triggers resolution
                    else:
                        batch = substrate_batch_ref  # Already resolved

                    print("Reference resolved:", batch)
                    print("Resolved batch type:", type(batch))
                    print("Is instance of ForOPVSubstrateBatch:", isinstance(batch, ForOPVSubstrateBatch))

                    if isinstance(batch, ForOPVSubstrateBatch):
                        substrate_refs = batch.entities or []
                        print("Entities: ", substrate_refs)
                        section.samples = substrate_refs
                        logger.info(f"Assigned {len(substrate_refs)} substrates from batch to processing step.")

                except Exception as e:
                    print("Could not resolve reference: ", e)


class ForOPVBladeCoating(Process, EntryData):
    m_def = Section(
        categories=[ForematicsCategory],
        label='Blade Coating Process',
        description='Describes a blade coating step used in device fabrication.'
    )

    substrate_temperature = Quantity(
        type=np.float64,
        unit='kelvin',
        description='Temperature of the substrate during coating.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'}
    )

    blade_speed = Quantity(
        type=np.float64,
        unit='m/s',
        description='Speed of the blade during the coating process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm / s'}
    )

    blade_gap = Quantity(
        type=np.float64,
        unit='m',
        description='Gap between the substrate and the blade.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'um'}
    )

    atmosphere = Quantity(
        type=MEnum(['Glovebox', 'Air', 'Others']),
        description='The atmosphere during coating.',
        a_eln={'component': 'RadioEnumEditQuantity'}
    )

    comments = Quantity(
        type=str,
        description='Additional notes or comments about the coating step.',
        a_eln={'component': 'RichTextEditQuantity'},
    )

class ForOPVBladeCoatingReference(ForOPVProcessingStepReference):
    reference = Quantity(
        type=ForOPVBladeCoating,
        description='The reference to a ForOPVBladeCoating entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

class ForOPVSpinCoating(Process, EntryData):
    m_def = Section(
        categories=[ForematicsCategory],
        label='Blade Coating Process',
        description='Describes a blade coating step used in device fabrication.'
    )

    substrate_temperature = Quantity(
        type=np.float64,
        unit='kelvin',
        description='Temperature of the substrate during coating.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'}
    )

    spin_speed = Quantity(
        type=np.float64,
        unit='m/s',
        description='Speed of the blade during the coating process.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mm / s'}
    )

    spin_time = Quantity(
        type=np.float64,
        unit='m',
        description='Gap between the substrate and the blade.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'um'}
    )

    atmosphere = Quantity(
        type=MEnum(['Glovebox', 'Air', 'Others']),
        description='The atmosphere during coating.',
        a_eln={'component': 'RadioEnumEditQuantity'}
    )

    comments = Quantity(
        type=str,
        description='Additional notes or comments about the coating step.',
        a_eln={'component': 'RichTextEditQuantity'},
    )

class ForOPVSpinCoatingReference(ForOPVProcessingStepReference):
    reference = Quantity(
        type=ForOPVBladeCoating,
        description='The reference to a ForOPVBladeCoating entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

class ForOPVAnnealing(Process, EntryData):
    m_def = Section(
        categories=[ForematicsCategory],
        label='Blade Coating Process',
        description='Describes a blade coating step used in device fabrication.'
    )

    temperature = Quantity(
        type=np.float64,
        unit='kelvin',
        description='Temperature of the substrate during coating.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'celsius'}
    )

    time = Quantity(
        type=np.float64,
        unit='second',
        description='Annealing time.',
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'minute'}
    )

    atmosphere = Quantity(
        type=MEnum(['Glovebox', 'Air', 'Others']),
        description='The atmosphere during coating.',
        a_eln={'component': 'RadioEnumEditQuantity'}
    )

    comments = Quantity(
        type=str,
        description='Additional notes or comments about the coating step.',
        a_eln={'component': 'RichTextEditQuantity'},
    )

class ForOPVAnnealing(ForOPVProcessingStepReference):
    reference = Quantity(
        type=ForOPVBladeCoating,
        description='The reference to a ForOPVBladeCoating entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )


m_package.__init_metainfo__()
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
    Entity,
    CompositeSystemReference,
    ProcessStep,
    Process,
    ReadableIdentifiers,
    PureSubstance
)
from nomad.metainfo import MEnum, MProxy, Package, Quantity, Section, SubSection, MSection
from nomad_material_processing.general import (
    RectangleCuboid,
    Substrate,
)
from nomad_material_processing.solution.general import (Solution)
from nomad_material_processing.utils import create_archive
from structlog.stdlib import BoundLogger

from nomad_forematics.categories import ForematicsCategory

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import EntryArchive
    from structlog.stdlib import BoundLogger

m_package = Package(name='Forematics customised solution preparation schema')


class SolventComponent(Entity):
    # Sill needs to be defined properly
    m_def = Section(
        categories=[ForematicsCategory],
        label='Forematics Solvent Component',
    )
    solvent_ratio = Quantity(
        type=np.float64,
        default=1,
        a_eln={'component': 'NumberEditQuantity'}
    )
    name = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    density = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'g / ml'},
        unit='g / ml',
    )
    material_reference = Quantity(
        type=PureSubstance,
        description='The pure substance of this solvent',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

class OrgSCComponent(Entity):
    # Sill needs to be defined properly
    m_def = Section(
        categories=[ForematicsCategory],
        label='Forematics Solvent Component',
    )
    organic_semiconductor_ratio = Quantity(
        type=np.float64,
        default=1,
        a_eln={'component': 'NumberEditQuantity'}
    )
    name = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    density = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'g / ml'},
        unit='g / ml',
    )
    material_reference = Quantity(
        type=PureSubstance,
        description='The pure substance of this solvent',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

class AdditiveComponent(Entity):
    # Sill needs to be defined properly
    m_def = Section(
        categories=[ForematicsCategory],
        label='Forematics Solvent Component',
    )
    # ratio = Quantity(
    #     type=np.float64,
    #     default=1,
    #     a_eln={'component': 'NumberEditQuantity'}
    # )
    name = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    solid_concentration = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'g / ml'},
        unit='g / ml',
    )
    liquid_concentration = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ml / ml'},
        unit='ml / ml',
    )
    material_reference = Quantity(
        type=PureSubstance,
        description='The pure substance of this solvent',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )


class ForOPVSolution(Schema):
    """
    Schema for one solar cell substrate in the Forematics lab.

    We define the solution as a compilation of solvents, donors, acceptors and additives.
    Each of those has its own class defined specifically for them.
    """

    m_def = Section(
        categories=[ForematicsCategory],
        label='Forematics Solution General',
    )
    solvents = SubSection(
        section_def=SolventComponent,
        description="""
        Add any solvents that contains the solution.
        """,
        repeats=True,
    )
    donors = SubSection(
        section_def=OrgSCComponent,
        description="""
        Add any donors that contains the solution.
        """,
        repeats=True,
    )
    acceptors = SubSection(
        section_def=OrgSCComponent,
        description="""
        Add any acceptors that contains the solution.
        """,
        repeats=True,
    )
    additives = SubSection(
        section_def=AdditiveComponent,
        description="""
        Add any additives that contains the solution.
        """,
        repeats=True,
    )
    total_volume = Quantity(
        type=np.float64,
        default=1,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ml'},
        unit = 'ml'
    )
    solute_concentration = Quantity(
        type=np.float64,
        default = 15,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mg / ml'},
        unit='mg / ml'
    )

    calculate_solution = Quantity(
        type=bool,
        default= False,
        a_eln = ELNAnnotation(component=ELNComponentEnum.BoolEditQuantity),
    )


    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ForematicsSubstrate` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        if self.calculate_solution:
            for solvent in self.solvents:
                print(solvent.solvent_ratio)



m_package.__init_metainfo__()
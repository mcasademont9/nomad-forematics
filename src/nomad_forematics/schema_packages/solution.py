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
    Entity,
    PureSubstance,
    CompositeSystemReference,
)
from nomad.metainfo import (
    Package,
    Quantity,
    Section,
    SubSection,
)
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
        label='Forematics Solvent Component of a solution',
    )
    ratio = Quantity(
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
    material_reference = Quantity( # I hve to check that this works properly, and add normalizers that defines a name when this is updated
        type=PureSubstance,
        description='The pure substance of this solvent',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

class OrgSCComponent(Entity):
    # Sill needs to be defined properly
    m_def = Section(
        categories=[ForematicsCategory],
        label='Forematics Solvent Component of a solution',
    )
    ratio = Quantity(
        type=np.float64,
        default=1,
        a_eln={'component': 'NumberEditQuantity'}
    )
    name = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    # density = Quantity(
    #     type=np.float64,
    #     a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'g / ml'},
    #     unit='g / ml',
    # )
    material_reference = Quantity( # I hve to check that this works properly, and add normalizers that defines a name when this is updated
        type=PureSubstance,
        description='The pure substance of this solvent',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

class AdditiveComponent(Entity):
    # Sill needs to be defined properly
    m_def = Section(
        categories=[ForematicsCategory],
        label='Forematics Solvent Component of a solution',
    )
    name = Quantity(
        type=str,
        a_eln={'component': 'StringEditQuantity'},
    )
    liquid_percent = Quantity(
        type=np.float64,
        a_eln={'component': 'NumberEditQuantity'}
    )
    material_reference = Quantity( # I hve to check that this works properly, and add normalizers that defines a name when this is updated
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
        default=0.0006,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'ml'},
        unit = 'l'
    )
    solute_concentration = Quantity(
        type=np.float64,
        default = 15,
        a_eln={'component': 'NumberEditQuantity', 'defaultDisplayUnit': 'mg / ml'},
        unit='g / l'
    )

    calculate_solution = Quantity(
        type=bool,
        default= False,
        a_eln = ELNAnnotation(component=ELNComponentEnum.BoolEditQuantity),
    )

    calculated_solution = Quantity(
        type=str,
        default= 'Check "Calculate solution" box to calculate volume and weigths of different components.',
        a_eln={'component': 'RichTextEditQuantity'},
    )

    def normalize(self, archive: 'EntryArchive', logger: 'BoundLogger') -> None:
        """
        The normalizer for the `ForOPVSolution` class.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger (BoundLogger): A structlog logger.
        """
        super().normalize(archive, logger)
        if self.calculate_solution:
            print_string = []
            self._calculate_solvent_strings(print_string)
            self._calculate_osc_strings(print_string)
            self._calculate_additive_strings(print_string)

            # Print the calculated parameters. The \n does not work for the kind of
            # output data we have. Let's try to use <br /> as in HTML formatting
            self.calculated_solution = '<br />'.join(print_string)
            self.calculate_solution = False  # back to false

    def _calculate_solvent_strings(self, print_string):
        if not self.solvents:
            print_string.append('No solvent components defined')
        else:
            total_solvent_ratio = sum(solvent.ratio for solvent in self.solvents)
            for solvent in self.solvents:
                solvent_volume = self.total_volume * solvent.ratio / total_solvent_ratio
                solvent_string = f"Solvent: {solvent.name} -> {solvent_volume.to('ml').magnitude:.6g} ml"
                print_string.append(solvent_string)

    def _calculate_osc_strings(self, print_string):
        total_osc_ratio = sum(donor.ratio for donor in self.donors) + sum(acceptor.ratio for acceptor in self.acceptors)
        total_osc_mg = self.solute_concentration.to('mg/ml') * self.total_volume.to('ml')

        if not self.donors:
            print_string.append('No donor components defined')
        else:
            for donor in self.donors:
                osc_mg = total_osc_mg * donor.ratio / total_osc_ratio
                osc_string = f"Donor: {donor.name} -> {osc_mg.to('mg').magnitude:.6g} mg"
                print_string.append(osc_string)

        if not self.acceptors:
            print_string.append('No acceptor components defined')
        else:
            for acceptor in self.acceptors:
                osc_mg = total_osc_mg * acceptor.ratio / total_osc_ratio
                osc_string = f"Acceptor: {acceptor.name} -> {osc_mg.to('mg').magnitude:.6g} mg"
                print_string.append(osc_string)

    def _calculate_additive_strings(self, print_string):
        if not self.additives:
            print_string.append('No additives components defined')
        else:
            for additive in self.additives:
                additive_volume = additive.liquid_percent / 100 * self.total_volume.to('microlitre')
                additive_string = f"Additive: {additive.name} -> {additive_volume.to('microlitre').magnitude:.6g} ul"
                print_string.append(additive_string)

class ForOPVSolutionReference(CompositeSystemReference):
    reference = Quantity(
        type=ForOPVSolution,
        description='The reference to a ForOPVSolution entity.',
        a_eln=ELNAnnotation(component=ELNComponentEnum.ReferenceEditQuantity),
    )

m_package.__init_metainfo__()
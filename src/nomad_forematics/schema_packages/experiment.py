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

from nomad.metainfo import (
    Package,
    Section,
    Quantity,
    SubSection,
)
from nomad.datamodel.data import (
    Schema,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
    ELNComponentEnum,
)

from nomad_forematics.schema_packages.substrate import (
    ForOPVSubstrate,
    ForOPVSubstrateBatch,
    ForOPVSubstrateCleaningReference,
)

from nomad_forematics.schema_packages.processing import (
    ForOPVProcessingStepReference,
)

from nomad_forematics.schema_packages.solution import (
    ForOPVSolution,
    ForOPVSolutionReference,
)
from nomad_forematics.categories import (
    ForematicsCategory,
)

m_package = Package(name='Forematics OPV Experiment Schema')

class ForOPVExperiment(Schema):
    """
    Schema for an OPV experiment, combining substrate, solution, fabrication, and characterization.
    """

    m_def = Section(
        categories=[ForematicsCategory],
        label='Forematics OPV Experiment',
    )

    # start a few RichTextEditQuantity regions to describe the experiment (like a ELN)
    objectives = Quantity(
        type=str,
        description='Describe the objective of this OPV experiment',
        a_eln={'component': 'RichTextEditQuantity'},
        default='Describe the objectives of this OPV experiment...'
    )

    comments = Quantity(
        type=str,
        description='Any general comment about this experiment',
        a_eln={'component': 'RichTextEditQuantity'},
        default='General comments about this experiment...'
    )

    conclusions = Quantity(
        type=str,
        description='Add any conclusions about this experiment',
        a_eln={'component': 'RichTextEditQuantity'},
        default='Add any conclusions about this experiment...'
    )

    # Reference to substrate batch entry
    substrate_batches = SubSection(
        section_def=ForOPVSubstrateBatch,
        description='Embeded substrate batch',
        repeats=True,
    )

    # Reference to solution entry
    solutions = SubSection(
        section_def=ForOPVSolutionReference,
        description='References to the used solutions.',
        repeats=True,
    )

    # Fabrication steps
    fabrication_steps = SubSection(
        section_def=ForOPVProcessingStepReference,
        description='Embeded substrate batch',
        repeats=True,
    )

    # Measurements - placeholder
    measurements = Quantity(
        type=str,
        description='Placeholder for measurements like JV curve, EQE, etc.',
        a_eln={'component': 'RichTextEditQuantity'},
        default='To be defined.'
    )

m_package.__init_metainfo__()

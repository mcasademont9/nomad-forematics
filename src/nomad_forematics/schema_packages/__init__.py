from nomad.config.models.plugins import SchemaPackageEntryPoint


class SubstrateEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_forematics.schema_packages.substrate import m_package

        return m_package

substrate = SubstrateEntryPoint(
    name='Substrate',
    description='Schema package defined for substrates.',
)

class SolutionEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_forematics.schema_packages.solution import m_package

        return m_package

solution = SolutionEntryPoint(
    name='Solution',
    description='Schema package defined for solutions.',
)

class ExperimentEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_forematics.schema_packages.experiment import m_package

        return m_package

experiment = ExperimentEntryPoint(
    name='Experiment',
    description='Schema package defined for OPV experiments.',
)

class ProcessingEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_forematics.schema_packages.processing import m_package

        return m_package

processing = ProcessingEntryPoint(
    name='Processing',
    description='Schema package defined for OPV processing steps.',
)
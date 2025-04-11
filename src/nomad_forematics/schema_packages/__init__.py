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
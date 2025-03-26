from nomad.datamodel.data import EntryDataCategory
from nomad.metainfo.metainfo import Category


class ForematicsCategory(EntryDataCategory):
    m_def = Category(
        label='ICMAB Forematics', categories=[EntryDataCategory]
    )
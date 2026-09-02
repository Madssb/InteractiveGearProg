"""
osrs_milestone_metadata
===============

Public API
----------
- query_milestone_metadata_record(milestone): resolve a single OSRS milestone metadata record or None
- query_milestone_metadata(milestones): resolve OSRS milestone metadata records and unresolved milestones

Notes
-----
All other functions are internal helpers and may change without notice.
"""

from .client import (
    MilestoneMetadata,
    MilestoneMetadataQueryResult,
    MilestoneMetadataRecord,
    item_rs3,
    query_milestone_metadata,
    query_milestone_metadata_record,
)

__all__ = [
    "MilestoneMetadata",
    "MilestoneMetadataQueryResult",
    "MilestoneMetadataRecord",
    "item_rs3",
    "query_milestone_metadata",
    "query_milestone_metadata_record",
]

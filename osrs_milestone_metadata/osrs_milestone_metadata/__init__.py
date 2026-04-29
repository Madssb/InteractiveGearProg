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

from .client import MilestoneMetadata, MilestoneMetadataRecord, MilestoneMetadataQueryResult, item_rs3, query_milestone_metadata_record, query_milestone_metadata

__all__ = [
    "MilestoneMetadata",
    "MilestoneMetadataRecord",
    "MilestoneMetadataQueryResult",
    "query_milestone_metadata_record",
    "query_milestone_metadata",
    "item_rs3",
]

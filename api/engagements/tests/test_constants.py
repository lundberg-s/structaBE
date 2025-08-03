"""
Test constants for engagements tests.
Centralized location for all test data, URLs, and expected values.
"""


class TestURLs:
    """URL constants for all engagement endpoints."""
    
    # Ticket URLs
    TICKET_LIST = "engagements:ticket-list"
    TICKET_DETAIL = "engagements:ticket-detail"
    
    # Job URLs
    JOB_LIST = "engagements:job-list"
    JOB_DETAIL = "engagements:job-detail"
    
    # Case URLs
    CASE_LIST = "engagements:case-list"
    CASE_DETAIL = "engagements:case-detail"
    
    # Comment URLs
    COMMENT_LIST = "engagements:comment-list"
    COMMENT_DETAIL = "engagements:comment-detail"
    
    # Attachment URLs
    ATTACHMENT_LIST = "engagements:attachment-list"
    ATTACHMENT_DETAIL = "engagements:attachment-detail"
    
    # Work Item Option URLs
    STATUS_LIST = "engagements:status-list"
    STATUS_DETAIL = "engagements:status-detail"
    CATEGORY_LIST = "engagements:category-list"
    CATEGORY_DETAIL = "engagements:category-detail"
    PRIORITY_LIST = "engagements:priority-list"
    PRIORITY_DETAIL = "engagements:priority-detail"


class TestData:
    """Test data constants for creating test objects."""
    
    # Default User constants
    DEFAULT_USER_PASSWORD = "testpass"
    DEFAULT_USER_EMAIL = "testuser@example.com"
    DEFAULT_USER_FIRST_NAME = "Test"
    DEFAULT_USER_LAST_NAME = "User"
    
    # Other User/Email constants
    OTHER_USER_EMAIL = "other_user@example.com"
    SPOOF_EMAIL = "spoof@example.com"
    SPOOF_PASSWORD = "pass"
    
    # Content constants
    UPDATED_TITLE = "Updated Title"
    HACKED_TITLE = "Hacked"
    INVALID_STATUS = "invalid_status"
    FAKE_CREATED_AT = "2000-01-01T00:00:00Z"
    
    # Filter/Search constants
    UNIQUE_STATUS_LABEL = "UniqueStatusForFilter"
    UNIQUE_PRIORITY_LABEL = "UniquePriorityForFilter"
    UNIQUE_CATEGORY_LABEL = "UniqueCategoryForFilter"
    UNIQUE_TITLE = "UniqueTitle"
    SPECIAL_DESC = "SpecialDesc"
    MY_TENANT_TITLE = "MyTenantTitle"
    OTHER_TENANT_TITLE = "OtherTenantTitle"


class SetupDefaults:
    """Default values for test setup."""
    
    DEFAULT_TENANT_WORK_ITEM_TYPE = "ticket"
    
    # Default amounts for creating test objects
    WORK_ITEM_AMOUNT = 3
    COMMENT_AMOUNT = 3
    ATTACHMENT_AMOUNT = 3
    STATUS_AMOUNT = 5
    CATEGORY_AMOUNT = 5
    PRIORITY_AMOUNT = 5


class QueryParams:
    """Query parameter constants for API requests."""
    
    STATUS_OPEN = "open"
    PRIORITY_HIGH = "high"
    SEARCH = "search"
    STATUS_LABEL = "status__label"
    PRIORITY_LABEL = "priority__label"
    CATEGORY_LABEL = "category__label"


class ExpectedResults:
    """Expected result constants for assertions."""
    
    RESULT_COUNT = 3
    FILTERED_COUNT = 1 
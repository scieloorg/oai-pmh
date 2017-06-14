from collections import namedtuple


OAIRequest = namedtuple('OAIRequest', '''verb identifier metadataPrefix from
        until set resumptionToken archive_url''')


class Repository:
    def __init__(self, repository_name, protocol_version, admin_email, 
            deleted_record='no', granularity='YYYY-MM-DD'):
        self.repository_name = repository_name
        self.protocol_version = protocol_version
        self.admin_email = admin_email
        self.deleted_record = deleted_record
        self.granularity = granularity

    def identify(self):
        """This verb is used to retrieve information about a repository.

        Some of the information returned is required as part of the OAI-PMH.
        Repositories may also employ the Identify verb to return additional
        descriptive information.
        """

    def list_metadata_formats(self):
        """This verb is used to retrieve the metadata formats available from a
        repository.
        
        An optional argument restricts the request to the formats available for
        a specific item.
        """

    def list_identifiers(self, metadata_prefix, _from=None, until=None,
            set=None, resumption_token=None):
        """This verb is an abbreviated form of ListRecords, retrieving only
        headers rather than records.
        
        Optional arguments permit selective harvesting of headers based on set
        membership and/or datestamp. Depending on the repository's support for
        deletions, a returned header may have a status attribute of "deleted"
        if a record matching the arguments specified in the request has been
        deleted.
        """

    def list_sets(self, resumption_token=None):
        """This verb is used to retrieve the set structure of a repository,
        useful for selective harvesting.
        """

    def list_records(self, metadata_prefix, _from=None, until=None,
            set=None, resumption_token=None):
        """This verb is used to harvest records from a repository.
        
        Optional arguments permit selective harvesting of records based on set
        membership and/or datestamp. Depending on the repository's support for
        deletions, a returned header may have a status attribute of "deleted"
        if a record matching the arguments specified in the request has been
        deleted. No metadata will be present for records with deleted status.
        """

    def get_record(self, identifier, metadata_prefix):
        """This verb is used to retrieve an individual metadata record from a
        repository.
        
        Required arguments specify the identifier of the item from which the
        record is requested and the format of the metadata that should be
        included in the record. Depending on the level at which a repository
        tracks deletions, a header with a "deleted" value for the status
        attribute may be returned, in case the metadata format specified by
        the metadataPrefix is no longer available from the repository or from
        the specified item.
        """


class Item:
    """An item is a constituent of a repository from which metadata about a
    resource can be disseminated. An item is conceptually a container that
    stores or dynamically generates metadata about a single resource in
    multiple formats, each of which can be harvested as records via the
    OAI-PMH. Each item has an identifier that is unique within the scope of
    the repository of which it is a constituent.
    """
    def __init__(self, resource, formats, scoped_id_getter):
        pass

    def get_identifier(self):
        pass

    def get_record(self, fmt):
        pass


class Record:
    """A record is metadata expressed in a single format. A record is returned
    in an XML-encoded byte stream in response to an OAI-PMH request for metadata
    from an item. A record is identified unambiguously by the combination of the
    unique identifier of the item from which the record is available, the
    metadataPrefix identifying the metadata format of the record, and the
    datestamp of the record.
    """




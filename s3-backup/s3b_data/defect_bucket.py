class DefectBucket:
    '''
    Dataclass that stores information about defective buckets.

    This is needed, to exclude these buckets from the backup. See OPS-1531
    '''
    drivename = None
    # The name of the drive, like 'hidrivenbc'.

    bucketname = None
    # Defines the name of the defective bucket.

    def __init__(self, drivename, bucketname):
        self.drivename = drivename
        self.bucketname = bucketname

    def is_defective_bucket(self, drivename, bucketname):
        '''
        Returns True, if the given bucket on the specified drive is marked as defect.
        '''
        return (self.drivename == drivename) and (self.bucketname == bucketname)

    def __str__(self):
        return "drivename: " + self.drivename + ", bucketname: " + str(self.bucketname)
        
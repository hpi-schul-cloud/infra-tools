class DefectFile:
    '''
    Dataclass that stores information about a defective file.

    This is needed, to exclude these files from the backup. See OPS-1545
    '''
    drivename = None
    # The name of the drive, like 'hidrivenbc'.

    bucketname = None
    # Defines the name of the defective bucket.

    filename = None
    # Defines the name of the defective file.

    def __init__(self, drivename, bucketname, filename):
        self.drivename = drivename
        self.bucketname = bucketname
        self.filename = filename

    def is_defective_file(self, drivename, bucketname, filename):
        '''
        Returns True, if the given file on the specified drive and bucket is marked as defect.
        '''
        return (self.drivename == drivename) and (self.bucketname == bucketname) and (self.filename == filename)

    def __str__(self):
        return "drivename: " + self.drivename + ", bucketname: " + str(self.bucketname) + ", filename: " + str(self.filename)
        
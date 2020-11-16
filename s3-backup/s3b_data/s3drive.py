class S3Drive:
    '''
    Dataclass that stores information about a (Hi)Drive.

    Typically part of the BackupConfiguration.
    '''
    drivename = None
    # The name of the drive, like 'hidrivenbc'.

    backupdrive = False
    # Defines, if this is a backup target drive.

    def __init__(self, drivename, backupdrive):
        self.drivename = drivename
        self.backupdrive = backupdrive

    def isBackupDrive(self):
        '''
        Returns True, if the drive is a drive, where backups may be stored. False otherwise.
        Only drives marked as backupdrives can be used as backup targets.
        Only drives that are not backupdrives can be backup sources.
        '''
        return self.backupdrive == True

    def __str__(self):
        return "drivename: " + self.drivename + ", backupdrive: " + str(self.backupdrive)
        
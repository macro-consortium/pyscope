# WCS
self._wcs = kwargs.get('wcs', self._wcs)
if self._wcs is None: self._wcs = self._import_driver('wcs_astrometrynet', 'WCS', ascom=False, required=True)
_check_class_inheritance(self._wcs, 'WCS')
self._wcs_driver = self._wcs.Name
self._config['wcs']['wcs_driver'] = self._wcs_driver

# WCS
self._wcs_driver = self.config.get('wcs_driver', None)
self._wcs_ascom = self.config.get('wcs_ascom', None)
self._wcs = self._import_driver(self.wcs_driver, 'WCS', ascom=self.wcs_ascom, required=False)

@property
def wcs_driver(self):
    return self._wcs_driver

@property
def ra_key(self):
    return self._ra_key
@ra_key.setter
def ra_key(self, value):
    self._ra_key = str(value) if value is not None or value !='' else None
    self._config['wcs']['ra_key'] = str(self._ra_key) if self._ra_key is not None else ''

@property
def dec_key(self):
    return self._dec_key
@dec_key.setter
def dec_key(self, value):
    self._dec_key = str(value) if value is not None or value !='' else None
    self._config['wcs']['dec_key'] = str(self._dec_key) if self._dec_key is not None else ''

@property
def wcs_timeout(self):
    return self._wcs_timeout
@wcs_timeout.setter
def wcs_timeout(self, value):
    self._wcs_timeout = max(float(value), 0) if value is not None or value !='' else None
    self._config['wcs']['wcs_timeout'] = str(self._wcs_timeout) if self._wcs_timeout is not None else ''
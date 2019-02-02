from typing import Mapping
from datetime import datetime, timedelta
from functools import partial
from pprint import pformat
import logging
import attr
from ..utils.dicom import DicomLevel, dicom_date, dicom_time
from ..utils import Endpoint, Serializable, FuncByDates
from . import Orthanc

@attr.s
class ProxiedDicom(Endpoint, Serializable):

    name = attr.ib( default="ProxiedDicom" )
    proxy_desc = attr.ib( factory=dict )
    proxy_domain = attr.ib( type=str, default="remote" )

    proxy = attr.ib( init=False )
    @proxy.default
    def setup_proxy(self):
        # if self.proxy_desc.get("ctype"):
        #     self.proxy_desc.pop("ctype")
        return Orthanc(**self.proxy_desc)

    def find(self, query: Mapping, level=DicomLevel.STUDIES, retrieve: bool=False, **kwargs):
        return self.proxy.rfind(query=query,
                                level=level,
                                domain=self.proxy_domain,
                                retrieve=retrieve)

    def iter_query_by_date(self, q: Mapping,
                           start: datetime, stop: datetime, step: timedelta):

        def qdt(q, start: datetime, stop: datetime):
            if not q:
                q = {}
            _start = min(start, stop)
            _end = max(start, stop)
            if _start.date() != _end.date():
                q['StudyDate'] = "{}-{}".format(dicom_date(_start), dicom_date(_end))
            else:
                q['StudyDate'] = "{}".format(dicom_date(_start))
            q['StudyTime'] = "{}-{}".format(dicom_time(_start), dicom_time(_end))
            return q

        func = partial(qdt, q)
        _gen = FuncByDates(func, start, stop, step)

        for q in _gen:
            logging.debug(pformat(q))
            yield self.find(q)

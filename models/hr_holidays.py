#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from openerp import api
# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.tools import float_is_zero
import datetime
import calendar
from datetime import datetime, timedelta, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)

HOURS_PER_DAY = 8

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    @api.onchange('date_to', 'date_from')
    def onchange_date_from(self):
        
        date_from = self.date_from
        date_to = self.date_to

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
            self.date_to = str(date_to_with_delta)
   
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            _date_from = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
            _date_to = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
            dates = _date_to - _date_from

            diff_day = dates.days + ((dates.seconds / float(3600)) / float(24))
            self.number_of_days_temp = diff_day
        else:
            self.number_of_days_temp = 0


class calendar_event_type(models.Model):
    _inherit = 'calendar.event.type'

    notunaffected_days = fields.Boolean('No Afecta Dias Laborados')


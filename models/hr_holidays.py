#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from openerp import api
# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.tools import float_is_zero
import re
import ast
from datetime import *
import calendar



from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)

HOURS_PER_DAY = 8

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    number_of_hours_temp = fields.Float('Numero de Horas')

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

            diff_day = dates.days
            diff_hours = (dates.seconds / float(3600))

            self.number_of_days_temp = diff_day
            self.number_of_hours_temp = diff_hours
        else:
            self.number_of_days_temp = 0
            self.number_of_hours_temp = 0

    @api.multi
    @api.onchange('number_of_days_temp', 'number_of_hours_temp')
    def onchange_days_hours(self):
        hours = self.number_of_hours_temp
        days = self.number_of_days_temp

        if self.date_from:

            date_from = datetime.strptime(self.date_from, "%Y-%m-%d %H:%M:%S") 
            self.date_to = datetime.strptime('%s-%s-%s %s:%s:%s' % ( date_from.year, date_from.month, date_from.day, date_from.hour, date_from.minute, date_from.second ), "%Y-%m-%d %H:%M:%S") +  timedelta( days = days ) + timedelta( hours = hours ) 
        
      


class calendar_event_type(models.Model):
    _inherit = 'calendar.event.type'

    notunaffected_days = fields.Boolean('No Afecta Dias Laborados')


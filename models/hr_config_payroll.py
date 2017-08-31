# -*- coding: utf-8 -*-
##############################################################################

##############################################################################
import logging
_logger = logging.getLogger(__name__)
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import osv
from openerp.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class hr_config_payroll(models.Model):
    _name = 'hr.config.payroll' 
    
    name = fields.Char('Nombre')
    tipo = fields.Selection([('salario_min','Salario Minimo'), ('aux_trans','Auxilio de Transporte'),('sub_alimen', 'Subsidio de Alimentacion')])
    valor = fields.Float('Valor para la Vigencia')
    fecha_inicial = fields.Date('Fecha Inicial de Vigencia')
    fecha_final = fields.Date('Fecha Final de Vigencia')



        

 
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

@api.model
def create(self, vals):
	res = super(hr_config_payroll, self).create(vals) 
	_logger.info('*********************************** Prueba*******************************')
	model_config_payroll = self.env['hr.config.payroll']
	tipo = vals['tipo']
	consulta = model_config_payroll.search([('tipo','=', tipo), ('fecha_inicial', '=', vals['fecha_inicial']), ('fecha_final', '=', vals['fecha_final'])])
	_logger.info('*******************************************************consulta')
	_logger.info(consulta)
	return res

        

 
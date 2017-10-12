import logging
_logger = logging.getLogger(__name__)
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.osv import osv
from openerp.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)


class hr_employee_category(models.Model):
    _inherit = 'hr.contract' 
    
    salario_minimo = fields.Float('Salario Minimo Vigente')
    aux_transporte = fields.Float('Auxilio de Transporte')
    salario_minimo_r = fields.Float('Salario Minimo Vigente', related = 'salario_minimo', readonly= True)
    aux_transporte_r = fields.Float('Auxilio de Transporte', related = 'aux_transporte', readonly= True)      
    base_sal_min = fields.Boolean('Base Salario Minimo')
    

    def configuracion(self):
        salario_minimo = 0
        auxilio_trans = 0
        sub_alimenentacion = 0
        fecha_actual = datetime.now().strftime('%Y-%m-%d')
        modelo_config_nomina = self.env['hr.config.payroll']
        consulta_config = modelo_config_nomina.search([('fecha_final','>=',fecha_actual)])
        if consulta_config:
            for data in consulta_config:
                if data.tipo == 'salario_min':
                    salario_minimo = data.valor
                if data.tipo == 'aux_trans':
                    auxilio_trans == data.valor
                if data.tipo == 'sub_alimen':
                    sub_alimenentacion = data.valor

        return sub_alimenentacion, auxilio_trans, salario_minimo
    @api.model
    def default_get(self, vals):   

        result = super(hr_employee_category, self).default_get(vals)
        _config = self.configuracion()  
        result.update({
                'salario_minimo' : _config[2],
                'aux_transporte' : _config[1],
                })
        
        return result

    @api.multi
    @api.onchange('base_sal_min')
    def _on_change_product(self):
        _config = self.configuracion()

        if self.base_sal_min:
            if self.salario_minimo != 0:
                self.wage = self.salario_minimo
            else:
                self.wage = _config[2]
                self.salario_minimo= _config[2]

        




   


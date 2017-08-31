# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

# Agrega campos EPS y Fondo de Pensiones en datos del empleado.

class hr_employee_co(osv.osv):
    _inherit = 'hr.employee'

    _columns = {
        'eps_id': fields.many2one('res.partner', 'EPS'),
        'fp_id': fields.many2one('res.partner', 'Fondo de Pensiones'),
        'fc_id': fields.many2one('res.partner', 'Fondo de Cesantías'),
    }

hr_employee_co()

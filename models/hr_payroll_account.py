#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from openerp import api
import babel
import time
from openerp import netsvc
from datetime import date, datetime, timedelta
from openerp import api, tools
from openerp.osv import fields, osv
# from openerp.tools import config, float_compare
from openerp.tools import config, float_compare, float_is_zero
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class hr_salary_rule(osv.osv):
    _inherit = 'hr.salary.rule'
    _columns = {
        'origin_partner': fields.selection((('employee','Empleado'),
                                            ('eps','EPS'),
                                            ('fp','Fondo de Pensiones'),
                                            ('fc','Fondo de cesantías'),
                                            ('rule','Regla salarial')),
                                  'Tipo de tercero', required=True),
        'partner_id':fields.many2one('res.partner', 'Tercero'),
    }

    _defaults = {
        'origin_partner': 'employee',
    }

hr_salary_rule()

class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee_id = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        self.name = _('Salary Slip of %s for %s') % (employee_id.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=self.env.context.get('lang', 'en_US'))))
        self.company_id = employee_id.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee_id, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.contract_id.browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(contract_ids, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        input_line_ids = self.get_inputs(contract_ids, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines
        return

    def process_sheet(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        hr_payslip_line_pool = self.pool['hr.payslip.line']
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Payroll')

        for slip in self.browse(cr, uid, ids, context=context):
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.date or slip.date_to

            partner_eps_id = slip.employee_id.eps_id.id
            partner_fp_id = slip.employee_id.fp_id.id
            partner_fc_id = slip.employee_id.fc_id.id

            default_partner_id = slip.employee_id.address_home_id.id

            name = _('Payslip of %s') % (slip.employee_id.name)
            move = {
                'narration': name,
                'ref': slip.number,
                'journal_id': slip.journal_id.id,
                'date': date,
            }
            for line in slip.details_by_salary_rule_category:
                amt = slip.credit_note and -line.total or line.total
                if float_is_zero(amt, precision_digits=precision):
                    continue

                partner_id = line.salary_rule_id.register_id.partner_id and line.salary_rule_id.register_id.partner_id.id or default_partner_id

                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if line.salary_rule_id.origin_partner == 'employee':
                    partner_id = default_partner_id
                elif line.salary_rule_id.origin_partner == 'eps':
                    partner_id = partner_eps_id
                elif line.salary_rule_id.origin_partner == 'fp':
                    partner_id = partner_fp_id
                elif line.salary_rule_id.origin_partner == 'fc':
                    partner_id = partner_fc_id
                elif line.salary_rule_id.origin_partner == 'rule':
                    partner_id = line.salary_rule_id.partner_id.id
                else:
                    partner_id = default_partner_id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        # 'partner_id': hr_payslip_line_pool._get_partner_id(cr, uid, line, credit_account=False, context=context),
                        'partner_id': partner_id,
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amt > 0.0 and amt or 0.0,
                        'credit': amt < 0.0 and -amt or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'tax_line_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        # 'partner_id': hr_payslip_line_pool._get_partner_id(cr, uid, line, credit_account=True, context=context),
                        'partner_id': partner_id,
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amt < 0.0 and -amt or 0.0,
                        'credit': amt > 0.0 and amt or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id and line.salary_rule_id.analytic_account_id.id or False,
                        'tax_line_id': line.salary_rule_id.account_tax_id and line.salary_rule_id.account_tax_id.id or False,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = slip.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)

            move.update({'line_ids': line_ids})
            move_id = move_pool.create(cr, uid, move, context=context)
            self.write(cr, uid, [slip.id], {'move_id': move_id, 'date' : date}, context=context)
            move_pool.post(cr, uid, [move_id], context=context)
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

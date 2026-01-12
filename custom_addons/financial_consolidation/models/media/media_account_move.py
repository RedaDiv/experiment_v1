# (Updated to store related date_from/date_to fields referenced by SQL constraints)
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import logging  
_logger = logging.getLogger(__name__)


class MediaAccountMove(models.Model):
    _name = 'media.account.move'
    _description = 'Media Layer - Account Move (Staging)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Number', required=True, index=True, tracking=True)
    sync_engine_id = fields.Many2one('sync.engine', string='Sync Engine',
                                      required=True, ondelete='cascade', index=True)
    subsidiary_id = fields.Many2one('subsidiary.instance', string='Subsidiary',
                                     required=True,
                                     store=True, index=True)
    company_id = fields.Many2one('res.company', related='subsidiary_id.company_id',
                                  store=True, readonly=True)
    # NOTE: these related fields must be stored because they're referenced in SQL constraints
    date_from = fields.Date(string='Period From', related='sync_engine_id.date_from', store=True)
    date_to = fields.Date(string='Period To', related='sync_engine_id.date_to', store=True)
    date = fields.Date(string='Date', required=True, index=True, tracking=True)
    ref = fields.Char(string='Reference', tracking=True)
    source_move_id = fields.Integer(string='Source Move ID', required=True,
                                     help='ID of the move in subsidiary Odoo')
    source_journal_id = fields.Integer(string='Source Journal ID', index=True)
    source_journal_code = fields.Char(string='Source Journal Code', index=True)
    source_journal_name = fields.Char(string='Source Journal Name')
    source_journal_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
        ('situation', 'Opening/Closing Situation'),
    ], string='Source Journal Type')

    mapped_journal_id = fields.Many2one('account.journal', string='Mapped Journal',
                                         compute='_compute_mapped_journal', store=True)
    journal_mapping_id = fields.Many2one('journal.mapping', string='Journal Mapping Used',
                                          compute='_compute_mapped_journal', store=True)

    amount_total = fields.Float(string='Total Amount', digits='Account')
    currency_id = fields.Many2one('res.currency', related='subsidiary_id.currency_id',
                                   store=True, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('reconciled', 'Reconciled'),
        ('promoted', 'Promoted'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True, index=True)

    state_machine_id = fields.Many2one('media.state.machine', string='State Machine',
                                        readonly=True)

    is_balanced = fields.Boolean(string='Balanced', compute='_compute_totals', store=True)
    total_debit = fields.Float(string='Total Debit', compute='_compute_totals', 
                                store=True, digits='Account')
    total_credit = fields.Float(string='Total Credit', compute='_compute_totals',
                                 store=True, digits='Account')
    balance_difference = fields.Float(string='Balance Difference', 
                                       compute='_compute_totals', store=True)

    promoted_move_id = fields.Many2one('account.move', string='Promoted Move',
                                        readonly=True, tracking=True)
    promotion_date = fields.Datetime(string='Promotion Date', readonly=True)

    error_message = fields.Text(string='Error Message', readonly=True)
    retry_count = fields.Integer(string='Retry Count', readonly=True, default=0)

    line_ids = fields.One2many('media.account.move.line', 'media_move_id', 
                                string='Lines')

    create_date = fields.Datetime(string='Created', readonly=True)
    write_date = fields.Datetime(string='Last Updated', readonly=True)

    _sql_constraints = [
        ('unique_source_move_per_subsidiary',
        'UNIQUE(subsidiary_id, source_move_id, sync_engine_id)',
        'Source move ID must be unique per subsidiary and sync engine'),
        
        ('check_date_range',
        'CHECK(date_from <= date_to)',
        'Date From must be before or equal to Date To'),
        
        ('check_balance_threshold',
        'CHECK(balance_difference <= 0.01)',
        'Move must be balanced within 0.01 tolerance'),
    ]

    @api.constrains('date')
    def _check_date_not_future(self):
        for rec in self:
            if rec.date > fields.Date.today():
                raise ValidationError(_('Move date cannot be in the future'))

    @api.constrains('line_ids')
    def _check_at_least_two_lines(self):
        for rec in self:
            if len(rec.line_ids) < 2:
                raise ValidationError(_('Move must have at least two lines'))

    @api.model
    def create(self, vals):
        state_machine = self.env['media.state.machine'].create({
            'initial_state': vals.get('state', 'draft'),
        })
        vals['state_machine_id'] = state_machine.id
        move = super().create(vals)
        state_machine.media_move_id = move.id
        return move

    @api.depends('source_journal_id', 'source_journal_code', 'subsidiary_id')
    def _compute_mapped_journal(self):
        for move in self:
            if move.subsidiary_id and (move.source_journal_id or move.source_journal_code):
                journal_mapping = False
                mapped_journal = False
                if move.source_journal_id:
                    journal_mapping = self.env['journal.mapping'].search([
                        ('subsidiary_id', '=', move.subsidiary_id.id),
                        ('subsidiary_journal_id', '=', move.source_journal_id),
                        ('active', '=', True),
                    ], limit=1)
                if not journal_mapping and move.source_journal_code:
                    journal_mapping = self.env['journal.mapping'].search([
                        ('subsidiary_id', '=', move.subsidiary_id.id),
                        ('subsidiary_journal_code', '=', move.source_journal_code),
                        ('active', '=', True),
                    ], limit=1)
                if journal_mapping:
                    mapped_journal = journal_mapping.get_parent_journal()
                    journal_mapping.increment_usage()
                move.mapped_journal_id = mapped_journal
                move.journal_mapping_id = journal_mapping
            else:
                move.mapped_journal_id = False
                move.journal_mapping_id = False

    @api.depends('line_ids.debit', 'line_ids.credit')
    def _compute_totals(self):
        for move in self:
            move.total_debit = sum(move.line_ids.mapped('debit'))
            move.total_credit = sum(move.line_ids.mapped('credit'))
            move.balance_difference = abs(move.total_debit - move.total_credit)
            move.is_balanced = move.balance_difference < 0.01

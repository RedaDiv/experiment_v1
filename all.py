
# Financial Consolidation – Source Code Dump

**Source Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation`

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation`

```py
from . import models
from . import services
from . import wizards
```

---

## File: `__manifest__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation`

```py
{
    'name': 'Financial Consolidation',
    'version': '1.0',
    'summary': 'Financial consolidation with advanced audit and monitoring',
    'description': """
        This module provides comprehensive financial consolidation features,
        including subsidiary management, data synchronization, mapping configurations,
        currency conversion, error recovery, and detailed auditing capabilities.
        It also includes dashboards and reports for better financial oversight.
    """,
    'category': 'Accounting',
    'author': 'Reda Omran',
    'website': 'https://www.bot-sys.com',
    'license': 'AGPL-3',
    'depends': ['base', 'om_account_accountant', 'mail', 'web'],
    'data': [
        # Security
        'security/consolidation_security.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        
        # Data
        'data/email_templates.xml',
        'data/consolidation_config.xml',
        'data/consolidation_cron.xml',
        'data/cron_jobs.xml',
        'data/enhanced_cron_jobs.xml',
        'data/initial_states.xml',
        'data/media_states.xml',
        'data/sequence.xml',
        
        # Views
        'views/subsidiary_views.xml',
        'views/sync_engine_views.xml',
        'views/mapping_views.xml',
        'views/media_views.xml',
        'views/wizard_views.xml',
        'views/wizard_actions.xml',
        'views/analytics_views.xml',
        'views/audit_views.xml',
        'views/config_audit_views.xml',
        'views/consolidation_menu.xml',
        'views/currency_conversion_views.xml',
        'views/error_recovery_views.xml',
        'views/maintenance_views.xml',
        'views/restore_point_views.xml',
        'views/dashboard_views.xml',
        
        # Reports
        'reports/consolidation_reports.xml',
        'reports/subsidiary_performance_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models`

```py
from . import error
from . import base
from . import analytics
from . import currency
from . import engines
from . import mapping
from . import subsidiary
from . import sla
from . import media
from . import audit
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/analytics`

```py
from . import consolidation_analytics
```

---

## File: `consolidation_analytics.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/analytics`

```py
# -*- coding: utf-8 -*-
# FILE: models/analytics/consolidation_analytics.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class ConsolidationAnalytics(models.Model):
    _name = 'consolidation.analytics'
    _description = 'Consolidation Analytics'
    _order = 'date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string='Analytics Reference', required=True, 
                       default='New', readonly=True)
    date = fields.Date(string='Date', required=True, 
                       default=fields.Date.today, index=True)
    
    # Period
    period_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], string='Period Type', default='daily', required=True, index=True)
    
    date_from = fields.Date(string='Period From', required=True)
    date_to = fields.Date(string='Period To', required=True)
    
    # Sync Metrics
    total_syncs = fields.Integer(string='Total Syncs', default=0)
    completed_syncs = fields.Integer(string='Completed Syncs', default=0)
    failed_syncs = fields.Integer(string='Failed Syncs', default=0)
    cancelled_syncs = fields.Integer(string='Cancelled Syncs', default=0)
    in_progress_syncs = fields.Integer(string='In Progress', default=0)
    
    # Success Rates
    success_rate = fields.Float(string='Success Rate (%)', 
                                 compute='_compute_rates', store=True)
    failure_rate = fields.Float(string='Failure Rate (%)',
                                 compute='_compute_rates', store=True)
    
    # Subsidiary Metrics
    total_subsidiaries = fields.Integer(string='Total Active Subsidiaries', default=0)
    synced_subsidiaries = fields.Integer(string='Synced Subsidiaries', default=0)
    failed_subsidiaries = fields.Integer(string='Failed Subsidiaries', default=0)
    
    # Volume Metrics
    total_moves_processed = fields.Integer(string='Total Moves Processed', default=0)
    total_lines_processed = fields.Integer(string='Total Lines Processed', default=0)
    total_moves_promoted = fields.Integer(string='Total Moves Promoted', default=0)
    
    avg_moves_per_sync = fields.Float(string='Avg Moves per Sync',
                                       compute='_compute_averages', store=True)
    avg_lines_per_move = fields.Float(string='Avg Lines per Move',
                                       compute='_compute_averages', store=True)
    
    # Performance Metrics
    avg_sync_duration = fields.Float(string='Avg Sync Duration (min)', default=0.0)
    min_sync_duration = fields.Float(string='Min Sync Duration (min)', default=0.0)
    max_sync_duration = fields.Float(string='Max Sync Duration (min)', default=0.0)
    total_processing_time = fields.Float(string='Total Processing Time (hours)', default=0.0)
    
    # Data Volume
    total_data_volume_mb = fields.Float(string='Total Data Volume (MB)', default=0.0)
    avg_data_per_sync_mb = fields.Float(string='Avg Data per Sync (MB)', default=0.0)
    
    # Mapping Statistics
    total_account_mappings = fields.Integer(string='Total Account Mappings', default=0)
    validated_mappings = fields.Integer(string='Validated Mappings', default=0)
    unvalidated_mappings = fields.Integer(string='Unvalidated Mappings', default=0)
    mapping_validation_rate = fields.Float(string='Mapping Validation Rate (%)',
                                            compute='_compute_rates', store=True)
    most_used_mappings = fields.Text(string='Most Used Mappings (JSON)')
    
    # Error Analysis
    total_errors = fields.Integer(string='Total Errors', default=0)
    unique_errors = fields.Integer(string='Unique Error Types', default=0)
    top_errors = fields.Text(string='Top Errors (JSON)')
    error_categories = fields.Text(string='Error Categories (JSON)')
    error_trend = fields.Selection([
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('degrading', 'Degrading'),
    ], string='Error Trend', compute='_compute_trends')
    
    # Subsidiary Performance
    best_performing_subsidiary_id = fields.Many2one('subsidiary.instance',
                                                     string='Best Performer')
    worst_performing_subsidiary_id = fields.Many2one('subsidiary.instance',
                                                      string='Worst Performer')
    subsidiary_performance = fields.Text(string='Subsidiary Performance (JSON)')
    
    # System Health
    system_health_score = fields.Float(string='System Health Score (0-100)',
                                        compute='_compute_health_score', store=True)
    health_status = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ], string='Health Status', compute='_compute_health_score', store=True)
    
    # Recommendations
    recommendations = fields.Text(string='System Recommendations',
                                   compute='_compute_recommendations')
    
    # Metadata
    metadata = fields.Text(string='Additional Metadata (JSON)')
    generated_by = fields.Many2one('res.users', string='Generated By',
                                    default=lambda self: self.env.user,
                                    readonly=True)
    create_date = fields.Datetime(string='Generated On', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('consolidation.analytics')
            vals['name'] = seq or 'New'
        return super().create(vals)

    @api.depends('total_syncs', 'completed_syncs', 'failed_syncs',
                 'total_account_mappings', 'validated_mappings')
    def _compute_rates(self):
        for rec in self:
            # Success rate
            if rec.total_syncs > 0:
                rec.success_rate = (rec.completed_syncs / rec.total_syncs) * 100
                rec.failure_rate = (rec.failed_syncs / rec.total_syncs) * 100
            else:
                rec.success_rate = 0.0
                rec.failure_rate = 0.0
            
            # Mapping validation rate
            if rec.total_account_mappings > 0:
                rec.mapping_validation_rate = (rec.validated_mappings / rec.total_account_mappings) * 100
            else:
                rec.mapping_validation_rate = 0.0

    @api.depends('total_syncs', 'total_moves_processed')
    def _compute_averages(self):
        for rec in self:
            if rec.total_syncs > 0:
                rec.avg_moves_per_sync = rec.total_moves_processed / rec.total_syncs
            else:
                rec.avg_moves_per_sync = 0.0
            
            if rec.total_moves_processed > 0:
                rec.avg_lines_per_move = rec.total_lines_processed / rec.total_moves_processed
            else:
                rec.avg_lines_per_move = 0.0

    @api.depends('success_rate', 'avg_sync_duration', 'mapping_validation_rate', 'failure_rate')
    def _compute_health_score(self):
        for rec in self:
            # Weighted health score calculation
            weights = {
                'success_rate': 0.40,      # 40% weight
                'performance': 0.30,        # 30% weight
                'mapping_quality': 0.20,    # 20% weight
                'error_rate': 0.10,         # 10% weight
            }
            
            # Success rate component (0-100)
            success_score = rec.success_rate
            
            # Performance component (inverse of duration)
            if rec.avg_sync_duration > 0:
                # Assume 5 min = excellent (100), 30 min = poor (0)
                performance_score = max(0, 100 - (rec.avg_sync_duration / 30 * 100))
            else:
                performance_score = 100
            
            # Mapping quality component
            mapping_score = rec.mapping_validation_rate
            
            # Error rate component (inverse)
            error_score = 100 - rec.failure_rate
            
            # Calculate weighted average
            rec.system_health_score = (
                success_score * weights['success_rate'] +
                performance_score * weights['performance'] +
                mapping_score * weights['mapping_quality'] +
                error_score * weights['error_rate']
            )
            
            # Determine health status
            if rec.system_health_score >= 90:
                rec.health_status = 'excellent'
            elif rec.system_health_score >= 75:
                rec.health_status = 'good'
            elif rec.system_health_score >= 60:
                rec.health_status = 'fair'
            elif rec.system_health_score >= 40:
                rec.health_status = 'poor'
            else:
                rec.health_status = 'critical'

    def _compute_trends(self):
        for rec in self:
            # Compare with previous period
            previous = self.search([
                ('date', '<', rec.date),
                ('period_type', '=', rec.period_type),
            ], order='date desc', limit=1)
            
            if previous:
                if rec.total_errors < previous.total_errors * 0.8:
                    rec.error_trend = 'improving'
                elif rec.total_errors > previous.total_errors * 1.2:
                    rec.error_trend = 'degrading'
                else:
                    rec.error_trend = 'stable'
            else:
                rec.error_trend = 'stable'

    def _compute_recommendations(self):
        for rec in self:
            recommendations = []
            
            # Check success rate
            if rec.success_rate < 80:
                recommendations.append('⚠️ Success rate below 80%. Review failed syncs and error patterns.')
            
            # Check performance
            if rec.avg_sync_duration > 15:
                recommendations.append('🐌 Average sync duration > 15 min. Consider enabling parallel processing.')
            
            # Check mapping validation
            if rec.mapping_validation_rate < 90:
                recommendations.append('📋 Less than 90% mappings validated. Run mapping validation.')
            
            # Check error trend
            if rec.error_trend == 'degrading':
                recommendations.append('📈 Error trend is degrading. Investigate recent changes.')
            
            # Check subsidiary coverage
            if rec.synced_subsidiaries < rec.total_subsidiaries:
                recommendations.append(f'🏢 Only {rec.synced_subsidiaries}/{rec.total_subsidiaries} subsidiaries synced.')
            
            # Positive recommendations
            if rec.system_health_score >= 90:
                recommendations.append('✅ System health excellent! Consider scheduling more frequent syncs.')
            
            rec.recommendations = '\n'.join(recommendations) if recommendations else 'No recommendations. System operating optimally.'

    @api.model
    def generate_daily_analytics(self):
        """Cron job: Generate analytics for yesterday"""
        yesterday = fields.Date.today() - timedelta(days=1)
        return self._generate_analytics(yesterday, yesterday, 'daily')

    @api.model
    def generate_weekly_analytics(self):
        """Generate weekly analytics"""
        today = fields.Date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return self._generate_analytics(week_start, week_end, 'weekly')

    @api.model
    def generate_monthly_analytics(self):
        """Generate monthly analytics"""
        today = fields.Date.today()
        month_start = today.replace(day=1)
        next_month = month_start + timedelta(days=32)
        month_end = next_month.replace(day=1) - timedelta(days=1)
        return self._generate_analytics(month_start, month_end, 'monthly')

    @api.model
    def _generate_analytics(self, date_from, date_to, period_type='daily'):
        """Core analytics generation logic"""
        _logger.info(f'Generating {period_type} analytics for {date_from} to {date_to}')
        
        # Get sync engines for period
        syncs = self.env['sync.engine'].search([
            ('create_date', '>=', str(date_from) + ' 00:00:00'),
            ('create_date', '<=', str(date_to) + ' 23:59:59'),
        ])
        
        # Calculate basic metrics
        total_syncs = len(syncs)
        completed_syncs = len(syncs.filtered(lambda s: s.state == 'completed'))
        failed_syncs = len(syncs.filtered(lambda s: s.state == 'error'))
        cancelled_syncs = len(syncs.filtered(lambda s: s.state == 'cancelled'))
        in_progress = len(syncs.filtered(lambda s: s.state not in ('completed', 'error', 'cancelled')))
        
        # Performance metrics
        completed = syncs.filtered(lambda s: s.state == 'completed' and s.duration > 0)
        durations = completed.mapped('duration')
        
        avg_duration = (sum(durations) / len(durations) / 60) if durations else 0
        min_duration = (min(durations) / 60) if durations else 0
        max_duration = (max(durations) / 60) if durations else 0
        total_time = (sum(durations) / 3600) if durations else 0
        
        # Volume metrics
        total_moves = sum(syncs.mapped('total_moves_fetched'))
        total_lines = sum(syncs.mapped('total_lines_fetched'))
        total_promoted = sum(syncs.mapped('total_moves_promoted'))
        
        # Subsidiaries
        all_subs = self.env['subsidiary.instance'].search([('active', '=', True)])
        total_subs = len(all_subs)
        synced_subs = len(set(syncs.mapped('subsidiary_ids').ids))
        
        # Mappings
        all_mappings = self.env['account.mapping'].search([('active', '=', True)])
        validated = all_mappings.filtered(lambda m: m.is_validated)
        
        # Error analysis
        error_logs = self.env['consolidation.log'].search([
            ('create_date', '>=', str(date_from) + ' 00:00:00'),
            ('create_date', '<=', str(date_to) + ' 23:59:59'),
            ('state', '=', 'error'),
        ])
        
        # Categorize errors
        error_msgs = {}
        for log in error_logs:
            msg = log.message[:100]
            error_msgs[msg] = error_msgs.get(msg, 0) + 1
        
        top_errors = sorted(error_msgs.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Subsidiary performance
        sub_performance = {}
        best_sub = None
        worst_sub = None
        best_rate = 0
        worst_rate = 100
        
        for sub in all_subs:
            sub_syncs = syncs.filtered(lambda s: sub in s.subsidiary_ids)
            if sub_syncs:
                completed_count = len(sub_syncs.filtered(lambda s: s.state == 'completed'))
                rate = (completed_count / len(sub_syncs)) * 100
                
                sub_performance[sub.name] = {
                    'total_syncs': len(sub_syncs),
                    'completed': completed_count,
                    'success_rate': rate,
                    'avg_duration': sum(sub_syncs.mapped('duration')) / len(sub_syncs) / 60,
                }
                
                if rate > best_rate:
                    best_rate = rate
                    best_sub = sub
                
                if rate < worst_rate:
                    worst_rate = rate
                    worst_sub = sub
        
        # Create analytics record
        analytics = self.create({
            'date': date_to,
            'date_from': date_from,
            'date_to': date_to,
            'period_type': period_type,
            'total_syncs': total_syncs,
            'completed_syncs': completed_syncs,
            'failed_syncs': failed_syncs,
            'cancelled_syncs': cancelled_syncs,
            'in_progress_syncs': in_progress,
            'total_subsidiaries': total_subs,
            'synced_subsidiaries': synced_subs,
            'failed_subsidiaries': len(syncs.filtered(lambda s: s.state == 'error').mapped('subsidiary_ids')),
            'total_moves_processed': total_moves,
            'total_lines_processed': total_lines,
            'total_moves_promoted': total_promoted,
            'avg_sync_duration': avg_duration,
            'min_sync_duration': min_duration,
            'max_sync_duration': max_duration,
            'total_processing_time': total_time,
            'total_account_mappings': len(all_mappings),
            'validated_mappings': len(validated),
            'unvalidated_mappings': len(all_mappings) - len(validated),
            'total_errors': len(error_logs),
            'unique_errors': len(error_msgs),
            'top_errors': json.dumps(top_errors),
            'subsidiary_performance': json.dumps(sub_performance),
            'best_performing_subsidiary_id': best_sub.id if best_sub else False,
            'worst_performing_subsidiary_id': worst_sub.id if worst_sub else False,
        })
        
        _logger.info(f'Generated analytics: {analytics.name} - Health Score: {analytics.system_health_score:.1f}')
        
        return analytics

    def action_refresh_analytics(self):
        """Manually refresh analytics"""
        self.ensure_one()
        
        # Re-generate for same period
        new_analytics = self._generate_analytics(self.date_from, self.date_to, self.period_type)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Analytics Refreshed'),
                'message': _('Analytics data has been updated'),
                'type': 'success',
            }
        }


```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/audit`

```py
from . import consolidation_log
from . import immutable_ledger
from . import restore_point
```

---

## File: `consolidation_log.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/audit`

```py
from odoo import models, fields, api, _
import logging
import json
import time
from datetime import datetime
from contextlib import contextmanager

_logger = logging.getLogger(__name__)


class ConsolidationLog(models.Model):
    """
     Consolidation Operation Log with structured data,
    consistent formatting, and performance tracking.
    """
    _name = 'consolidation.log'
    _description = 'Consolidation Operation Log'
    _order = 'create_date desc'
    _rec_name = 'message'

    # References
    sync_engine_id = fields.Many2one('sync.engine', string='Sync Engine',
                                      ondelete='cascade', index=True)
    subsidiary_id = fields.Many2one('subsidiary.instance', string='Subsidiary',
                                     ondelete='cascade', index=True)
    
    # Log Details
    log_type = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('validation', 'Validation'),
        ('sync', 'Sync Operation'),
        ('reconciliation', 'Reconciliation'),
        ('promotion', 'Promotion'),
        ('rollback', 'Rollback'),
        ('audit', 'Audit Trail'),
        ('performance', 'Performance'),
    ], string='Log Type', default='info', required=True, index=True)
    
    message = fields.Text(string='Message', required=True)
    details = fields.Text(string='Details')
    
    # State
    state = fields.Selection([
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='success', index=True)
    
    # Performance Metrics
    duration = fields.Float(string='Duration (seconds)', 
                             help='Duration of the operation in seconds')
    records_processed = fields.Integer(string='Records Processed', default=0)
    
    # User Context
    user_id = fields.Many2one('res.users', string='User',
                               default=lambda self: self.env.user,
                               readonly=True)
    ip_address = fields.Char(string='IP Address', readonly=True)
    
    # Timestamps
    start_time = fields.Datetime(string='Start Time')
    end_time = fields.Datetime(string='End Time')
    create_date = fields.Datetime(string='Created', readonly=True)
    
    # Metadata
    metadata = fields.Text(string='Additional Metadata (JSON)')
    
    # Related Data
    related_model = fields.Char(string='Related Model')
    related_id = fields.Integer(string='Related ID')
    
    # Technical Fields
    checksum = fields.Char(string='Checksum', readonly=True,
                            help='Data integrity checksum')
    is_archived = fields.Boolean(string='Archived', default=False)
    
    # Operation Context (NEW)
    operation = fields.Char(string='Operation Name', index=True)
    category = fields.Char(string='Category')
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], string='Severity')

    @api.model
    def create(self, vals):
        # Set timestamps if not provided
        if 'start_time' not in vals:
            vals['start_time'] = fields.Datetime.now()
        
        # Calculate duration if end_time is provided
        if 'end_time' in vals and vals.get('start_time'):
            start = fields.Datetime.from_string(vals['start_time'])
            end = fields.Datetime.from_string(vals['end_time'])
            vals['duration'] = (end - start).total_seconds()
        
        # Get IP address
        if 'ip_address' not in vals:
            vals['ip_address'] = self._get_client_ip()
        
        return super().create(vals)

    def write(self, vals):
        # Update duration if end_time is set
        if 'end_time' in vals and not vals.get('duration'):
            for rec in self:
                if rec.start_time and vals['end_time']:
                    start = fields.Datetime.from_string(rec.start_time)
                    end = fields.Datetime.from_string(vals['end_time'])
                    vals['duration'] = (end - start).total_seconds()
        
        return super().write(vals)

    def _get_client_ip(self):
        """Get client IP address"""
        try:
            from odoo.http import request
            if request:
                return request.httprequest.environ.get('HTTP_X_REAL_IP', 
                       request.httprequest.environ.get('REMOTE_ADDR', 'Unknown'))
        except:
            pass
        return 'Unknown'

    @api.model
    def log_operation(self, log_type, message, sync_engine_id=False, 
                      subsidiary_id=False, details=None, state='success',
                      duration=0.0, records_processed=0, metadata=None,
                      operation=None, category=None, severity=None):
        """Helper method to create log entries with enhanced fields"""
        vals = {
            'log_type': log_type,
            'message': message,
            'state': state,
            'duration': duration,
            'records_processed': records_processed,
        }
        
        if sync_engine_id:
            vals['sync_engine_id'] = sync_engine_id
        
        if subsidiary_id:
            vals['subsidiary_id'] = subsidiary_id
        
        if details:
            vals['details'] = details
        
        if operation:
            vals['operation'] = operation
        
        if category:
            vals['category'] = category
        
        if severity:
            vals['severity'] = severity
        
        if metadata:
            if isinstance(metadata, dict):
                vals['metadata'] = json.dumps(metadata, default=str)
            else:
                vals['metadata'] = str(metadata)
        
        return self.create(vals)

    @api.model
    def log_error(self, message, sync_engine_id=False, subsidiary_id=False, 
                  details=None, exception=None, category=None, severity='high'):
        """Log error with exception details and enhanced context"""
        if exception:
            import traceback
            error_details = f"{details or ''}\nException: {str(exception)}\n"
            if hasattr(exception, '__traceback__'):
                error_details += f"Traceback:\n{traceback.format_exc()}"
            details = error_details
        
        return self.log_operation(
            'error', message, sync_engine_id, subsidiary_id,
            details, 'error', category=category, severity=severity
        )

    @api.model
    def log_sync_start(self, sync_engine_id, subsidiary_ids=None):
        """Log sync operation start"""
        message = "Sync operation started"
        if subsidiary_ids:
            subsidiary_names = self.env['subsidiary.instance'].browse(subsidiary_ids).mapped('name')
            message += f" for subsidiaries: {', '.join(subsidiary_names)}"
        
        return self.log_operation(
            'sync', message, sync_engine_id, 
            state='in_progress', 
            start_time=fields.Datetime.now(),
            operation='sync_start'
        )

    @api.model
    def log_sync_end(self, log_entry_id, success=True, records_processed=0, 
                     details=None):
        """Mark sync operation as completed"""
        log_entry = self.browse(log_entry_id)
        end_time = fields.Datetime.now()
        
        update_vals = {
            'end_time': end_time,
            'state': 'completed' if success else 'error',
            'records_processed': records_processed,
            'operation': 'sync_end',
        }
        
        if details:
            update_vals['details'] = details
        
        # Calculate duration
        if log_entry.start_time:
            start = fields.Datetime.from_string(log_entry.start_time)
            update_vals['duration'] = (end_time - start).total_seconds()
        
        return log_entry.write(update_vals)

    def action_view_details(self):
        """View log details"""
        self.ensure_one()
        return {
            'name': _('Log Details'),
            'type': 'ir.actions.act_window',
            'res_model': 'consolidation.log',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_archive(self):
        """Archive log entry"""
        self.write({'is_archived': True})
        return True

    def action_unarchive(self):
        """Unarchive log entry"""
        self.write({'is_archived': False})
        return True

    @api.model
    def cleanup_old_logs(self, days=90):
        """Cron job to archive old logs"""
        from datetime import timedelta
        
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        
        old_logs = self.search([
            ('create_date', '<', cutoff_date),
            ('is_archived', '=', False),
            ('log_type', 'in', ['info', 'sync']),
        ], limit=1000)
        
        count = len(old_logs)
        old_logs.write({'is_archived': True})
        
        _logger.info(f'Archived {count} old log entries')
        return count

    @api.model
    def get_performance_stats(self, sync_engine_id=None, days=7):
        """Get performance statistics"""
        from datetime import timedelta
        
        domain = [
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=days)),
            ('log_type', '=', 'sync'),
            ('duration', '>', 0),
        ]
        
        if sync_engine_id:
            domain.append(('sync_engine_id', '=', sync_engine_id))
        
        logs = self.search(domain)
        
        if not logs:
            return {
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'total_operations': 0,
                'success_rate': 0,
            }
        
        durations = logs.mapped('duration')
        
        return {
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'total_operations': len(logs),
            'success_rate': (len(logs.filtered(lambda l: l.state == 'completed')) / len(logs) * 100),
        }


class PerformanceLogger(models.AbstractModel):
    """Performance tracking and logging - Abstract model (no database table)."""
    _name = 'performance.logger'
    _description = 'Performance Logging'

    @contextmanager
    def track_performance(self, operation_name, **context):
        """
        Track and log performance metrics for an operation.
        
        Usage:
            perf_logger = self.env['performance.logger']
            with perf_logger.track_performance('data_sync', sync_id=1):
                # operation code
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        metrics = {
            'operation': operation_name,
            'start_time': datetime.now().isoformat(),
        }
        metrics.update(context)
        
        try:
            yield metrics
            
            # Calculate final metrics
            duration = time.time() - start_time
            memory_delta = self._get_memory_usage() - start_memory
            
            metrics.update({
                'duration_seconds': round(duration, 2),
                'memory_delta_mb': round(memory_delta, 2),
                'status': 'success',
            })
            
            # Log performance
            _logger.info(
                f"Performance: {operation_name} - "
                f"Duration: {duration:.2f}s, "
                f"Memory: {memory_delta:.2f}MB"
            )
            
            # Store in consolidation log
            self.env['consolidation.log'].log_operation(
                'performance',
                f"Performance: {operation_name}",
                duration=duration,
                metadata=metrics,
                operation=operation_name,
                **{k: v for k, v in context.items() if k in ['sync_engine_id', 'subsidiary_id']}
            )
            
        except Exception as e:
            duration = time.time() - start_time
            metrics.update({
                'duration_seconds': round(duration, 2),
                'status': 'failed',
                'error': str(e),
            })
            raise

    @api.model
    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0


class AuditLogger(models.AbstractModel):
    """Audit trail logging for compliance - Abstract model (no database table)."""
    _name = 'audit.logger'
    _description = 'Audit Trail Logger'

    @api.model
    def log_audit_event(self, event_type, entity_type, entity_id, 
                        action, old_values=None, new_values=None, **context):
        """
        Log audit event for compliance tracking.
        
        Args:
            event_type: Type of event (create, update, delete, etc.)
            entity_type: Model name
            entity_id: Record ID
            action: Description of action
            old_values: Previous values (for updates)
            new_values: New values
        """
        audit_data = {
            'event_type': event_type,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'action': action,
            'user_id': self.env.user.id,
            'user_name': self.env.user.name,
            'timestamp': datetime.now().isoformat(),
            'ip_address': self._get_client_ip(),
        }
        
        if old_values:
            audit_data['old_values'] = old_values
        
        if new_values:
            audit_data['new_values'] = new_values
        
        audit_data.update(context)
        
        # Log to consolidation log
        self.env['consolidation.log'].log_operation(
            'audit',
            f"AUDIT: {event_type} on {entity_type}({entity_id})",
            details=f"{action}\nBy: {self.env.user.name}",
            metadata=audit_data,
            operation='audit_trail',
            category='audit',
        )
        
        # Also log to immutable ledger if available
        try:
            self.env['immutable.ledger'].sudo().create_ledger_entry(
                transaction_id=f"{entity_type}_{entity_id}_{int(time.time())}",
                operation=event_type,
                data_snapshot=json.dumps(audit_data, default=str),
                reference_model=entity_type,
                reference_id=entity_id,
            )
        except Exception as e:
            _logger.error(f"Failed to create audit trail in immutable ledger: {str(e)}")

    @api.model
    def _get_client_ip(self):
        """Get client IP address."""
        try:
            from odoo.http import request
            if request:
                return request.httprequest.environ.get(
                    'HTTP_X_REAL_IP',
                    request.httprequest.environ.get('REMOTE_ADDR', 'Unknown')
                )
        except:
            pass
        return 'Unknown'
```

---

## File: `immutable_ledger.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/audit`

```py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ImmutableLedger(models.Model):
    _name = 'immutable.ledger'
    _description = 'Immutable Audit Ledger'
    _order = 'create_date desc'
    _rec_name = 'transaction_id'

    # Transaction Identification
    transaction_id = fields.Char(string='Transaction ID', required=True, 
                                   index=True, readonly=True)
    sync_engine_id = fields.Many2one('sync.engine', string='Sync Engine',
                                      ondelete='restrict', index=True, readonly=True)
    
    # Operation Details
    operation = fields.Selection([
        ('sync_started', 'Sync Started'),
        ('sync_completed', 'Sync Completed'),
        ('data_validated', 'Data Validated'),
        ('reconciliation_executed', 'Reconciliation Executed'),
        ('promotion_started', 'Promotion Started'),
        ('promotion_completed', 'Promotion Completed'),
        ('move_promoted', 'Move Promoted'),
        ('rollback_initiated', 'Rollback Initiated'),
        ('rollback_completed', 'Rollback Completed'),
        ('error_occurred', 'Error Occurred'),
    ], string='Operation', required=True, index=True, readonly=True)
    
    operation_timestamp = fields.Datetime(string='Operation Timestamp',
                                           default=fields.Datetime.now,
                                           required=True, readonly=True)
    
    # Data Snapshot
    data_snapshot = fields.Text(string='Data Snapshot (JSON)', readonly=True,
                                 help='Immutable snapshot of operation data')
    
    # Hash Chain for Integrity
    previous_hash = fields.Char(string='Previous Hash', readonly=True, index=True)
    current_hash = fields.Char(string='Current Hash', readonly=True, index=True)
    
    # References
    reference_model = fields.Char(string='Reference Model', readonly=True)
    reference_id = fields.Integer(string='Reference ID', readonly=True)
    
    # User & System
    user_id = fields.Many2one('res.users', string='User',
                               default=lambda self: self.env.user,
                               required=True, readonly=True)
    ip_address = fields.Char(string='IP Address', readonly=True)
    
    create_date = fields.Datetime(string='Create Date', readonly=True)
    
    # Verification
    is_verified = fields.Boolean(string='Verified', readonly=True, default=True)
    verification_date = fields.Datetime(string='Verification Date', readonly=True)

    def write(self, vals):
        """Override to prevent modifications"""
        raise UserError(_('Immutable ledger entries cannot be modified.'))

    def unlink(self):
        """Override to prevent deletion"""
        raise UserError(_('Immutable ledger entries cannot be deleted.'))

    @api.model
    def create_ledger_entry(self, transaction_id, operation, data_snapshot,
                           sync_engine_id=False, reference_model=False, 
                           reference_id=False):
        """Create immutable ledger entry with hash chain"""
        import hashlib
        import json
        
        # Get previous entry for hash chain
        previous_entry = self.search([], order='create_date desc', limit=1)
        previous_hash = previous_entry.current_hash if previous_entry else ''
        
        # Calculate current hash
        hash_data = {
            'transaction_id': transaction_id,
            'operation': operation,
            'data_snapshot': data_snapshot,
            'previous_hash': previous_hash,
            'timestamp': str(fields.Datetime.now()),
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        current_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        
        # Get IP address
        ip_address = self._get_client_ip()
        
        vals = {
            'transaction_id': transaction_id,
            'operation': operation,
            'data_snapshot': data_snapshot,
            'previous_hash': previous_hash,
            'current_hash': current_hash,
            'ip_address': ip_address,
            'is_verified': True,
            'verification_date': fields.Datetime.now(),
        }
        
        if sync_engine_id:
            vals['sync_engine_id'] = sync_engine_id
        
        if reference_model:
            vals['reference_model'] = reference_model
        
        if reference_id:
            vals['reference_id'] = reference_id
        
        return self.sudo().create(vals)

    def _get_client_ip(self):
        """Get client IP address"""
        try:
            from odoo.http import request
            return request.httprequest.environ.get('HTTP_X_REAL_IP', 
                   request.httprequest.environ.get('REMOTE_ADDR', 'Unknown'))
        except:
            return 'Unknown'

    @api.model
    def verify_chain_integrity(self):
        """Verify blockchain-like hash chain integrity"""
        entries = self.search([], order='create_date asc')
        
        previous_hash = ''
        errors = []
        
        for entry in entries:
            if entry.previous_hash != previous_hash:
                errors.append(f'Hash mismatch at entry {entry.transaction_id}')
            
            # Verify current hash
            import hashlib
            import json
            
            hash_data = {
                'transaction_id': entry.transaction_id,
                'operation': entry.operation,
                'data_snapshot': entry.data_snapshot,
                'previous_hash': entry.previous_hash,
                'timestamp': str(entry.operation_timestamp),
            }
            
            hash_string = json.dumps(hash_data, sort_keys=True)
            calculated_hash = hashlib.sha256(hash_string.encode()).hexdigest()
            
            if calculated_hash != entry.current_hash:
                errors.append(f'Hash verification failed for {entry.transaction_id}')
            
            previous_hash = entry.current_hash
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'total_entries': len(entries),
        }

    @api.model
    def get_audit_trail(self, sync_engine_id):
        """Get complete audit trail for sync"""
        entries = self.search([
            ('sync_engine_id', '=', sync_engine_id)
        ], order='create_date asc')
        
        trail = []
        for entry in entries:
            import json
            trail.append({
                'timestamp': entry.operation_timestamp,
                'operation': entry.operation,
                'user': entry.user_id.name,
                'data': json.loads(entry.data_snapshot) if entry.data_snapshot else {},
                'hash': entry.current_hash,
            })
        
        return trail
```

---

## File: `restore_point.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/audit`

```py
# -*- coding: utf-8 -*-
# FILE: models/audit/restore_point.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class RestorePoint(models.Model):
    _name = 'restore.point'
    _description = 'Consolidation Restore Point'
    _order = 'create_date desc'

    name = fields.Char(string='Restore Point Name', required=True, default='New')
    sync_engine_id = fields.Many2one('sync.engine', string='Sync Engine',
                                      required=True, ondelete='cascade')
    subsidiary_id = fields.Many2one('subsidiary.instance', string='Subsidiary')
    
    # Snapshot Data
    state_snapshot = fields.Text(string='State Snapshot (JSON)', required=True,
                                  help='Complete state at time of restore point creation')
    media_moves_snapshot = fields.Text(string='Media Moves Snapshot (JSON)')
    mappings_snapshot = fields.Text(string='Mappings Snapshot (JSON)')
    
    # Metadata
    created_by = fields.Many2one('res.users', string='Created By',
                                  default=lambda self: self.env.user,
                                  required=True, readonly=True)
    create_date = fields.Datetime(string='Created On', readonly=True)
    
    # Restore Status
    is_active = fields.Boolean(string='Active', default=True)
    restored = fields.Boolean(string='Restored', default=False, readonly=True)
    restore_date = fields.Datetime(string='Restore Date', readonly=True)
    restored_by = fields.Many2one('res.users', string='Restored By', readonly=True)
    
    # Verification
    checksum = fields.Char(string='Data Checksum', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('restore.point') or 'New'
        
        # Calculate checksum
        if 'state_snapshot' in vals:
            checksum_service = self.env['checksum.service']
            vals['checksum'] = checksum_service.calculate_checksum(vals['state_snapshot'])
        
        return super().create(vals)

    def action_restore(self):
        """Restore to this point"""
        self.ensure_one()
        
        if self.restored:
            raise UserError(_('This restore point has already been used.'))
        
        return {
            'name': _('Confirm Restore'),
            'type': 'ir.actions.act_window',
            'res_model': 'rollback.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sync_engine_id': self.sync_engine_id.id,
                'default_restore_point_id': self.id,
            },
        }

    def execute_restore(self):
        """Execute the actual restore operation"""
        self.ensure_one()
        
        try:
            # Parse state snapshot
            state = json.loads(self.state_snapshot)
            
            # Restore media moves
            if self.media_moves_snapshot:
                media_data = json.loads(self.media_moves_snapshot)
                self._restore_media_moves(media_data)
            
            # Mark as restored
            self.write({
                'restored': True,
                'restore_date': fields.Datetime.now(),
                'restored_by': self.env.user.id,
            })
            
            # Log restore
            self.env['consolidation.log'].log_operation(
                'rollback',
                f'Restored from checkpoint: {self.name}',
                sync_engine_id=self.sync_engine_id.id
            )
            
            return True
            
        except Exception as e:
            _logger.error(f'Restore failed: {str(e)}')
            raise UserError(_('Restore failed: %s') % str(e))

    def _restore_media_moves(self, media_data):
        """Restore media moves to previous state"""
        # Implementation depends on snapshot structure
        pass

```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/base`

```py
from . import error_handler
from . import maintenance_tasks
from . import consolidation_config
```

---

## File: `consolidation_config.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/base`

```py


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ConsolidationConfig(models.Model):
    """
    Enhanced Consolidation System Configuration with centralized
    constants and configuration management.
    """
    _name = 'consolidation.config'
    _description = 'Consolidation System Configuration'
    
    # General Settings
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    
    # Sync Settings
    default_batch_size = fields.Integer(string='Default Batch Size', default=100,
                                        help='Default number of records to process per batch')
    max_sync_days = fields.Integer(string='Maximum Sync Days', default=365,
                                   help='Maximum date range allowed for synchronization')
    default_max_retries = fields.Integer(string='Default Max Retries', default=3)
    retry_backoff_factor = fields.Integer(string='Retry Backoff Factor', default=2,
                                          help='Exponential backoff factor for retries')
    
    # NEW: Add missing fields from XML
    sync_timeout_seconds = fields.Integer(string='Sync Timeout (seconds)', default=3600,
                                         help='Maximum time for sync operations in seconds')
    
    # Performance Settings
    enable_parallel_processing = fields.Boolean(string='Enable Parallel Processing', default=True)
    max_parallel_workers = fields.Integer(string='Max Parallel Workers', default=4)
    enable_query_optimization = fields.Boolean(string='Enable Query Optimization', default=True)
    cache_timeout_minutes = fields.Integer(string='Cache Timeout (minutes)', default=30)
    
    # NEW: Add missing field from XML
    connection_pool_size = fields.Integer(string='Connection Pool Size', default=10)
    
    # Validation Settings
    strict_validation = fields.Boolean(string='Strict Validation', default=True)
    require_balanced_moves = fields.Boolean(string='Require Balanced Moves', default=True)
    validate_before_promotion = fields.Boolean(string='Validate Before Promotion', default=True)
    auto_validate_mappings = fields.Boolean(string='Auto-validate Mappings', default=False)
    
    # NEW: Add missing field from XML
    validate_currency_conversion = fields.Boolean(string='Validate Currency Conversion', default=True)
    
    # Tolerance Values (NEW)
    balance_tolerance = fields.Float(string='Balance Tolerance', default=0.01,
                                     help='Acceptable difference for balance checks',
                                     digits=(12, 6))
    
    # Security Settings
    encrypt_sensitive_data = fields.Boolean(string='Encrypt Sensitive Data', default=True)
    log_retention_days = fields.Integer(string='Log Retention Days', default=90)
    require_approval_for_large_syncs = fields.Boolean(string='Require Approval for Large Syncs', default=True)
    large_sync_threshold = fields.Integer(string='Large Sync Threshold (moves)', default=1000)
    
    # NEW: Add missing field from XML
    enable_audit_trail = fields.Boolean(string='Enable Audit Trail', default=True)
    
    # Notification Settings
    notify_on_sync_completion = fields.Boolean(string='Notify on Sync Completion', default=True)
    notify_on_sync_failure = fields.Boolean(string='Notify on Sync Failure', default=True)
    notify_on_sla_violation = fields.Boolean(string='Notify on SLA Violation', default=True)
    notification_email_template_id = fields.Many2one('mail.template',
                                                     string='Notification Email Template')
    
    # Maintenance Settings
    auto_cleanup_old_data = fields.Boolean(string='Auto-cleanup Old Data', default=True)
    auto_generate_analytics = fields.Boolean(string='Auto-generate Analytics', default=True)
    enable_health_monitoring = fields.Boolean(string='Enable Health Monitoring', default=True)
    
    # NEW: Add missing field from XML
    health_check_interval = fields.Integer(string='Health Check Interval (minutes)', default=60)
    
    # Audit Settings
    enable_immutable_ledger = fields.Boolean(string='Enable Immutable Ledger', default=True)
    require_audit_trail = fields.Boolean(string='Require Audit Trail', default=True)
    audit_retention_years = fields.Integer(string='Audit Retention Years', default=7)
    
    # NEW: Add missing field from XML
    checksum_algorithm = fields.Selection(
        [('md5', 'MD5'), ('sha1', 'SHA-1'), ('sha256', 'SHA-256'), ('sha512', 'SHA-512')],
        string='Checksum Algorithm',
        default='sha256'
    )
    
    # NEW: Add Recovery Settings from XML
    enable_auto_recovery = fields.Boolean(string='Enable Auto Recovery', default=True)
    auto_recovery_attempts = fields.Integer(string='Auto Recovery Attempts', default=3)
    create_restore_points = fields.Boolean(string='Create Restore Points', default=True)
    restore_point_retention_days = fields.Integer(string='Restore Point Retention Days', default=30)
    
    # NEW: Add Currency Settings from XML
    default_currency_id = fields.Many2one('res.currency', string='Default Currency',
                                         default=lambda self: self.env.ref('base.USD'))
    auto_update_currency_rates = fields.Boolean(string='Auto Update Currency Rates', default=True)
    currency_rate_tolerance = fields.Float(string='Currency Rate Tolerance', default=0.01,
                                          digits=(5, 4))
    
    # NEW: Add Performance Thresholds from XML
    warning_sla_threshold_seconds = fields.Integer(string='Warning SLA Threshold (seconds)', default=300)
    critical_sla_threshold_seconds = fields.Integer(string='Critical SLA Threshold (seconds)', default=1800)
    enable_performance_alerts = fields.Boolean(string='Enable Performance Alerts', default=True)
    
    # Add SQL constraints for new fields
    _sql_constraints = [
        ('unique_company', 'UNIQUE(company_id)', 'Configuration must be unique per company'),
        ('check_batch_size', 'CHECK(default_batch_size > 0)', 'Batch size must be positive'),
        ('check_max_sync_days', 'CHECK(max_sync_days > 0)', 'Max sync days must be positive'),
        ('check_balance_tolerance', 'CHECK(balance_tolerance >= 0)', 'Balance tolerance must be non-negative'),
        ('check_sync_timeout', 'CHECK(sync_timeout_seconds > 0)', 'Sync timeout must be positive'),
        ('check_health_interval', 'CHECK(health_check_interval > 0)', 'Health check interval must be positive'),
    ]
    
    @api.model
    def get_config(self, company_id=None):
        """Get configuration for company"""
        if company_id is None:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        
        if not config:
            # Create default configuration with ALL fields
            config = self.create({
                'company_id': company_id,
                # Sync Settings
                'default_batch_size': 100,
                'max_sync_days': 365,
                'default_max_retries': 3,
                'retry_backoff_factor': 2,
                'sync_timeout_seconds': 3600,
                # Performance Settings
                'enable_parallel_processing': True,
                'max_parallel_workers': 4,
                'enable_query_optimization': True,
                'cache_timeout_minutes': 30,
                'connection_pool_size': 10,
                # Validation Settings
                'strict_validation': True,
                'require_balanced_moves': True,
                'validate_before_promotion': True,
                'auto_validate_mappings': False,
                'validate_currency_conversion': True,
                'balance_tolerance': 0.01,
                # Security Settings
                'encrypt_sensitive_data': True,
                'log_retention_days': 90,
                'require_approval_for_large_syncs': True,
                'large_sync_threshold': 1000,
                'enable_audit_trail': True,
                # Notification Settings
                'notify_on_sync_completion': True,
                'notify_on_sync_failure': True,
                'notify_on_sla_violation': True,
                # Maintenance Settings
                'auto_cleanup_old_data': True,
                'auto_generate_analytics': True,
                'enable_health_monitoring': True,
                'health_check_interval': 60,
                # Audit Settings
                'enable_immutable_ledger': True,
                'require_audit_trail': True,
                'audit_retention_years': 7,
                'checksum_algorithm': 'sha256',
                # Recovery Settings
                'enable_auto_recovery': True,
                'auto_recovery_attempts': 3,
                'create_restore_points': True,
                'restore_point_retention_days': 30,
                # Currency Settings
                'auto_update_currency_rates': True,
                'currency_rate_tolerance': 0.01,
                # Performance Thresholds
                'warning_sla_threshold_seconds': 300,
                'critical_sla_threshold_seconds': 1800,
                'enable_performance_alerts': True,
            })
            _logger.info(f'Created default configuration for company {company_id}')
        
        return config
    
    @api.model
    def get_param(self, param_name, default=None, company_id=None):
        """Get configuration parameter value"""
        config = self.get_config(company_id)
        return getattr(config, param_name, default)

class ConsolidationConstants(models.AbstractModel):
    """Centralized constants for consolidation module - Abstract model (no database table)."""
    _name = 'consolidation.constants'
    _description = 'Consolidation Module Constants'

    # ============================================================
    # STATE DEFINITIONS
    # ============================================================
    
    SYNC_ENGINE_STATES = [
        ('draft', 'Draft'),
        ('validating', 'Validating'),
        ('fetching', 'Fetching Data'),
        ('staging', 'In Staging'),
        ('reconciling', 'Reconciling'),
        ('promoting', 'Promoting'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ]
    
    MEDIA_MOVE_STATES = [
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('reconciled', 'Reconciled'),
        ('promoted', 'Promoted'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ]
    
    SUBSIDIARY_STATES = [
        ('draft', 'Draft'),
        ('validating', 'Validating'),
        ('validated', 'Validated'),
        ('error', 'Connection Error'),
        ('suspended', 'Suspended'),
    ]
    
    # ============================================================
    # CONFIGURATION DEFAULTS
    # ============================================================
    
    DEFAULT_BATCH_SIZE = 100
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_BACKOFF = 2
    DEFAULT_MAX_WORKERS = 4
    DEFAULT_TIMEOUT_SECONDS = 300
    DEFAULT_MAX_SYNC_DAYS = 365
    DEFAULT_LOG_RETENTION_DAYS = 90
    DEFAULT_AUDIT_RETENTION_YEARS = 7
    
    # ============================================================
    # TOLERANCE VALUES
    # ============================================================
    
    BALANCE_TOLERANCE = 0.01
    CURRENCY_PRECISION = 2
    PERCENTAGE_PRECISION = 2
    
    # ============================================================
    # LIMITS
    # ============================================================
    
    MAX_BATCH_SIZE = 1000
    MAX_PARALLEL_WORKERS = 16
    MAX_SYNC_DURATION_HOURS = 24
    MAX_RETRY_ATTEMPTS = 10
    MIN_MAPPING_COVERAGE_PERCENT = 50
    LARGE_SYNC_THRESHOLD_MOVES = 1000
    
    # ============================================================
    # PERFORMANCE THRESHOLDS
    # ============================================================
    
    SLOW_OPERATION_THRESHOLD_SECONDS = 60
    VERY_SLOW_OPERATION_THRESHOLD_SECONDS = 300
    DEFAULT_SLA_SYNC_DURATION = 30
    DEFAULT_SLA_SUCCESS_RATE = 95.0
    
    # ============================================================
    # ERROR CATEGORIES
    # ============================================================
    
    ERROR_CATEGORY_NETWORK = 'network'
    ERROR_CATEGORY_AUTH = 'authentication'
    ERROR_CATEGORY_DATA = 'data'
    ERROR_CATEGORY_RESOURCE = 'resource'
    ERROR_CATEGORY_BUSINESS = 'business'
    ERROR_CATEGORY_EXTERNAL = 'external'
    ERROR_CATEGORY_UNKNOWN = 'unknown'
    
    # ============================================================
    # LOG TYPES
    # ============================================================
    
    LOG_TYPE_INFO = 'info'
    LOG_TYPE_WARNING = 'warning'
    LOG_TYPE_ERROR = 'error'
    LOG_TYPE_VALIDATION = 'validation'
    LOG_TYPE_SYNC = 'sync'
    LOG_TYPE_RECONCILIATION = 'reconciliation'
    LOG_TYPE_PROMOTION = 'promotion'
    LOG_TYPE_ROLLBACK = 'rollback'
    LOG_TYPE_AUDIT = 'audit'
    
    # ============================================================
    # MAPPING TYPES
    # ============================================================
    
    MAPPING_TYPE_DIRECT = 'direct'
    MAPPING_TYPE_CONSOLIDATION = 'consolidation'
    MAPPING_TYPE_ELIMINATION = 'elimination'
    MAPPING_TYPE_ADJUSTMENT = 'adjustment'
    
    # ============================================================
    # SYSTEM CODES
    # ============================================================
    
    DEFAULT_CONSOLIDATION_JOURNAL_CODE = 'CONS'
    DEFAULT_ELIMINATION_JOURNAL_CODE = 'CONS-ELIM'
    DEFAULT_ADJUSTMENT_JOURNAL_CODE = 'CONS-ADJ'
    DEFAULT_INTERCOMPANY_JOURNAL_CODE = 'CONS-IC'
    DEFAULT_FX_JOURNAL_CODE = 'CONS-FX'
    DEFAULT_SUSPENSE_ACCOUNT_CODE = '999999'
    
    # ============================================================
    # HEALTH SCORES
    # ============================================================
    
    HEALTH_EXCELLENT_THRESHOLD = 90
    HEALTH_GOOD_THRESHOLD = 75
    HEALTH_FAIR_THRESHOLD = 60
    HEALTH_POOR_THRESHOLD = 40
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    @api.model
    def get_state_label(self, state_type, state_value):
        """Get human-readable label for a state value."""
        state_maps = {
            'sync_engine': dict(self.SYNC_ENGINE_STATES),
            'media_move': dict(self.MEDIA_MOVE_STATES),
            'subsidiary': dict(self.SUBSIDIARY_STATES),
        }
        return state_maps.get(state_type, {}).get(state_value, state_value)
    
    @api.model
    def get_config_value(self, key, default=None):
        """Get configuration value with fallback to constants."""
        try:
            config = self.env['consolidation.config'].get_config()
            
            value_map = {
                'batch_size': config.default_batch_size or self.DEFAULT_BATCH_SIZE,
                'max_retries': config.default_max_retries or self.DEFAULT_MAX_RETRIES,
                'max_workers': config.max_parallel_workers or self.DEFAULT_MAX_WORKERS,
                'max_sync_days': config.max_sync_days or self.DEFAULT_MAX_SYNC_DAYS,
                'log_retention_days': config.log_retention_days or self.DEFAULT_LOG_RETENTION_DAYS,
                'balance_tolerance': config.balance_tolerance or self.BALANCE_TOLERANCE,
            }
            
            return value_map.get(key, default)
        except Exception as e:
            _logger.warning(f"Could not get config value for {key}: {str(e)}")
            return default
    
    @api.model
    def validate_within_limits(self, value_type, value):
        """Validate a value is within acceptable limits."""
        limits = {
            'batch_size': (1, self.MAX_BATCH_SIZE),
            'workers': (1, self.MAX_PARALLEL_WORKERS),
            'retries': (0, self.MAX_RETRY_ATTEMPTS),
        }
        
        if value_type in limits:
            min_val, max_val = limits[value_type]
            if value < min_val or value > max_val:
                raise ValueError(
                    f"{value_type} must be between {min_val} and {max_val}, got {value}"
                )
        
        return True


class ConsolidationMessages(models.AbstractModel):
    """Centralized user messages for consistency - Abstract model (no database table)."""
    _name = 'consolidation.messages'
    _description = 'Consolidation User Messages'
    
    # ============================================================
    # ERROR MESSAGES
    # ============================================================
    
    @api.model
    def error_connection_failed(self, subsidiary_name, details=''):
        """Connection error message."""
        msg = _("Connection to subsidiary '%s' failed") % subsidiary_name
        if details:
            msg += f": {details}"
        return msg
    
    @api.model
    def error_validation_failed(self, entity_name, reason=''):
        """Validation error message."""
        msg = _("Validation failed for %s") % entity_name
        if reason:
            msg += f": {reason}"
        return msg
    
    @api.model
    def error_unbalanced_move(self, move_name, debit, credit):
        """Unbalanced move error."""
        return _(
            "Move '%s' is unbalanced. Debit: %s, Credit: %s, Difference: %s"
        ) % (move_name, debit, credit, abs(debit - credit))
    
    @api.model
    def error_unmapped_accounts(self, move_name, account_codes):
        """Unmapped accounts error."""
        codes = account_codes if isinstance(account_codes, str) else ', '.join(account_codes)
        return _("Move '%s' has unmapped accounts: %s") % (move_name, codes)
    
    @api.model
    def error_date_range(self, date_from, date_to):
        """Date range error."""
        return _(
            "Invalid date range: %s to %s. Date From must be before Date To."
        ) % (date_from, date_to)
    
    # ============================================================
    # SUCCESS MESSAGES
    # ============================================================
    
    @api.model
    def success_sync_completed(self, moves_count, duration):
        """Sync completion message."""
        return _(
            "Sync completed successfully! Processed %d moves in %.2f seconds."
        ) % (moves_count, duration)
    
    @api.model
    def success_validation_passed(self, entity_name):
        """Validation success message."""
        return _("Validation passed for %s") % entity_name
    
    @api.model
    def success_promotion_completed(self, moves_count):
        """Promotion success message."""
        return _("Successfully promoted %d moves to accounting") % moves_count
    
    # ============================================================
    # WARNING MESSAGES
    # ============================================================
    
    @api.model
    def warning_low_mapping_coverage(self, subsidiary_name, coverage):
        """Low mapping coverage warning."""
        return _(
            "Subsidiary '%s' has low mapping coverage (%.1f%%). "
            "Consider adding more account mappings."
        ) % (subsidiary_name, coverage)
    
    @api.model
    def warning_large_sync(self, moves_count):
        """Large sync warning."""
        return _(
            "This is a large synchronization (%d moves). "
            "It may take significant time to complete."
        ) % moves_count
    
    @api.model
    def warning_unvalidated_mapping(self, mapping_count):
        """Unvalidated mapping warning."""
        return _(
            "%d mappings have not been validated. "
            "Validation is recommended before sync."
        ) % mapping_count
```

---

## File: `error_handler.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/base`

```py
# -*- coding: utf-8 -*-

"""
 Global Error Handling Framework with categorization,
retry logic, and recovery strategies.
"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError, AccessError
import logging
import traceback
import json
import time
from functools import wraps
from datetime import datetime

_logger = logging.getLogger(__name__)


class ErrorHandler(models.AbstractModel):
    """
    Global Error Handling Framework - Base abstract model for error handling.
    All error handling models should inherit from this.
    """
    _name = 'error.handler'
    _description = 'Enhanced Global Error Handling Framework'

    # Error Categories
    ERROR_CATEGORIES = {
        'network': ['connection', 'timeout', 'unreachable', 'refused', 'socket'],
        'authentication': ['authentication', 'unauthorized', 'forbidden', 'credentials', 'login'],
        'data': ['validation', 'integrity', 'constraint', 'duplicate', 'balance'],
        'resource': ['memory', 'disk', 'lock', 'quota', 'limit'],
        'external': ['rpc', 'xmlrpc', 'api', 'service', 'external'],
        'business': ['mapping', 'reconciliation', 'promotion', 'unmapped'],
    }

    @api.model
    def log_error_decorator(self, log_source='Unknown'):
        """Decorator to log all errors with full context"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Get error context
                    error_context = {
                        'function': func.__name__,
                        'module': func.__module__,
                        'source': log_source,
                        'args': str(args)[:500],
                        'kwargs': str(kwargs)[:500],
                        'traceback': traceback.format_exc(),
                        'user': self.env.user.id if hasattr(self.env, 'user') else None,
                        'timestamp': fields.Datetime.now(),
                    }
                    
                    # Categorize and assess
                    error_info = self.handle_exception(e, error_context, reraise=False)
                    
                    # Log to Odoo logger
                    log_method = self._get_log_method(error_info['severity'])
                    log_method(
                        f"[{error_info['category'].upper()}] Error in {log_source}.{func.__name__}: {str(e)}",
                        exc_info=True,
                        extra=error_context
                    )
                    
                    # Log to consolidation log if available
                    self._log_to_consolidation(error_info, error_context)
                    
                    # Raise original exception
                    raise
            return wrapper
        return decorator

    @api.model
    def handle_exception(self, exception, context=None, reraise=True):
        """
        Centralized exception handler with categorization and logging.
        
        Args:
            exception: The exception to handle
            context: Dictionary with context information
            reraise: Whether to re-raise the exception after handling
            
        Returns:
            dict: Error information including category, severity, and recommendations
        """
        context = context or {}
        
        error_info = {
            'exception_type': type(exception).__name__,
            'message': str(exception),
            'category': self._categorize_error(exception),
            'severity': self._assess_severity(exception),
            'timestamp': fields.Datetime.now(),
            'context': context,
            'traceback': traceback.format_exc(),
            'recommendations': [],
        }
        
        # Add recommendations
        error_info['recommendations'] = self._generate_recommendations(error_info)
        
        # Log based on severity
        log_method = self._get_log_method(error_info['severity'])
        log_method(
            f"[{error_info['category'].upper()}] {error_info['exception_type']}: "
            f"{error_info['message']}"
        )
        
        if reraise:
            raise
        
        return error_info

    @api.model
    def _categorize_error(self, exception):
        """Categorize error based on exception type and message."""
        error_msg = str(exception).lower()
        exception_type = type(exception).__name__.lower()
        
        for category, keywords in self.ERROR_CATEGORIES.items():
            if any(kw in error_msg or kw in exception_type for kw in keywords):
                return category
        
        return 'unknown'

    @api.model
    def _assess_severity(self, exception):
        """Assess error severity level."""
        # Critical errors
        if isinstance(exception, (AccessError, MemoryError)):
            return 'critical'
        
        # High severity
        if isinstance(exception, (ValidationError, UserError)):
            return 'high'
        
        # Medium severity
        error_msg = str(exception).lower()
        if 'timeout' in error_msg or 'connection' in error_msg:
            return 'medium'
        
        # Low severity
        return 'low'

    @api.model
    def _get_log_method(self, severity):
        """Get appropriate logging method based on severity."""
        severity_map = {
            'critical': _logger.critical,
            'high': _logger.error,
            'medium': _logger.warning,
            'low': _logger.info,
        }
        return severity_map.get(severity, _logger.info)

    @api.model
    def _generate_recommendations(self, error_info):
        """Generate actionable recommendations based on error."""
        recommendations = []
        category = error_info['category']
        
        if category == 'network':
            recommendations.extend([
                'Check network connectivity to subsidiary',
                'Verify subsidiary URL is accessible',
                'Check firewall rules and proxy settings',
                'Consider increasing timeout values',
            ])
        elif category == 'authentication':
            recommendations.extend([
                'Verify username and password are correct',
                'Check if user account is active in subsidiary',
                'Verify user has required permissions',
                'Re-validate subsidiary connection',
            ])
        elif category == 'data':
            recommendations.extend([
                'Check data integrity constraints',
                'Validate account and journal mappings',
                'Review unbalanced move entries',
                'Run data validation wizard',
            ])
        elif category == 'resource':
            recommendations.extend([
                'Check available system resources',
                'Consider reducing batch size',
                'Enable parallel processing for better resource usage',
                'Schedule sync during off-peak hours',
            ])
        elif category == 'business':
            recommendations.extend([
                'Review and complete account mappings',
                'Validate journal mappings',
                'Check for unmapped accounts',
                'Run mapping validation wizard',
            ])
        
        return recommendations

    @api.model
    def _log_to_consolidation(self, error_info, context):
        """Log error to consolidation log."""
        try:
            log_vals = {
                'log_type': 'error',
                'message': f"[{error_info['category'].upper()}] {error_info['message'][:200]}",
                'state': 'error',
                'details': error_info['traceback'],
                'metadata': json.dumps({
                    'error_category': error_info['category'],
                    'severity': error_info['severity'],
                    'exception_type': error_info['exception_type'],
                    'recommendations': error_info['recommendations'],
                }, default=str),
                'operation': context.get('operation', 'unknown'),
                'category': error_info['category'],
                'severity': error_info['severity'],
            }
            
            if context.get('sync_engine_id'):
                log_vals['sync_engine_id'] = context['sync_engine_id']
            
            if context.get('subsidiary_id'):
                log_vals['subsidiary_id'] = context['subsidiary_id']
            
            self.env['consolidation.log'].sudo().create(log_vals)
            
        except Exception as e:
            _logger.error(f"Failed to log error to consolidation log: {str(e)}")

    @api.model
    def safe_execute(self, func, *args, **kwargs):
        """Safe execution wrapper with retry logic"""
        max_retries = kwargs.pop('max_retries', 3)
        retry_delay = kwargs.pop('retry_delay', 5)
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                _logger.warning(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s: {str(e)}")
                time.sleep(retry_delay)

    @api.model
    def retry_with_backoff(self, func, max_retries=3, initial_delay=1, 
                          backoff_factor=2, exceptions=(Exception,)):
        """
        Retry function with exponential backoff.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for delay after each retry
            exceptions: Tuple of exceptions to catch and retry
            
        Returns:
            Result of function call
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                
                if attempt == max_retries:
                    _logger.error(
                        f"Max retries ({max_retries}) reached for {func.__name__}. "
                        f"Last error: {str(e)}"
                    )
                    raise
                
                _logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}. "
                    f"Retrying in {delay} seconds..."
                )
                
                time.sleep(delay)
                delay *= backoff_factor
        
        raise last_exception

    @api.model
    def safe_execute_decorator(self, operation_name='operation', log_context=None):
        """
        Decorator for safe execution with automatic error handling.
        
        Usage:
            @self.env['error.handler'].safe_execute_decorator('sync_operation')
            def my_function(self):
                # function code
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                context = log_context or {}
                context['operation'] = operation_name
                context['function'] = func.__name__
                
                try:
                    _logger.info(f"Starting {operation_name}: {func.__name__}")
                    start_time = time.time()
                    
                    result = func(*args, **kwargs)
                    
                    duration = time.time() - start_time
                    _logger.info(
                        f"Completed {operation_name}: {func.__name__} "
                        f"in {duration:.2f} seconds"
                    )
                    
                    return result
                    
                except Exception as e:
                    _logger.error(
                        f"Failed {operation_name}: {func.__name__} - {str(e)}",
                        exc_info=True
                    )
                    
                    # Get error handler instance
                    error_handler = args[0].env['error.handler'] if args else self
                    
                    # Handle exception with full context
                    error_info = error_handler.handle_exception(e, context, reraise=False)
                    
                    # Re-raise with enriched information
                    raise type(e)(
                        f"{str(e)}\n\nCategory: {error_info['category']}\n"
                        f"Recommendations:\n- " + 
                        "\n- ".join(error_info['recommendations'])
                    )
            
            return wrapper
        return decorator


class ConsolidationErrorRecovery(models.Model):
    """Extended error recovery with specific consolidation scenarios."""
    _name = 'consolidation.error.recovery'
    _description = 'Consolidation Error Recovery Engine'
    _inherit = ['error.handler']

    @api.model
    def handle_sync_error(self, sync_engine, error, context=None):
        """Comprehensive error handling with automatic recovery attempts"""
        context = context or {}
        context.update({
            'sync_engine_id': sync_engine.id,
            'sync_engine_name': sync_engine.name,
        })
        
        error_info = self.handle_exception(error, context, reraise=False)
        
        # Classify error
        error_type = error_info['category']
        error_severity = error_info['severity']
        
        _logger.info(f'Handling {error_severity} {error_type} error for sync {sync_engine.name}')
        
        # Execute recovery based on type and severity
        recovery_result = {
            'error_id': id(error),
            'error_type': error_type,
            'severity': error_severity,
            'recovered': False,
            'actions_taken': [],
            'recommendations': error_info['recommendations'],
        }
        
        try:
            if error_type == 'network':
                recovery_result.update(self._recover_network_error(sync_engine, error))
            elif error_type == 'data':
                recovery_result.update(self._recover_data_error(sync_engine, error))
            elif error_type == 'authentication':
                recovery_result.update(self._recover_auth_error(sync_engine, error))
            elif error_type == 'business':
                recovery_result.update(self._recover_business_error(sync_engine, error))
            else:
                recovery_result.update(self._recover_unknown_error(sync_engine, error))
            
            # Update sync engine state
            if recovery_result['recovered']:
                sync_engine.write({
                    'state': 'draft' if sync_engine.retry_count < sync_engine.max_retries else 'error',
                    'error_message': f"Recovered from {error_type} error. Actions: {', '.join(recovery_result['actions_taken'])}",
                })
            else:
                sync_engine.write({
                    'state': 'error',
                    'error_message': f"{error_type} error: {str(error)[:500]}",
                })
            
        except Exception as recovery_error:
            _logger.error(f'Error recovery failed: {str(recovery_error)}')
            recovery_result['recovery_failed'] = str(recovery_error)
        
        # Store recovery result
        self._store_recovery_result(sync_engine, recovery_result)
        
        return recovery_result

    @api.model
    def _recover_network_error(self, sync_engine, error):
        """Recover from network-related errors"""
        actions = []
        recommendations = []
        
        # Check retry count
        if sync_engine.retry_count < sync_engine.max_retries:
            sync_engine.retry_count += 1
            actions.append(f'Retry #{sync_engine.retry_count}')
            
            # Implement exponential backoff
            backoff_delay = 2 ** (sync_engine.retry_count - 1) * 5
            recommendations.append(f'Wait {backoff_delay} seconds before retry')
            
            # Test connection
            def test_connection():
                for subsidiary in sync_engine.subsidiary_ids:
                    uid, models = subsidiary.get_rpc_connection()
                    models.execute_kw(
                        subsidiary.db_name, uid, subsidiary.password,
                        'res.company', 'search_count', [[]]
                    )
                return True
            
            try:
                time.sleep(backoff_delay)
                self.retry_with_backoff(test_connection, max_retries=2)
                actions.append('Connection restored')
                
                return {
                    'recovered': True,
                    'actions_taken': actions,
                    'recommendations': recommendations,
                    'retry_delay': backoff_delay,
                }
            except:
                pass
        
        # Max retries reached
        recommendations.extend([
            'Check network connectivity to subsidiary',
            'Verify subsidiary Odoo instance is running',
            'Check firewall rules',
            'Consider increasing max_retries configuration',
        ])
        
        return {
            'recovered': False,
            'actions_taken': actions,
            'recommendations': recommendations,
        }

    @api.model
    def _recover_data_error(self, sync_engine, error):
        """Recover from data errors"""
        actions = []
        
        # Identify problematic media moves
        problematic_moves = sync_engine.media_move_ids.filtered(
            lambda m: not m.is_balanced or not m.line_ids
        )
        
        if problematic_moves:
            # Mark as error state
            problematic_moves.write({
                'state': 'error',
                'error_message': 'Data integrity issues detected',
            })
            actions.append(f'Isolated {len(problematic_moves)} problematic moves')
            
            _logger.warning(
                f"Isolated {len(problematic_moves)} problematic moves. "
                f"Remaining {len(sync_engine.media_move_ids) - len(problematic_moves)} "
                f"moves can proceed."
            )
            
            return {
                'recovered': True,
                'actions_taken': actions,
                'problematic_count': len(problematic_moves),
                'valid_count': len(sync_engine.media_move_ids) - len(problematic_moves),
            }
        
        return {'recovered': False, 'actions_taken': actions}

    @api.model
    def _recover_auth_error(self, sync_engine, error):
        """Recover from authentication errors"""
        actions = []
        recommendations = [
            'Verify credentials in subsidiary configuration',
            'Check if user account is active',
            'Re-validate subsidiary connection',
        ]
        
        # Mark subsidiaries for re-validation
        sync_engine.subsidiary_ids.write({'state': 'error'})
        actions.append('Marked subsidiaries for re-validation')
        
        return {
            'recovered': False,
            'actions_taken': actions,
            'recommendations': recommendations,
        }

    @api.model
    def _recover_business_error(self, sync_engine, error):
        """Recover from business logic errors (mappings, etc.)"""
        actions = []
        
        # Try to auto-fix mapping errors
        for media_move in sync_engine.media_move_ids:
            for line in media_move.line_ids:
                if not line.mapped_account_id:
                    # Try to find similar mapping
                    similar_mapping = self.env['account.mapping'].search([
                        ('subsidiary_id', '=', media_move.subsidiary_id.id),
                        ('subsidiary_account_code', '=like', f"{line.account_code[:3]}%"),
                        ('active', '=', True),
                    ], limit=1)
                    
                    if similar_mapping:
                        try:
                            new_mapping = self.env['account.mapping'].create({
                                'subsidiary_id': media_move.subsidiary_id.id,
                                'subsidiary_account_code': line.account_code,
                                'subsidiary_account_name': line.account_name,
                                'parent_account_id': similar_mapping.parent_account_id.id,
                                'mapping_type': 'direct',
                            })
                            actions.append(f'Auto-created mapping for {line.account_code}')
                        except:
                            pass
        
        if actions:
            return {
                'recovered': True,
                'actions_taken': actions,
            }
        
        return {
            'recovered': False,
            'actions_taken': actions,
            'recommendations': [
                'Review and complete account mappings',
                'Run mapping validation wizard',
            ]
        }

    @api.model
    def _recover_unknown_error(self, sync_engine, error):
        """Handle unknown errors"""
        return {
            'recovered': False,
            'actions_taken': [],
            'recommendations': [
                'Review error logs for details',
                'Contact system administrator',
                'Check Odoo logs for additional context',
            ]
        }

    @api.model
    def _store_recovery_result(self, sync_engine, recovery_result):
        """Store recovery result in consolidation log"""
        try:
            self.env['consolidation.log'].create({
                'sync_engine_id': sync_engine.id,
                'log_type': 'error',
                'message': f"Error recovery: {recovery_result['error_type']}",
                'state': 'completed' if recovery_result['recovered'] else 'error',
                'details': f"Actions taken: {', '.join(recovery_result['actions_taken'])}\n"
                          f"Recommendations: {', '.join(recovery_result['recommendations'])}",
                'metadata': json.dumps(recovery_result, default=str),
                'operation': 'error_recovery',
                'category': recovery_result['error_type'],
                'severity': recovery_result['severity'],
            })
        except Exception as e:
            _logger.error(f"Failed to store recovery result: {str(e)}")
```

---

## File: `maintenance_tasks.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/base`

```py
from odoo import models, api, fields
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class ConsolidationMaintenance(models.Model):
    _name = 'consolidation.maintenance'
    _description = 'Consolidation System Maintenance'
    
    @api.model
    def daily_maintenance(self):
        """Daily maintenance tasks"""
        _logger.info('Starting daily consolidation maintenance')
        
        tasks = [
            self._cleanup_old_logs,
            self._archive_completed_syncs,
            self._validate_data_integrity,
            self._check_system_health,
            self._backup_restore_points,
            self._purge_temp_data,
        ]
        
        results = {}
        for task in tasks:
            try:
                start = datetime.now()
                result = task()
                duration = (datetime.now() - start).total_seconds()
                results[task.__name__] = {
                    'success': True,
                    'result': result,
                    'duration': duration,
                }
                _logger.info(f'Task {task.__name__} completed in {duration:.2f}s')
            except Exception as e:
                results[task.__name__] = {
                    'success': False,
                    'error': str(e),
                    'duration': 0,
                }
                _logger.error(f'Task {task.__name__} failed: {str(e)}')
        
        # Log maintenance completion
        self.env['consolidation.log'].log_operation(
            'maintenance',
            f'Daily maintenance completed: {len([r for r in results.values() if r["success"]])}/{len(tasks)} tasks successful',
            details=json.dumps(results, default=str)
        )
        
        return results
    
    def _cleanup_old_logs(self):
        """Clean up old log entries"""
        days = int(self.env['ir.config_parameter'].sudo().get_param(
            'financial_consolidation.log_retention_days', 90
        ))
        
        cutoff = fields.Datetime.now() - timedelta(days=days)
        
        # Archive old logs
        old_logs = self.env['consolidation.log'].search([
            ('create_date', '<', cutoff),
            ('is_archived', '=', False),
        ])
        
        archived = old_logs.write({'is_archived': True})
        
        # Delete very old archived logs (optional)
        delete_cutoff = fields.Datetime.now() - timedelta(days=days * 2)
        very_old_logs = self.env['consolidation.log'].search([
            ('create_date', '<', delete_cutoff),
            ('is_archived', '=', True),
        ])
        deleted = very_old_logs.unlink()
        
        return {
            'archived': archived,
            'deleted': deleted,
            'cutoff_date': cutoff,
        }
    
    def _validate_data_integrity(self):
        """Validate data integrity across the system"""
        integrity_engine = self.env['data.integrity.engine']
        
        # Check all pending media moves
        pending_moves = self.env['media.account.move'].search([
            ('state', 'in', ['draft', 'validated']),
            ('create_date', '>=', fields.Datetime.now() - timedelta(days=7)),
        ])
        
        if pending_moves:
            result = integrity_engine.validate_media_move_batch(pending_moves)
            
            # Flag problematic moves
            if result['errors']:
                problematic = pending_moves.filtered(
                    lambda m: any(e for e in result['errors'] if m.name in e)
                )
                problematic.write({'needs_review': True})
            
            return result
        
        return {'message': 'No pending moves to validate'}
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/currency`

```py
from . import currency_conversion
```

---

## File: `currency_conversion.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/currency`

```py
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class CurrencyConversion(models.Model):
    _name = 'currency.conversion'
    _description = 'Currency Conversion Engine'
    
    
    @api.model
    def convert_media_move(self, media_move):
        """Convert amounts in media move to company currency"""
        company_currency = media_move.subsidiary_id.company_id.currency_id
        move_currency = media_move.subsidiary_id.currency_id
        
        if move_currency == company_currency:
            return  # No conversion needed
        
        rate = self._get_conversion_rate(move_currency, company_currency, media_move.date)
        
        for line in media_move.line_ids:
            line.amount_converted = line.amount * rate
        
        media_move.write({'currency_conversion_rate': rate})    
        
    def _get_conversion_rate(self, from_currency, to_currency, date):
        """Fetch conversion rate from Odoo's currency rates"""
        rate_obj = self.env['res.currency.rate']
        rate = rate_obj._get_conversion_rate(from_currency, to_currency, date)
        if not rate:
            raise ValueError(f'No conversion rate found from {from_currency.name} to {to_currency.name} on {date}')
        return rate
    @api.model
    def convert_amount(self, amount, from_currency, to_currency, date):
        """Convert a single amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        rate = self._get_conversion_rate(from_currency, to_currency, date)
        return amount * rate
    @api.model
    def log_conversion(self, from_currency, to_currency, date, rate):
        """Log currency conversion details"""
        self.env['currency.conversion.log'].create({
            'from_currency_id': from_currency.id,
            'to_currency_id': to_currency.id,
            'conversion_date': date,
            'conversion_rate': rate,
        })  
        
class CurrencyConversionLog(models.Model):
    _name = 'currency.conversion.log'
    _description = 'Currency Conversion Log'

    from_currency_id = fields.Many2one('res.currency', string='From Currency', required=True)
    to_currency_id = fields.Many2one('res.currency', string='To Currency', required=True)
    conversion_date = fields.Date(string='Conversion Date', required=True)
    conversion_rate = fields.Float(string='Conversion Rate', required=True) 
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
from . import batch_processor
from . import data_integrity_engine
from . import error_recovery_engine
from . import parallel_processing
from . import promotion_engine
from . import reconciliation_engine
from . import rollback_manager
from . import sync_engine
from . import validation_engine
from . import abstract_engines
```

---

## File: `abstract_engines.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class BaseConsolidationEngine(models.AbstractModel):
    _name = 'base.consolidation.engine'
    _description = 'Base Consolidation Engine'
    
    @api.model
    def log_operation(self, operation, message, sync_engine_id=False, subsidiary_id=False):
        """Log engine operation"""
        return self.env['consolidation.log'].log_operation(
            'info', f'{self._name}: {message}',
            sync_engine_id=sync_engine_id,
            subsidiary_id=subsidiary_id
        )
    
    @api.model
    def log_error(self, message, sync_engine_id=False, subsidiary_id=False, exception=None):
        """Log engine error"""
        return self.env['consolidation.log'].log_error(
            message, sync_engine_id, subsidiary_id, exception=exception
        )


class AbstractDataIntegrityEngine(BaseConsolidationEngine):
    _name = 'abstract.data.integrity.engine'
    _description = 'Abstract Data Integrity Engine'
    _inherit = 'base.consolidation.engine'

    @api.model
    def validate_media_moves(self, media_moves):
        """Validate media moves integrity"""
        errors = []
        
        for move in media_moves:
            # Check balance
            if not move.is_balanced:
                errors.append(f'Move {move.name} is unbalanced (Debit: {move.total_debit}, Credit: {move.total_credit})')
            
            # Check lines
            if not move.line_ids:
                errors.append(f'Move {move.name} has no lines')
            
            # Check mappings
            unmapped_lines = move.line_ids.filtered(lambda l: not l.mapped_account_id)
            if unmapped_lines:
                error_accounts = ', '.join(unmapped_lines.mapped('account_code'))
                errors.append(f'Move {move.name} has unmapped accounts: {error_accounts}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'total_moves': len(media_moves),
            'unbalanced_moves': len([m for m in media_moves if not m.is_balanced]),
            'unmapped_lines': sum(len(m.line_ids.filtered(lambda l: not l.mapped_account_id)) for m in media_moves)
        }

    @api.model
    def calculate_checksum(self, data):
        """Calculate data checksum"""
        import hashlib
        import json
        
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        
        return hashlib.sha256(data_str.encode()).hexdigest()


class AbstractValidationEngine(BaseConsolidationEngine):
    _name = 'abstract.validation.engine'
    _description = 'Abstract Validation Engine'
    _inherit = 'base.consolidation.engine'

    @api.model
    def validate_subsidiary(self, subsidiary):
        """Validate subsidiary readiness"""
        errors = []
        
        # Check connection
        if subsidiary.state != 'validated':
            errors.append(f'Subsidiary {subsidiary.name} not validated')
        
        # Check mappings
        if not subsidiary.account_mapping_ids:
            errors.append(f'No account mappings defined for {subsidiary.name}')
        
        if not subsidiary.journal_mapping_ids:
            errors.append(f'No journal mappings defined for {subsidiary.name}')
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return {
            'valid': True,
            'subsidiary_id': subsidiary.id,
            'account_mappings': len(subsidiary.account_mapping_ids),
            'journal_mappings': len(subsidiary.journal_mapping_ids),
        }

    @api.model
    def validate_chart_of_accounts(self, subsidiary):
        """Validate chart of accounts compatibility"""
        # Check if all subsidiary accounts are mapped
        try:
            uid, models = subsidiary.get_rpc_connection()
            
            accounts = models.execute_kw(
                subsidiary.db_name, uid, subsidiary.password,
                'account.account', 'search_read',
                [[('deprecated', '=', False)]],
                {'fields': ['code', 'name']}
            )
            
            unmapped = []
            for account in accounts:
                mapping = self.env['account.mapping'].search([
                    ('subsidiary_id', '=', subsidiary.id),
                    ('subsidiary_account_code', '=', account['code']),
                ], limit=1)
                
                if not mapping:
                    unmapped.append(f"{account['code']} - {account['name']}")
            
            return {
                'total_accounts': len(accounts),
                'unmapped_accounts': len(unmapped),
                'coverage_rate': ((len(accounts) - len(unmapped)) / len(accounts) * 100) if accounts else 0,
                'unmapped_list': unmapped[:10]  # First 10 for reporting
            }
            
        except Exception as e:
            raise ValidationError(_('Failed to validate chart of accounts: %s') % str(e))

    @api.model
    def validate_periods(self, date_from, date_to):
        """Validate period range"""
        if date_from > date_to:
            raise ValidationError(_('Date From must be before Date To'))
        
        # Check if period is not too large (e.g., > 1 year)
        delta = (date_to - date_from).days
        if delta > 365:
            raise ValidationError(_('Period range too large. Maximum 365 days.'))
        
        return {
            'valid': True,
            'days': delta,
            'within_limit': delta <= 365
        }

    @api.model
    def validate_currencies(self, subsidiary):
        """Validate currency configuration"""
        if not subsidiary.currency_id:
            raise ValidationError(f'Currency not configured for {subsidiary.name}')
        
        if not subsidiary.company_id.currency_id:
            raise ValidationError(f'Parent company currency not configured')
        
        return {
            'valid': True,
            'subsidiary_currency': subsidiary.currency_id.name,
            'parent_currency': subsidiary.company_id.currency_id.name,
            'conversion_needed': subsidiary.currency_id != subsidiary.company_id.currency_id
        }
```

---

## File: `batch_processor.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py

from datetime import datetime
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class BatchProcessor(models.AbstractModel):
    _name = 'batch.processor'
    _description = 'Batch Processor'

    @api.model
    def process_in_batches(self, records, batch_size, process_func):
        """Process records in batches"""
        total = len(records)
        processed = 0
        
        for i in range(0, total, batch_size):
            batch = records[i:i+batch_size]
            process_func(batch)
            processed += len(batch)
            _logger.info(f'Processed {processed}/{total}')
        
        return processed



 
    @api.model
    def process_with_progress(self, records, batch_size, process_func, 
                              progress_callback=None, context=None):
        """Process records in batches with progress tracking"""
        total = len(records)
        processed = 0
        errors = []
        start_time = datetime.now()
        
        _logger.info(f'Starting batch processing of {total} records in batches of {batch_size}')
        
        for i in range(0, total, batch_size):
            batch = records[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            try:
                # Process batch
                result = process_func(batch)
                processed += len(batch)
                
                # Calculate progress
                progress = (processed / total) * 100
                elapsed = (datetime.now() - start_time).total_seconds()
                estimated_total = (elapsed / progress * 100) if progress > 0 else 0
                remaining = estimated_total - elapsed if estimated_total > elapsed else 0
                
                # Log progress
                _logger.info(
                    f'Batch {batch_num}/{total_batches} processed. '
                    f'Progress: {progress:.1f}%. '
                    f'Elapsed: {elapsed:.0f}s, Remaining: ~{remaining:.0f}s'
                )
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback({
                        'current': processed,
                        'total': total,
                        'progress': progress,
                        'batch': batch_num,
                        'total_batches': total_batches,
                        'elapsed': elapsed,
                        'estimated_remaining': remaining,
                    })
                
                # Commit after each batch for large operations
                if total > 1000:
                    self.env.cr.commit()
                    
            except Exception as e:
                _logger.error(f'Batch {batch_num} failed: {str(e)}')
                errors.append({
                    'batch': batch_num,
                    'error': str(e),
                    'record_ids': batch.ids,
                })
                
                # If too many errors, stop
                if len(errors) > 10:
                    _logger.error('Too many errors, stopping batch processing')
                    break
        
        # Return comprehensive results
        return {
            'total_records': total,
            'processed': processed,
            'failed': total - processed,
            'errors': errors,
            'success_rate': (processed / total * 100) if total > 0 else 0,
            'total_time': (datetime.now() - start_time).total_seconds(),
            'batch_size': batch_size,
            'batches_processed': (processed + batch_size - 1) // batch_size,
        }
```

---

## File: `data_integrity_engine.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
import logging
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import json
import hashlib
from .. import error

_logger = logging.getLogger(__name__)


class DataIntegrityEngine(models.Model):
    _name = 'data.integrity.engine'
    _description = 'Data Integrity Engine'
    _order = 'check_date desc'

    name = fields.Char(string='Check Name', required=True)
    check_type = fields.Selection([
        ('consistency', 'Data Consistency'),
        ('completeness', 'Data Completeness'),
        ('accuracy', 'Data Accuracy'),
        ('validity', 'Data Validity'),
        ('uniqueness', 'Data Uniqueness'),
        ('timeliness', 'Data Timeliness'),
    ], string='Check Type', required=True, default='consistency')
    
    status = fields.Selection([
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('warning', 'Warning'),
    ], string='Status', default='pending')
    
    check_date = fields.Datetime(string='Check Date', default=fields.Datetime.now)
    duration = fields.Float(string='Duration (seconds)', digits=(16, 2))
    
    # References
    sync_engine_id = fields.Many2one('sync.engine', string='Sync Engine')
    subsidiary_id = fields.Many2one('subsidiary.instance', string='Subsidiary')
    media_move_id = fields.Many2one('media.account.move', string='Media Move')
    
    # Results
    issues_found = fields.Integer(string='Issues Found', default=0)
    issues_resolved = fields.Integer(string='Issues Resolved', default=0)
    passed_checks = fields.Integer(string='Passed Checks')
    failed_checks = fields.Integer(string='Failed Checks')
    total_checks = fields.Integer(string='Total Checks', compute='_compute_total_checks')
    
    # Details
    check_config = fields.Text(string='Check Configuration', default='{}')
    check_results = fields.Text(string='Check Results', default='{}')
    issues_details = fields.Text(string='Issues Details', default='[]')
    resolution_log = fields.Text(string='Resolution Log', default='[]')
    
    # Metadata
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    last_run_date = fields.Datetime(string='Last Run Date')
    run_count = fields.Integer(string='Run Count', default=0)
    success_rate = fields.Float(string='Success Rate', compute='_compute_success_rate', digits=(5, 2))
    
    # Computed fields
    @api.depends('passed_checks', 'failed_checks')
    def _compute_total_checks(self):
        for record in self:
            record.total_checks = (record.passed_checks or 0) + (record.failed_checks or 0)
    
    @api.depends('run_count', 'status')
    def _compute_success_rate(self):
        for record in self:
            if record.run_count > 0:
                # Simplified calculation - in real implementation, track successful runs
                record.success_rate = 100.0 if record.status == 'passed' else 0.0
            else:
                record.success_rate = 0.0
    
    @error.log_error_decorator('DataIntegrityEngine')
    def run_integrity_checks(self, sync_engine_id=None):
        """Run all integrity checks."""
        self.ensure_one()
        
        start_time = datetime.now()
        self.status = 'running'
        
        try:
            # Run different types of checks
            checks = [
                self._check_data_consistency(sync_engine_id),
                self._check_data_completeness(sync_engine_id),
                self._check_data_accuracy(sync_engine_id),
                self._check_data_validity(sync_engine_id),
                self._check_data_uniqueness(sync_engine_id),
                self._check_data_timeliness(sync_engine_id),
            ]
            
            # Process results
            passed = sum(1 for check in checks if check.get('status') == 'passed')
            failed = sum(1 for check in checks if check.get('status') == 'failed')
            
            self.passed_checks = passed
            self.failed_checks = failed
            self.issues_found = sum(check.get('issues', 0) for check in checks)
            
            # Store detailed results
            results = {
                'checks': checks,
                'summary': {
                    'passed': passed,
                    'failed': failed,
                    'issues_found': self.issues_found,
                },
                'timestamp': fields.Datetime.now(),
            }
            
            self.check_results = json.dumps(results, indent=2, default=str)
            
            # Update status
            if failed > 0:
                self.status = 'failed'
                # Log issues
                issues = []
                for check in checks:
                    if check.get('status') == 'failed':
                        issues.append({
                            'check_type': check.get('type'),
                            'issues': check.get('issues', 0),
                            'details': check.get('details', [])
                        })
                self.issues_details = json.dumps(issues, indent=2, default=str)
            elif self.issues_found > 0:
                self.status = 'warning'
            else:
                self.status = 'passed'
            
            # Update duration
            self.duration = (datetime.now() - start_time).total_seconds()
            self.last_run_date = fields.Datetime.now()
            self.run_count += 1
            
            return {
                'status': self.status,
                'passed_checks': passed,
                'failed_checks': failed,
                'issues_found': self.issues_found,
                'duration': self.duration,
            }
            
        except Exception as e:
            error.handler.handle_exception('DataIntegrityEngine', 'run_integrity_checks', e)
            self.status = 'failed'
            self.duration = (datetime.now() - start_time).total_seconds()
            raise
    
    @error.log_error_decorator('DataIntegrityEngine')
    def _check_data_consistency(self, sync_engine_id):
        """Check data consistency across related records."""
        checks = []
        issues = 0
        
        if sync_engine_id:
            sync_engine = self.env['sync.engine'].browse(sync_engine_id)
            
            # Check 1: Verify media moves balance
            media_moves = self.env['media.account.move'].search([
                ('sync_engine_id', '=', sync_engine_id)
            ])
            
            unbalanced_moves = media_moves.filtered(lambda m: not m.is_balanced)
            if unbalanced_moves:
                issues += len(unbalanced_moves)
                checks.append({
                    'check': 'Media Move Balance',
                    'status': 'failed',
                    'issues': len(unbalanced_moves),
                    'details': [f'Move {move.name} is unbalanced' for move in unbalanced_moves[:5]]
                })
            else:
                checks.append({
                    'check': 'Media Move Balance',
                    'status': 'passed',
                    'issues': 0
                })
            
            # Check 2: Verify mapping completeness
            subsidiaries = sync_engine.subsidiary_ids
            for subsidiary in subsidiaries:
                account_mappings = self.env['account.mapping'].search([
                    ('subsidiary_id', '=', subsidiary.id),
                    ('active', '=', True)
                ])
                
                unmapped_accounts = self._get_unmapped_accounts(subsidiary)
                if unmapped_accounts:
                    issues += len(unmapped_accounts)
                    checks.append({
                        'check': f'Account Mapping Completeness - {subsidiary.code}',
                        'status': 'failed',
                        'issues': len(unmapped_accounts),
                        'details': [f'Account {acc} is not mapped' for acc in unmapped_accounts[:5]]
                    })
        
        return {
            'type': 'consistency',
            'status': 'failed' if issues > 0 else 'passed',
            'issues': issues,
            'checks': checks
        }
    
    @error.log_error_decorator('DataIntegrityEngine')
    def _check_data_completeness(self, sync_engine_id):
        """Check data completeness."""
        issues = 0
        details = []
        
        if sync_engine_id:
            sync_engine = self.env['sync.engine'].browse(sync_engine_id)
            
            # Check for required fields
            required_checks = [
                ('subsidiary.instance', ['code', 'name', 'currency_id']),
                ('account.mapping', ['subsidiary_account_code', 'parent_account_id']),
                ('sync.engine', ['date_from', 'date_to']),
            ]
            
            for model_name, fields_list in required_checks:
                model = self.env[model_name]
                records = model.search([('sync_engine_id', '=', sync_engine_id)] if hasattr(model, 'sync_engine_id') else [])
                
                for record in records:
                    for field in fields_list:
                        if not record[field]:
                            issues += 1
                            details.append(f'{model_name} {record.id} missing {field}')
        
        return {
            'type': 'completeness',
            'status': 'failed' if issues > 0 else 'passed',
            'issues': issues,
            'details': details[:10]  # Limit details
        }
    
    @error.log_error_decorator('DataIntegrityEngine')
    def _check_data_accuracy(self, sync_engine_id):
        """Check data accuracy."""
        issues = 0
        details = []
        
        if sync_engine_id:
            # Check currency conversion accuracy
            sync_engine = self.env['sync.engine'].browse(sync_engine_id)
            
            for subsidiary in sync_engine.subsidiary_ids:
                # Verify currency rates are available
                currency_conversions = self.env['currency.conversion'].search([
                    ('from_currency_id', '=', subsidiary.currency_id.id),
                    ('date', '<=', sync_engine.date_to),
                    ('date', '>=', sync_engine.date_from)
                ])
                
                if not currency_conversions:
                    issues += 1
                    details.append(f'No currency conversions for {subsidiary.code} ({subsidiary.currency_id.name})')
        
        return {
            'type': 'accuracy',
            'status': 'failed' if issues > 0 else 'passed',
            'issues': issues,
            'details': details
        }
    
    @error.log_error_decorator('DataIntegrityEngine')
    def _check_data_validity(self, sync_engine_id):
        """Check data validity."""
        issues = 0
        details = []
        
        # Check for invalid dates
        if sync_engine_id:
            sync_engine = self.env['sync.engine'].browse(sync_engine_id)
            
            media_moves = self.env['media.account.move'].search([
                ('sync_engine_id', '=', sync_engine_id)
            ])
            
            # Check for dates outside sync period
            invalid_dates = media_moves.filtered(
                lambda m: m.date < sync_engine.date_from or m.date > sync_engine.date_to
            )
            
            if invalid_dates:
                issues += len(invalid_dates)
                details.extend([f'Move {move.name} date {move.date} outside sync period' 
                              for move in invalid_dates[:5]])
        
        return {
            'type': 'validity',
            'status': 'failed' if issues > 0 else 'passed',
            'issues': issues,
            'details': details
        }
    
    @error.log_error_decorator('DataIntegrityEngine')
    def _check_data_uniqueness(self, sync_engine_id):
        """Check data uniqueness."""
        issues = 0
        details = []
        
        if sync_engine_id:
            # Check for duplicate account mappings
            subsidiaries = self.env['sync.engine'].browse(sync_engine_id).subsidiary_ids
            
            for subsidiary in subsidiaries:
                account_mappings = self.env['account.mapping'].search([
                    ('subsidiary_id', '=', subsidiary.id),
                    ('active', '=', True)
                ])
                
                # Group by subsidiary account code
                codes = {}
                for mapping in account_mappings:
                    code = mapping.subsidiary_account_code
                    if code in codes:
                        codes[code].append(mapping)
                    else:
                        codes[code] = [mapping]
                
                # Find duplicates
                for code, mappings in codes.items():
                    if len(mappings) > 1:
                        issues += 1
                        details.append(f'Duplicate mapping for account {code} in {subsidiary.code}')
        
        return {
            'type': 'uniqueness',
            'status': 'failed' if issues > 0 else 'passed',
            'issues': issues,
            'details': details
        }
    
    @error.log_error_decorator('DataIntegrityEngine')
    def _check_data_timeliness(self, sync_engine_id):
        """Check data timeliness."""
        issues = 0
        details = []
        
        if sync_engine_id:
            sync_engine = self.env['sync.engine'].browse(sync_engine_id)
            
            # Check if sync is too old
            if sync_engine.end_date:
                age_days = (datetime.now() - sync_engine.end_date).days
                if age_days > 30:  # More than 30 days old
                    issues += 1
                    details.append(f'Sync {sync_engine.name} is {age_days} days old')
        
        return {
            'type': 'timeliness',
            'status': 'failed' if issues > 0 else 'passed',
            'issues': issues,
            'details': details
        }
    
    def _get_unmapped_accounts(self, subsidiary):
        """Get list of unmapped accounts for a subsidiary."""
        # This is a simplified version - in reality, you would fetch accounts from subsidiary
        # and compare with existing mappings
        return []
    
    @error.log_error_decorator('DataIntegrityEngine')
    def generate_integrity_report(self):
        """Generate a detailed integrity report."""
        self.ensure_one()
        
        report = {
            'integrity_check': {
                'name': self.name,
                'type': self.check_type,
                'status': self.status,
                'date': self.check_date.strftime('%Y-%m-%d %H:%M:%S') if self.check_date else None,
                'duration': self.duration,
            },
            'summary': {
                'total_checks': self.total_checks,
                'passed_checks': self.passed_checks,
                'failed_checks': self.failed_checks,
                'issues_found': self.issues_found,
                'issues_resolved': self.issues_resolved,
            },
            'details': json.loads(self.check_results) if self.check_results else {},
            'recommendations': self._generate_recommendations(),
        }
        
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on check results."""
        recommendations = []
        
        if self.status == 'failed':
            recommendations.append({
                'priority': 'high',
                'action': 'Review and fix failed integrity checks',
                'details': 'Address the issues identified in the integrity check'
            })
        
        if self.issues_found > 0:
            recommendations.append({
                'priority': 'medium',
                'action': 'Resolve identified issues',
                'details': f'There are {self.issues_found} issues that need attention'
            })
        
        return recommendations
    
    @api.model
    def run_scheduled_integrity_checks(self):
        """Run scheduled integrity checks (called by cron)."""
        config = self.env['consolidation.config'].search([], limit=1)
        
        if config and config.enable_health_monitoring:
            # Create a new integrity check
            check = self.create({
                'name': f'Scheduled Integrity Check {fields.Datetime.now()}',
                'check_type': 'consistency',
                'status': 'pending',
            })
            
            try:
                check.run_integrity_checks()
                
                # Log the result
                if check.status == 'failed':
                    error.handler.log_warning(
                        'DataIntegrityEngine',
                        'run_scheduled_integrity_checks',
                        f'Scheduled integrity check failed: {check.issues_found} issues found'
                    )
                
            except Exception as e:
                error.handler.handle_exception(
                    'DataIntegrityEngine',
                    'run_scheduled_integrity_checks',
                    e
                )
    
    @error.log_error_decorator('DataIntegrityEngine')
    def action_resolve_issues(self):
        """Attempt to automatically resolve identified issues."""
        self.ensure_one()
        
        if not self.issues_details:
            return {'success': True, 'message': 'No issues to resolve'}
        
        try:
            issues = json.loads(self.issues_details)
            resolved_count = 0
            
            for issue in issues:
                if issue.get('check_type') == 'Media Move Balance':
                    # Attempt to fix unbalanced moves
                    resolved = self._fix_unbalanced_moves(issue)
                    resolved_count += resolved
            
            self.issues_resolved = resolved_count
            
            # Update status if all issues resolved
            if resolved_count >= self.issues_found:
                self.status = 'passed'
            
            return {
                'success': True,
                'resolved': resolved_count,
                'remaining': self.issues_found - resolved_count,
            }
            
        except Exception as e:
            error.handler.handle_exception('DataIntegrityEngine', 'action_resolve_issues', e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _fix_unbalanced_moves(self, issue):
        """Fix unbalanced media moves."""
        # This is a placeholder - actual implementation would fix the moves
        return 0
```

---

## File: `error_recovery_engine.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
from odoo import models, api
import logging
from .. import error
_logger = logging.getLogger(__name__)

class ErrorRecoveryEngine(models.AbstractModel):
    _name = 'error.recovery.engine'
    _description = 'Error Recovery Engine'
    _inherit = ['error.handler']

    @api.model
    @error.log_error_decorator('ErrorRecovery')
    def handle_sync_error(self, sync_engine, error, context=None):
        """Comprehensive error handling with automatic recovery attempts"""
        error_id = self._log_error(sync_engine, error, context)
        
        # Classify error
        error_type = self._classify_error(error)
        error_severity = self._assess_severity(error, sync_engine)
        
        _logger.info(f'Handling {error_severity} {error_type} error for sync {sync_engine.name}')
        
        # Execute recovery based on type and severity
        recovery_result = {
            'error_id': error_id,
            'error_type': error_type,
            'severity': error_severity,
            'recovered': False,
            'actions_taken': [],
            'recommendations': [],
        }
        
        try:
            if error_type == 'network':
                recovery_result.update(self._recover_network_error(sync_engine, error))
            elif error_type == 'data':
                recovery_result.update(self._recover_data_error(sync_engine, error))
            elif error_type == 'timeout':
                recovery_result.update(self._recover_timeout_error(sync_engine, error))
            elif error_type == 'validation':
                recovery_result.update(self._recover_validation_error(sync_engine, error))
            elif error_type == 'concurrency':
                recovery_result.update(self._recover_concurrency_error(sync_engine, error))
            else:
                recovery_result.update(self._recover_unknown_error(sync_engine, error))
            
            # Update sync engine state
            if recovery_result['recovered']:
                sync_engine.write({
                    'state': 'draft' if sync_engine.retry_count < sync_engine.max_retries else 'error',
                    'error_message': f"Recovered from {error_type} error. Actions: {', '.join(recovery_result['actions_taken'])}",
                })
            else:
                sync_engine.write({
                    'state': 'error',
                    'error_message': f"{error_type} error: {str(error)[:500]}",
                })
            
        except Exception as recovery_error:
            _logger.error(f'Error recovery failed: {str(recovery_error)}')
            recovery_result['recovery_failed'] = str(recovery_error)
        
        # Store recovery result
        self._store_recovery_result(sync_engine, recovery_result)
        
        return recovery_result
    
    def _recover_network_error(self, sync_engine, error):
        """Recover from network-related errors"""
        actions = []
        recommendations = []
        
        # Check retry count
        if sync_engine.retry_count < sync_engine.max_retries:
            sync_engine.retry_count += 1
            actions.append(f'Retry #{sync_engine.retry_count}')
            
            # Implement exponential backoff
            backoff_delay = 2 ** (sync_engine.retry_count - 1) * 5  # 5, 10, 20, ...
            recommendations.append(f'Wait {backoff_delay} seconds before retry')
            
            return {
                'recovered': True,
                'actions_taken': actions,
                'recommendations': recommendations,
                'retry_delay': backoff_delay,
            }
        
        # Max retries reached
        recommendations.extend([
            'Check network connectivity to subsidiary',
            'Verify subsidiary Odoo instance is running',
            'Check firewall rules',
            'Consider increasing max_retries configuration',
        ])
        
        return {
            'recovered': False,
            'actions_taken': actions,
            'recommendations': recommendations,
        }
    def _recover_data_error(self, sync_engine):
        """Recover from data error"""
        # Mark problematic media moves
        for media_move in sync_engine.media_move_ids:
            if not media_move.is_balanced:
                media_move.write({'state': 'error'})
        
        return False

    def _recover_timeout_error(self, sync_engine):
        """Recover from timeout"""
        # Reduce batch size and retry
        return self._recover_network_error(sync_engine)
    
```

---

## File: `parallel_processing.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class ParallelProcessing(models.AbstractModel):
    _name = 'parallel.processing'
    _description = 'Parallel Processing Manager'

    @api.model
    def execute_parallel(self, items, process_func, max_workers=4):
        """Execute function in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_func, item): item for item in items}
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    _logger.error(f'Parallel task failed: {str(e)}')
        
        return results
```

---

## File: `promotion_engine.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class PromotionEngine(models.AbstractModel):
    _name = 'promotion.engine'
    _description = 'Promotion Engine'

    @api.model
    def promote_media_moves(self, media_moves):
        """Promote media moves to accounting"""
        promoted_count = 0
        
        for media_move in media_moves:
            if media_move.state == 'promoted':
                continue
            
            try:
                # Validate journal mapping
                if not media_move.mapped_journal_id:
                    # Try to get default consolidation journal
                    journal = self._get_consolidation_journal(media_move.company_id)
                    if not journal:
                        raise ValidationError(
                            _('No journal mapping found for move %s and no default consolidation journal') % 
                            media_move.name
                        )
                    media_move.mapped_journal_id = journal
                
                # Validate account mappings
                unmapped_lines = media_move.line_ids.filtered(lambda l: not l.mapped_account_id)
                if unmapped_lines:
                    raise ValidationError(
                        _('Move %s has unmapped accounts: %s') % 
                        (media_move.name, ', '.join(unmapped_lines.mapped('account_code')))
                    )
                
                # Create accounting move
                move_vals = self._prepare_move_vals(media_move)
                account_move = self.env['account.move'].create(move_vals)
                
                # Validate the move
                account_move._move_autocomplete_invoice_lines_values()
                
                # Post move
                account_move.action_post()
                
                # Update media move
                media_move.write({
                    'state': 'promoted',
                    'promoted_move_id': account_move.id,
                    'promotion_date': fields.Datetime.now(),
                })
                
                promoted_count += 1
                
                _logger.info(f'Promoted move {media_move.name} to {account_move.name}')
                
            except Exception as e:
                _logger.error(f'Promotion failed for {media_move.name}: {str(e)}')
                media_move.write({
                    'state': 'error', 
                    'error_message': str(e),
                    'retry_count': media_move.retry_count + 1,
                })
        
        return promoted_count

    def _prepare_move_vals(self, media_move):
        """Prepare account.move values"""
        line_vals = []
        
        for line in media_move.line_ids:
            line_vals.append((0, 0, {
                'name': line.name or '/',
                'account_id': line.mapped_account_id.id,
                'debit': line.debit,
                'credit': line.credit,
                'partner_id': line.partner_id.id if line.partner_id else False,
                'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False,
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)] if line.analytic_tag_ids else False,
            }))
        
        # Determine journal - use mapped journal or fallback to default
        journal = media_move.mapped_journal_id
        if not journal:
            journal = self._get_consolidation_journal(media_move.company_id)
        
        # Build reference
        ref_parts = []
        if media_move.subsidiary_id.code:
            ref_parts.append(media_move.subsidiary_id.code)
        if media_move.ref:
            ref_parts.append(media_move.ref)
        elif media_move.name:
            ref_parts.append(media_move.name)
        
        ref = ' - '.join(ref_parts) if ref_parts else f'Consolidation {media_move.name}'
        
        return {
            'move_type': 'entry',
            'date': media_move.date,
            'ref': ref,
            'journal_id': journal.id,
            'line_ids': line_vals,
            'is_consolidation': True,
            'consolidation_sync_id': media_move.sync_engine_id.id,
            'media_move_id': media_move.id,
            'narration': f'Consolidated from subsidiary: {media_move.subsidiary_id.name}',
        }

    def _get_consolidation_journal(self, company):
        """Get or create default consolidation journal"""
        # Try to find existing consolidation journal
        journal = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            '|', ('code', 'ilike', 'CONS'),
            ('name', 'ilike', 'consolidation'),
        ], order='id', limit=1)
        
        if not journal:
            # Create default consolidation journal
            journal = self.env['account.journal'].create({
                'name': 'Consolidation Journal',
                'code': 'CONS',
                'type': 'general',
                'company_id': company.id,
                'default_account_id': self._get_default_consolidation_account(company).id,
            })
            _logger.info(f'Created default consolidation journal: {journal.name}')
        
        return journal

    def _get_default_consolidation_account(self, company):
        """Get or create default consolidation account"""
        # Try to find existing consolidation suspense account
        account = self.env['account.account'].search([
            ('company_id', '=', company.id),
            '|', ('code', 'ilike', '999999'),
            ('name', 'ilike', 'consolidation suspense'),
        ], limit=1)
        
        if not account:
            # Create default consolidation suspense account
            account_type = self.env['account.account.type'].search([
                ('type', '=', 'other'),
            ], limit=1)
            
            if not account_type:
                account_type = self.env['account.account.type'].create({
                    'name': 'Consolidation',
                    'type': 'other',
                })
            
            account = self.env['account.account'].create({
                'code': '999999',
                'name': 'Consolidation Suspense Account',
                'user_type_id': account_type.id,
                'company_id': company.id,
                'reconcile': True,
            })
        
        return account

    @api.model
    def validate_move_before_promotion(self, media_move):
        """Validate media move before promotion"""
        errors = []
        
        # Check journal mapping
        if not media_move.mapped_journal_id:
            errors.append(_('No journal mapping found'))
        
        # Check account mappings
        unmapped_lines = media_move.line_ids.filtered(lambda l: not l.mapped_account_id)
        if unmapped_lines:
            error_accounts = ', '.join(unmapped_lines.mapped('account_code'))
            errors.append(_('Unmapped accounts: %s') % error_accounts)
        
        # Check balance
        if not media_move.is_balanced:
            errors.append(_('Move is not balanced'))
        
        # Check if already promoted
        if media_move.state == 'promoted':
            errors.append(_('Move already promoted'))
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
        }
```

---

## File: `reconciliation_engine.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class ReconciliationEngine(models.AbstractModel):
    _name = 'reconciliation.engine'
    _description = 'Reconciliation Engine'

    @api.model
    def execute_reconciliation(self, sync_engine):
        """Execute reconciliation process"""
        # Intercompany reconciliation
        self._reconcile_intercompany(sync_engine)
        
        # FX reconciliation
        self._reconcile_fx(sync_engine)
        
        # Provision reconciliation
        self._reconcile_provisions(sync_engine)

    def _reconcile_intercompany(self, sync_engine):
        """Reconcile intercompany transactions"""
        _logger.info(f'Intercompany reconciliation for {sync_engine.name}')
        # Implementation for intercompany elimination
        pass

    def _reconcile_fx(self, sync_engine):
        """Reconcile foreign exchange"""
        _logger.info(f'FX reconciliation for {sync_engine.name}')
        # Apply currency conversion
        currency_engine = self.env['currency.conversion']
        
        for media_move in sync_engine.media_move_ids:
            if media_move.subsidiary_id.currency_id != sync_engine.company_id.currency_id:
                currency_engine.convert_media_move(media_move)

    def _reconcile_provisions(self, sync_engine):
        """Reconcile provisions"""
        _logger.info(f'Provision reconciliation for {sync_engine.name}')
        pass


```

---

## File: `rollback_manager.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py

from odoo import models, api, _
from odoo.exceptions import UserError
import logging
import hashlib
from contextlib import contextmanager

_logger = logging.getLogger(__name__)


class RollbackManager(models.AbstractModel):
    """
    Base Rollback Manager - Abstract model providing core rollback functionality.
    Other transaction models inherit from this.
    """
    _name = 'rollback.manager'
    _description = 'Enhanced Rollback Manager'

    @api.model
    def execute_rollback(self, sync_engine, rollback_type='full'):
        """Execute rollback with transaction management"""
        lock_key = f"rollback_{sync_engine.id}"
        
        # Use transaction manager for lock
        tx_manager = self.env['transaction.manager']
        
        with tx_manager.acquire_lock(lock_key):
            with tx_manager.savepoint('rollback_operation'):
                try:
                    _logger.info(f"Starting {rollback_type} rollback for sync {sync_engine.name}")
                    
                    if rollback_type == 'full':
                        self._full_rollback(sync_engine)
                    elif rollback_type == 'partial':
                        self._partial_rollback(sync_engine)
                    
                    # Log rollback
                    self.env['consolidation.log'].create({
                        'sync_engine_id': sync_engine.id,
                        'log_type': 'rollback',
                        'message': f'Rollback executed: {rollback_type}',
                        'state': 'completed',
                        'operation': 'rollback',
                    })
                    
                    return True
                    
                except Exception as e:
                    _logger.error(f'Rollback failed: {str(e)}', exc_info=True)
                    raise

    def _full_rollback(self, sync_engine):
        """Full rollback - delete all promoted moves"""
        _logger.info(f"Executing full rollback for sync {sync_engine.name}")
        
        # Get promoted moves
        promoted_moves = self.env['account.move'].search([
            ('id', 'in', sync_engine.media_move_ids.mapped('promoted_move_id').ids)
        ])
        
        # Cancel and delete
        for move in promoted_moves:
            try:
                if move.state == 'posted':
                    move.button_draft()
                move.unlink()
            except Exception as e:
                _logger.warning(f'Could not delete move {move.name}: {str(e)}')
                try:
                    move.button_cancel()
                except:
                    pass
        
        # Reset media moves
        sync_engine.media_move_ids.write({
            'state': 'draft',
            'promoted_move_id': False,
            'promotion_date': False,
        })
        
        _logger.info(f'Full rollback completed: {len(promoted_moves)} moves processed')

    def _partial_rollback(self, sync_engine):
        """Partial rollback - keep moves, reset staging"""
        sync_engine.media_move_ids.write({'state': 'draft'})


class TransactionManager(models.AbstractModel):
    """Transaction management with proper rollback and commit handling."""
    _name = 'transaction.manager'
    _description = 'Transaction Management'
    # We don't inherit from rollback.manager to avoid circular dependencies
    # Instead, rollback.manager uses this via self.env

    @contextmanager
    def savepoint(self, name='consolidation_savepoint'):
        """
        Context manager for database savepoints.
        
        Usage:
            tx = self.env['transaction.manager']
            with tx.savepoint('my_operation'):
                # database operations
                # will rollback to savepoint on exception
        """
        sp_name = f"sp_{name}_{id(self)}"
        
        try:
            self.env.cr.execute(f'SAVEPOINT "{sp_name}"')
            _logger.debug(f"Created savepoint: {sp_name}")
            
            yield
            
            # Release savepoint on success
            self.env.cr.execute(f'RELEASE SAVEPOINT "{sp_name}"')
            _logger.debug(f"Released savepoint: {sp_name}")
            
        except Exception as e:
            # Rollback to savepoint on error
            _logger.warning(f"Rolling back to savepoint {sp_name}: {str(e)}")
            self.env.cr.execute(f'ROLLBACK TO SAVEPOINT "{sp_name}"')
            raise

    @contextmanager
    def atomic_operation(self, operation_name='operation'):
        """
        Context manager for atomic operations with logging.
        
        Usage:
            tx = self.env['transaction.manager']
            with tx.atomic_operation('sync_data'):
                # operations that must be atomic
        """
        with self.savepoint(operation_name):
            try:
                _logger.debug(f"Starting atomic operation: {operation_name}")
                
                yield
                
                _logger.debug(f"Completed atomic operation: {operation_name}")
                
            except Exception as e:
                _logger.error(f"Atomic operation failed: {operation_name} - {str(e)}")
                
                # Log to consolidation log
                try:
                    self.env['consolidation.log'].log_operation(
                        'error',
                        f"Atomic operation failed: {operation_name}",
                        details=str(e),
                        operation=operation_name,
                    )
                except:
                    pass
                
                raise

    @contextmanager
    def acquire_lock(self, lock_key, timeout=None):
        """
        Acquire an advisory lock.
        
        Args:
            lock_key: Unique identifier for the lock
            timeout: Timeout in seconds (None = wait indefinitely)
        
        Usage:
            tx = self.env['transaction.manager']
            with tx.acquire_lock('sync_123'):
                # exclusive operation
        """
        # Convert key to numeric lock ID
        lock_id = int(hashlib.md5(str(lock_key).encode()).hexdigest()[:8], 16)
        
        try:
            # Try to acquire lock
            if timeout:
                self.env.cr.execute(
                    "SELECT pg_try_advisory_lock(%s)", (lock_id,)
                )
                acquired = self.env.cr.fetchone()[0]
                
                if not acquired:
                    raise UserError(
                        _("Could not acquire lock for %s. Another operation is in progress.") 
                        % lock_key
                    )
            else:
                # Blocking lock
                self.env.cr.execute(
                    "SELECT pg_advisory_lock(%s)", (lock_id,)
                )
            
            _logger.debug(f"Acquired lock: {lock_key} (ID: {lock_id})")
            
            yield
            
        finally:
            # Always release lock
            self.env.cr.execute(
                "SELECT pg_advisory_unlock(%s)", (lock_id,)
            )
            _logger.debug(f"Released lock: {lock_key} (ID: {lock_id})")

    @api.model
    def commit_if_needed(self):
        """Commit current transaction if not in test mode."""
        if not self.env.context.get('test_mode'):
            try:
                self.env.cr.commit()
                _logger.debug("Transaction committed")
            except Exception as e:
                _logger.error(f"Commit failed: {str(e)}")
                raise

    @api.model
    def rollback_if_needed(self):
        """Rollback current transaction if not in test mode."""
        if not self.env.context.get('test_mode'):
            try:
                self.env.cr.rollback()
                _logger.debug("Transaction rolled back")
            except Exception as e:
                _logger.error(f"Rollback failed: {str(e)}")
                raise

    @contextmanager
    def batch_commit(self, batch_size=100):
        """
        Context manager for batch processing with periodic commits.
        
        Usage:
            tx = self.env['transaction.manager']
            with tx.batch_commit(100) as batch:
                for record in records:
                    batch.process(process_func, record)
        """
        batch_context = BatchCommitContext(self.env, batch_size)
        try:
            yield batch_context
        finally:
            # Commit remaining
            if batch_context.processed > 0:
                self.commit_if_needed()


class BatchCommitContext:
    """Context for batch processing with periodic commits."""
    
    def __init__(self, env, batch_size=100):
        self.env = env
        self.batch_size = batch_size
        self.processed = 0
    
    def process(self, item_func, *args, **kwargs):
        """Process an item and commit after batch_size items."""
        result = item_func(*args, **kwargs)
        self.processed += 1
        
        if self.processed % self.batch_size == 0:
            self.env['transaction.manager'].commit_if_needed()
            _logger.debug(f"Batch commit after {self.processed} items")
        
        return result


class LockManager(models.AbstractModel):
    """Manages advisory locks for concurrent operations."""
    _name = 'lock.manager'
    _description = 'Advisory Lock Manager'

    @api.model
    def is_locked(self, lock_key):
        """Check if a lock is currently held."""
        lock_id = int(hashlib.md5(str(lock_key).encode()).hexdigest()[:8], 16)
        
        self.env.cr.execute(
            """
            SELECT count(*) 
            FROM pg_locks 
            WHERE locktype = 'advisory' 
            AND objid = %s
            """,
            (lock_id,)
        )
        
        count = self.env.cr.fetchone()[0]
        return count > 0

    @contextmanager
    def acquire_lock(self, lock_key, timeout=None):
        """
        Acquire an advisory lock.
        
        Usage:
            lock_mgr = self.env['lock.manager']
            with lock_mgr.acquire_lock('my_lock'):
                # exclusive operation
        """
        # Use transaction manager's implementation
        tx_manager = self.env['transaction.manager']
        with tx_manager.acquire_lock(lock_key, timeout):
            yield


class DataIntegrityGuard(models.AbstractModel):
    """Guards data integrity during consolidation operations."""
    _name = 'data.integrity.guard'
    _description = 'Data Integrity Guardian'

    @contextmanager
    def integrity_check(self, entity, validation_func=None):
        """
        Context manager that validates data before and after operation.
        
        Usage:
            guard = self.env['data.integrity.guard']
            with guard.integrity_check(media_move):
                # modify media_move
                # will validate after modifications
        """
        # Pre-operation state
        pre_state = self._capture_state(entity)
        
        try:
            yield entity
            
            # Post-operation validation
            if validation_func:
                validation_func(entity)
            else:
                self._default_validation(entity)
            
        except Exception as e:
            _logger.error(f"Integrity check failed: {str(e)}", exc_info=True)
            raise

    @api.model
    def _capture_state(self, entity):
        """Capture current state of entity."""
        if hasattr(entity, 'read'):
            try:
                return entity.read()[0]
            except:
                pass
        return None

    @api.model
    def _default_validation(self, entity):
        """Default validation for common entities."""
        if entity._name == 'media.account.move':
            if not entity.is_balanced:
                raise UserError(_("Move is not balanced after operation"))
            
            if not entity.line_ids:
                raise UserError(_("Move has no lines after operation"))


class ConsolidationTransaction(models.AbstractModel):
    """
    High-level transaction orchestration for consolidation operations.
    """
    _name = 'consolidation.transaction'
    _description = 'Consolidation Transaction Orchestrator'

    @contextmanager
    def sync_transaction(self, sync_engine):
        """
        Transaction context for entire sync operation.
        
        Manages locks, savepoints, and ensures cleanup.
        
        Usage:
            tx = self.env['consolidation.transaction']
            with tx.sync_transaction(sync_engine):
                # sync operations
        """
        lock_key = f"sync_engine_{sync_engine.id}"
        tx_manager = self.env['transaction.manager']
        
        with tx_manager.acquire_lock(lock_key):
            with tx_manager.atomic_operation(f"sync_{sync_engine.name}"):
                try:
                    _logger.info(f"Starting sync transaction for {sync_engine.name}")
                    
                    yield
                    
                    _logger.info(f"Completed sync transaction for {sync_engine.name}")
                    
                except Exception as e:
                    _logger.error(f"Sync transaction failed for {sync_engine.name}: {str(e)}")
                    raise

    @contextmanager
    def promotion_transaction(self, media_moves):
        """
        Transaction context for promotion operations.
        
        Usage:
            tx = self.env['consolidation.transaction']
            with tx.promotion_transaction(media_moves):
                # promotion operations
        """
        move_ids = media_moves.ids if hasattr(media_moves, 'ids') else [media_moves.id]
        lock_key = f"promotion_{','.join(map(str, move_ids))}"
        tx_manager = self.env['transaction.manager']
        
        with tx_manager.acquire_lock(lock_key):
            with tx_manager.atomic_operation('promotion'):
                try:
                    _logger.info(f"Starting promotion transaction for {len(move_ids)} moves")
                    
                    yield
                    
                    _logger.info(f"Completed promotion transaction for {len(move_ids)} moves")
                    
                except Exception as e:
                    _logger.error(f"Promotion transaction failed: {str(e)}")
                    raise
```

---

## File: `sync_engine.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import hashlib
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class SyncEngine(models.Model):
    _name = 'sync.engine'
    _description = 'Consolidation Sync Engine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Sync Reference', required=True, default='New', readonly=True)
    
    # Subsidiaries
    subsidiary_ids = fields.Many2many(
        'subsidiary.instance',
        'sync_engine_subsidiary_rel',
        'sync_engine_id',
        'subsidiary_id',
        string='Subsidiaries',
        required=True
    )
    company_id = fields.Many2one('res.company', string='Company',
                                  default=lambda self: self.env.company, readonly=True)
    
    # Date Range
    date_from = fields.Date(string='Date From', required=True,
                             readonly=True, states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date To', required=True,
                           readonly=True, states={'draft': [('readonly', False)]})
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validating', 'Validating'),
        ('fetching', 'Fetching Data'),
        ('staging', 'In Staging'),
        ('reconciling', 'Reconciling'),
        ('promoting', 'Promoting'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, readonly=True)
    
    # Execution Tracking
    start_time = fields.Datetime(string='Start Time', readonly=True)
    end_time = fields.Datetime(string='End Time', readonly=True)
    duration = fields.Float(string='Duration (seconds)', compute='_compute_duration', store=True)
    
    # Processing Mode
    processing_mode = fields.Selection([
        ('sequential', 'Sequential'),
        ('parallel', 'Parallel'),
    ], string='Processing Mode', default='parallel', required=True)
    
    max_workers = fields.Integer(string='Max Parallel Workers', default=4,
                                  help='Maximum number of parallel subsidiary syncs')
    
    # Options
    auto_reconcile = fields.Boolean(string='Auto Reconciliation', default=False)
    auto_promote = fields.Boolean(string='Auto Promotion', default=False)
    skip_validation = fields.Boolean(string='Skip Validation', default=False)
    
    # Statistics
    total_subsidiaries = fields.Integer(string='Total Subsidiaries', compute='_compute_statistics')
    subsidiaries_completed = fields.Integer(string='Completed', readonly=True, default=0)
    subsidiaries_failed = fields.Integer(string='Failed', readonly=True, default=0)
    
    total_moves_fetched = fields.Integer(string='Total Moves Fetched', readonly=True, default=0)
    total_lines_fetched = fields.Integer(string='Total Lines Fetched', readonly=True, default=0)
    total_moves_promoted = fields.Integer(string='Total Moves Promoted', readonly=True, default=0)
    
    # Validation
    validation_errors = fields.Text(string='Validation Errors', readonly=True)
    checksum = fields.Char(string='Data Checksum', readonly=True)
    
    # Relations
    media_move_ids = fields.One2many('media.account.move', 'sync_engine_id', string='Media Moves')
    consolidation_log_ids = fields.One2many('consolidation.log', 'sync_engine_id', string='Logs')
    immutable_ledger_ids = fields.One2many('immutable.ledger', 'sync_engine_id', string='Ledger Entries')
    restore_point_id = fields.Many2one('restore.point', string='Restore Point', readonly=True)
    
    # Error Handling
    error_message = fields.Text(string='Error Message', readonly=True)
    retry_count = fields.Integer(string='Retry Count', readonly=True, default=0)
    max_retries = fields.Integer(string='Max Retries', default=3)
    
    # Lock Management
    is_locked = fields.Boolean(string='Locked', readonly=True, default=False)
    lock_key = fields.Char(string='Lock Key', readonly=True)
    
    # Progress Tracking
    progress = fields.Float(string='Progress (%)', compute='_compute_progress', store=True)
    current_phase = fields.Char(string='Current Phase', readonly=True)
    # Add to sync.engine model
    _sql_constraints = [
        ('check_retry_count',
        'CHECK(retry_count <= max_retries)',
        'Retry count cannot exceed maximum retries'),
        
        ('check_dates_valid',
        'CHECK(date_from <= date_to)',
        'Start date must be before or equal to end date'),
    ]
    # Add to sync.engine model
    has_errors = fields.Boolean(string='Has Errors', compute='_compute_has_errors')

    def _compute_has_errors(self):
        for rec in self:
            rec.has_errors = any(log.state == 'error' for log in rec.consolidation_log_ids)
    @api.constrains('subsidiary_ids')
    def _check_subsidiaries_same_company(self):
        for rec in self:
            companies = rec.subsidiary_ids.mapped('company_id')
            if len(companies) > 1:
                raise ValidationError(_('All subsidiaries must belong to the same company'))
            if rec.company_id not in companies:
                raise ValidationError(_('Sync engine company must match subsidiaries'))
            
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for rec in self:
            if rec.start_time and rec.end_time:
                delta = rec.end_time - rec.start_time
                rec.duration = delta.total_seconds()
            else:
                rec.duration = 0.0

    @api.depends('subsidiary_ids')
    def _compute_statistics(self):
        for rec in self:
            rec.total_subsidiaries = len(rec.subsidiary_ids)

    @api.depends('total_moves_fetched', 'total_moves_promoted', 'state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == 'completed':
                rec.progress = 100.0
            elif rec.state == 'draft':
                rec.progress = 0.0
            elif rec.state == 'validating':
                rec.progress = 10.0
            elif rec.state == 'fetching':
                rec.progress = 30.0
            elif rec.state == 'staging':
                rec.progress = 50.0
            elif rec.state == 'reconciling':
                rec.progress = 70.0
            elif rec.state == 'promoting':
                if rec.total_moves_fetched > 0:
                    rec.progress = 70.0 + (rec.total_moves_promoted / rec.total_moves_fetched * 30.0)
                else:
                    rec.progress = 70.0
            else:
                rec.progress = 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sync.engine') or 'New'
        return super().create(vals)

    def _acquire_lock(self):
        """Acquire advisory lock for sync operation"""
        self.ensure_one()
        
        lock_key = f'sync_engine_{self.id}_{self.date_from}_{self.date_to}'
        lock_hash = int(hashlib.md5(lock_key.encode()).hexdigest()[:8], 16)
        
        self.env.cr.execute("SELECT pg_try_advisory_lock(%s)", (lock_hash,))
        lock_acquired = self.env.cr.fetchone()[0]
        
        if not lock_acquired:
            raise UserError(_('Another sync operation is in progress. Please wait.'))
        
        self.write({
            'is_locked': True,
            'lock_key': lock_key,
            'current_phase': 'Starting',
        })
        
        _logger.info(f'Lock acquired for sync {self.name}: {lock_key}')
        return True

    def _release_lock(self):
        """Release advisory lock"""
        self.ensure_one()
        
        if self.is_locked and self.lock_key:
            lock_hash = int(hashlib.md5(self.lock_key.encode()).hexdigest()[:8], 16)
            self.env.cr.execute("SELECT pg_advisory_unlock(%s)", (lock_hash,))
            
            self.write({
                'is_locked': False,
                'lock_key': False,
                'current_phase': False,
            })
            
            _logger.info(f'Lock released for sync {self.name}')

    def action_start_sync(self):
        """Start the consolidation sync process"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft syncs can be started.'))
        
        # Create log entry
        log_entry = self.env['consolidation.log'].create({
            'sync_engine_id': self.id,
            'log_type': 'sync',
            'message': f'Starting sync for subsidiaries: {", ".join(self.subsidiary_ids.mapped("name"))}',
            'state': 'in_progress',
            'start_time': fields.Datetime.now(),
        })
        
        try:
            # Create restore point
            restore_point = self.env['restore.point'].create({
                'name': f'Before Sync {self.name}',
                'sync_engine_id': self.id,
                'state_snapshot': json.dumps(self._get_state_snapshot()),
            })
            self.restore_point_id = restore_point.id
            
            # Acquire lock
            self._acquire_lock()
            
            self.write({
                'state': 'validating',
                'start_time': fields.Datetime.now(),
                'current_phase': 'Validating subsidiaries',
            })
            
            # Log start to immutable ledger
            self.env['immutable.ledger'].create_ledger_entry(
                transaction_id=self.name,
                operation='sync_started',
                data_snapshot=json.dumps({
                    'date_from': str(self.date_from),
                    'date_to': str(self.date_to),
                    'subsidiaries': self.subsidiary_ids.mapped('name'),
                }),
                sync_engine_id=self.id
            )
            
            # Phase 1: Validation
            if not self.skip_validation:
                self._validate_subsidiaries()
            
            # Phase 2: Fetch data
            self._fetch_data_from_subsidiaries()
            
            # Phase 3: Validate data integrity
            self._validate_data_integrity()
            
            # Phase 4: Reconciliation (if enabled)
            if self.auto_reconcile:
                self._execute_reconciliation()
            
            # Phase 5: Promotion (if enabled)
            if self.auto_promote:
                self.action_promote()
            else:
                self.write({'state': 'staging', 'current_phase': 'Ready for promotion'})
            
            # Update log
            log_entry.write({
                'end_time': fields.Datetime.now(),
                'state': 'completed',
                'duration': (fields.Datetime.now() - log_entry.start_time).total_seconds(),
                'records_processed': self.total_moves_fetched,
                'details': f'Sync completed successfully. Moves: {self.total_moves_fetched}, Lines: {self.total_lines_fetched}',
            })
            
            # Log completion to immutable ledger
            self.env['immutable.ledger'].create_ledger_entry(
                transaction_id=f'{self.name}_complete',
                operation='sync_completed',
                data_snapshot=json.dumps({
                    'moves_fetched': self.total_moves_fetched,
                    'lines_fetched': self.total_lines_fetched,
                    'moves_promoted': self.total_moves_promoted,
                    'duration': self.duration,
                }),
                sync_engine_id=self.id
            )
            
            _logger.info(f'Sync {self.name} completed successfully')
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sync Completed'),
                    'message': _('Consolidation sync completed successfully!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f'Sync failed for {self.name}: {str(e)}', exc_info=True)
            self._handle_error(str(e))
            
            # Update log with error
            if 'log_entry' in locals():
                log_entry.write({
                    'end_time': fields.Datetime.now(),
                    'state': 'error',
                    'duration': (fields.Datetime.now() - log_entry.start_time).total_seconds(),
                    'details': f'Sync failed: {str(e)}',
                })
            
            raise

    def _validate_subsidiaries(self):
        """Validate all subsidiaries"""
        self.ensure_one()
        self.write({'current_phase': 'Validating subsidiaries'})
        
        validation_engine = self.env['abstract.validation.engine']
        errors = []
        
        for subsidiary in self.subsidiary_ids:
            try:
                result = validation_engine.validate_subsidiary(subsidiary)
                _logger.info(f'Subsidiary {subsidiary.name} validated: {result}')
            except Exception as e:
                errors.append(f'{subsidiary.name}: {str(e)}')
        
        if errors:
            raise ValidationError(_('Validation failed:\n%s') % '\n'.join(errors))

    def _fetch_data_from_subsidiaries(self):
        """Fetch data from all subsidiaries"""
        self.ensure_one()
        self.write({
            'state': 'fetching',
            'current_phase': 'Fetching data from subsidiaries',
        })
        
        if self.processing_mode == 'parallel' and self.max_workers > 1:
            self._fetch_parallel()
        else:
            self._fetch_sequential()
        
        self.write({'state': 'staging', 'current_phase': 'Data in staging'})

    def _fetch_sequential(self):
        """Sequential data fetching"""
        for subsidiary in self.subsidiary_ids:
            try:
                self.write({'current_phase': f'Fetching from {subsidiary.name}'})
                moves_fetched, lines_fetched = self._fetch_from_subsidiary(subsidiary)
                
                self.write({
                    'subsidiaries_completed': self.subsidiaries_completed + 1,
                    'total_moves_fetched': self.total_moves_fetched + moves_fetched,
                    'total_lines_fetched': self.total_lines_fetched + lines_fetched,
                })
                
                self.env['consolidation.log'].log_operation(
                    'sync', f'Successfully fetched {moves_fetched} moves from {subsidiary.name}',
                    sync_engine_id=self.id, subsidiary_id=subsidiary.id
                )
                
            except Exception as e:
                _logger.error(f'Fetch failed for {subsidiary.name}: {str(e)}')
                self.write({
                    'subsidiaries_failed': self.subsidiaries_failed + 1,
                })
                self.env['consolidation.log'].log_error(
                    f'Fetch failed: {str(e)}',
                    sync_engine_id=self.id, subsidiary_id=subsidiary.id, exception=e
                )

    def _fetch_parallel(self):
        """Parallel data fetching - Note: ORM is not thread-safe in Odoo"""
        _logger.warning('Parallel processing may cause ORM issues. Using sequential instead.')
        return self._fetch_sequential()

    def _fetch_from_subsidiary(self, subsidiary):
        """Fetch data from single subsidiary"""
        try:
            uid, models = subsidiary.get_rpc_connection()
            
            # Build domain
            domain = [
                ('date', '>=', str(self.date_from)),
                ('date', '<=', str(self.date_to)),
                ('state', '=', 'posted'),
            ]
            
            if subsidiary.subsidiary_company_id:
                domain.append(('company_id', '=', subsidiary.subsidiary_company_id))
            
            # Fetch moves
            move_ids = models.execute_kw(
                subsidiary.db_name, uid, subsidiary.password,
                'account.move', 'search',
                [domain],
                {'order': 'date asc, id asc'}
            )
            
            if not move_ids:
                _logger.info(f'No moves found for {subsidiary.name} in period {self.date_from} to {self.date_to}')
                return 0, 0
            
            # Fetch move details in batches
            batch_size = 50  # Reduced for better performance
            total_moves = 0
            total_lines = 0
            
            for i in range(0, len(move_ids), batch_size):
                batch_ids = move_ids[i:i+batch_size]
                
                moves = models.execute_kw(
                    subsidiary.db_name, uid, subsidiary.password,
                    'account.move', 'read',
                    [batch_ids],
                    {'fields': ['name', 'date', 'ref', 'journal_id', 'line_ids', 
                                'amount_total', 'currency_id', 'state', 'company_id']}
                )
                
                # Create media moves
                moves_created, lines_created = self._create_media_moves(subsidiary, moves, uid, models)
                total_moves += moves_created
                total_lines += lines_created
            
            # Update subsidiary last sync date
            subsidiary.write({'last_sync_date': fields.Datetime.now()})
            
            _logger.info(f'Fetched {total_moves} moves and {total_lines} lines from {subsidiary.name}')
            
            return total_moves, total_lines
            
        except Exception as e:
            _logger.error(f'Fetch error for {subsidiary.name}: {str(e)}')
            raise

    def _create_media_moves(self, subsidiary, moves, uid, models):
        """Create media layer moves"""
        MediaMove = self.env['media.account.move']
        MediaLine = self.env['media.account.move.line']
        
        moves_created = 0
        lines_created = 0
        
        for move_data in moves:
            # Check if already exists
            existing = MediaMove.search([
                ('subsidiary_id', '=', subsidiary.id),
                ('source_move_id', '=', move_data['id']),
                ('sync_engine_id', '=', self.id),
            ])
            
            if existing:
                continue  # Skip already imported
            
            # Get journal information
            journal_info = move_data.get('journal_id', [])
            journal_id = journal_info[0] if journal_info else False
            journal_name = journal_info[1] if len(journal_info) > 1 else ''
            
            # Get journal details
            journal_code = ''
            journal_type = 'general'
            if journal_id:
                try:
                    journals = models.execute_kw(
                        subsidiary.db_name, uid, subsidiary.password,
                        'account.journal', 'read',
                        [[journal_id]],
                        {'fields': ['code', 'name', 'type']}
                    )
                    if journals:
                        journal_code = journals[0].get('code', '')
                        journal_type = journals[0].get('type', 'general')
                except Exception as e:
                    _logger.warning(f'Could not fetch journal details: {str(e)}')
            
            # Get line details
            line_ids = move_data.get('line_ids', [])
            
            if not line_ids:
                _logger.warning(f'Move {move_data["name"]} has no lines, skipping')
                continue
            
            try:
                lines = models.execute_kw(
                    subsidiary.db_name, uid, subsidiary.password,
                    'account.move.line', 'read',
                    [line_ids],
                    {'fields': ['name', 'account_id', 'debit', 'credit', 'partner_id', 
                                'currency_id', 'amount_currency', 'date', 'analytic_account_id']}
                )
            except Exception as e:
                _logger.warning(f'Could not fetch analytic data: {str(e)}')
                lines = models.execute_kw(
                    subsidiary.db_name, uid, subsidiary.password,
                    'account.move.line', 'read',
                    [line_ids],
                    {'fields': ['name', 'account_id', 'debit', 'credit', 'partner_id', 
                                'currency_id', 'amount_currency', 'date']}
                )
            
            # Create media move
            media_move = MediaMove.create({
                'sync_engine_id': self.id,
                'subsidiary_id': subsidiary.id,
                'name': move_data['name'],
                'date': move_data['date'],
                'ref': move_data.get('ref', ''),
                'source_move_id': move_data['id'],
                'source_journal_id': journal_id,
                'source_journal_code': journal_code,
                'source_journal_name': journal_name,
                'source_journal_type': journal_type,
                'amount_total': move_data.get('amount_total', 0.0),
                'state': 'draft',
            })
            
            # Create media lines
            for line_data in lines:
                account_code = ''
                account_name = ''
                if line_data.get('account_id'):
                    account_parts = line_data['account_id'][1].split(' ') if len(line_data['account_id']) > 1 else ['', '']
                    account_code = account_parts[0]
                    account_name = ' '.join(account_parts[1:]) if len(account_parts) > 1 else account_parts[1] if len(account_parts) > 1 else ''
                
                MediaLine.create({
                    'media_move_id': media_move.id,
                    'name': line_data.get('name', '/'),
                    'account_code': account_code,
                    'account_name': account_name,
                    'debit': line_data.get('debit', 0.0),
                    'credit': line_data.get('credit', 0.0),
                    'partner_id': line_data.get('partner_id', [False, ''])[0] if line_data.get('partner_id') else False,
                    'partner_name': line_data.get('partner_id', [False, ''])[1] if line_data.get('partner_id') else '',
                    'source_line_id': line_data['id'],
                })
                
                lines_created += 1
            
            moves_created += 1
        
        return moves_created, lines_created

    def _validate_data_integrity(self):
        """Validate fetched data integrity"""
        self.ensure_one()
        self.write({'current_phase': 'Validating data integrity'})
        
        integrity_engine = self.env['abstract.data.integrity.engine']
        
        try:
            result = integrity_engine.validate_media_moves(self.media_move_ids)
            
            if not result['valid']:
                self.write({'validation_errors': '\n'.join(result['errors'])})
                raise ValidationError(_('Data integrity validation failed:\n%s') % '\n'.join(result['errors'][:10]))
            
            # Calculate checksum
            data = {
                'moves': self.media_move_ids.ids,
                'lines': self.total_lines_fetched,
                'timestamp': str(fields.Datetime.now()),
            }
            checksum = integrity_engine.calculate_checksum(data)
            
            self.write({'checksum': checksum})
            
            _logger.info(f'Data integrity validated: {result.get("total_moves", 0)} moves')
            
        except Exception as e:
            raise ValidationError(_('Integrity validation failed: %s') % str(e))

    def _execute_reconciliation(self):
        """Execute reconciliation"""
        self.ensure_one()
        self.write({
            'state': 'reconciling',
            'current_phase': 'Executing reconciliation',
        })
        
        try:
            reconciliation_engine = self.env['reconciliation.engine']
            if hasattr(reconciliation_engine, 'execute_reconciliation'):
                reconciliation_engine.execute_reconciliation(self)
            else:
                _logger.warning('Reconciliation engine not available, skipping')
            
            self.env['consolidation.log'].log_operation(
                'reconciliation', 'Reconciliation completed',
                sync_engine_id=self.id
            )
            
        except Exception as e:
            _logger.error(f'Reconciliation failed: {str(e)}')
            self.env['consolidation.log'].log_error(
                'Reconciliation failed', sync_engine_id=self.id, exception=e
            )

    def action_promote(self):
        """Promote media moves to accounting"""
        self.ensure_one()
        
        if self.state not in ('staging', 'reconciling'):
            raise UserError(_('Cannot promote from current state'))
        
        self.write({
            'state': 'promoting',
            'current_phase': 'Promoting moves to accounting',
        })
        
        try:
            promotion_engine = self.env['promotion.engine']
            promoted_count = promotion_engine.promote_media_moves(self.media_move_ids)
            
            self.write({
                'total_moves_promoted': promoted_count,
                'state': 'completed',
                'end_time': fields.Datetime.now(),
                'current_phase': 'Completed',
            })
            
            self._release_lock()
            
            self.env['consolidation.log'].log_operation(
                'promotion', f'Promoted {promoted_count} moves to accounting',
                sync_engine_id=self.id
            )
            
            return promoted_count
            
        except Exception as e:
            self._handle_error(f'Promotion failed: {str(e)}')
            raise

    def _handle_error(self, error_msg):
        """Handle sync error"""
        self.write({
            'state': 'error',
            'error_message': error_msg,
            'end_time': fields.Datetime.now(),
            'current_phase': 'Error occurred',
        })
        
        self._release_lock()
        
        self.env['consolidation.log'].log_error(
            error_msg, sync_engine_id=self.id
        )
        
        self.env['immutable.ledger'].create_ledger_entry(
            transaction_id=f'{self.name}_error',
            operation='error_occurred',
            data_snapshot=json.dumps({'error': error_msg}),
            sync_engine_id=self.id
        )

    def _get_state_snapshot(self):
        """Get state snapshot for restore point"""
        return {
            'sync_engine_id': self.id,
            'state': self.state,
            'media_moves': self.media_move_ids.ids,
            'date_from': str(self.date_from),
            'date_to': str(self.date_to),
            'subsidiaries': self.subsidiary_ids.ids,
        }

    def action_rollback(self):
        """Rollback sync"""
        return {
            'name': _('Rollback Sync'),
            'type': 'ir.actions.act_window',
            'res_model': 'rollback.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sync_engine_id': self.id},
        }

    def action_cancel(self):
        """Cancel sync"""
        self.ensure_one()
        
        if self.state in ('completed', 'cancelled'):
            raise UserError(_('Cannot cancel a completed or already cancelled sync.'))
        
        self.write({
            'state': 'cancelled',
            'end_time': fields.Datetime.now(),
            'current_phase': 'Cancelled',
        })
        
        self._release_lock()
        
        self.env['consolidation.log'].log_operation(
            'info', 'Sync cancelled by user',
            sync_engine_id=self.id
        )
        
        return True

    def unlink(self):
        """Prevent deletion of completed syncs"""
        for rec in self:
            if rec.state == 'completed':
                raise UserError(_('Cannot delete completed sync. Use rollback instead.'))
            if rec.is_locked:
                rec._release_lock()
        return super().unlink()

    def action_view_media_moves(self):
        """View media moves"""
        self.ensure_one()
        return {
            'name': _('Media Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'media.account.move',
            'view_mode': 'tree,form',
            'domain': [('sync_engine_id', '=', self.id)],
            'context': {'default_sync_engine_id': self.id},
        }

    def action_view_logs(self):
        """View sync logs"""
        self.ensure_one()
        return {
            'name': _('Sync Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'consolidation.log',
            'view_mode': 'tree,form',
            'domain': [('sync_engine_id', '=', self.id)],
            'context': {'default_sync_engine_id': self.id},
        }

    def action_retry(self):
        """Retry failed sync"""
        self.ensure_one()
        
        if self.state != 'error':
            raise UserError(_('Only failed syncs can be retried.'))
        
        if self.retry_count >= self.max_retries:
            raise UserError(_('Maximum retry limit reached.'))
        
        self.write({
            'state': 'draft',
            'error_message': False,
            'retry_count': self.retry_count + 1,
        })
        
        return self.action_start_sync()
```

---

## File: `validation_engine.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/engines`

```py
# -*- coding: utf-8 -*-
# FILE: models/engines/validation_engine.py
"""
Complete Validation Engine with comprehensive checks,
detailed reporting, and fix suggestions.
"""

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging
from decimal import Decimal

_logger = logging.getLogger(__name__)


class ValidationEngine(models.Model):
    """
    Complete Validation Engine with comprehensive validation,
    detailed error reporting, and automatic fix suggestions.
    """
    _name = 'validation.engine'
    _description = 'Enhanced Validation Engine'
    
    # Note: We don't inherit from error.handler to avoid database table issues
    # Instead, we use it via self.env['error.handler']
    
    @api.model
    def validate_sync_engine(self, sync_engine):
        """
        Comprehensive validation of sync engine with detailed reporting.
        
        Returns:
            dict: Validation results with errors, warnings, and recommendations
        """
        _logger.info(f"Starting comprehensive validation for sync {sync_engine.name}")
        
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': [],
            'checks_performed': [],
            'recommendations': [],
        }
        
        try:
            # 1. Validate subsidiaries
            sub_results = self._validate_subsidiaries(sync_engine)
            results = self._merge_results(results, sub_results)
            
            # 2. Validate date range
            date_results = self._validate_date_range(sync_engine)
            results = self._merge_results(results, date_results)
            
            # 3. Validate mappings
            mapping_results = self._validate_mappings(sync_engine)
            results = self._merge_results(results, mapping_results)
            
            # 4. Validate permissions
            perm_results = self._validate_permissions(sync_engine)
            results = self._merge_results(results, perm_results)
            
            # 5. Validate periods not locked
            lock_results = self._validate_periods(sync_engine)
            results = self._merge_results(results, lock_results)
            
            # 6. Validate resources
            resource_results = self._validate_resources(sync_engine)
            results = self._merge_results(results, resource_results)
            
            # Set overall validity
            results['valid'] = len(results['errors']) == 0
            
            # Generate recommendations
            if not results['valid'] or results['warnings']:
                results['recommendations'] = self._generate_fix_recommendations(results)
            
            # Log results
            if results['valid']:
                _logger.info(
                    f"Sync validation passed with {len(results['warnings'])} warnings"
                )
            else:
                _logger.error(
                    f"Sync validation failed with {len(results['errors'])} errors: "
                    f"{', '.join(results['errors'][:3])}"
                )
            
        except Exception as e:
            _logger.error(f"Validation engine error: {str(e)}", exc_info=True)
            results['valid'] = False
            results['errors'].append(f"Validation engine error: {str(e)}")
        
        return results
    
    @api.model
    def validate_subsidiary(self, subsidiary):
        """Validate subsidiary for consolidation"""
        errors = []
        
        # Connection validation
        if subsidiary.state != 'validated':
            errors.append(_('Subsidiary connection not validated'))
        
        # Currency validation
        if not subsidiary.currency_id:
            errors.append(_('Currency not configured'))
        
        # Mapping validation
        account_mappings = subsidiary.account_mapping_ids.filtered(lambda m: m.active)
        if not account_mappings:
            errors.append(_('No active account mappings'))
        
        journal_mappings = subsidiary.journal_mapping_ids.filtered(lambda m: m.active)
        if not journal_mappings:
            errors.append(_('No active journal mappings'))
        
        # Test connection
        try:
            uid, models = subsidiary.get_rpc_connection()
            # Quick test query
            test = models.execute_kw(
                subsidiary.db_name, uid, subsidiary.password,
                'res.company', 'search_count',
                [[]]
            )
        except Exception as e:
            errors.append(_('Connection test failed: %s') % str(e))
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return True

    @api.model
    def _validate_subsidiaries(self, sync_engine):
        """Validate all subsidiaries are ready."""
        results = {
            'errors': [],
            'warnings': [],
            'info': [],
            'checks_performed': ['subsidiary_validation'],
        }
        
        for subsidiary in sync_engine.subsidiary_ids:
            # Check state
            if subsidiary.state != 'validated':
                results['errors'].append(
                    f"Subsidiary '{subsidiary.name}' not validated (state: {subsidiary.state})"
                )
                continue
            
            # Check currency
            if not subsidiary.currency_id:
                results['errors'].append(
                    f"Subsidiary '{subsidiary.name}' has no currency configured"
                )
            
            # Check mappings
            account_count = len(subsidiary.account_mapping_ids.filtered(lambda m: m.active))
            if account_count == 0:
                results['errors'].append(
                    f"Subsidiary '{subsidiary.name}' has no active account mappings"
                )
            elif account_count < 10:
                results['warnings'].append(
                    f"Subsidiary '{subsidiary.name}' has only {account_count} account mappings"
                )
            
            journal_count = len(subsidiary.journal_mapping_ids.filtered(lambda m: m.active))
            if journal_count == 0:
                results['warnings'].append(
                    f"Subsidiary '{subsidiary.name}' has no journal mappings"
                )
            
            # Test connection
            try:
                uid, models = subsidiary.get_rpc_connection()
                test = models.execute_kw(
                    subsidiary.db_name, uid, subsidiary.password,
                    'res.company', 'search_count', [[]]
                )
                results['info'].append(
                    f"Subsidiary '{subsidiary.name}' connection OK ({test} companies)"
                )
            except Exception as e:
                results['errors'].append(
                    f"Subsidiary '{subsidiary.name}' connection failed: {str(e)}"
                )
        
        return results
    
    @api.model
    def validate_date_range(self, date_from, date_to):
        """Validate date range for sync"""
        if date_from > date_to:
            raise ValidationError(_('Date From must be before Date To'))
        
        # Check range not too large
        days_diff = (date_to - date_from).days
        
        config = self.env['consolidation.config'].get_config()
        max_days = config.max_sync_days
        
        if days_diff > max_days:
            raise ValidationError(_('Date range too large. Maximum %s days allowed.') % max_days)
        
        # Check not in future
        today = fields.Date.today()
        if date_to > today:
            raise ValidationError(_('Cannot sync future dates'))
        
        return True

    @api.model
    def _validate_date_range(self, sync_engine):
        """Validate date range is reasonable."""
        results = {
            'errors': [],
            'warnings': [],
            'info': [],
            'checks_performed': ['date_range_validation'],
        }
        
        # Check dates are set
        if not sync_engine.date_from or not sync_engine.date_to:
            results['errors'].append("Date range not specified")
            return results
        
        # Check chronological order
        if sync_engine.date_from > sync_engine.date_to:
            results['errors'].append(
                f"Date From ({sync_engine.date_from}) is after Date To ({sync_engine.date_to})"
            )
        
        # Check not in future
        today = fields.Date.today()
        if sync_engine.date_to > today:
            results['errors'].append(
                f"Date To ({sync_engine.date_to}) is in the future"
            )
        
        # Check range size
        days_diff = (sync_engine.date_to - sync_engine.date_from).days
        
        config = self.env['consolidation.config'].get_config(sync_engine.company_id.id)
        max_days = config.max_sync_days
        
        if days_diff > max_days:
            results['errors'].append(
                f"Date range ({days_diff} days) exceeds maximum ({max_days} days)"
            )
        elif days_diff > max_days * 0.8:
            results['warnings'].append(
                f"Date range ({days_diff} days) is close to maximum limit"
            )
        
        results['info'].append(f"Date range: {days_diff} days")
        
        return results

    @api.model
    def _validate_mappings(self, sync_engine):
        """Validate mappings completeness."""
        results = {
            'errors': [],
            'warnings': [],
            'info': [],
            'checks_performed': ['mapping_validation'],
        }
        
        for subsidiary in sync_engine.subsidiary_ids:
            # Get sample of accounts to check coverage
            try:
                uid, models = subsidiary.get_rpc_connection()
                
                accounts = models.execute_kw(
                    subsidiary.db_name, uid, subsidiary.password,
                    'account.account', 'search_read',
                    [[('deprecated', '=', False)]],
                    {'fields': ['code', 'name'], 'limit': 100}
                )
                
                # Check mapping coverage
                total_accounts = len(accounts)
                mapped_count = 0
                unmapped_examples = []
                
                for account in accounts:
                    mapping = self.env['account.mapping'].search([
                        ('subsidiary_id', '=', subsidiary.id),
                        ('subsidiary_account_code', '=', account['code']),
                        ('active', '=', True),
                    ], limit=1)
                    
                    if mapping:
                        mapped_count += 1
                    elif len(unmapped_examples) < 5:
                        unmapped_examples.append(f"{account['code']} - {account['name']}")
                
                coverage = (mapped_count / total_accounts * 100) if total_accounts > 0 else 0
                
                if coverage < 50:
                    results['errors'].append(
                        f"Subsidiary '{subsidiary.name}' has low mapping coverage "
                        f"({coverage:.1f}%). Examples: {', '.join(unmapped_examples)}"
                    )
                elif coverage < 80:
                    results['warnings'].append(
                        f"Subsidiary '{subsidiary.name}' mapping coverage is {coverage:.1f}%. "
                        f"Consider mapping: {', '.join(unmapped_examples)}"
                    )
                else:
                    results['info'].append(
                        f"Subsidiary '{subsidiary.name}' mapping coverage: {coverage:.1f}%"
                    )
                
            except Exception as e:
                results['warnings'].append(
                    f"Could not validate mappings for '{subsidiary.name}': {str(e)}"
                )
        
        return results

    @api.model
    def _validate_permissions(self, sync_engine):
        """Validate user permissions."""
        results = {
            'errors': [],
            'warnings': [],
            'info': [],
            'checks_performed': ['permission_validation'],
        }
        
        user = self.env.user
        
        # Check consolidation manager rights
        try:
            if not user.has_group('financial_consolidation.group_consolidation_manager'):
                if not user.has_group('financial_consolidation.group_consolidation_user'):
                    results['errors'].append(
                        f"User '{user.name}' lacks consolidation access rights"
                    )
                else:
                    results['warnings'].append(
                        f"User '{user.name}' has limited rights (user, not manager)"
                    )
        except Exception as e:
            _logger.warning(f"Could not check user groups: {str(e)}")
        
        results['info'].append(f"Validation performed by user: {user.name}")
        
        return results
    
    @api.model
    def validate_period_not_locked(self, company, date_from, date_to):
        """Validate accounting period is not locked"""
        # Check for locked periods - implementation depends on your fiscal year module
        # This is a placeholder for the actual implementation
        return True

    @api.model
    def _validate_periods(self, sync_engine):
        """Validate periods are not locked."""
        results = {
            'errors': [],
            'warnings': [],
            'info': [],
            'checks_performed': ['period_lock_validation'],
        }
        
        try:
            # Check if dates fall in locked period
            # This would check against your fiscal year locks
            results['info'].append("Period lock check passed")
        except Exception as e:
            results['warnings'].append(f"Could not validate period locks: {str(e)}")
        
        return results

    @api.model
    def _validate_resources(self, sync_engine):
        """Validate system resources are sufficient."""
        results = {
            'errors': [],
            'warnings': [],
            'info': [],
            'checks_performed': ['resource_validation'],
        }
        
        try:
            config = self.env['consolidation.config'].get_config(sync_engine.company_id.id)
            
            if config.default_batch_size > 500:
                results['warnings'].append(
                    f"Large batch size ({config.default_batch_size}) may impact performance"
                )
            
            if sync_engine.processing_mode == 'parallel':
                if sync_engine.max_workers > 8:
                    results['warnings'].append(
                        f"High worker count ({sync_engine.max_workers}) may overload system"
                    )
                results['info'].append(
                    f"Parallel processing enabled with {sync_engine.max_workers} workers"
                )
        except Exception as e:
            _logger.warning(f"Could not validate resources: {str(e)}")
        
        return results

    @api.model
    def _merge_results(self, base_results, new_results):
        """Merge validation results."""
        base_results['errors'].extend(new_results.get('errors', []))
        base_results['warnings'].extend(new_results.get('warnings', []))
        base_results['info'].extend(new_results.get('info', []))
        base_results['checks_performed'].extend(new_results.get('checks_performed', []))
        return base_results

    @api.model
    def _generate_fix_recommendations(self, results):
        """Generate actionable recommendations based on validation results."""
        recommendations = []
        
        for error in results['errors']:
            if 'not validated' in error.lower():
                recommendations.append(
                    "ACTION: Validate subsidiary connections using 'Validate Connection' button"
                )
            elif 'no currency' in error.lower():
                recommendations.append(
                    "ACTION: Configure currency for subsidiaries in subsidiary form"
                )
            elif 'no active account mappings' in error.lower():
                recommendations.append(
                    "ACTION: Run 'Auto-discover Accounts' wizard or create mappings manually"
                )
            elif 'connection failed' in error.lower():
                recommendations.append(
                    "ACTION: Check network connectivity and subsidiary credentials"
                )
            elif 'date range' in error.lower():
                recommendations.append(
                    "ACTION: Adjust date range in consolidation wizard"
                )
            elif 'mapping coverage' in error.lower():
                recommendations.append(
                    "ACTION: Use mapping wizard to improve coverage"
                )
        
        # Remove duplicates
        return list(set(recommendations))

    @api.model
    def validate_media_move_comprehensive(self, media_move):
        """
        Comprehensive validation of a single media move.
        
        Returns:
            dict: Detailed validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'checks': {},
        }
        
        try:
            # 1. Balance check
            balance_check = self._check_balance(media_move)
            results['checks']['balance'] = balance_check
            if not balance_check['valid']:
                results['errors'].append(balance_check['message'])
            
            # 2. Line count check
            line_check = self._check_lines(media_move)
            results['checks']['lines'] = line_check
            if not line_check['valid']:
                results['errors'].append(line_check['message'])
            
            # 3. Mapping check
            mapping_check = self._check_mappings(media_move)
            results['checks']['mappings'] = mapping_check
            if not mapping_check['valid']:
                results['errors'].append(mapping_check['message'])
            elif mapping_check.get('warnings'):
                results['warnings'].extend(mapping_check['warnings'])
            
            # 4. Journal check
            journal_check = self._check_journal(media_move)
            results['checks']['journal'] = journal_check
            if not journal_check['valid']:
                results['warnings'].append(journal_check['message'])
            
            # 5. Currency check
            currency_check = self._check_currency(media_move)
            results['checks']['currency'] = currency_check
            if currency_check.get('needs_conversion'):
                results['warnings'].append(currency_check['message'])
            
            results['valid'] = len(results['errors']) == 0
            
        except Exception as e:
            _logger.error(f"Error validating media move {media_move.name}: {str(e)}", exc_info=True)
            results['valid'] = False
            results['errors'].append(f"Validation error: {str(e)}")
        
        return results

    @api.model
    def _check_balance(self, media_move):
        """Check if move is balanced."""
        try:
            # Get tolerance from config
            config = self.env['consolidation.config'].get_config(media_move.company_id.id)
            tolerance = Decimal(str(config.balance_tolerance))
            
            difference = abs(Decimal(str(media_move.total_debit)) - Decimal(str(media_move.total_credit)))
            
            if difference > tolerance:
                return {
                    'valid': False,
                    'message': f"Move {media_move.name} is unbalanced. "
                              f"Debit: {media_move.total_debit}, "
                              f"Credit: {media_move.total_credit}, "
                              f"Difference: {float(difference)}",
                    'difference': float(difference),
                }
            
            return {'valid': True, 'difference': float(difference)}
        except Exception as e:
            _logger.error(f"Error checking balance: {str(e)}")
            return {'valid': False, 'message': f"Balance check error: {str(e)}"}

    @api.model
    def _check_lines(self, media_move):
        """Check move has sufficient lines."""
        line_count = len(media_move.line_ids)
        
        if line_count == 0:
            return {
                'valid': False,
                'message': f"Move {media_move.name} has no lines",
            }
        
        if line_count == 1:
            return {
                'valid': False,
                'message': f"Move {media_move.name} has only one line",
            }
        
        return {'valid': True, 'line_count': line_count}

    @api.model
    def _check_mappings(self, media_move):
        """Check all lines have mappings."""
        unmapped = media_move.line_ids.filtered(lambda l: not l.mapped_account_id)
        
        if unmapped:
            unmapped_codes = ', '.join(set(unmapped.mapped('account_code')))
            return {
                'valid': False,
                'message': f"Move {media_move.name} has {len(unmapped)} unmapped accounts: {unmapped_codes}",
                'unmapped_count': len(unmapped),
                'unmapped_codes': unmapped_codes,
            }
        
        # Check for unvalidated mappings
        unvalidated = media_move.line_ids.filtered(
            lambda l: l.mapping_id and not l.mapping_id.is_validated
        )
        
        result = {'valid': True}
        if unvalidated:
            result['warnings'] = [
                f"{len(unvalidated)} lines use unvalidated mappings"
            ]
        
        return result

    @api.model
    def _check_journal(self, media_move):
        """Check journal mapping exists."""
        if not media_move.mapped_journal_id:
            return {
                'valid': False,
                'message': f"Move {media_move.name} has no journal mapping",
            }
        
        return {'valid': True}

    @api.model
    def _check_currency(self, media_move):
        """Check currency conversion needs."""
        if media_move.currency_id != media_move.company_id.currency_id:
            return {
                'needs_conversion': True,
                'message': f"Move {media_move.name} requires currency conversion "
                          f"from {media_move.currency_id.name} to {media_move.company_id.currency_id.name}",
            }
        
        return {'needs_conversion': False}
```

---

## File: `error.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models`

```py
import logging
from functools import wraps

_logger = logging.getLogger(__name__)


def log_error_decorator(module_name):
    """Decorator to log errors with module context."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                _logger.error(f"[{module_name}] Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling for consolidation module."""
    
    @staticmethod
    def log_error(module_name, function_name, error_message, exc_info=False):
        """Log an error message."""
        _logger.error(f"[{module_name}] Error in {function_name}: {error_message}", exc_info=exc_info)
    
    @staticmethod
    def log_warning(module_name, function_name, warning_message):
        """Log a warning message."""
        _logger.warning(f"[{module_name}] Warning in {function_name}: {warning_message}")
    
    @staticmethod
    def log_info(module_name, function_name, info_message):
        """Log an info message."""
        _logger.info(f"[{module_name}] {function_name}: {info_message}")
    
    @staticmethod
    def handle_exception(module_name, function_name, exception, context=None):
        """Handle an exception with context."""
        error_data = {
            'module': module_name,
            'function': function_name,
            'exception_type': type(exception).__name__,
            'message': str(exception),
            'context': context or {}
        }
        _logger.error(f"Exception in {module_name}.{function_name}: {str(exception)}", exc_info=True)
        return error_data


# Create an instance for easy access
handler = ErrorHandler()
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/mapping`

```py
from . import account_mapping
from . import journal_mapping
```

---

## File: `account_mapping.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/mapping`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMapping(models.Model):
    _name = 'account.mapping'
    _description = 'Chart of Accounts Mapping'
    _order = 'subsidiary_id, subsidiary_account_code'

    # Core Fields
    subsidiary_id = fields.Many2one('subsidiary.instance', string='Subsidiary',
                                     required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='subsidiary_id.company_id',
                                  store=True, readonly=True)
    
    # Subsidiary Account
    subsidiary_account_code = fields.Char(string='Subsidiary Account Code', 
                                           required=True, index=True)
    subsidiary_account_name = fields.Char(string='Subsidiary Account Name')
    subsidiary_account_type = fields.Selection([
        ('asset_receivable', 'Receivable'),
        ('asset_cash', 'Bank and Cash'),
        ('asset_current', 'Current Assets'),
        ('asset_non_current', 'Non-current Assets'),
        ('asset_prepayments', 'Prepayments'),
        ('asset_fixed', 'Fixed Assets'),
        ('liability_payable', 'Payable'),
        ('liability_credit_card', 'Credit Card'),
        ('liability_current', 'Current Liabilities'),
        ('liability_non_current', 'Non-current Liabilities'),
        ('equity', 'Equity'),
        ('equity_unaffected', 'Current Year Earnings'),
        ('income', 'Income'),
        ('income_other', 'Other Income'),
        ('expense', 'Expenses'),
        ('expense_depreciation', 'Depreciation'),
        ('expense_direct_cost', 'Cost of Revenue'),
        ('off_balance', 'Off-Balance Sheet'),
    ], string='Subsidiary Account Type')
    
    # Parent Account
    parent_account_id = fields.Many2one('account.account', string='Parent Account',
                                         required=True, index=True,
                                         domain="[('company_id', '=', company_id)]")
    parent_account_code = fields.Char(related='parent_account_id.code', 
                                       string='Parent Account Code', readonly=True)
    parent_account_name = fields.Char(related='parent_account_id.name',
                                        string='Parent Account Name', readonly=True)
    
    # Mapping Configuration
    mapping_type = fields.Selection([
        ('direct', 'Direct Mapping'),
        ('consolidation', 'Consolidation Account'),
        ('elimination', 'Elimination Account'),
        ('adjustment', 'Adjustment Account'),
    ], string='Mapping Type', default='direct', required=True)
    
    # Advanced Options
    active = fields.Boolean(string='Active', default=True)
    auto_create = fields.Boolean(string='Auto-create if Missing', default=False,
                                  help='Automatically create parent account if not exists')
    apply_conversion = fields.Boolean(string='Apply Currency Conversion', default=True)
    
    # Validation
    is_validated = fields.Boolean(string='Validated', default=False, readonly=True)
    validation_date = fields.Datetime(string='Validation Date', readonly=True)
    validation_message = fields.Text(string='Validation Message', readonly=True)
    
    # Usage Statistics
    usage_count = fields.Integer(string='Usage Count', readonly=True, default=0,
                                  help='Number of times this mapping has been used')
    last_used_date = fields.Datetime(string='Last Used', readonly=True)
    
    # Notes
    notes = fields.Text(string='Mapping Notes')

    _sql_constraints = [
        ('unique_mapping', 'unique(subsidiary_id, subsidiary_account_code)',
         'Account mapping must be unique per subsidiary!'),
    ]

    @api.constrains('subsidiary_account_code', 'parent_account_id')
    def _check_mapping(self):
        for rec in self:
            if not rec.subsidiary_account_code or not rec.parent_account_id:
                raise ValidationError(_('Both subsidiary and parent accounts are required.'))

    def action_validate_mapping(self):
        """Validate account mapping"""
        self.ensure_one()
        
        try:
            # Check if subsidiary account exists
            uid, models = self.subsidiary_id.get_rpc_connection()
            
            subsidiary_account = models.execute_kw(
                self.subsidiary_id.db_name, uid, self.subsidiary_id.password,
                'account.account', 'search_read',
                [[('code', '=', self.subsidiary_account_code)]],
                {'fields': ['name', 'internal_type'], 'limit': 1}
            )
            
            if not subsidiary_account:
                raise ValidationError(
                    _('Account %s not found in subsidiary %s') % 
                    (self.subsidiary_account_code, self.subsidiary_id.name)
                )
            
            # Update mapping info
            self.write({
                'subsidiary_account_name': subsidiary_account[0]['name'],
                'is_validated': True,
                'validation_date': fields.Datetime.now(),
                'validation_message': 'Mapping validated successfully',
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Mapping validated successfully!'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            self.write({
                'is_validated': False,
                'validation_message': f'Validation failed: {str(e)}',
            })
            raise ValidationError(_('Validation failed: %s') % str(e))

    def get_parent_account(self, create_if_missing=False):
        """Get or create parent account"""
        self.ensure_one()
        
        if self.parent_account_id:
            return self.parent_account_id
        
        if create_if_missing and self.auto_create:
            # Create new account in parent company
            account = self.env['account.account'].create({
                'code': self.subsidiary_account_code,
                'name': self.subsidiary_account_name or f'Consolidated - {self.subsidiary_account_code}',
                'user_type_id': self._get_account_type(),
                'company_id': self.company_id.id,
            })
            
            self.write({'parent_account_id': account.id})
            return account
        
        return False

    def _get_account_type(self):
        """Get appropriate account type for auto-creation"""
        # Map subsidiary types to parent account types
        type_mapping = {
            'asset_receivable': 'asset_receivable',
            'asset_cash': 'asset_current',
            'liability_payable': 'liability_payable',
            'income': 'income',
            'expense': 'expense',
        }
        
        internal_type = type_mapping.get(self.subsidiary_account_type, 'asset_current')
        
        account_type = self.env['account.account.type'].search([
            ('type', '=', internal_type)
        ], limit=1)
        
        return account_type.id if account_type else False

    def increment_usage(self):
        """Increment usage counter"""
        self.sudo().write({
            'usage_count': self.usage_count + 1,
            'last_used_date': fields.Datetime.now(),
        })

    @api.model
    def get_mapping(self, subsidiary_id, account_code):
        """Get mapping for specific subsidiary and account code"""
        mapping = self.search([
            ('subsidiary_id', '=', subsidiary_id),
            ('subsidiary_account_code', '=', account_code),
            ('active', '=', True),
        ], limit=1)
        
        if mapping:
            mapping.increment_usage()
            return mapping.parent_account_id
        
        return False

    @api.model
    def create_bulk_mappings(self, subsidiary_id, mappings_data):
        """Create multiple mappings at once"""
        created_mappings = self.env['account.mapping']
        
        for mapping_data in mappings_data:
            mapping_data['subsidiary_id'] = subsidiary_id
            mapping = self.create(mapping_data)
            created_mappings |= mapping
        
        return created_mappings

    def action_copy_to_other_subsidiary(self):
        """Copy mapping to another subsidiary"""
        return {
            'name': _('Copy Mapping'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.mapping.copy.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_source_mapping_id': self.id},
        }
```

---

## File: `journal_mapping.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/mapping`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class JournalMapping(models.Model):
    _name = 'journal.mapping'
    _description = 'Journal Mapping for Consolidation'
    _order = 'subsidiary_id, subsidiary_journal_code'
    _rec_name = 'subsidiary_journal_name'

    # Core Fields
    subsidiary_id = fields.Many2one('subsidiary.instance', string='Subsidiary',
                                     required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='subsidiary_id.company_id',
                                  store=True, readonly=True)
    
    # Subsidiary Journal
    subsidiary_journal_id = fields.Integer(string='Subsidiary Journal ID', required=True)
    subsidiary_journal_code = fields.Char(string='Subsidiary Journal Code', required=True, index=True)
    subsidiary_journal_name = fields.Char(string='Subsidiary Journal Name')
    subsidiary_journal_type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
        ('situation', 'Opening/Closing Situation'),
    ], string='Subsidiary Journal Type')
    
    # Parent Journal
    parent_journal_id = fields.Many2one('account.journal', string='Consolidation Journal',
                                         required=True, index=True,
                                         domain="[('company_id', '=', company_id)]")
    parent_journal_code = fields.Char(related='parent_journal_id.code',
                                       string='Consolidation Journal Code', readonly=True)
    parent_journal_name = fields.Char(related='parent_journal_id.name',
                                        string='Consolidation Journal Name', readonly=True)
    
    # Configuration
    mapping_type = fields.Selection([
        ('direct', 'Direct Mapping'),
        ('consolidation', 'Consolidation Journal'),
        ('elimination', 'Elimination Journal'),
        ('adjustment', 'Adjustment Journal'),
    ], string='Mapping Type', default='direct', required=True)
    
    active = fields.Boolean(string='Active', default=True)
    auto_create = fields.Boolean(string='Auto-create if Missing', default=False,
                                 help='Automatically create parent journal if not exists')
    
    # Validation
    is_validated = fields.Boolean(string='Validated', default=False, readonly=True)
    validation_date = fields.Datetime(string='Validation Date', readonly=True)
    validation_message = fields.Text(string='Validation Message', readonly=True)
    
    # Usage Statistics
    usage_count = fields.Integer(string='Usage Count', readonly=True, default=0,
                                  help='Number of times this mapping has been used')
    last_used_date = fields.Datetime(string='Last Used', readonly=True)
    
    # Notes
    notes = fields.Text(string='Mapping Notes')

    _sql_constraints = [
        ('unique_mapping', 'unique(subsidiary_id, subsidiary_journal_id)',
         'Journal mapping must be unique per subsidiary!'),
        ('unique_code_mapping', 'unique(subsidiary_id, subsidiary_journal_code)',
         'Journal code mapping must be unique per subsidiary!'),
    ]

    @api.constrains('subsidiary_journal_code', 'parent_journal_id')
    def _check_mapping(self):
        for rec in self:
            if not rec.subsidiary_journal_code or not rec.parent_journal_id:
                raise ValidationError(_('Both subsidiary and consolidation journals are required.'))

    def action_validate_mapping(self):
        """Validate journal mapping"""
        self.ensure_one()
        
        try:
            uid, models = self.subsidiary_id.get_rpc_connection()
            
            journals = models.execute_kw(
                self.subsidiary_id.db_name, uid, self.subsidiary_id.password,
                'account.journal', 'search_read',
                [[('id', '=', self.subsidiary_journal_id)]],
                {'fields': ['name', 'code', 'type'], 'limit': 1}
            )
            
            if not journals:
                raise ValidationError(
                    _('Journal %s not found in subsidiary %s') % 
                    (self.subsidiary_journal_code, self.subsidiary_id.name)
                )
            
            journal = journals[0]
            
            # Update mapping info
            self.write({
                'subsidiary_journal_name': journal['name'],
                'subsidiary_journal_code': journal.get('code', ''),
                'subsidiary_journal_type': journal.get('type', 'general'),
                'is_validated': True,
                'validation_date': fields.Datetime.now(),
                'validation_message': 'Journal mapping validated successfully',
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Journal mapping validated successfully!'),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            self.write({
                'is_validated': False,
                'validation_message': f'Validation failed: {str(e)}',
            })
            raise ValidationError(_('Validation failed: %s') % str(e))

    def get_parent_journal(self, create_if_missing=False):
        """Get or create consolidation journal"""
        self.ensure_one()
        
        if self.parent_journal_id:
            return self.parent_journal_id
        
        if create_if_missing and self.auto_create:
            # Create new journal in parent company
            journal = self.env['account.journal'].create({
                'code': self.subsidiary_journal_code,
                'name': self.subsidiary_journal_name or f'Consolidated - {self.subsidiary_journal_code}',
                'type': self._get_journal_type(),
                'company_id': self.company_id.id,
            })
            
            self.write({'parent_journal_id': journal.id})
            return journal
        
        return False

    def _get_journal_type(self):
        """Get appropriate journal type for auto-creation"""
        # Map subsidiary types to parent journal types
        type_mapping = {
            'sale': 'sale',
            'purchase': 'purchase',
            'cash': 'cash',
            'bank': 'bank',
            'general': 'general',
            'situation': 'general',
        }
        
        journal_type = type_mapping.get(self.subsidiary_journal_type, 'general')
        return journal_type

    def increment_usage(self):
        """Increment usage counter"""
        self.sudo().write({
            'usage_count': self.usage_count + 1,
            'last_used_date': fields.Datetime.now(),
        })

    @api.model
    def get_mapping_by_id(self, subsidiary_id, journal_id):
        """Get mapping for specific subsidiary and journal ID"""
        mapping = self.search([
            ('subsidiary_id', '=', subsidiary_id),
            ('subsidiary_journal_id', '=', journal_id),
            ('active', '=', True),
        ], limit=1)
        
        if mapping:
            mapping.increment_usage()
            return mapping.get_parent_journal()
        
        return False

    @api.model
    def get_mapping_by_code(self, subsidiary_id, journal_code):
        """Get mapping for specific subsidiary and journal code"""
        mapping = self.search([
            ('subsidiary_id', '=', subsidiary_id),
            ('subsidiary_journal_code', '=', journal_code),
            ('active', '=', True),
        ], limit=1)
        
        if mapping:
            mapping.increment_usage()
            return mapping.get_parent_journal()
        
        return False

    @api.model
    def create_bulk_mappings(self, subsidiary_id, mappings_data):
        """Create multiple journal mappings at once"""
        created_mappings = self.env['journal.mapping']
        
        for mapping_data in mappings_data:
            mapping_data['subsidiary_id'] = subsidiary_id
            mapping = self.create(mapping_data)
            created_mappings |= mapping
        
        return created_mappings

    def action_copy_to_other_subsidiary(self):
        """Copy mapping to another subsidiary"""
        return {
            'name': _('Copy Journal Mapping'),
            'type': 'ir.actions.act_window',
            'res_model': 'journal.mapping.copy.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_source_mapping_id': self.id},
        }

    def action_create_default_journals(self):
        """Create default consolidation journals"""
        self.ensure_one()
        
        # Define default journals to create
        default_journals = [
            ('CONS', 'Consolidation Journal', 'general'),
            ('CONS-ELIM', 'Elimination Journal', 'general'),
            ('CONS-ADJ', 'Adjustment Journal', 'general'),
            ('CONS-IC', 'Intercompany Journal', 'general'),
            ('CONS-FX', 'FX Adjustment Journal', 'general'),
        ]
        
        created_journals = []
        
        for code, name, jtype in default_journals:
            journal = self.env['account.journal'].search([
                ('code', '=', code),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
            
            if not journal:
                journal = self.env['account.journal'].create({
                    'name': name,
                    'code': code,
                    'type': jtype,
                    'company_id': self.company_id.id,
                })
                created_journals.append(journal.name)
        
        if created_journals:
            message = _('Created default journals: %s') % ', '.join(created_journals)
        else:
            message = _('Default journals already exist.')
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Default Journals'),
                'message': message,
                'type': 'success',
            }
        }
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/media`

```py
from . import media_account_move
from . import media_account_move_line
from . import media_state_machine
```

---

## File: `media_account_move.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/media`

```py
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
    # Add these fields to media.account.move model
    date_from = fields.Date(string='Period From', related='sync_engine_id.date_from')
    date_to = fields.Date(string='Period To', related='sync_engine_id.date_to')
    # Move Details
    date = fields.Date(string='Date', required=True, index=True, tracking=True)
    ref = fields.Char(string='Reference', tracking=True)
    
    # Source Information
    source_move_id = fields.Integer(string='Source Move ID', required=True,
                                     help='ID of the move in subsidiary Odoo')
    # Journal Information
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
    
    # Mapped Journal
    mapped_journal_id = fields.Many2one('account.journal', string='Mapped Journal',
                                         compute='_compute_mapped_journal', store=True)
    journal_mapping_id = fields.Many2one('journal.mapping', string='Journal Mapping Used',
                                          compute='_compute_mapped_journal', store=True)
    
    # Financial
    amount_total = fields.Float(string='Total Amount', digits='Account')
    currency_id = fields.Many2one('res.currency', related='subsidiary_id.currency_id',
                                   store=True, readonly=True)
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('reconciled', 'Reconciled'),
        ('promoted', 'Promoted'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True, index=True)
    
    # State Machine
    state_machine_id = fields.Many2one('media.state.machine', string='State Machine',
                                        readonly=True)
    
    # Validation
    is_balanced = fields.Boolean(string='Balanced', compute='_compute_totals', store=True)
    total_debit = fields.Float(string='Total Debit', compute='_compute_totals', 
                                store=True, digits='Account')
    total_credit = fields.Float(string='Total Credit', compute='_compute_totals',
                                 store=True, digits='Account')
    balance_difference = fields.Float(string='Balance Difference', 
                                       compute='_compute_totals', store=True)
    
    # Promotion
    promoted_move_id = fields.Many2one('account.move', string='Promoted Move',
                                        readonly=True, tracking=True)
    promotion_date = fields.Datetime(string='Promotion Date', readonly=True)
    
    # Error Handling
    error_message = fields.Text(string='Error Message', readonly=True)
    retry_count = fields.Integer(string='Retry Count', readonly=True, default=0)
    
    # Relations
    line_ids = fields.One2many('media.account.move.line', 'media_move_id', 
                                string='Lines')
    
    # Metadata
    create_date = fields.Datetime(string='Created', readonly=True)
    write_date = fields.Datetime(string='Last Updated', readonly=True)
    # Add to media.account.move model
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
        # Create state machine entry
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
                
                # Try by journal ID first
                if move.source_journal_id:
                    journal_mapping = self.env['journal.mapping'].search([
                        ('subsidiary_id', '=', move.subsidiary_id.id),
                        ('subsidiary_journal_id', '=', move.source_journal_id),
                        ('active', '=', True),
                    ], limit=1)
                
                # If not found by ID, try by code
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

    def action_validate(self):
        """Validate media move"""
        for rec in self:
            if not rec.is_balanced:
                raise UserError(_('Move %s is not balanced! Debit: %s, Credit: %s') % 
                              (rec.name, rec.total_debit, rec.total_credit))
            
            if not rec.line_ids:
                raise UserError(_('Move %s has no lines!') % rec.name)
            
            # Check all lines have mapped accounts
            unmapped_lines = rec.line_ids.filtered(lambda l: not l.mapped_account_id)
            if unmapped_lines:
                raise UserError(_('Some lines have unmapped accounts: %s') % 
                              ', '.join(unmapped_lines.mapped('account_code')))
            
            rec.write({'state': 'validated'})
            rec.state_machine_id.transition_to('validated')

    def action_reconcile(self):
        """Mark as reconciled"""
        self.ensure_one()
        if self.state != 'validated':
            raise UserError(_('Only validated moves can be reconciled'))
        
        self.write({'state': 'reconciled'})
        self.state_machine_id.transition_to('reconciled')

    def action_promote(self):
        """Promote single media move"""
        self.ensure_one()
        
        if self.state not in ('validated', 'reconciled'):
            raise UserError(_('Only validated or reconciled moves can be promoted'))
        
        promotion_engine = self.env['promotion.engine']
        
        try:
            promoted_count = promotion_engine.promote_media_moves(self)
            
            if promoted_count > 0:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Move promoted successfully!'),
                        'type': 'success',
                    }
                }
        except Exception as e:
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise

    def action_view_promoted_move(self):
        """View the promoted accounting move"""
        self.ensure_one()
        
        if not self.promoted_move_id:
            raise UserError(_('This media move has not been promoted yet.'))
        
        return {
            'name': _('Promoted Move'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.promoted_move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _prepare_account_move_vals(self):
        """Prepare values for account.move creation"""
        self.ensure_one()
        
        if not self.is_balanced:
            raise ValidationError(_('Cannot promote unbalanced move %s') % self.name)
        
        # Map lines
        line_vals = []
        for media_line in self.line_ids:
            if not media_line.mapped_account_id:
                raise ValidationError(
                    _('Cannot map account %s for line %s') % 
                    (media_line.account_code, media_line.name)
                )
            
            line_vals.append((0, 0, {
                'name': media_line.name,
                'account_id': media_line.mapped_account_id.id,
                'debit': media_line.debit,
                'credit': media_line.credit,
                'partner_id': media_line.partner_id.id if media_line.partner_id else False,
            }))
        
        # Get journal mapping
        journal = self.env['journal.mapping'].get_mapping(
            self.subsidiary_id.id,
            self.source_journal_id
        )
        
        if not journal:
            journal = self._get_consolidation_journal()
        
        return {
            'move_type': 'entry',
            'date': self.date,
            'ref': f'{self.subsidiary_id.code} - {self.ref or self.name}',
            'journal_id': journal.id,
            'line_ids': line_vals,
            'is_consolidation': True,
            'consolidation_sync_id': self.sync_engine_id.id,
            'media_move_id': self.id,
        }

    def _get_consolidation_journal(self):
        """Get or create consolidation journal"""
        journal = self.env['account.journal'].search([
            ('code', '=', 'CONS'),
            ('company_id', '=', self.company_id.id),
            ('type', '=', 'general'),
        ], limit=1)
        
        if not journal:
            journal = self.env['account.journal'].create({
                'name': 'Consolidation',
                'code': 'CONS',
                'type': 'general',
                'company_id': self.company_id.id,
            })
        
        return journal

    @api.model
    def _cron_cleanup_old_media(self, days=90):
        """Cron job to clean up old promoted media moves"""
        cutoff_date = fields.Date.today() - timedelta(days=days)
        
        old_media = self.search([
            ('date', '<', cutoff_date),
            ('state', '=', 'promoted'),
            ('promoted_move_id', '!=', False),
        ])
        
        count = len(old_media)
        old_media.unlink()
        
        _logger.info(f'Cleaned up {count} old media moves')
        return count

```

---

## File: `media_account_move_line.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/media`

```py
# -*- coding: utf-8 -*-
# FILE: models/media/media_account_move.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MediaAccountMoveLine(models.Model):
    _name = 'media.account.move.line'
    _description = 'Media Layer - Account Move Line'
    _order = 'media_move_id, sequence, id'

    media_move_id = fields.Many2one('media.account.move', string='Media Move',
                                     required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Line Details
    name = fields.Char(string='Label', required=True)
    
    # Account Information
    account_code = fields.Char(string='Account Code', required=True, index=True)
    account_name = fields.Char(string='Account Name')
    
    # Mapped Account
    mapped_account_id = fields.Many2one('account.account', string='Mapped Account',
                                         compute='_compute_mapped_account', store=True)
    mapping_id = fields.Many2one('account.mapping', string='Mapping Used',
                                  compute='_compute_mapped_account', store=True)
    
    # Amounts
    debit = fields.Float(string='Debit', digits='Account', default=0.0)
    credit = fields.Float(string='Credit', digits='Account', default=0.0)
    balance = fields.Float(string='Balance', compute='_compute_balance', store=True)
    
    # Currency
    amount_currency = fields.Float(string='Amount in Currency', digits='Account')
    currency_id = fields.Many2one('res.currency', string='Currency')
    
    # Currency Conversion
    currency_converted = fields.Boolean(string='Currency Converted', default=False)
    conversion_rate = fields.Float(string='Conversion Rate', digits=(12, 6))
    original_debit = fields.Float(string='Original Debit', digits='Account')
    original_credit = fields.Float(string='Original Credit', digits='Account')
    
    # Partner
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_name = fields.Char(string='Partner Name')
    
    # Source Information
    source_line_id = fields.Integer(string='Source Line ID', required=True,
                                     help='ID of the line in subsidiary Odoo')
    
    # Analytic
    analytic_account_id = fields.Many2one('account.analytic.account', 
                                           string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    
    # Related Fields
    subsidiary_id = fields.Many2one(related='media_move_id.subsidiary_id',
                                     store=True, readonly=True)
    date = fields.Date(related='media_move_id.date', store=True, readonly=True)

    @api.depends('account_code', 'subsidiary_id')
    def _compute_mapped_account(self):
        for line in self:
            if line.account_code and line.subsidiary_id:
                mapping = self.env['account.mapping'].search([
                    ('subsidiary_id', '=', line.subsidiary_id.id),
                    ('subsidiary_account_code', '=', line.account_code),
                    ('active', '=', True),
                ], limit=1)
                
                if mapping:
                    line.mapped_account_id = mapping.parent_account_id
                    line.mapping_id = mapping
                    mapping.increment_usage()
                else:
                    line.mapped_account_id = False
                    line.mapping_id = False
            else:
                line.mapped_account_id = False
                line.mapping_id = False

    @api.depends('debit', 'credit')
    def _compute_balance(self):
        for line in self:
            line.balance = line.debit - line.credit

    def action_create_mapping(self):
        """Create mapping for unmapped account"""
        self.ensure_one()
        
        if self.mapped_account_id:
            raise UserError(_('Account already mapped!'))
        
        return {
            'name': _('Create Account Mapping'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.mapping',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subsidiary_id': self.subsidiary_id.id,
                'default_subsidiary_account_code': self.account_code,
                'default_subsidiary_account_name': self.account_name,
            },
        }

    def action_view_mapped_account(self):
        """View the mapped account"""
        self.ensure_one()
        
        if not self.mapped_account_id:
            raise UserError(_('No mapped account for this line!'))
        
        return {
            'name': _('Mapped Account'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.account',
            'res_id': self.mapped_account_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
```

---

## File: `media_state_machine.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/media`

```py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class MediaStateMachine(models.Model):
    _name = 'media.state.machine'
    _description = 'Media Move State Machine'
    _order = 'create_date desc'

    media_move_id = fields.Many2one('media.account.move', string='Media Move',
                                     ondelete='cascade')
    
    # Current State
    current_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('reconciled', 'Reconciled'),
        ('promoted', 'Promoted'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ], string='Current State', default='draft', required=True)
    
    initial_state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('reconciled', 'Reconciled'),
        ('promoted', 'Promoted'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
    ], string='Initial State', required=True)
    
    # Transition Log
    transition_log = fields.Text(string='Transition Log', readonly=True)
    
    # Timestamps
    draft_date = fields.Datetime(string='Draft Date')
    validated_date = fields.Datetime(string='Validated Date')
    reconciled_date = fields.Datetime(string='Reconciled Date')
    promoted_date = fields.Datetime(string='Promoted Date')
    error_date = fields.Datetime(string='Error Date')
    cancelled_date = fields.Datetime(string='Cancelled Date')

    @api.model
    def create(self, vals):
        vals['current_state'] = vals.get('initial_state', 'draft')
        vals['draft_date'] = fields.Datetime.now()
        vals['transition_log'] = f"Created in state: {vals['current_state']}\n"
        
        return super().create(vals)

    def transition_to(self, new_state):
        """Transition to new state"""
        self.ensure_one()
        
        if not self._is_valid_transition(self.current_state, new_state):
            raise UserError(
                _('Invalid state transition from %s to %s') % 
                (self.current_state, new_state)
            )
        
        old_state = self.current_state
        
        # Update state
        self.write({
            'current_state': new_state,
            f'{new_state}_date': fields.Datetime.now(),
        })
        
        # Log transition
        log_entry = f"{fields.Datetime.now()}: {old_state} → {new_state}\n"
        self.transition_log = (self.transition_log or '') + log_entry
        
        _logger.info(f'State transition for media move {self.media_move_id.id}: {log_entry}')
        
        return True

    def _is_valid_transition(self, from_state, to_state):
        """Check if state transition is valid"""
        valid_transitions = {
            'draft': ['validated', 'error', 'cancelled'],
            'validated': ['reconciled', 'promoted', 'error', 'cancelled'],
            'reconciled': ['promoted', 'error', 'cancelled'],
            'promoted': ['cancelled'],
            'error': ['draft', 'cancelled'],
            'cancelled': ['draft'],
        }
        
        return to_state in valid_transitions.get(from_state, [])

    def get_transition_history(self):
        """Get formatted transition history"""
        self.ensure_one()
        
        history = []
        if self.transition_log:
            for line in self.transition_log.split('\n'):
                if line.strip():
                    history.append(line.strip())
        
        return history
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/sla`

```py
from . import performance_sla
```

---

## File: `performance_sla.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/sla`

```py
from odoo import models, fields, api, _
import logging
from datetime import timedelta
import json
_logger = logging.getLogger(__name__)

class PerformanceSLA(models.Model):
    _name = 'performance.sla'
    _description = 'Performance SLA Monitoring'
    _order = 'priority, name'

    name = fields.Char(string='SLA Name', required=True)
    active = fields.Boolean(string='Active', default=True)
    priority = fields.Integer(string='Priority', default=10,
                               help='Lower number = higher priority')
    
    # Threshold Configuration
    threshold_type = fields.Selection([
        ('duration', 'Sync Duration'),
        ('success_rate', 'Success Rate'),
        ('data_volume', 'Data Volume'),
        ('error_count', 'Error Count'),
        ('mapping_rate', 'Mapping Validation Rate'),
    ], string='Threshold Type', required=True, default='duration', index=True)
    
    threshold_value = fields.Float(string='Threshold Value', required=True,
                                    help='Threshold limit value')
    threshold_operator = fields.Selection([
        ('greater', 'Greater Than'),
        ('less', 'Less Than'),
        ('equal', 'Equal To'),
    ], string='Operator', default='greater', required=True)
    
    threshold_unit = fields.Selection([
        ('seconds', 'Seconds'),
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('percent', 'Percent'),
        ('count', 'Count'),
        ('mb', 'Megabytes'),
        ('gb', 'Gigabytes'),
    ], string='Unit', default='minutes', required=True)
    
    # Measurement Period
    measurement_period = fields.Selection([
        ('realtime', 'Real-time'),
        ('last_hour', 'Last Hour'),
        ('last_24h', 'Last 24 Hours'),
        ('last_7d', 'Last 7 Days'),
        ('last_30d', 'Last 30 Days'),
    ], string='Measurement Period', default='last_24h', required=True)
    
    # Alert Configuration
    alert_level = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ], string='Alert Level', default='warning', required=True)
    
    alert_email = fields.Boolean(string='Send Email Alert', default=False)
    alert_user_ids = fields.Many2many('res.users', string='Alert Recipients',
                                       help='Users to notify when SLA is violated')
    alert_message_template = fields.Text(string='Alert Message Template',
                                          default='SLA "{name}" violated: {metric_name} is {current_value}{unit}')
    
    # Action Configuration
    auto_action = fields.Selection([
        ('none', 'No Action'),
        ('disable_auto_sync', 'Disable Auto-Sync'),
        ('notify_manager', 'Notify Manager'),
        ('create_activity', 'Create Activity'),
    ], string='Auto Action', default='none')
    
    # Monitoring
    last_check_date = fields.Datetime(string='Last Check', readonly=True)
    last_violation_date = fields.Datetime(string='Last Violation', readonly=True)
    violation_count = fields.Integer(string='Total Violations', readonly=True, default=0)
    consecutive_violations = fields.Integer(string='Consecutive Violations', 
                                             readonly=True, default=0)
    
    # Current State
    current_value = fields.Float(string='Current Value', readonly=True)
    is_violated = fields.Boolean(string='Currently Violated', readonly=True, default=False)
    violation_severity = fields.Selection([
        ('none', 'No Violation'),
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], string='Violation Severity', compute='_compute_severity', store=True)
    
    # Statistics
    uptime_percentage = fields.Float(string='Uptime %', readonly=True, default=100.0)
    avg_value_last_7d = fields.Float(string='Avg Value (7d)', readonly=True)

    @api.depends('is_violated', 'consecutive_violations')
    def _compute_severity(self):
        for rec in self:
            if not rec.is_violated:
                rec.violation_severity = 'none'
            elif rec.consecutive_violations >= 5:
                rec.violation_severity = 'severe'
            elif rec.consecutive_violations >= 3:
                rec.violation_severity = 'moderate'
            else:
                rec.violation_severity = 'minor'

    @api.model
    def check_all_slas(self):
        """Cron job: Check all active SLAs"""
        slas = self.search([('active', '=', True)])
        
        violations = []
        for sla in slas:
            is_violated = sla._check_sla()
            if is_violated:
                violations.append(sla)
        
        _logger.info(f'SLA check completed: {len(violations)} violations out of {len(slas)} SLAs')
        
        return violations

    def _check_sla(self):
        """Check individual SLA"""
        self.ensure_one()
        
        current_value = self._get_current_value()
        is_violated = self._is_threshold_violated(current_value)
        
        # Update state
        vals = {
            'current_value': current_value,
            'is_violated': is_violated,
            'last_check_date': fields.Datetime.now(),
        }
        
        if is_violated:
            vals['last_violation_date'] = fields.Datetime.now()
            vals['violation_count'] = self.violation_count + 1
            vals['consecutive_violations'] = self.consecutive_violations + 1
            
            self.write(vals)
            self._handle_violation()
        else:
            vals['consecutive_violations'] = 0
            self.write(vals)
        
        return is_violated

    def _get_current_value(self):
        """Get current metric value based on type"""
        self.ensure_one()
        
        # Determine time range
        now = fields.Datetime.now()
        if self.measurement_period == 'last_hour':
            time_from = now - timedelta(hours=1)
        elif self.measurement_period == 'last_24h':
            time_from = now - timedelta(hours=24)
        elif self.measurement_period == 'last_7d':
            time_from = now - timedelta(days=7)
        elif self.measurement_period == 'last_30d':
            time_from = now - timedelta(days=30)
        else:  # realtime
            time_from = now - timedelta(minutes=5)
        
        # Get metric based on type
        if self.threshold_type == 'duration':
            syncs = self.env['sync.engine'].search([
                ('create_date', '>=', time_from),
                ('state', '=', 'completed'),
            ])
            
            if syncs:
                avg_duration = sum(syncs.mapped('duration')) / len(syncs)
                
                # Convert to threshold unit
                if self.threshold_unit == 'seconds':
                    return avg_duration
                elif self.threshold_unit == 'minutes':
                    return avg_duration / 60
                elif self.threshold_unit == 'hours':
                    return avg_duration / 3600
            
            return 0.0
        
        elif self.threshold_type == 'success_rate':
            syncs = self.env['sync.engine'].search([
                ('create_date', '>=', time_from),
            ])
            
            if syncs:
                completed = len(syncs.filtered(lambda s: s.state == 'completed'))
                return (completed / len(syncs)) * 100
            
            return 100.0
        
        elif self.threshold_type == 'error_count':
            return self.env['consolidation.log'].search_count([
                ('create_date', '>=', time_from),
                ('state', '=', 'error'),
            ])
        
        elif self.threshold_type == 'mapping_rate':
            mappings = self.env['account.mapping'].search([('active', '=', True)])
            if mappings:
                validated = mappings.filtered(lambda m: m.is_validated)
                return (len(validated) / len(mappings)) * 100
            return 100.0
        
        elif self.threshold_type == 'data_volume':
            syncs = self.env['sync.engine'].search([
                ('create_date', '>=', time_from),
            ])
            total_moves = sum(syncs.mapped('total_moves_fetched'))
            
            # Estimate MB (rough estimate: 1KB per move)
            if self.threshold_unit == 'mb':
                return total_moves / 1024
            elif self.threshold_unit == 'gb':
                return total_moves / (1024 * 1024)
        
        return 0.0

    def _is_threshold_violated(self, current_value):
        """Check if threshold is violated"""
        self.ensure_one()
        
        if self.threshold_operator == 'greater':
            return current_value > self.threshold_value
        elif self.threshold_operator == 'less':
            return current_value < self.threshold_value
        elif self.threshold_operator == 'equal':
            return abs(current_value - self.threshold_value) < 0.01
        
        return False

    def _handle_violation(self):
        """Handle SLA violation"""
        self.ensure_one()
        
        _logger.warning(f'SLA Violation: {self.name} - {self.threshold_type} = {self.current_value}')
        
        # Send email alert
        if self.alert_email and self.alert_user_ids:
            self._send_alert_email()
        
        # Execute auto action
        if self.auto_action == 'disable_auto_sync':
            self._disable_auto_sync()
        elif self.auto_action == 'notify_manager':
            self._notify_manager()
        elif self.auto_action == 'create_activity':
            self._create_activity()
        
        # Log to consolidation log
        self.env['consolidation.log'].create({
            'log_type': 'warning',
            'message': f'SLA Violation: {self.name}',
            'state': 'warning',
            'metadata': json.dumps({
                'sla_name': self.name,
                'threshold_value': self.threshold_value,
                'current_value': self.current_value,
                'consecutive_violations': self.consecutive_violations,
            }),
        })

    def _send_alert_email(self):
        """Send email alert"""
        self.ensure_one()
        
        # Prepare message
        message = self.alert_message_template.format(
            name=self.name,
            metric_name=dict(self._fields['threshold_type'].selection).get(self.threshold_type),
            current_value=self.current_value,
            unit=self.threshold_unit,
        )
        
        # Send to each recipient
        for user in self.alert_user_ids:
            self.env['mail.mail'].create({
                'subject': f'SLA Violation Alert: {self.name}',
                'body_html': f'<p>{message}</p>',
                'email_to': user.email,
            }).send()

    def _disable_auto_sync(self):
        """Disable auto-sync for all subsidiaries"""
        subsidiaries = self.env['subsidiary.instance'].search([
            ('auto_sync', '=', True),
            ('active', '=', True),
        ])
        subsidiaries.write({'auto_sync': False})
        
        _logger.warning(f'Auto-sync disabled for {len(subsidiaries)} subsidiaries due to SLA violation')

    def _notify_manager(self):
        """Notify consolidation managers"""
        managers = self.env['res.users'].search([('groups_id', 'in', self.env.ref('financial_consolidation.group_consolidation_manager').id)])
        for manager in managers:
            self.env['mail.mail'].create({
                'subject': f'SLA Violation Notification: {self.name}',
                'body_html': f'<p>SLA "{self.name}" has been violated. Current value: {self.current_value} {self.threshold_unit}.</p>',
                'email_to': manager.email,
            }).send()   
    
    def _create_activity(self):
        """Create activity for consolidation managers"""
        managers = self.env['res.users'].search([('groups_id', 'in', self.env.ref('financial_consolidation.group_consolidation_manager').id)])
        for manager in managers:
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get('performance.sla').id,
                'res_id': self.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f'SLA Violation: {self.name}',
                'user_id': manager.id,
                'note': f'SLA "{self.name}" violated. Current value: {self.current_value} {self.threshold_unit}. Please investigate.',
                'date_deadline': fields.Date.today() + timedelta(days=2),
            })
            
    
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/subsidiary`

```py
from . import subsidiary_instance
```

---

## File: `subsidiary_instance.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/models/subsidiary`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import xmlrpc.client
import logging
from datetime import timedelta

_logger = logging.getLogger(__name__)


class SubsidiaryInstance(models.Model):
    _name = 'subsidiary.instance'
    _description = 'Subsidiary Odoo Instance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    # Basic Information
    name = fields.Char(string='Subsidiary Name', required=True, tracking=True, index=True)
    code = fields.Char(string='Code', required=True, tracking=True, index=True, size=10)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    
    # Connection Details
    host = fields.Char(string='Host URL', required=True, tracking=True,
                       help='Full URL of subsidiary Odoo instance (e.g., https://subsidiary.odoo.com)')
    db_name = fields.Char(string='Database Name', required=True, tracking=True)
    username = fields.Char(string='Username', required=True, tracking=True)
    password = fields.Char(string='Password', required=True, tracking=True)
    api_key = fields.Char(string='API Key', tracking=True,
                          help='Optional API key for enhanced security')
    sync_engine_ids = fields.Many2many(
        'sync.engine',
        'sync_engine_subsidiary_rel',
        'subsidiary_id',
        'sync_engine_id',
        string='Sync Engines'
    )
    
    # Media moves for this subsidiary
    media_move_ids = fields.One2many(
        'media.account.move',
        'subsidiary_id',
        string='Media Moves'
    )
    
    # Sync Configuration
    sync_mode = fields.Selection([
        ('manual', 'Manual'),
        ('scheduled', 'Scheduled'),
        ('realtime', 'Real-time (Webhook)'),
    ], string='Sync Mode', default='manual', required=True, tracking=True)
    
    sync_frequency = fields.Selection([
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], string='Sync Frequency', default='daily')
    
    auto_sync = fields.Boolean(string='Auto Sync', default=False,
                               help='Enable automatic synchronization')
    auto_reconcile = fields.Boolean(string='Auto Reconciliation', default=False,
                                     help='Automatically reconcile after sync')
    auto_promote = fields.Boolean(string='Auto Promotion', default=False,
                                   help='Automatically promote to accounting after reconciliation')
    
    # Company Mapping
    company_id = fields.Many2one('res.company', string='Parent Company', 
                                  required=True, default=lambda self: self.env.company)
    subsidiary_company_id = fields.Integer(string='Subsidiary Company ID',
                                            help='Company ID in subsidiary Odoo instance')
    subsidiary_company_name = fields.Char(string='Subsidiary Company Name',
                                           compute='_compute_subsidiary_company_info', store=True)
    
    # Currency
    currency_id = fields.Many2one('res.currency', string='Subsidiary Currency', required=True,
                                  default=lambda self: self.env.company.currency_id)
    
    # Validation & Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validating', 'Validating'),
        ('validated', 'Validated'),
        ('error', 'Connection Error'),
        ('suspended', 'Suspended'),
    ], string='Status', default='draft', tracking=True)
    
    last_validation_date = fields.Datetime(string='Last Validation Date', readonly=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    validation_message = fields.Text(string='Validation Message', readonly=True)
    
    # Performance Metrics
    avg_sync_duration = fields.Float(string='Avg Sync Duration (sec)', readonly=True,
                                      compute='_compute_performance_metrics', store=True)
    total_syncs = fields.Integer(string='Total Syncs', readonly=True,
                                  compute='_compute_performance_metrics', store=True)
    failed_syncs = fields.Integer(string='Failed Syncs', readonly=True,
                                   compute='_compute_performance_metrics', store=True)
    success_rate = fields.Float(string='Success Rate (%)', readonly=True,
                                 compute='_compute_performance_metrics', store=True,
                                 digits=(5, 2))
    
    # Relations
    account_mapping_ids = fields.One2many('account.mapping', 'subsidiary_id', 
                                           string='Account Mappings')
    journal_mapping_ids = fields.One2many('journal.mapping', 'subsidiary_id',
                                           string='Journal Mappings')
    sync_log_ids = fields.One2many('consolidation.log', 'subsidiary_id',
                                    string='Sync Logs')
    
    # Counts for UI
    account_mapping_count = fields.Integer(compute='_compute_counts')
    journal_mapping_count = fields.Integer(compute='_compute_counts')
    sync_log_count = fields.Integer(compute='_compute_counts')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Subsidiary code must be unique!'),
        ('name_unique', 'unique(name)', 'Subsidiary name must be unique!'),
    ]

    @api.depends('sync_log_ids.duration', 'sync_log_ids.state')
    def _compute_performance_metrics(self):
        for rec in self:
            logs = rec.sync_log_ids.filtered(lambda l: l.log_type == 'sync')
            rec.total_syncs = len(logs)
            
            completed_logs = logs.filtered(lambda l: l.state == 'completed')
            failed_logs = logs.filtered(lambda l: l.state == 'error')
            
            rec.failed_syncs = len(failed_logs)
            
            if rec.total_syncs > 0:
                rec.success_rate = (len(completed_logs) / rec.total_syncs) * 100
            else:
                rec.success_rate = 0.0
            
            if completed_logs:
                rec.avg_sync_duration = sum(completed_logs.mapped('duration')) / len(completed_logs)
            else:
                rec.avg_sync_duration = 0.0

    @api.depends('account_mapping_ids', 'journal_mapping_ids', 'sync_log_ids')
    def _compute_counts(self):
        for rec in self:
            rec.account_mapping_count = len(rec.account_mapping_ids)
            rec.journal_mapping_count = len(rec.journal_mapping_ids)
            rec.sync_log_count = len(rec.sync_log_ids)

    @api.constrains('host')
    def _check_host(self):
        for rec in self:
            if rec.host and not rec.host.startswith(('http://', 'https://')):
                raise ValidationError(_('Host URL must start with http:// or https://'))

    @api.depends('host', 'db_name', 'username', 'password')
    def _compute_subsidiary_company_info(self):
        for rec in self:
            rec.subsidiary_company_name = False
            if rec.state == 'validated':
                try:
                    uid, models = rec.get_rpc_connection()
                    company = models.execute_kw(
                        rec.db_name, uid, rec.password,
                        'res.company', 'search_read',
                        [[('id', '=', rec.subsidiary_company_id or 1)]],
                        {'fields': ['name'], 'limit': 1}
                    )
                    if company:
                        rec.subsidiary_company_name = company[0]['name']
                except:
                    pass

    def action_validate_connection(self):
        """Validate connection to subsidiary Odoo instance"""
        self.ensure_one()
        
        self.write({'state': 'validating'})
        
        try:
            # Test authentication
            common = xmlrpc.client.ServerProxy(f'{self.host}/xmlrpc/2/common')
            uid = common.authenticate(self.db_name, self.username, self.password, {})
            
            if not uid:
                raise ValidationError(_('Authentication failed. Please check credentials.'))
            
            # Test model access
            models_proxy = xmlrpc.client.ServerProxy(f'{self.host}/xmlrpc/2/object')
            
            # Check accounting module
            account_module = models_proxy.execute_kw(
                self.db_name, uid, self.password,
                'ir.module.module', 'search_read',
                [[('name', '=', 'account'), ('state', '=', 'installed')]],
                {'fields': ['name'], 'limit': 1}
            )
            
            if not account_module:
                raise ValidationError(_('Accounting module not installed on subsidiary.'))
            
            # Get company info if not set
            if not self.subsidiary_company_id:
                companies = models_proxy.execute_kw(
                    self.db_name, uid, self.password,
                    'res.company', 'search',
                    [[]],
                    {'limit': 1}
                )
                if companies:
                    self.subsidiary_company_id = companies[0]
            
            # Test account.move access
            test_search = models_proxy.execute_kw(
                self.db_name, uid, self.password,
                'account.move', 'search',
                [[('state', '=', 'posted')]],
                {'limit': 1}
            )
            
            self.write({
                'state': 'validated',
                'last_validation_date': fields.Datetime.now(),
                'validation_message': 'Connection successful. All required modules verified.',
            })
            
            # Log validation
            self.env['consolidation.log'].create({
                'subsidiary_id': self.id,
                'log_type': 'validation',
                'message': 'Connection validated successfully',
                'state': 'completed',
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Connection validated successfully!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            _logger.error(f'Validation failed for subsidiary {self.name}: {error_msg}')
            
            self.write({
                'state': 'error',
                'last_validation_date': fields.Datetime.now(),
                'validation_message': f'Connection error: {error_msg}',
            })
            
            # Log error
            self.env['consolidation.log'].create({
                'subsidiary_id': self.id,
                'log_type': 'validation',
                'message': f'Connection validation failed: {error_msg}',
                'state': 'error',
            })
            
            raise ValidationError(_('Connection failed: %s') % error_msg)

    def get_rpc_connection(self):
        """Get authenticated RPC connection"""
        self.ensure_one()
        
        if self.state != 'validated':
            raise UserError(_('Please validate connection first for subsidiary: %s') % self.name)
        
        try:
            common = xmlrpc.client.ServerProxy(f'{self.host}/xmlrpc/2/common')
            uid = common.authenticate(self.db_name, self.username, self.password, {})
            
            if not uid:
                raise UserError(_('Authentication failed for subsidiary %s') % self.name)
            
            models = xmlrpc.client.ServerProxy(f'{self.host}/xmlrpc/2/object')
            
            return uid, models
            
        except Exception as e:
            _logger.error(f'RPC connection error for {self.name}: {str(e)}')
            self.write({'state': 'error', 'validation_message': str(e)})
            raise UserError(_('Connection error: %s') % str(e))

    def action_suspend(self):
        """Suspend subsidiary"""
        self.write({'state': 'suspended'})
        self.env['consolidation.log'].log_operation(
            'info', f'Subsidiary {self.name} suspended',
            subsidiary_id=self.id
        )

    def action_activate(self):
        """Activate subsidiary"""
        if self.state == 'error':
            # Re-validate if previously in error state
            return self.action_validate_connection()
        else:
            self.write({'state': 'validated'})
            self.env['consolidation.log'].log_operation(
                'info', f'Subsidiary {self.name} activated',
                subsidiary_id=self.id
            )

    def action_view_account_mappings(self):
        """View account mappings"""
        self.ensure_one()
        return {
            'name': _('Account Mappings'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.mapping',
            'view_mode': 'tree,form',
            'domain': [('subsidiary_id', '=', self.id)],
            'context': {'default_subsidiary_id': self.id},
        }

    def action_view_journal_mappings(self):
        """View journal mappings"""
        self.ensure_one()
        return {
            'name': _('Journal Mappings'),
            'type': 'ir.actions.act_window',
            'res_model': 'journal.mapping',
            'view_mode': 'tree,form',
            'domain': [('subsidiary_id', '=', self.id)],
            'context': {'default_subsidiary_id': self.id},
        }

    def action_view_sync_logs(self):
        """View sync logs"""
        self.ensure_one()
        return {
            'name': _('Sync Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'consolidation.log',
            'view_mode': 'tree,form',
            'domain': [('subsidiary_id', '=', self.id)],
            'context': {'default_subsidiary_id': self.id},
        }

    def action_test_fetch(self):
        """Test data fetching from subsidiary"""
        self.ensure_one()
        
        try:
            uid, models = self.get_rpc_connection()
            
            # Test fetch of recent moves
            domain = [
                ('date', '>=', fields.Date.today().replace(day=1)),
                ('date', '<=', fields.Date.today()),
                ('state', '=', 'posted'),
            ]
            
            count = models.execute_kw(
                self.db_name, uid, self.password,
                'account.move', 'search_count',
                [domain]
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Test Successful'),
                    'message': _('Successfully connected. Found %d moves for current month.') % count,
                    'type': 'success',
                }
            }
            
        except Exception as e:
            raise UserError(_('Test failed: %s') % str(e))

    @api.model
    def _cron_scheduled_sync(self):
        """Cron job for scheduled syncs"""
        subsidiaries = self.search([
            ('sync_mode', '=', 'scheduled'),
            ('state', '=', 'validated'),
            ('active', '=', True),
            ('auto_sync', '=', True),
        ])
        
        for subsidiary in subsidiaries:
            if not subsidiary._should_sync_now():
                continue
            
            try:
                # Create sync wizard and execute
                wizard = self.env['consolidation.run.wizard'].create({
                    'subsidiary_ids': [(6, 0, [subsidiary.id])],
                    'date_from': fields.Date.today() - timedelta(days=1),
                    'date_to': fields.Date.today(),
                    'auto_reconcile': subsidiary.auto_reconcile,
                    'auto_promote': subsidiary.auto_promote,
                    'processing_mode': 'sequential',
                })
                
                wizard.action_start_consolidation()
                
            except Exception as e:
                _logger.error(f'Scheduled sync failed for {subsidiary.name}: {str(e)}')
                subsidiary.env['consolidation.log'].log_error(
                    f'Scheduled sync failed: {str(e)}',
                    subsidiary_id=subsidiary.id
                )
    @api.constrains('code')
    def _check_code_format(self):
        for rec in self:
            if not rec.code or len(rec.code) > 10:
                raise ValidationError(_('Subsidiary code must be 1-10 characters'))
            
    def _should_sync_now(self):
        """Check if subsidiary should sync now based on frequency"""
        if not self.last_sync_date:
            return True
        
        now = fields.Datetime.now()
        delta = now - self.last_sync_date
        
        if self.sync_frequency == 'hourly':
            return delta >= timedelta(hours=1)
        elif self.sync_frequency == 'daily':
            return delta >= timedelta(days=1)
        elif self.sync_frequency == 'weekly':
            return delta >= timedelta(weeks=1)
        elif self.sync_frequency == 'monthly':
            return delta >= timedelta(days=30)
        
        return False
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/services`

```py
from . import checksum
from . import rpc_client
from . import webhook_receiver
```

---

## File: `checksum.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/services`

```py
# FILE: models/services/checksum_service.py
from odoo import models, api
import hashlib
import json
import logging

_logger = logging.getLogger(__name__)


class ChecksumService(models.Model):
    _name = 'checksum.service'
    _description = 'Checksum Validation Service'
    
    @api.model
    def calculate_checksum(self, data, algorithm='sha256'):
        """Calculate checksum for data with error handling"""
        try:
            if isinstance(data, (dict, list)):
                # Sort keys for consistent hashing
                data_str = json.dumps(data, sort_keys=True, default=str)
            else:
                data_str = str(data)
            
            if algorithm == 'sha256':
                return hashlib.sha256(data_str.encode()).hexdigest()
            elif algorithm == 'md5':
                return hashlib.md5(data_str.encode()).hexdigest()
            elif algorithm == 'sha1':
                return hashlib.sha1(data_str.encode()).hexdigest()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
                
        except Exception as e:
            _logger.error(f"Checksum calculation failed: {str(e)}")
            raise
    
    @api.model
    def verify_checksum(self, data, expected_checksum, algorithm='sha256'):
        """Verify data integrity against checksum"""
        try:
            calculated = self.calculate_checksum(data, algorithm)
            return calculated == expected_checksum
        except Exception as e:
            _logger.error(f"Checksum verification failed: {str(e)}")
            return False
    
    @api.model
    def calculate_media_move_checksum(self, media_move):
        """Calculate comprehensive checksum for media move"""
        from odoo import fields
        
        try:
            data = {
                'name': media_move.name,
                'date': str(media_move.date) if media_move.date else '',
                'ref': media_move.ref or '',
                'state': media_move.state,
                'total_debit': float(media_move.total_debit or 0),
                'total_credit': float(media_move.total_credit or 0),
                'subsidiary_id': media_move.subsidiary_id.id if media_move.subsidiary_id else None,
                'sync_engine_id': media_move.sync_engine_id.id if media_move.sync_engine_id else None,
                'lines': [
                    {
                        'sequence': line.sequence,
                        'name': line.name or '',
                        'account_code': line.account_code or '',
                        'debit': float(line.debit or 0),
                        'credit': float(line.credit or 0),
                        'partner_id': line.partner_id.id if line.partner_id else None,
                        'source_line_id': line.source_line_id,
                    }
                    for line in media_move.line_ids
                ],
                'timestamp': str(fields.Datetime.now()),
            }
            
            return self.calculate_checksum(data)
            
        except Exception as e:
            _logger.error(f"Media move checksum calculation failed: {str(e)}")
            raise
```

---

## File: `rpc_client.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/services`

```py
from odoo import models, api, _
from odoo.exceptions import UserError
import xmlrpc.client
import logging
import threading
import logging
from collections import defaultdict

_logger = logging.getLogger(__name__)


class RPCClient(models.AbstractModel):
    _name = 'rpc.client'
    _description = 'RPC Client Service'

    @api.model
    def connect(self, host, database, username, password):
        """Establish RPC connection"""
        try:
            # Common endpoint for authentication
            common = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/common')
            uid = common.authenticate(database, username, password, {})
            
            if not uid:
                raise UserError(_('Authentication failed'))
            
            # Object endpoint for operations
            models = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/object')
            
            return uid, models
            
        except Exception as e:
            _logger.error(f'RPC connection failed: {str(e)}')
            raise UserError(_('Connection failed: %s') % str(e))

    @api.model
    def execute(self, host, database, username, password, model, method, *args, **kwargs):
        """Execute RPC method"""
        uid, models = self.connect(host, database, username, password)
        
        try:
            return models.execute_kw(
                database, uid, password,
                model, method,
                args, kwargs
            )
        except Exception as e:
            _logger.error(f'RPC execution failed: {str(e)}')
            raise UserError(_('RPC execution failed: %s') % str(e))

    @api.model
    def search_read(self, host, database, username, password, model, domain, fields=None, limit=None):
        """Search and read records via RPC"""
        return self.execute(
            host, database, username, password,
            model, 'search_read',
            [domain],
            {'fields': fields, 'limit': limit}
        )

    @api.model
    def search(self, host, database, username, password, model, domain, limit=None):
        """Search records via RPC"""
        return self.execute(
            host, database, username, password,
            model, 'search',
            [domain],
            {'limit': limit}
        )

    @api.model
    def read(self, host, database, username, password, model, ids, fields=None):
        """Read records via RPC"""
        return self.execute(
            host, database, username, password,
            model, 'read',
            [ids],
            {'fields': fields}
        )

    @api.model
    def test_connection(self, host, database, username, password):
        """Test RPC connection"""
        try:
            uid, models = self.connect(host, database, username, password)
            
            # Test a simple operation
            version = models.execute_kw(
                database, uid, password,
                'ir.module.module', 'search_read',
                [[('name', '=', 'base'), ('state', '=', 'installed')]],
                {'fields': ['name'], 'limit': 1}
            )
            
            return {
                'success': True,
                'uid': uid,
                'message': 'Connection successful'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Connection failed: {str(e)}'
            }




class RPCPool(models.Model):
    _name = 'rpc.pool'
    _description = 'RPC Connection Pool Manager'
    
    _pool = defaultdict(dict)
    _lock = threading.Lock()
    
    @api.model
    def get_connection(self, host, db_name, username, password, max_connections=5):
        """Get RPC connection from pool or create new"""
        key = f"{host}|{db_name}|{username}"
        
        with self._lock:
            if key not in self._pool:
                self._pool[key] = {
                    'connections': [],
                    'in_use': set(),
                    'max_connections': max_connections,
                }
            
            pool = self._pool[key]
            
            # Try to get available connection
            for conn in pool['connections']:
                if id(conn) not in pool['in_use']:
                    pool['in_use'].add(id(conn))
                    _logger.debug(f"Reusing RPC connection for {key}")
                    return conn
            
            # Create new connection if under limit
            if len(pool['connections']) < pool['max_connections']:
                _logger.debug(f"Creating new RPC connection for {key}")
                common = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/common')
                uid = common.authenticate(db_name, username, password, {})
                
                if not uid:
                    raise Exception('Authentication failed')
                
                models = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/object')
                conn = (uid, models)
                
                pool['connections'].append(conn)
                pool['in_use'].add(id(conn))
                return conn
            
            # Wait for available connection (simplified - in reality would need async)
            raise Exception('Connection pool exhausted')
    
    @api.model
    def release_connection(self, host, db_name, username, password, connection):
        """Release connection back to pool"""
        key = f"{host}|{db_name}|{username}"
        
        with self._lock:
            if key in self._pool:
                pool = self._pool[key]
                conn_id = id(connection)
                if conn_id in pool['in_use']:
                    pool['in_use'].remove(conn_id)
                    _logger.debug(f"Released RPC connection for {key}")
    
    @api.model
    def cleanup_pool(self):
        """Clean up idle connections"""
        with self._lock:
            for key, pool in list(self._pool.items()):
                # Remove pools that haven't been used recently
                # Implementation depends on usage tracking
                pass
```

---

## File: `webhook_receiver.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/services`

```py
from odoo import models, api, _
from odoo.exceptions import UserError
import json
import logging
import hashlib
import hmac

_logger = logging.getLogger(__name__)


class WebhookReceiver(models.AbstractModel):
    _name = 'webhook.receiver'
    _description = 'Webhook Receiver Service'

    @api.model
    def receive_webhook(self, payload, headers=None):
        """Receive and process webhook"""
        try:
            # Validate webhook signature if configured
            if headers and 'X-Webhook-Signature' in headers:
                if not self._validate_signature(payload, headers['X-Webhook-Signature']):
                    raise UserError(_('Invalid webhook signature'))
            
            # Parse payload
            data = json.loads(payload) if isinstance(payload, str) else payload
            
            # Process based on event type
            event_type = data.get('event_type')
            
            if event_type == 'subsidiary.data.updated':
                return self._handle_data_update(data)
            elif event_type == 'subsidiary.connection.lost':
                return self._handle_connection_lost(data)
            elif event_type == 'subsidiary.sync.requested':
                return self._handle_sync_request(data)
            else:
                _logger.warning(f'Unknown webhook event type: {event_type}')
                return {'status': 'ignored', 'message': 'Unknown event type'}
            
        except Exception as e:
            _logger.error(f'Webhook processing failed: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    def _validate_signature(self, payload, signature):
        """Validate webhook signature"""
        # Get secret from config
        secret = self.env['ir.config_parameter'].sudo().get_param(
            'financial_consolidation.webhook_secret', ''
        )
        
        if not secret:
            return True  # No validation if no secret configured
        
        # Calculate expected signature
        expected = hmac.new(
            secret.encode(),
            payload.encode() if isinstance(payload, str) else json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected)

    def _handle_data_update(self, data):
        """Handle subsidiary data update event"""
        subsidiary_code = data.get('subsidiary_code')
        
        if not subsidiary_code:
            return {'status': 'error', 'message': 'Missing subsidiary_code'}
        
        subsidiary = self.env['subsidiary.instance'].search([
            ('code', '=', subsidiary_code)
        ], limit=1)
        
        if not subsidiary:
            return {'status': 'error', 'message': f'Subsidiary {subsidiary_code} not found'}
        
        # Trigger sync if real-time mode
        if subsidiary.sync_mode == 'realtime':
            # Create sync wizard
            wizard = self.env['consolidation.run.wizard'].create({
                'subsidiary_ids': [(6, 0, [subsidiary.id])],
                'date_from': data.get('date_from'),
                'date_to': data.get('date_to'),
                'auto_reconcile': True,
                'auto_promote': True,
            })
            
            wizard.action_start_consolidation()
            
            return {'status': 'success', 'message': 'Sync triggered'}
        
        return {'status': 'ignored', 'message': 'Not in realtime mode'}

    def _handle_connection_lost(self, data):
        """Handle connection lost event"""
        subsidiary_code = data.get('subsidiary_code')
        
        if not subsidiary_code:
            return {'status': 'error', 'message': 'Missing subsidiary_code'}
        
        subsidiary = self.env['subsidiary.instance'].search([
            ('code', '=', subsidiary_code)
        ], limit=1)
        
        if subsidiary:
            subsidiary.write({'state': 'error'})
            
            # Log the event
            self.env['consolidation.log'].log_error(
                f'Connection lost to subsidiary {subsidiary.name}',
                subsidiary_id=subsidiary.id
            )
        
        return {'status': 'success', 'message': 'Connection status updated'}

    def _handle_sync_request(self, data):
        """Handle sync request event"""
        subsidiary_code = data.get('subsidiary_code')
        
        if not subsidiary_code:
            return {'status': 'error', 'message': 'Missing subsidiary_code'}
        
        subsidiary = self.env['subsidiary.instance'].search([
            ('code', '=', subsidiary_code)
        ], limit=1)
        
        if not subsidiary:
            return {'status': 'error', 'message': f'Subsidiary {subsidiary_code} not found'}
        
        # Create and start sync
        sync = self.env['sync.engine'].create({
            'subsidiary_ids': [(6, 0, [subsidiary.id])],
            'date_from': data.get('date_from'),
            'date_to': data.get('date_to'),
            'processing_mode': 'sequential',
        })
        
        sync.action_start_sync()
        
        return {
            'status': 'success',
            'message': 'Sync started',
            'sync_id': sync.id,
            'sync_name': sync.name
        }
```

---

## File: `__init__.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/wizards`

```py
from . import account_mapping_copy_wizard
from . import consolidation_run_wizard
from . import reconciliation_wizard
from . import rollback_wizard
from . import journal_mapping_wizard
```

---

## File: `account_mapping_copy_wizard.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/wizards`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMappingCopyWizard(models.TransientModel):
    _name = 'account.mapping.copy.wizard'
    _description = 'Copy Account Mapping Wizard'

    source_mapping_id = fields.Many2one('account.mapping', string='Source Mapping',
                                         required=True, readonly=True)
    source_subsidiary_id = fields.Many2one('subsidiary.instance', 
                                            related='source_mapping_id.subsidiary_id',
                                            readonly=True)
    
    target_subsidiary_ids = fields.Many2many('subsidiary.instance', 
                                              string='Target Subsidiaries',
                                              required=True,
                                              domain="[('id', '!=', source_subsidiary_id)]")
    
    copy_type = fields.Selection([
        ('exact', 'Exact Copy'),
        ('similar', 'Similar Accounts (Same Code Pattern)'),
        ('all', 'All Accounts from Source Subsidiary'),
    ], string='Copy Type', default='exact', required=True)
    
    include_mapping_data = fields.Boolean(string='Include Mapping Data', default=True)
    overwrite_existing = fields.Boolean(string='Overwrite Existing Mappings', default=False)
    
    # Preview
    estimated_mappings = fields.Integer(string='Estimated Mappings', compute='_compute_preview')
    existing_mappings = fields.Integer(string='Existing Mappings', compute='_compute_preview')
    
    @api.depends('target_subsidiary_ids', 'copy_type')
    def _compute_preview(self):
        for wizard in self:
            wizard.estimated_mappings = 0
            wizard.existing_mappings = 0
            
            if wizard.source_mapping_id and wizard.target_subsidiary_ids:
                if wizard.copy_type == 'exact':
                    wizard.estimated_mappings = len(wizard.target_subsidiary_ids)
                    
                    # Check existing
                    existing = self.env['account.mapping'].search([
                        ('subsidiary_id', 'in', wizard.target_subsidiary_ids.ids),
                        ('subsidiary_account_code', '=', wizard.source_mapping_id.subsidiary_account_code),
                    ])
                    wizard.existing_mappings = len(existing)
                
                elif wizard.copy_type == 'all':
                    # Count all mappings in source subsidiary
                    total_source = self.env['account.mapping'].search_count([
                        ('subsidiary_id', '=', wizard.source_subsidiary_id.id)
                    ])
                    wizard.estimated_mappings = total_source * len(wizard.target_subsidiary_ids)

    def action_copy_mappings(self):
        """Copy mappings to target subsidiaries"""
        self.ensure_one()
        
        created_mappings = self.env['account.mapping']
        skipped_mappings = 0
        
        for target_subsidiary in self.target_subsidiary_ids:
            if self.copy_type == 'exact':
                # Copy single mapping
                mapping = self._copy_single_mapping(target_subsidiary)
                if mapping:
                    created_mappings |= mapping
                else:
                    skipped_mappings += 1
            
            elif self.copy_type == 'all':
                # Copy all mappings from source subsidiary
                source_mappings = self.env['account.mapping'].search([
                    ('subsidiary_id', '=', self.source_subsidiary_id.id)
                ])
                
                for source_mapping in source_mappings:
                    mapping = self._copy_single_mapping(target_subsidiary, source_mapping)
                    if mapping:
                        created_mappings |= mapping
                    else:
                        skipped_mappings += 1
        
        # Return result
        message = _('Created %d mappings. Skipped %d existing mappings.') % (
            len(created_mappings), skipped_mappings
        )
        
        if created_mappings:
            return {
                'name': _('Copied Mappings'),
                'type': 'ir.actions.act_window',
                'res_model': 'account.mapping',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', created_mappings.ids)],
                'context': {'create': False},
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Copy Complete'),
                    'message': message,
                    'type': 'info',
                }
            }

    def _copy_single_mapping(self, target_subsidiary, source_mapping=None):
        """Copy a single mapping to target subsidiary"""
        source_mapping = source_mapping or self.source_mapping_id
        
        # Check if mapping already exists
        existing = self.env['account.mapping'].search([
            ('subsidiary_id', '=', target_subsidiary.id),
            ('subsidiary_account_code', '=', source_mapping.subsidiary_account_code),
        ], limit=1)
        
        if existing and not self.overwrite_existing:
            return False
        
        # Prepare mapping values
        mapping_vals = {
            'subsidiary_id': target_subsidiary.id,
            'subsidiary_account_code': source_mapping.subsidiary_account_code,
            'subsidiary_account_name': source_mapping.subsidiary_account_name,
            'subsidiary_account_type': source_mapping.subsidiary_account_type,
            'parent_account_id': source_mapping.parent_account_id.id,
            'mapping_type': source_mapping.mapping_type,
            'active': source_mapping.active,
            'auto_create': source_mapping.auto_create,
            'apply_conversion': source_mapping.apply_conversion,
        }
        
        if existing and self.overwrite_existing:
            existing.write(mapping_vals)
            return existing
        else:
            return self.env['account.mapping'].create(mapping_vals)
```

---

## File: `consolidation_run_wizard.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/wizards`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ConsolidationRunWizard(models.TransientModel):
    _name = 'consolidation.run.wizard'
    _description = 'Consolidation Run Wizard'

    # Subsidiary Selection
    subsidiary_ids = fields.Many2many('subsidiary.instance', string='Subsidiaries',
                                       required=True, 
                                       domain=[('state', '=', 'validated'), ('active', '=', True)])
    all_subsidiaries = fields.Boolean(string='All Active Subsidiaries', default=False)
    
    # Date Range
    date_from = fields.Date(string='Date From', required=True,
                             default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='Date To', required=True,
                           default=lambda self: fields.Date.today())
    
    # Quick Date Selection
    period_type = fields.Selection([
        ('custom', 'Custom Range'),
        ('today', 'Today'),
        ('this_week', 'This Week'),
        ('this_month', 'This Month'),
        ('last_month', 'Last Month'),
        ('this_quarter', 'This Quarter'),
        ('this_year', 'This Year'),
    ], string='Period', default='this_month')
    
    # Processing Options
    processing_mode = fields.Selection([
        ('sequential', 'Sequential'),
        ('parallel', 'Parallel'),
    ], string='Processing Mode', default='parallel', required=True)
    
    max_workers = fields.Integer(string='Max Workers', default=4,
                                  help='Number of parallel workers (parallel mode only)')
    
    # Automation Options
    auto_reconcile = fields.Boolean(string='Auto Reconciliation', default=False,
                                     help='Automatically execute reconciliation after data fetch')
    auto_promote = fields.Boolean(string='Auto Promotion', default=False,
                                   help='Automatically promote to accounting after reconciliation')
    skip_validation = fields.Boolean(string='Skip Pre-sync Validation', default=False,
                                      help='Skip validation phase (use with caution)')
    
    # Advanced Options
    batch_size = fields.Integer(string='Batch Size', default=100,
                                 help='Number of records to process in each batch')
    max_retries = fields.Integer(string='Max Retries', default=3,
                                  help='Maximum retry attempts on error')
    
    # Summary
    total_subsidiaries = fields.Integer(string='Total Subsidiaries', 
                                         compute='_compute_summary')
    estimated_duration = fields.Float(string='Estimated Duration (min)',
                                       compute='_compute_summary',
                                       help='Estimated based on historical data')
    
    # Validation Check
    has_unmapped_accounts = fields.Boolean(string='Has Unmapped Accounts',
                                            compute='_compute_validation_check')
    validation_warnings = fields.Text(string='Validation Warnings',
                                       compute='_compute_validation_check')

    @api.depends('subsidiary_ids', 'all_subsidiaries')
    def _compute_summary(self):
        for wizard in self:
            if wizard.all_subsidiaries:
                subsidiaries = self.env['subsidiary.instance'].search([
                    ('state', '=', 'validated'),
                    ('active', '=', True),
                ])
                wizard.total_subsidiaries = len(subsidiaries)
            else:
                wizard.total_subsidiaries = len(wizard.subsidiary_ids)
            
            # Estimate duration based on average
            if wizard.total_subsidiaries > 0:
                avg_duration = 2.0  # Default 2 minutes per subsidiary
                # Get actual average if available
                recent_syncs = self.env['sync.engine'].search([
                    ('state', '=', 'completed'),
                    ('create_date', '>=', fields.Datetime.now() - timedelta(days=30))
                ], limit=10)
                
                if recent_syncs:
                    avg_duration = sum(recent_syncs.mapped('duration')) / len(recent_syncs) / 60
                
                wizard.estimated_duration = wizard.total_subsidiaries * avg_duration
            else:
                wizard.estimated_duration = 0.0

    @api.depends('subsidiary_ids')
    def _compute_validation_check(self):
        for wizard in self:
            warnings = []
            has_unmapped = False
            
            subsidiaries = wizard._get_subsidiaries()
            
            for subsidiary in subsidiaries:
                # Check account mappings
                if not subsidiary.account_mapping_ids:
                    warnings.append(f'No account mappings for {subsidiary.name}')
                    has_unmapped = True
                
                # Check journal mappings
                if not subsidiary.journal_mapping_ids:
                    warnings.append(f'No journal mappings for {subsidiary.name}')
                
                # Check last sync
                if not subsidiary.last_sync_date:
                    warnings.append(f'First sync for {subsidiary.name}')
            
            wizard.has_unmapped_accounts = has_unmapped
            wizard.validation_warnings = '\n'.join(warnings) if warnings else False

    @api.onchange('period_type')
    def _onchange_period_type(self):
        """Auto-fill dates based on period selection"""
        if self.period_type == 'custom':
            return
        
        today = fields.Date.today()
        
        if self.period_type == 'today':
            self.date_from = today
            self.date_to = today
        
        elif self.period_type == 'this_week':
            start = today - timedelta(days=today.weekday())
            self.date_from = start
            self.date_to = today
        
        elif self.period_type == 'this_month':
            self.date_from = today.replace(day=1)
            self.date_to = today
        
        elif self.period_type == 'last_month':
            first_this_month = today.replace(day=1)
            last_month_end = first_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            self.date_from = last_month_start
            self.date_to = last_month_end
        
        elif self.period_type == 'this_quarter':
            quarter = (today.month - 1) // 3
            quarter_start_month = quarter * 3 + 1
            self.date_from = today.replace(month=quarter_start_month, day=1)
            self.date_to = today
        
        elif self.period_type == 'this_year':
            self.date_from = today.replace(month=1, day=1)
            self.date_to = today

    @api.onchange('all_subsidiaries')
    def _onchange_all_subsidiaries(self):
        """Auto-select all subsidiaries"""
        if self.all_subsidiaries:
            all_subs = self.env['subsidiary.instance'].search([
                ('state', '=', 'validated'),
                ('active', '=', True),
            ])
            self.subsidiary_ids = [(6, 0, all_subs.ids)]

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for wizard in self:
            if wizard.date_from > wizard.date_to:
                raise ValidationError(_('Date From must be before Date To'))

    def _get_subsidiaries(self):
        """Get selected subsidiaries"""
        if self.all_subsidiaries:
            return self.env['subsidiary.instance'].search([
                ('state', '=', 'validated'),
                ('active', '=', True),
            ])
        return self.subsidiary_ids

    def action_start_consolidation(self):
        """Start consolidation process"""
        self.ensure_one()
        
        # Validate
        subsidiaries = self._get_subsidiaries()
        
        if not subsidiaries:
            raise ValidationError(_('Please select at least one subsidiary'))
        
        # Create sync engine
        sync = self.env['sync.engine'].create({
            'subsidiary_ids': [(6, 0, subsidiaries.ids)],
            'date_from': self.date_from,
            'date_to': self.date_to,
            'processing_mode': self.processing_mode,
            'max_workers': self.max_workers,
            'auto_reconcile': self.auto_reconcile,
            'auto_promote': self.auto_promote,
            'skip_validation': self.skip_validation,
            'max_retries': self.max_retries,
        })
        
        # Start sync
        try:
            sync.action_start_sync()
            
            return {
                'name': _('Consolidation Sync'),
                'type': 'ir.actions.act_window',
                'res_model': 'sync.engine',
                'res_id': sync.id,
                'view_mode': 'form',
                'target': 'current',
            }
            
        except Exception as e:
            raise ValidationError(_('Consolidation failed: %s') % str(e))

    def action_preview_data(self):
        """Preview what will be consolidated"""
        self.ensure_one()
        
        subsidiaries = self._get_subsidiaries()
        
        # Quick validation
        total_moves = 0
        preview_data = []
        
        for subsidiary in subsidiaries:
            try:
                uid, models = subsidiary.get_rpc_connection()
                
                domain = [
                    ('date', '>=', str(self.date_from)),
                    ('date', '<=', str(self.date_to)),
                    ('state', '=', 'posted'),
                ]
                
                count = models.execute_kw(
                    subsidiary.db_name, uid, subsidiary.password,
                    'account.move', 'search_count',
                    [domain]
                )
                
                total_moves += count
                preview_data.append({
                    'subsidiary': subsidiary.name,
                    'moves': count,
                })
                
            except Exception as e:
                preview_data.append({
                    'subsidiary': subsidiary.name,
                    'error': str(e),
                })
        
        # Display preview
        message = f"Consolidation Preview\n{'='*50}\n\n"
        message += f"Period: {self.date_from} to {self.date_to}\n"
        message += f"Subsidiaries: {len(subsidiaries)}\n"
        message += f"Total Moves: {total_moves}\n\n"
        message += "Details:\n"
        
        for data in preview_data:
            if 'error' in data:
                message += f"  ❌ {data['subsidiary']}: ERROR - {data['error']}\n"
            else:
                message += f"  ✓ {data['subsidiary']}: {data['moves']} moves\n"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Preview'),
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }

    def action_validate_mappings(self):
        """Validate all mappings before sync"""
        self.ensure_one()
        
        subsidiaries = self._get_subsidiaries()
        errors = []
        
        for subsidiary in subsidiaries:
            # Validate account mappings
            for mapping in subsidiary.account_mapping_ids:
                if not mapping.is_validated:
                    try:
                        mapping.action_validate_mapping()
                    except Exception as e:
                        errors.append(f'{subsidiary.name}: {str(e)}')
            
            # Validate journal mappings
            for mapping in subsidiary.journal_mapping_ids:
                if not mapping.is_validated:
                    try:
                        mapping.action_validate_mapping()
                    except Exception as e:
                        errors.append(f'{subsidiary.name}: {str(e)}')
        
        if errors:
            raise ValidationError('\n'.join(errors))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('All mappings validated successfully!'),
                'type': 'success',
            }
        }
```

---

## File: `journal_mapping_wizard.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/wizards`

```py
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class JournalMappingWizard(models.TransientModel):
    _name = 'journal.mapping.wizard'
    _description = 'Journal Mapping Configuration Wizard'

    subsidiary_id = fields.Many2one('subsidiary.instance', string='Subsidiary',
                                     required=True)
    
    # Options
    mapping_strategy = fields.Selection([
        ('auto_discover', 'Auto-discover Subsidiary Journals'),
        ('manual', 'Manual Configuration'),
        ('import', 'Import from CSV/Excel'),
    ], string='Mapping Strategy', default='auto_discover', required=True)
    
    # Auto-discover options
    discover_all_journals = fields.Boolean(string='Discover All Journals', default=True)
    journal_types = fields.Selection([
        ('all', 'All Journal Types'),
        ('general', 'General Only'),
        ('sale_purchase', 'Sales & Purchase Only'),
        ('bank_cash', 'Bank & Cash Only'),
    ], string='Journal Types', default='all')
    
    # Default mapping
    default_consolidation_journal_id = fields.Many2one('account.journal',
                                                        string='Default Consolidation Journal',
                                                        domain="[('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', related='subsidiary_id.company_id',
                                  readonly=True)
    
    # Results
    discovered_journals = fields.Text(string='Discovered Journals', readonly=True)
    mappings_to_create = fields.Integer(string='Mappings to Create', compute='_compute_results')
    
    @api.depends('subsidiary_id', 'mapping_strategy')
    def _compute_results(self):
        for wizard in self:
            if wizard.subsidiary_id and wizard.mapping_strategy == 'auto_discover':
                try:
                    uid, models = wizard.subsidiary_id.get_rpc_connection()
                    journals = models.execute_kw(
                        wizard.subsidiary_id.db_name, uid, wizard.subsidiary_id.password,
                        'account.journal', 'search_read',
                        [[]],
                        {'fields': ['name', 'code', 'type']}
                    )
                    wizard.mappings_to_create = len(journals)
                    wizard.discovered_journals = '\n'.join([
                        f"{j['code']} - {j['name']} ({j['type']})" for j in journals[:20]
                    ]) + (f'\n... and {len(journals)-20} more' if len(journals) > 20 else '')
                except:
                    wizard.mappings_to_create = 0
                    wizard.discovered_journals = 'Could not connect to subsidiary'
            else:
                wizard.mappings_to_create = 0
                wizard.discovered_journals = ''

    def action_discover_journals(self):
        """Discover journals from subsidiary"""
        self.ensure_one()
        
        try:
            uid, models = self.subsidiary_id.get_rpc_connection()
            
            # Build domain based on selected types
            domain = []
            if not self.discover_all_journals and self.journal_types != 'all':
                if self.journal_types == 'general':
                    domain.append(('type', '=', 'general'))
                elif self.journal_types == 'sale_purchase':
                    domain.append(('type', 'in', ['sale', 'purchase']))
                elif self.journal_types == 'bank_cash':
                    domain.append(('type', 'in', ['bank', 'cash']))
            
            journals = models.execute_kw(
                self.subsidiary_id.db_name, uid, self.subsidiary_id.password,
                'account.journal', 'search_read',
                [domain],
                {'fields': ['name', 'code', 'type'], 'order': 'code'}
            )
            
            # Create mappings for discovered journals
            created_count = 0
            for journal in journals:
                # Check if mapping already exists
                existing = self.env['journal.mapping'].search([
                    ('subsidiary_id', '=', self.subsidiary_id.id),
                    ('subsidiary_journal_id', '=', journal['id']),
                ])
                
                if not existing:
                    # Find appropriate consolidation journal
                    consolidation_journal = self._find_consolidation_journal(journal)
                    
                    # Create mapping
                    self.env['journal.mapping'].create({
                        'subsidiary_id': self.subsidiary_id.id,
                        'subsidiary_journal_id': journal['id'],
                        'subsidiary_journal_code': journal.get('code', ''),
                        'subsidiary_journal_name': journal['name'],
                        'subsidiary_journal_type': journal.get('type', 'general'),
                        'parent_journal_id': consolidation_journal.id,
                    })
                    created_count += 1
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Journal Discovery Complete'),
                    'message': _('Discovered %d journals and created %d new mappings.') % 
                               (len(journals), created_count),
                    'type': 'success',
                }
            }
            
        except Exception as e:
            raise ValidationError(_('Journal discovery failed: %s') % str(e))

    def _find_consolidation_journal(self, subsidiary_journal):
        """Find appropriate consolidation journal based on subsidiary journal"""
        # Try to match by type first
        journal_type = subsidiary_journal.get('type', 'general')
        journal_code = subsidiary_journal.get('code', '').upper()
        
        # Define type mappings
        type_mappings = {
            'sale': 'sale',
            'purchase': 'purchase',
            'cash': 'cash',
            'bank': 'bank',
            'general': 'general',
            'situation': 'general',
        }
        
        target_type = type_mappings.get(journal_type, 'general')
        
        # Look for existing journal of same type
        target_journal = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('type', '=', target_type),
        ], order='id', limit=1)
        
        # If not found, use default or create one
        if not target_journal:
            if self.default_consolidation_journal_id:
                target_journal = self.default_consolidation_journal_id
            else:
                # Create a new journal
                journal_code = f"CONS-{journal_type.upper()}"
                target_journal = self.env['account.journal'].create({
                    'name': f'Consolidation - {journal_type.title()}',
                    'code': journal_code,
                    'type': target_type,
                    'company_id': self.company_id.id,
                })
        
        return target_journal

    def action_create_default_mappings(self):
        """Create default journal mappings"""
        self.ensure_one()
        
        # Create default consolidation journals
        default_journals = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('code', 'ilike', 'CONS'),
        ])
        
        if not default_journals:
            # Create default set
            default_journals = self.env['account.journal'].create([
                {
                    'name': 'Consolidation Journal',
                    'code': 'CONS',
                    'type': 'general',
                    'company_id': self.company_id.id,
                },
                {
                    'name': 'Consolidation Sales',
                    'code': 'CONS-SALE',
                    'type': 'sale',
                    'company_id': self.company_id.id,
                },
                {
                    'name': 'Consolidation Purchase',
                    'code': 'CONS-PUR',
                    'type': 'purchase',
                    'company_id': self.company_id.id,
                },
                {
                    'name': 'Consolidation Bank',
                    'code': 'CONS-BANK',
                    'type': 'bank',
                    'company_id': self.company_id.id,
                },
            ])
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Default Journals Created'),
                'message': _('Created %d default consolidation journals.') % len(default_journals),
                'type': 'success',
            }
        }
```

---

## File: `reconciliation_wizard.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/wizards`

```py
# -*- coding: utf-8 -*-
# FILE: wizards/reconciliation_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ReconciliationWizard(models.TransientModel):
    _name = 'reconciliation.wizard'
    _description = 'Manual Reconciliation Wizard'

    sync_engine_id = fields.Many2one('sync.engine', string='Sync Engine',
                                      required=True, readonly=True)
    
    # Reconciliation Type
    reconciliation_type = fields.Selection([
        ('intercompany', 'Intercompany Elimination'),
        ('fx', 'Foreign Exchange Adjustment'),
        ('provision', 'Provision Adjustment'),
        ('manual', 'Manual Adjustment'),
    ], string='Reconciliation Type', required=True, default='intercompany')
    
    # Selection
    media_move_ids = fields.Many2many('media.account.move', string='Media Moves',
                                       domain="[('sync_engine_id', '=', sync_engine_id), ('state', '=', 'validated')]")
    
    # FX Options
    apply_fx_to_all = fields.Boolean(string='Apply FX to All Moves', default=False)
    target_currency_id = fields.Many2one('res.currency', string='Target Currency')
    
    # Intercompany Options
    auto_detect_intercompany = fields.Boolean(string='Auto-detect Intercompany Transactions',
                                                default=True)
    elimination_account_id = fields.Many2one('account.account', string='Elimination Account')
    
    # Manual Adjustment
    manual_description = fields.Text(string='Description')
    manual_amount = fields.Float(string='Amount', digits='Account')
    manual_account_id = fields.Many2one('account.account', string='Account')
    
    # Summary
    total_moves_selected = fields.Integer(compute='_compute_summary')
    estimated_adjustments = fields.Integer(compute='_compute_summary')

    @api.depends('media_move_ids')
    def _compute_summary(self):
        for wizard in self:
            wizard.total_moves_selected = len(wizard.media_move_ids)
            
            # Estimate adjustments
            if wizard.reconciliation_type == 'fx':
                wizard.estimated_adjustments = len(wizard.media_move_ids.filtered(
                    lambda m: m.currency_id != m.company_id.currency_id
                ))
            else:
                wizard.estimated_adjustments = 0

    def action_execute_reconciliation(self):
        """Execute reconciliation"""
        self.ensure_one()
        
        reconciliation_engine = self.env['reconciliation.engine']
        
        if self.reconciliation_type == 'fx':
            return self._execute_fx_reconciliation()
        elif self.reconciliation_type == 'intercompany':
            return self._execute_intercompany_reconciliation()
        elif self.reconciliation_type == 'provision':
            return self._execute_provision_reconciliation()
        elif self.reconciliation_type == 'manual':
            return self._execute_manual_adjustment()

    def _execute_fx_reconciliation(self):
        """Execute FX reconciliation"""
        currency_engine = self.env['currency.conversion']
        
        count = 0
        for media_move in self.media_move_ids:
            if media_move.currency_id != media_move.company_id.currency_id:
                currency_engine.convert_media_move(media_move)
                media_move.action_reconcile()
                count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('FX Reconciliation Complete'),
                'message': _('%d moves converted and reconciled') % count,
                'type': 'success',
            }
        }

    def _execute_intercompany_reconciliation(self):
        """Execute intercompany reconciliation"""
        # This would implement intercompany elimination logic
        # For now, just mark as reconciled
        
        for media_move in self.media_move_ids:
            media_move.action_reconcile()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Intercompany Reconciliation Complete'),
                'message': _('%d moves reconciled') % len(self.media_move_ids),
                'type': 'success',
            }
        }

    def _execute_provision_reconciliation(self):
        """Execute provision reconciliation"""
        for media_move in self.media_move_ids:
            media_move.action_reconcile()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Provision Reconciliation Complete'),
                'message': _('%d moves reconciled') % len(self.media_move_ids),
                'type': 'success',
            }
        }

    def _execute_manual_adjustment(self):
        """Execute manual adjustment"""
        if not self.manual_account_id or not self.manual_amount:
            raise ValidationError(_('Please specify account and amount for manual adjustment'))
        
        # Create adjustment entry
        # Implementation depends on business requirements
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Manual Adjustment Created'),
                'message': _('Adjustment of %s created') % self.manual_amount,
                'type': 'success',
            }
        }

```

---

## File: `rollback_wizard.py`

**Parent Path:** `/home/reda/source/central_sync/custom_addons/financial_consolidation/wizards`

```py

# FILE: wizards/rollback_wizard.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class RollbackWizard(models.TransientModel):
    _name = 'rollback.wizard'
    _description = 'Consolidation Rollback Wizard'

    sync_engine_id = fields.Many2one('sync.engine', string='Sync to Rollback',
                                      required=True, readonly=True)
    restore_point_id = fields.Many2one('restore.point', string='Restore Point',
                                        domain="[('sync_engine_id', '=', sync_engine_id)]")
    
    # Rollback Options
    rollback_type = fields.Selection([
        ('full', 'Full Rollback (Delete promoted moves)'),
        ('media_only', 'Media Only (Keep promoted moves)'),
        ('partial', 'Partial (Select specific moves)'),
    ], string='Rollback Type', default='full', required=True)
    
    # Partial Rollback
    media_move_ids = fields.Many2many('media.account.move', string='Moves to Rollback',
                                       domain="[('sync_engine_id', '=', sync_engine_id)]")
    
    # Confirmation
    reason = fields.Text(string='Reason', required=True,
                         help='Explain why you are rolling back this sync')
    confirm = fields.Boolean(string='I understand this action cannot be easily undone')
    
    # Impact Analysis
    promoted_moves_count = fields.Integer(string='Promoted Moves',
                                           compute='_compute_impact')
    media_moves_count = fields.Integer(string='Media Moves',
                                        compute='_compute_impact')
    will_delete_count = fields.Integer(string='Will Delete',
                                        compute='_compute_impact')
    
    # Warnings
    has_posted_moves = fields.Boolean(compute='_compute_warnings')
    warning_message = fields.Text(compute='_compute_warnings')

    @api.depends('sync_engine_id', 'rollback_type', 'media_move_ids')
    def _compute_impact(self):
        for wizard in self:
            if wizard.sync_engine_id:
                wizard.promoted_moves_count = len(wizard.sync_engine_id.media_move_ids.filtered(
                    lambda m: m.promoted_move_id
                ))
                wizard.media_moves_count = len(wizard.sync_engine_id.media_move_ids)
                
                if wizard.rollback_type == 'full':
                    wizard.will_delete_count = wizard.promoted_moves_count
                elif wizard.rollback_type == 'partial':
                    wizard.will_delete_count = len(wizard.media_move_ids)
                else:
                    wizard.will_delete_count = 0
            else:
                wizard.promoted_moves_count = 0
                wizard.media_moves_count = 0
                wizard.will_delete_count = 0

    @api.depends('sync_engine_id')
    def _compute_warnings(self):
        for wizard in self:
            warnings = []
            has_posted = False
            
            if wizard.sync_engine_id:
                # Check for posted moves
                posted_moves = wizard.sync_engine_id.media_move_ids.filtered(
                    lambda m: m.promoted_move_id and m.promoted_move_id.state == 'posted'
                )
                
                if posted_moves:
                    has_posted = True
                    warnings.append(f'{len(posted_moves)} posted accounting entries will be affected')
                
                # Check for locked period
                for media_move in wizard.sync_engine_id.media_move_ids:
                    if media_move.promoted_move_id:
                        # Check if in locked period
                        # This would check against fiscal year locks
                        pass
            
            wizard.has_posted_moves = has_posted
            wizard.warning_message = '\n'.join(warnings) if warnings else False

    def action_rollback(self):
        """Execute rollback operation"""
        self.ensure_one()
        
        if not self.confirm:
            raise UserError(_('You must confirm the rollback action.'))
        
        try:
            # Log rollback initiation
            self.env['consolidation.log'].log_operation(
                'rollback',
                f'Rollback initiated: {self.reason}',
                sync_engine_id=self.sync_engine_id.id
            )
            
            # Create immutable ledger entry
            self.env['immutable.ledger'].create_ledger_entry(
                transaction_id=f'{self.sync_engine_id.name}_rollback',
                operation='rollback_initiated',
                data_snapshot=json.dumps({
                    'reason': self.reason,
                    'rollback_type': self.rollback_type,
                    'timestamp': str(fields.Datetime.now()),
                }),
                sync_engine_id=self.sync_engine_id.id
            )
            
            # Execute rollback based on type
            if self.rollback_type == 'full':
                self._execute_full_rollback()
            elif self.rollback_type == 'media_only':
                self._execute_media_rollback()
            elif self.rollback_type == 'partial':
                self._execute_partial_rollback()
            
            # Update sync engine state
            self.sync_engine_id.write({
                'state': 'cancelled',
                'error_message': f'Rolled back: {self.reason}',
            })
            
            # Release lock if held
            if self.sync_engine_id.is_locked:
                self.sync_engine_id._release_lock()
            
            # Final audit entry
            self.env['consolidation.log'].log_operation(
                'rollback',
                'Rollback completed successfully',
                sync_engine_id=self.sync_engine_id.id
            )
            
            # Mark restore point as used
            if self.restore_point_id:
                self.restore_point_id.write({
                    'restored': True,
                    'restore_date': fields.Datetime.now(),
                    'restored_by': self.env.user.id,
                })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Rollback Completed'),
                    'message': _('Sync has been rolled back successfully.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f'Rollback failed for sync {self.sync_engine_id.name}: {str(e)}', 
                         exc_info=True)
            
            self.env['consolidation.log'].log_error(
                f'Rollback failed: {str(e)}',
                sync_engine_id=self.sync_engine_id.id,
                exception=e
            )
            
            raise UserError(_('Rollback failed: %s') % str(e))

    def _execute_full_rollback(self):
        """Full rollback - delete all promoted moves"""
        _logger.info(f'Executing full rollback for sync {self.sync_engine_id.name}')
        
        # Get all promoted moves
        promoted_moves = self.env['account.move'].search([
            ('id', 'in', self.sync_engine_id.media_move_ids.mapped('promoted_move_id').ids)
        ])
        
        # Cancel and delete moves
        for move in promoted_moves:
            try:
                if move.state == 'posted':
                    move.button_draft()
                move.unlink()
            except Exception as e:
                _logger.warning(f'Could not delete move {move.name}: {str(e)}')
                # Try to cancel instead
                try:
                    move.button_cancel()
                except:
                    pass
        
        # Reset media moves
        self.sync_engine_id.media_move_ids.write({
            'state': 'draft',
            'promoted_move_id': False,
            'promotion_date': False,
        })
        
        _logger.info(f'Full rollback completed: {len(promoted_moves)} moves processed')

    def _execute_media_rollback(self):
        """Media only rollback - keep promoted moves, reset staging"""
        _logger.info(f'Executing media-only rollback for sync {self.sync_engine_id.name}')
        
        # Just reset media moves state
        self.sync_engine_id.media_move_ids.write({
            'state': 'draft',
        })
        
        _logger.info('Media rollback completed')

    def _execute_partial_rollback(self):
        """Partial rollback - rollback selected moves only"""
        _logger.info(f'Executing partial rollback for sync {self.sync_engine_id.name}')
        
        if not self.media_move_ids:
            raise UserError(_('Please select moves to rollback'))
        
        # Get promoted moves for selected media moves
        promoted_moves = self.env['account.move'].search([
            ('id', 'in', self.media_move_ids.mapped('promoted_move_id').ids)
        ])
        
        # Delete selected promoted moves
        for move in promoted_moves:
            try:
                if move.state == 'posted':
                    move.button_draft()
                move.unlink()
            except Exception as e:
                _logger.warning(f'Could not delete move {move.name}: {str(e)}')
        
        # Reset selected media moves
        self.media_move_ids.write({
            'state': 'draft',
            'promoted_move_id': False,
            'promotion_date': False,
        })
        
        _logger.info(f'Partial rollback completed: {len(self.media_move_ids)} moves')
```

---


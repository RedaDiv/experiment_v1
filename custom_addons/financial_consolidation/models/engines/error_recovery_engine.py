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
        # Use the module/function style handler for compatibility
        error_info = self.handle_exception('ErrorRecovery', 'handle_sync_error', error, context=context, reraise=False)

        error_type = error_info.get('category', 'unknown') if isinstance(error_info, dict) else 'unknown'
        error_severity = error_info.get('severity', 'low') if isinstance(error_info, dict) else 'low'

        _logger.info(f'Handling {error_severity} {error_type} error for sync {getattr(sync_engine, "name", "?" )}')

        recovery_result = {
            'error_type': error_type,
            'severity': error_severity,
            'recovered': False,
            'actions_taken': [],
            'recommendations': error_info.get('recommendations', []) if isinstance(error_info, dict) else [],
        }

        try:
            # Attempt basic recovery strategies based on keywords
            msg = str(error).lower()
            if 'connection' in msg or 'timeout' in msg:
                # Suggest retry
                recovery_result.update({
                    'recovered': False,
                    'actions_taken': ['retry suggested'],
                    'recommendations': ['Check connectivity', 'Increase retry settings']
                })
            elif 'mapping' in msg or 'unmapped' in msg or 'balance' in msg:
                # Isolate problematic moves
                problematic = sync_engine.media_move_ids.filtered(lambda m: not m.is_balanced or not m.line_ids)
                if problematic:
                    problematic.write({'state': 'error', 'error_message': 'Isolated by recovery engine'})
                    recovery_result.update({
                        'recovered': True,
                        'actions_taken': [f'Isolated {len(problematic)} problematic moves'],
                    })
            else:
                recovery_result.update({
                    'recovered': False,
                    'actions_taken': [],
                })

            # Update sync engine state
            if recovery_result.get('recovered'):
                sync_engine.write({'state': 'draft', 'error_message': False})
            else:
                sync_engine.write({'state': 'error', 'error_message': str(error)[:500]})

        except Exception as recovery_error:
            _logger.error(f'Error recovery failed: {str(recovery_error)}')
            recovery_result['recovery_failed'] = str(recovery_error)

        # Store recovery result into consolidation.log if available
        try:
            self._store_recovery_result(sync_engine, recovery_result)
        except Exception:
            _logger.exception('Failed to store recovery result')

        return recovery_result

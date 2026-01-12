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
        moves = media_moves if hasattr(media_moves, 'mapped') else (media_moves or [])

        for media_move in moves:
            if media_move.state == 'promoted':
                continue

            try:
                if not media_move.mapped_journal_id:
                    journal = self._get_consolidation_journal(media_move.company_id)
                    if not journal:
                        raise ValidationError(
                            _('No journal mapping found for move %s and no default consolidation journal') % 
                            media_move.name
                        )
                    media_move.mapped_journal_id = journal

                unmapped_lines = media_move.line_ids.filtered(lambda l: not l.mapped_account_id)
                if unmapped_lines:
                    raise ValidationError(
                        _('Move %s has unmapped accounts: %s') % 
                        (media_move.name, ', '.join(unmapped_lines.mapped('account_code')))
                    )

                move_vals = self._prepare_move_vals(media_move)
                account_move = self.env['account.move'].create(move_vals)

                # Use public API to post the move. Avoid private/non-documented helpers.
                try:
                    account_move.action_post()
                except Exception as e:
                    # If posting fails due to permissions, surface the error
                    _logger.error(f'Failed to post account.move {account_move.id}: {str(e)}')
                    raise

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

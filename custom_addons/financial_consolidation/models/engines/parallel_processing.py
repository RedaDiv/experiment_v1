from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class ParallelProcessing(models.AbstractModel):
    _name = 'parallel.processing'
    _description = 'Parallel Processing Manager (safe sequential fallback)'

    @api.model
    def execute_parallel(self, items, process_func, max_workers=4):
        """Sequential execution fallback for parallel processing.

        NOTE: Odoo ORM is not thread-safe. Running ORM operations inside
        ThreadPoolExecutor can corrupt state and crash workers. This helper
        therefore executes tasks sequentially and logs a clear warning. If
        true parallelism is required, implement an external worker pool that
        connects via RPC.
        """
        results = []
        _logger.warning('ParallelProcessing.execute_parallel: running sequential fallback to avoid ORM threading issues')
        for item in items:
            try:
                res = process_func(item)
                results.append(res)
            except Exception as e:
                _logger.error(f'Parallel (sequential fallback) task failed: {str(e)}')
        return results

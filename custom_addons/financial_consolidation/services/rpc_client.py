from odoo import models, api, _
from odoo.exceptions import UserError
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)


class RPCClient(models.AbstractModel):
    _name = 'rpc.client'
    _description = 'RPC Client Service'

    @api.model
    def connect(self, host, database, username, password):
        """Establish RPC connection (fresh connection every call).

        Pooling/reusing ServerProxy objects across threads/requests is unsafe
        because ServerProxy objects are not guaranteed to be thread-safe. We
        therefore create a fresh connection per call. This is simpler and safer
        for Odoo worker / threaded environments.
        """
        try:
            common = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/common')
            uid = common.authenticate(database, username, password, {})

            if not uid:
                raise UserError(_('Authentication failed'))

            models = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/object')

            return uid, models

        except Exception as e:
            _logger.error(f'RPC connection failed: {str(e)}')
            raise UserError(_('Connection failed: %s') % str(e))

    @api.model
    def execute(self, host, database, username, password, model, method, *args, **kwargs):
        """Execute RPC method using a fresh connection."""
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
    _description = 'RPC Connection Pool Manager (compat shim)'

    @api.model
    def get_connection(self, host, db_name, username, password, max_connections=5):
        """Compatibility shim: returns a fresh connection tuple (uid, models).

        Previously the code attempted to pool connections and reuse them across
        threads which is unsafe. Callers should use rpc.client.connect or this
        helper which returns a fresh connection.
        """
        try:
            common = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/common')
            uid = common.authenticate(db_name, username, password, {})
            if not uid:
                raise Exception('Authentication failed')
            models = xmlrpc.client.ServerProxy(f'{host}/xmlrpc/2/object')
            return (uid, models)
        except Exception as e:
            _logger.error(f'RPCPool get_connection failed: {str(e)}')
            raise

    @api.model
    def release_connection(self, host, db_name, username, password, connection):
        """No-op release for compatibility."""
        return True

    @api.model
    def cleanup_pool(self):
        """No-op cleanup (pooling removed)."""
        return True

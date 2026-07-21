import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PastelSyncEngine(models.AbstractModel):
    _name = 'pastel.sync.engine'
    _description = 'Pastel Sync Engine'

    DEBTORS_TABLE = 'DebtorsMaster'
    STOCK_TABLE = 'StockMaster'
    TRANS_TABLE = 'DebtorTrans'
    TRANS_LINES_TABLE = 'DebtorTransLines'

    DEBTOR_FIELDS = [
        'AccountCode', 'AccountName', 'ContactPerson',
        'Address1', 'Address2', 'Address3', 'Address4', 'PostalCode',
        'Phone', 'Fax', 'Email',
        'VatRegNo', 'CreditLimit', 'CurrentBalance',
        'TermsCode', 'SalesRepCode', 'PriceCode',
        'Active', 'DateCreated', 'LastActivity',
    ]

    STOCK_FIELDS = [
        'StockCode', 'Description1', 'Description2',
        'UnitOfMeasure', 'SellingPrice1', 'SellingPrice2',
        'SellingPrice3', 'SellingPrice4', 'SellingPrice5',
        'CostPrice', 'CostPriceAve', 'QtyOnHand',
        'QtyOnOrder', 'QtyAllocated', 'QtyAvailable',
        'SupplierCode', 'SupplierStockCode',
        'StockGroupCode', 'Taxable',
        'Active', 'DateCreated', 'LastActivity',
    ]

    TRANS_FIELDS = [
        'TransactNo', 'AccountCode', 'TransDate', 'Type',
        'Reference', 'Description', 'Amount', 'TaxAmount',
        'AllocAmount', 'Outstanding', 'DueDate',
        'CurrencyCode', 'ExchRate', 'CreatedBy',
    ]

    # --- Parters ---

    @api.model
    def fetch_pastel_debtors(self, active_only=False):
        db = self.env['pastel.odbc.manager']
        field_list = ', '.join(self.DEBTOR_FIELDS)
        sql = f'SELECT {field_list} FROM {self.DEBTORS_TABLE}'
        clauses = []
        if active_only:
            clauses.append("Active = 'Y'")
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
        sql += ' ORDER BY AccountCode'
        return db.execute_query(sql)

    @api.model
    def fetch_pastel_debtor(self, account_code):
        db = self.env['pastel.odbc.manager']
        field_list = ', '.join(self.DEBTOR_FIELDS)
        rows = db.execute_query(
            f'SELECT {field_list} FROM {self.DEBTORS_TABLE} WHERE AccountCode = ?',
            [account_code]
        )
        return rows[0] if rows else None

    @api.model
    def fetch_pastel_debtor_by_vat(self, vat):
        if not vat:
            return None
        db = self.env['pastel.odbc.manager']
        field_list = ', '.join(self.DEBTOR_FIELDS)
        rows = db.execute_query(
            f'SELECT {field_list} FROM {self.DEBTORS_TABLE} WHERE VatRegNo = ?',
            [vat]
        )
        return rows[0] if rows else None

    @api.model
    def create_pastel_debtor(self, data):
        db = self.env['pastel.odbc.manager']
        keys = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join(['?'] * len(keys))
        columns = ', '.join(keys)
        db.execute_query(
            f'INSERT INTO {self.DEBTORS_TABLE} ({columns}) VALUES ({placeholders})',
            values
        )

    @api.model
    def update_pastel_debtor(self, account_code, data):
        db = self.env['pastel.odbc.manager']
        set_clause = ', '.join([f'{k} = ?' for k in data])
        values = list(data.values()) + [account_code]
        db.execute_query(
            f'UPDATE {self.DEBTORS_TABLE} SET {set_clause} WHERE AccountCode = ?',
            values
        )

    def upsert_pastel_debtor(self, data):
        existing = self.fetch_pastel_debtor(data.get('AccountCode', ''))
        if existing:
            self.update_pastel_debtor(data['AccountCode'], data)
            return {'action': 'updated', 'key': data['AccountCode']}
        self.create_pastel_debtor(data)
        return {'action': 'created', 'key': data['AccountCode']}

    # --- Products ---

    @api.model
    def fetch_pastel_stock(self, active_only=False):
        db = self.env['pastel.odbc.manager']
        field_list = ', '.join(self.STOCK_FIELDS)
        sql = f'SELECT {field_list} FROM {self.STOCK_TABLE}'
        clauses = []
        if active_only:
            clauses.append("Active = 'Y'")
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
        sql += ' ORDER BY StockCode'
        return db.execute_query(sql)

    @api.model
    def fetch_pastel_stock_item(self, stock_code):
        db = self.env['pastel.odbc.manager']
        field_list = ', '.join(self.STOCK_FIELDS)
        rows = db.execute_query(
            f'SELECT {field_list} FROM {self.STOCK_TABLE} WHERE StockCode = ?',
            [stock_code]
        )
        return rows[0] if rows else None

    @api.model
    def create_pastel_stock(self, data):
        db = self.env['pastel.odbc.manager']
        keys = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join(['?'] * len(keys))
        columns = ', '.join(keys)
        db.execute_query(
            f'INSERT INTO {self.STOCK_TABLE} ({columns}) VALUES ({placeholders})',
            values
        )

    @api.model
    def update_pastel_stock(self, stock_code, data):
        db = self.env['pastel.odbc.manager']
        set_clause = ', '.join([f'{k} = ?' for k in data])
        values = list(data.values()) + [stock_code]
        db.execute_query(
            f'UPDATE {self.STOCK_TABLE} SET {set_clause} WHERE StockCode = ?',
            values
        )

    def upsert_pastel_stock(self, data):
        existing = self.fetch_pastel_stock_item(data.get('StockCode', ''))
        if existing:
            self.update_pastel_stock(data['StockCode'], data)
            return {'action': 'updated', 'key': data['StockCode']}
        self.create_pastel_stock(data)
        return {'action': 'created', 'key': data['StockCode']}

    # --- Invoices ---

    @api.model
    def fetch_pastel_transactions(self, from_date=None, account_code=None):
        db = self.env['pastel.odbc.manager']
        field_list = ', '.join(self.TRANS_FIELDS)
        sql = f'SELECT {field_list} FROM {self.TRANS_TABLE}'
        clauses = []
        params = []
        if from_date:
            clauses.append('TransDate >= ?')
            params.append(from_date)
        if account_code:
            clauses.append('AccountCode = ?')
            params.append(account_code)
        if clauses:
            sql += ' WHERE ' + ' AND '.join(clauses)
        sql += ' ORDER BY TransDate DESC'
        return db.execute_query(sql, params)

    @api.model
    def create_pastel_transaction_header(self, data):
        db = self.env['pastel.odbc.manager']
        keys = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join(['?'] * len(keys))
        columns = ', '.join(keys)
        db.execute_query(
            f'INSERT INTO {self.TRANS_TABLE} ({columns}) VALUES ({placeholders})',
            values
        )

    @api.model
    def create_pastel_transaction_line(self, data):
        db = self.env['pastel.odbc.manager']
        keys = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join(['?'] * len(keys))
        columns = ', '.join(keys)
        db.execute_query(
            f'INSERT INTO {self.TRANS_LINES_TABLE} ({columns}) VALUES ({placeholders})',
            values
        )

    # --- Mapping Helpers ---

    @staticmethod
    def _safe_field(record, field_name, default=''):
        if field_name in record._fields:
            val = getattr(record, field_name)
            return val if val is not False else default
        return default

    @api.model
    def _map_odoo_partner_to_pastel(self, partner):
        addr = self._split_address(partner)
        return {
            'AccountCode': (partner.ref or str(partner.id))[:15].upper(),
            'AccountName': (partner.name or '')[:50],
            'ContactPerson': '',
            'Address1': addr[0][:50],
            'Address2': addr[1][:50],
            'Address3': addr[2][:50],
            'Address4': addr[3][:50],
            'PostalCode': (partner.zip or '')[:10],
            'Phone': (partner.phone or self._safe_field(partner, 'mobile') or '')[:30],
            'Fax': (self._safe_field(partner, 'fax') or '')[:30],
            'Email': (partner.email or '')[:60],
            'VatRegNo': (partner.vat or '').replace(' ', '')[:20],
            'CreditLimit': partner.credit_limit or 0,
            'Active': 'Y' if partner.active else 'N',
        }

    @api.model
    def _map_pastel_debtor_to_odoo(self, debtor):
        return {
            'ref': debtor['AccountCode'],
            'name': (debtor.get('AccountName', '') or '')[:150],
            'street': (debtor.get('Address1', '') or '')[:128],
            'street2': (debtor.get('Address2', '') or '')[:128],
            'city': (debtor.get('Address3', '') or '')[:128],
            'zip': (debtor.get('PostalCode', '') or '')[:24],
            'email': (debtor.get('Email', '') or '')[:240],
            'phone': (debtor.get('Phone', '') or '')[:64],
            'fax': (debtor.get('Fax', '') or '')[:64],
            'vat': (debtor.get('VatRegNo', '') or '')[:40],
            'credit_limit': debtor.get('CreditLimit', 0) or 0,
            'active': debtor.get('Active') == 'Y',
            'company_type': 'company',
            'customer_rank': 1,
        }

    @api.model
    def _map_odoo_product_to_pastel(self, product):
        uom = product.uom_id.name if product.uom_id else 'Each'
        return {
            'StockCode': (product.default_code or f'P{product.id}')[:30].upper(),
            'Description1': (product.name or '')[:60],
            'Description2': (product.description_sale or '')[:60],
            'UnitOfMeasure': uom[:10],
            'SellingPrice1': product.list_price or 0,
            'CostPrice': product.standard_price or 0,
            'CostPriceAve': product.standard_price or 0,
            'Taxable': 'Y',
            'Active': 'Y' if product.active else 'N',
        }

    @api.model
    def _map_pastel_stock_to_odoo(self, item):
        return {
            'default_code': item['StockCode'],
            'name': (item.get('Description1', '') or item.get('StockCode', ''))[:200],
            'description_sale': (item.get('Description2', '') or '')[:255],
            'list_price': item.get('SellingPrice1', 0) or 0,
            'standard_price': item.get('CostPrice', 0) or item.get('CostPriceAve', 0) or 0,
            'type': 'product',
            'active': item.get('Active') == 'Y',
        }

    @api.model
    def _map_odoo_invoice_to_pastel(self, invoice, account_code):
        return {
            'AccountCode': account_code,
            'TransDate': str(invoice.invoice_date or fields.Date.today()),
            'DueDate': str(invoice.invoice_date_due or invoice.invoice_date or fields.Date.today()),
            'Type': 'INV',
            'Reference': (invoice.name or '')[:30],
            'Description': (invoice.ref or invoice.name or '')[:60],
            'Amount': invoice.amount_total or 0,
            'TaxAmount': invoice.amount_tax or 0,
            'CurrencyCode': 'ZAR',
            'ExchRate': 1,
        }

    @api.model
    def _map_odoo_line_to_pastel(self, line, line_num):
        stock_code = ''
        if line.product_id and line.product_id.default_code:
            stock_code = line.product_id.default_code[:30]
        return {
            'LineNo': line_num,
            'StockCode': stock_code,
            'Description': (line.name or '')[:60],
            'Quantity': line.quantity or 1,
            'UnitPrice': line.price_unit or 0,
            'DiscountPct': line.discount or 0,
            'LineTotal': line.price_subtotal or 0,
        }

    @staticmethod
    def _split_address(partner):
        parts = []
        if partner.street:
            parts.append(partner.street)
        if partner.street2:
            parts.append(partner.street2)
        if partner.city:
            parts.append(partner.city)
        state_name = partner.state_id.name if partner.state_id else ''
        if state_name:
            parts.append(state_name)
        country_name = partner.country_id.name if partner.country_id else ''
        if country_name:
            parts.append(country_name)
        while len(parts) < 4:
            parts.append('')
        return parts

    # --- Sync Operations ---

    def sync_partners_odoo_to_pastel(self):
        partners = self.env['res.partner'].search([('customer_rank', '>', 0)])
        results = {'created': 0, 'updated': 0, 'skipped': 0}
        for partner in partners:
            data = self._map_odoo_partner_to_pastel(partner)
            if not data['AccountCode'] or not data['AccountName']:
                results['skipped'] += 1
                continue
            existing = self.fetch_pastel_debtor(data['AccountCode'])
            if existing:
                self.update_pastel_debtor(data['AccountCode'], data)
                results['updated'] += 1
            else:
                self.create_pastel_debtor(data)
                results['created'] += 1
        return results

    def sync_partners_pastel_to_odoo(self):
        debtors = self.fetch_pastel_debtors()
        results = {'created': 0, 'updated': 0, 'skipped': 0}
        Partner = self.env['res.partner']
        for debtor in debtors:
            data = self._map_pastel_debtor_to_odoo(debtor)
            existing = Partner.search([('ref', '=', data['ref'])], limit=1)
            if existing:
                existing.write(data)
                results['updated'] += 1
            else:
                Partner.create(data)
                results['created'] += 1
        return results

    def sync_products_odoo_to_pastel(self):
        products = self.env['product.product'].search([('sale_ok', '=', True)])
        results = {'created': 0, 'updated': 0, 'skipped': 0}
        for product in products:
            data = self._map_odoo_product_to_pastel(product)
            if not data['StockCode'] or not data['Description1']:
                results['skipped'] += 1
                continue
            existing = self.fetch_pastel_stock_item(data['StockCode'])
            if existing:
                self.update_pastel_stock(data['StockCode'], data)
                results['updated'] += 1
            else:
                self.create_pastel_stock(data)
                results['created'] += 1
        return results

    def sync_products_pastel_to_odoo(self):
        stock = self.fetch_pastel_stock()
        results = {'created': 0, 'updated': 0, 'skipped': 0}
        Product = self.env['product.product']
        for item in stock:
            data = self._map_pastel_stock_to_odoo(item)
            existing = Product.search([('default_code', '=', data['default_code'])], limit=1)
            if existing:
                existing.write(data)
                results['updated'] += 1
            else:
                try:
                    Product.create(data)
                    results['created'] += 1
                except Exception as e:
                    _logger.warning('Failed to create product %s: %s', data['default_code'], e)
                    results['skipped'] += 1
        return results

    def sync_invoices_odoo_to_pastel(self):
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ])
        results = {'created': 0, 'skipped': 0}
        for inv in invoices:
            partner = inv.partner_id
            if not partner:
                results['skipped'] += 1
                continue
            account_code = (partner.ref or str(partner.id))[:15].upper()
            debtor = self.fetch_pastel_debtor(account_code)
            if not debtor:
                _logger.warning('Debtor %s not found in Pastel, skipping invoice %s', account_code, inv.name)
                results['skipped'] += 1
                continue
            header = self._map_odoo_invoice_to_pastel(inv, account_code)
            self.create_pastel_transaction_header(header)
            for i, line in enumerate(inv.invoice_line_ids, 1):
                line_data = self._map_odoo_line_to_pastel(line, i)
                self.create_pastel_transaction_line(line_data)
            results['created'] += 1
        return results

    def run_full_sync(self, direction='bidirectional', scope='all'):
        output = []
        if direction in ('odoo-to-pastel', 'bidirectional'):
            if scope in ('all', 'partners'):
                r = self.sync_partners_odoo_to_pastel()
                output.append(f'Partners Odoo->Pastel: {r["created"]} created, {r["updated"]} updated, {r["skipped"]} skipped')
            if scope in ('all', 'products'):
                r = self.sync_products_odoo_to_pastel()
                output.append(f'Products Odoo->Pastel: {r["created"]} created, {r["updated"]} updated, {r["skipped"]} skipped')
            if scope in ('all', 'invoices'):
                r = self.sync_invoices_odoo_to_pastel()
                output.append(f'Invoices Odoo->Pastel: {r["created"]} created, {r["skipped"]} skipped')
        if direction in ('pastel-to-odoo', 'bidirectional'):
            if scope in ('all', 'partners'):
                r = self.sync_partners_pastel_to_odoo()
                output.append(f'Partners Pastel->Odoo: {r["created"]} created, {r["updated"]} updated, {r["skipped"]} skipped')
            if scope in ('all', 'products'):
                r = self.sync_products_pastel_to_odoo()
                output.append(f'Products Pastel->Odoo: {r["created"]} created, {r["updated"]} updated, {r["skipped"]} skipped')
        return '\n'.join(output)
